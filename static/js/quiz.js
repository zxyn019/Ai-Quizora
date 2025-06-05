// Quiz Master - Interactive Quiz JavaScript

class QuizApp {
    constructor() {
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.timeRemaining = 300; // 5 minutes in seconds
        this.timer = null;
        this.username = '';
        this.email = '';
        this.startTime = null;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Start quiz button
        document.getElementById('startQuizBtn').addEventListener('click', () => {
            this.startQuiz();
        });
        
        // Navigation buttons
        document.getElementById('prevBtn').addEventListener('click', () => {
            this.previousQuestion();
        });
        
        document.getElementById('nextBtn').addEventListener('click', () => {
            this.nextQuestion();
        });
        
        document.getElementById('submitBtn').addEventListener('click', () => {
            this.submitQuiz();
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (document.getElementById('quizSection').style.display !== 'none') {
                if (e.key === 'ArrowLeft') this.previousQuestion();
                if (e.key === 'ArrowRight') this.nextQuestion();
                if (e.key === 'Enter' && this.currentQuestionIndex === QUIZ_DATA.questions.length - 1) {
                    this.submitQuiz();
                }
            }
        });
    }
    
    startQuiz() {
        // Validate user info
        const usernameInput = document.getElementById('username');
        const emailInput = document.getElementById('email');
        
        if (!usernameInput.value.trim()) {
            usernameInput.focus();
            this.showError('Please enter your name');
            return;
        }
        
        this.username = usernameInput.value.trim();
        this.email = emailInput.value.trim() || `user_${Date.now()}@quiz.app`;
        
        // Hide user info section and show quiz
        document.getElementById('userInfoSection').style.display = 'none';
        document.getElementById('quizSection').style.display = 'block';
        
        // Start timer
        this.startTime = Date.now();
        this.startTimer();
        
        // Show first question
        this.showQuestion(0);
        
        // Add fade-in animation
        document.getElementById('quizSection').classList.add('fade-in');
    }
    
