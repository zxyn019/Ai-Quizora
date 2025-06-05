from app import db
from datetime import datetime
from sqlalchemy import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with quiz results
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)
    
    def get_total_score(self):
        """Calculate total score across all quizzes"""
        total = db.session.query(func.sum(QuizResult.score)).filter_by(user_id=self.id).scalar()
        return total or 0
    
    def get_average_score(self):
        """Calculate average score across all quizzes"""
        avg = db.session.query(func.avg(QuizResult.score)).filter_by(user_id=self.id).scalar()
        return round(avg, 2) if avg else 0
    
    def get_quiz_count(self):
        """Get total number of quizzes taken"""
        return QuizResult.query.filter_by(user_id=self.id).count()

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with questions and results
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('QuizResult', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # mcq, true_false, fill_blank
    correct_answer = db.Column(db.String(500), nullable=False)
    options = db.Column(db.Text)  # JSON string for MCQ options
    points = db.Column(db.Integer, default=1)
    order = db.Column(db.Integer, nullable=False)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer)  # in seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Store user answers
    answers = db.Column(db.Text)  # JSON string of user answers
