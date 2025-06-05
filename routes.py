from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, db
from models import User, Quiz, Question, QuizResult
from gemini_service import GeminiQuizService
import json
from datetime import datetime
from sqlalchemy import desc

# Initialize Gemini service
gemini_service = GeminiQuizService()

@app.route('/')
def index():
    """Home page with quiz categories and recent activity"""
    recent_quizzes = Quiz.query.order_by(desc(Quiz.created_at)).limit(5).all()
    top_users = db.session.query(User).join(QuizResult).group_by(User.id).order_by(desc(db.func.avg(QuizResult.score))).limit(5).all()
    
    question_types = [
        {'name': 'Multiple Choice', 'value': 'mcq', 'icon': 'list-ul', 'description': 'Choose from multiple options'},
        {'name': 'True or False', 'value': 'true_false', 'icon': 'check-circle', 'description': 'Simple true/false questions'},
        {'name': 'Fill in the Blank', 'value': 'fill_blank', 'icon': 'edit', 'description': 'Complete the missing words'},
        {'name': 'Mixed Questions', 'value': 'mixed', 'icon': 'random', 'description': 'Combination of all question types'}
    ]
    
    return render_template('index.html', question_types=question_types, recent_quizzes=recent_quizzes, top_users=top_users)

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    """Create a new quiz using Gemini AI"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        question_type = request.form.get('question_type')
        difficulty = request.form.get('difficulty')
        num_questions = int(request.form.get('num_questions', 10))
        
        if not all([topic, question_type, difficulty]):
            flash('All fields are required!', 'error')
            return redirect(url_for('index'))
        
        try:
            # Create quiz record
            quiz = Quiz(
                title=f"{topic} Quiz ({difficulty.title()})",
                category=question_type.replace('_', ' ').title(),
                difficulty=difficulty
            )
            db.session.add(quiz)
            db.session.flush()  # Get the quiz ID
            
            # Generate questions using Gemini
            questions_data = gemini_service.generate_quiz_questions(topic, difficulty, num_questions, question_type)
            
            if not questions_data:
                flash('Failed to generate quiz questions. Please try again.', 'error')
                db.session.rollback()
                return redirect(url_for('index'))
            
            # Save questions to database
            for q_data in questions_data:
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_data['question_text'],
                    question_type=q_data['question_type'],
                    correct_answer=q_data['correct_answer'],
                    options=q_data['options'],
                    points=q_data['points'],
                    order=q_data['order']
                )
                db.session.add(question)
            
            db.session.commit()
            flash(f'Quiz "{quiz.title}" created successfully!', 'success')
            return redirect(url_for('take_quiz', quiz_id=quiz.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quiz: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    """Take a specific quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
    
    if not questions:
        flash('This quiz has no questions!', 'error')
        return redirect(url_for('index'))
    
    # Prepare questions for template
    quiz_data = {
        'id': quiz.id,
        'title': quiz.title,
        'category': quiz.category,
        'difficulty': quiz.difficulty,
        'total_questions': len(questions),
        'questions': []
    }
    
    for q in questions:
        question_data = {
            'id': q.id,
            'text': q.question_text,
            'type': q.question_type,
            'points': q.points,
            'order': q.order
        }
        
        if q.options:
            try:
                question_data['options'] = json.loads(q.options)
            except:
                question_data['options'] = []
        
        quiz_data['questions'].append(question_data)
    
    return render_template('quiz.html', quiz=quiz_data)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and calculate score"""
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        username = data.get('username', 'Anonymous')
        email = data.get('email', f'user_{datetime.now().timestamp()}@quiz.app')
        
        # Get or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            # Check if username exists, if so modify it
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                username = f"{username}_{datetime.now().timestamp()}"
            
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.flush()
        
        # Get quiz and questions
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        # Calculate score
        score = 0
        total_points = 0
        results = {}
        
        for question in questions:
            total_points += question.points
            user_answer = answers.get(str(question.id), '').strip().lower()
            correct_answer = question.correct_answer.strip().lower()
            
            is_correct = False
            if question.question_type == 'true_false':
                is_correct = user_answer == correct_answer
            elif question.question_type == 'mcq':
                is_correct = user_answer == correct_answer.lower()
            elif question.question_type == 'fill_blank':
                # More flexible matching for fill in the blank
                is_correct = user_answer in correct_answer or correct_answer in user_answer
            
            if is_correct:
                score += question.points
            
            results[str(question.id)] = {
                'user_answer': answers.get(str(question.id), ''),
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'points_earned': question.points if is_correct else 0
            }
        
        # Save quiz result
        quiz_result = QuizResult(
            user_id=user.id,
            quiz_id=quiz_id,
            score=score,
            total_questions=len(questions),
            time_taken=time_taken,
            answers=json.dumps(results)
        )
        db.session.add(quiz_result)
        db.session.commit()
        
        # Calculate percentage
        percentage = (score / total_points * 100) if total_points > 0 else 0
        
        return jsonify({
            'success': True,
            'score': score,
            'total_points': total_points,
            'percentage': round(percentage, 1),
            'results': results,
            'result_id': quiz_result.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/results/<int:result_id>')
def quiz_results(result_id):
    """Display quiz results"""
    result = QuizResult.query.get_or_404(result_id)
    quiz = result.quiz
    user = result.user
    
    # Parse answers
    try:
        answers_data = json.loads(result.answers)
    except:
        answers_data = {}
    
    # Get questions for detailed results
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order).all()
    
    detailed_results = []
    for question in questions:
        q_result = answers_data.get(str(question.id), {})
        
        question_result = {
            'question': question.question_text,
            'type': question.question_type,
            'user_answer': q_result.get('user_answer', 'No answer'),
            'correct_answer': q_result.get('correct_answer', question.correct_answer),
            'is_correct': q_result.get('is_correct', False),
            'points_earned': q_result.get('points_earned', 0),
            'max_points': question.points
        }
        
        if question.options:
            try:
                question_result['options'] = json.loads(question.options)
            except:
                question_result['options'] = []
        
        detailed_results.append(question_result)
    
    # Calculate percentage
    percentage = (result.score / sum(q.points for q in questions) * 100) if questions else 0
    
    return render_template('results.html', 
                         result=result, 
                         quiz=quiz, 
                         user=user, 
                         percentage=round(percentage, 1),
                         detailed_results=detailed_results)

@app.route('/leaderboard')
def leaderboard():
    """Display global leaderboard"""
    # Get top users by average score
    top_users_avg = db.session.query(
        User.username,
        User.email,
        db.func.avg(QuizResult.score).label('avg_score'),
        db.func.count(QuizResult.id).label('quiz_count'),
        db.func.sum(QuizResult.score).label('total_score')
    ).join(QuizResult).group_by(User.id).order_by(desc('avg_score')).limit(20).all()
    
    # Get recent high scores
    recent_scores = db.session.query(QuizResult, User, Quiz).join(User).join(Quiz).order_by(desc(QuizResult.completed_at)).limit(10).all()
    
    # Get category leaders
    category_leaders = db.session.query(
        Quiz.category,
        User.username,
        db.func.max(QuizResult.score).label('best_score')
    ).join(Quiz).join(User).group_by(Quiz.category).all()
    
    return render_template('leaderboard.html', 
                         top_users=top_users_avg,
                         recent_scores=recent_scores,
                         category_leaders=category_leaders)

@app.route('/quiz_list')
def quiz_list():
    """List all available quizzes"""
    quizzes = Quiz.query.order_by(desc(Quiz.created_at)).all()
    return render_template('quiz_list.html', quizzes=quizzes)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