    startTimer() {
        this.timer = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            if (this.timeRemaining <= 0) {
                this.timeUp();
            } else if (this.timeRemaining <= 60) {
                // Add urgent styling when less than 1 minute
                document.getElementById('timer').classList.add('urgent');
            }
        }, 1000);
    }
    
    updateTimerDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        document.getElementById('timer').textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    timeUp() {
        clearInterval(this.timer);
        this.showError('Time\'s up! Quiz will be submitted automatically.');
        setTimeout(() => {
            this.submitQuiz();
        }, 2000);
    }
    
    showQuestion(index) {
        if (index < 0 || index >= QUIZ_DATA.questions.length) return;
        
        this.currentQuestionIndex = index;
        const question = QUIZ_DATA.questions[index];
        
        // Update progress
        this.updateProgress();
        
        // Generate question HTML
        let questionHTML = `
            <div class="question-header mb-4">
                <h4 class="question-title">
                    <span class="badge bg-secondary me-2">${question.type.replace('_', ' ').toUpperCase()}</span>
                    Question ${index + 1}
                </h4>
                <p class="question-text fs-5">${question.text}</p>
            </div>
            <div class="question-answers">
        `;
        
        if (question.type === 'mcq') {
            questionHTML += this.generateMCQHTML(question, index);
        } else if (question.type === 'true_false') {
            questionHTML += this.generateTrueFalseHTML(question, index);
        } else if (question.type === 'fill_blank') {
            questionHTML += this.generateFillBlankHTML(question, index);
        }
        
        questionHTML += '</div>';
        
        // Update content with animation
        const questionContent = document.getElementById('questionContent');
        questionContent.style.opacity = '0';
        
        setTimeout(() => {
            questionContent.innerHTML = questionHTML;
            questionContent.style.opacity = '1';
            
            // Add event listeners for new elements
            this.addAnswerEventListeners(question.type, index);
        }, 150);
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }
    
    generateMCQHTML(question, questionIndex) {
        let html = '<div class="mcq-options">';
        
        question.options.forEach((option, optionIndex) => {
            const isSelected = this.userAnswers[question.id] === option;
            html += `
                <div class="answer-option card mb-2 ${isSelected ? 'selected' : ''}" 
                     data-question-id="${question.id}" 
                     data-answer="${option}">
                    <div class="card-body d-flex align-items-center">
                        <div class="form-check">
                            <input class="form-check-input" type="radio" 
                                   name="question_${question.id}" 
                                   value="${option}" 
                                   id="option_${question.id}_${optionIndex}"
                                   ${isSelected ? 'checked' : ''}>
                            <label class="form-check-label ms-2" for="option_${question.id}_${optionIndex}">
                                ${option}
                            </label>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }
    
    generateTrueFalseHTML(question, questionIndex) {
        const selectedAnswer = this.userAnswers[question.id];
        
        return `
            <div class="true-false-options">
                <div class="row">
                    <div class="col-md-6">
                        <div class="answer-option card ${selectedAnswer === 'true' ? 'selected' : ''}" 
                             data-question-id="${question.id}" 
                             data-answer="true">
                            <div class="card-body text-center">
                                <i class="fas fa-check fa-2x text-success mb-2"></i>
                                <h5>True</h5>
                                <input type="radio" name="question_${question.id}" value="true" 
                                       ${selectedAnswer === 'true' ? 'checked' : ''} style="display: none;">
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="answer-option card ${selectedAnswer === 'false' ? 'selected' : ''}" 
                             data-question-id="${question.id}" 
                             data-answer="false">
                            <div class="card-body text-center">
                                <i class="fas fa-times fa-2x text-danger mb-2"></i>
                                <h5>False</h5>
                                <input type="radio" name="question_${question.id}" value="false" 
                                       ${selectedAnswer === 'false' ? 'checked' : ''} style="display: none;">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    generateFillBlankHTML(question, questionIndex) {
        const userAnswer = this.userAnswers[question.id] || '';
        
        return `
            <div class="fill-blank-section">
                <div class="mb-3">
                    <label for="fill_blank_${question.id}" class="form-label">Your Answer:</label>
                    <input type="text" 
                           class="form-control form-control-lg" 
                           id="fill_blank_${question.id}"
                           data-question-id="${question.id}"
                           value="${userAnswer}"
                           placeholder="Type your answer here..."
                           autocomplete="off">
                </div>
                <div class="text-muted">
                    <small><i class="fas fa-lightbulb me-1"></i>Hint: Fill in the blank with the most appropriate word or phrase</small>
                </div>
            </div>
        `;
    }
    
    addAnswerEventListeners(questionType, questionIndex) {
        if (questionType === 'mcq' || questionType === 'true_false') {
            // Add click listeners for option cards
            document.querySelectorAll('.answer-option').forEach(option => {
                option.addEventListener('click', (e) => {
                    const questionId = option.dataset.questionId;
                    const answer = option.dataset.answer;
                    
                    // Update user answers
                    this.userAnswers[questionId] = answer;
                    
                    // Update UI
                    document.querySelectorAll(`[data-question-id="${questionId}"]`).forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    option.classList.add('selected');
                    
                    // Update radio button
                    const radio = option.querySelector('input[type="radio"]');
                    if (radio) radio.checked = true;
                });
            });
        } else if (questionType === 'fill_blank') {
            // Add input listener for fill in the blank
            const input = document.querySelector('input[data-question-id]');
            if (input) {
                input.addEventListener('input', (e) => {
                    const questionId = e.target.dataset.questionId;
                    this.userAnswers[questionId] = e.target.value.trim();
                });
                
                // Focus on input
                input.focus();
            }
        }
    }
    
    updateProgress() {
        const progress = ((this.currentQuestionIndex + 1) / QUIZ_DATA.questions.length) * 100;
        document.getElementById('progressBar').style.width = `${progress}%`;
        document.getElementById('currentQuestion').textContent = this.currentQuestionIndex + 1;
        document.getElementById('progressPercent').textContent = Math.round(progress);
    }
    
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');
        
        // Previous button
        prevBtn.disabled = this.currentQuestionIndex === 0;
        
        // Next/Submit button
        if (this.currentQuestionIndex === QUIZ_DATA.questions.length - 1) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
        } else {
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
        }
    }
    
    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.showQuestion(this.currentQuestionIndex - 1);
        }
    }
    
    nextQuestion() {
        if (this.currentQuestionIndex < QUIZ_DATA.questions.length - 1) {
            this.showQuestion(this.currentQuestionIndex + 1);
        }
    }
    
    async submitQuiz() {
        // Show loading overlay
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        try {
            const timeTaken = Math.floor((Date.now() - this.startTime) / 1000);
            
            // Debug logging
            console.log('Submitting quiz with data:', {
                quiz_id: QUIZ_DATA.id,
                answers: this.userAnswers,
                time_taken: timeTaken,
                username: this.username,
                email: this.email
            });
            
            const response = await fetch('/submit_quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    quiz_id: QUIZ_DATA.id,
                    answers: this.userAnswers,
                    time_taken: timeTaken,
                    username: this.username,
                    email: this.email
                })
            });
            
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Quiz submission result:', result);
            
            if (result.success) {
                // Clear timer
                if (this.timer) clearInterval(this.timer);
                
                // Redirect to results page
                window.location.href = `/results/${result.result_id}`;
            } else {
                throw new Error(result.error || 'Failed to submit quiz');
            }
            
        } catch (error) {
            console.error('Error submitting quiz:', error);
            console.error('Error details:', error.message);
            this.showError(`Failed to submit quiz: ${error.message}. Please try again.`);
            document.getElementById('loadingOverlay').style.display = 'none';
        }
    }
    
    showError(message) {
        // Create and show error toast
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed top-0 end-0 m-3';
        toast.style.zIndex = '1055';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    // Utility method to get answered questions count
    getAnsweredCount() {
        return Object.keys(this.userAnswers).length;
    }
    
    // Method to highlight unanswered questions
    showUnansweredQuestions() {
        const unanswered = [];
        QUIZ_DATA.questions.forEach((question, index) => {
            if (!this.userAnswers[question.id]) {
                unanswered.push(index + 1);
            }
        });
        return unanswered;
    }
}

// Initialize quiz app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (typeof QUIZ_DATA !== 'undefined') {
        new QuizApp();
    }
});

// Prevent accidental page refresh during quiz
window.addEventListener('beforeunload', (e) => {
    if (document.getElementById('quizSection').style.display !== 'none') {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave? Your quiz progress will be lost.';
        return e.returnValue;
    }
});
