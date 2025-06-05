# Quiz Master - AI-Powered Quiz Platform

A modern quiz application built with Flask and Google Gemini AI that generates dynamic quizzes with multiple question types.

## Features

- **AI-Powered Quiz Generation**: Uses Google Gemini AI to create authentic, topic-specific questions
- **Multiple Question Types**: 
  - Multiple Choice Questions (MCQ)
  - True/False Questions
  - Fill in the Blank Questions
  - Mixed question types
- **Interactive Quiz Interface**: Clean, responsive design with timer functionality
- **Real-time Scoring**: Instant feedback and detailed results
- **Leaderboard System**: Track top performers and recent scores
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL with SQLAlchemy
- **AI Integration**: Google Gemini 1.5 Flash
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Styling**: Replit-themed Bootstrap dark mode

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/quiz-master.git
cd quiz-master
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export DATABASE_URL="your_postgresql_database_url"
export GEMINI_API_KEY="your_google_gemini_api_key"
export SESSION_SECRET="your_session_secret_key"
```

4. Initialize the database:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

5. Run the application:
```bash
python main.py
```

## Usage

1. **Create a Quiz**: Enter a topic, select question type, difficulty, and number of questions
2. **Take the Quiz**: Answer questions with timer, navigate between questions
3. **View Results**: See detailed breakdown of answers and scores
4. **Check Leaderboard**: Compare your performance with other users

## API Endpoints

- `GET /` - Homepage with quiz creation form
- `POST /create_quiz` - Generate new quiz with AI
- `GET /quiz/<id>` - Take a specific quiz
- `POST /submit_quiz` - Submit quiz answers
- `GET /results/<id>` - View quiz results
- `GET /leaderboard` - View leaderboard

## Environment Variables

- `DATABASE_URL` - PostgreSQL database connection string
- `GEMINI_API_KEY` - Google Gemini API key for question generation
- `SESSION_SECRET` - Secret key for Flask sessions

## Getting Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and set it as `GEMINI_API_KEY` environment variable

## Database Schema

- **Users**: Store user information and statistics
- **Quizzes**: Quiz metadata and configuration
- **Questions**: Individual quiz questions with answers
- **Quiz Results**: User scores and detailed results

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for question generation
- Bootstrap for responsive design
- Font Awesome for icons
- Flask community for excellent documentation