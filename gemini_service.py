import os
import json
import logging
import google.generativeai as genai
from typing import List, Dict, Any

class GeminiQuizService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "default-api-key")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def generate_quiz_questions(self, topic: str, difficulty: str, num_questions: int = 10, question_type: str = "mixed") -> List[Dict[str, Any]]:
        """Generate quiz questions using Gemini AI"""
        try:
            prompt = self._create_quiz_prompt(topic, difficulty, num_questions, question_type)
            response = self.model.generate_content(prompt)
            
            # Parse the response
            questions = self._parse_gemini_response(response.text)
            return questions
            
        except Exception as e:
            logging.error(f"Error generating quiz questions: {str(e)}")
            return self._get_fallback_questions(topic, difficulty, num_questions, question_type)
    
    def _create_quiz_prompt(self, topic: str, difficulty: str, num_questions: int, question_type: str = "mixed") -> str:
        """Create a structured prompt for quiz generation"""
        
        if question_type == "mcq":
            type_instruction = "Generate ONLY Multiple Choice Questions (4 options each)"
        elif question_type == "true_false":
            type_instruction = "Generate ONLY True/False Questions"
        elif question_type == "fill_blank":
            type_instruction = "Generate ONLY Fill in the blank Questions"
        else:  # mixed
            type_instruction = "Mix different question types: Multiple Choice (4 options), True/False, and Fill in the blank"
        
        return f"""
        Generate {num_questions} quiz questions about {topic} at {difficulty} difficulty level.
        
        {type_instruction}
        
        Return the response in this exact JSON format:
        {{
            "questions": [
                {{
                    "type": "mcq",
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Brief explanation"
                }},
                {{
                    "type": "true_false",
                    "question": "Statement to evaluate",
                    "correct_answer": "true",
                    "explanation": "Brief explanation"
                }},
                {{
                    "type": "fill_blank",
                    "question": "Question with _____ to fill",
                    "correct_answer": "missing word",
                    "explanation": "Brief explanation"
                }}
            ]
        }}
        
        Make sure questions are educational, accurate, and appropriate for the {difficulty} level.
        Focus on {topic} and ensure variety based on the requested question type.
        """
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Gemini's response and extract questions"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse JSON
            data = json.loads(response_text)
            questions = data.get('questions', [])
            
            # Validate and format questions
            formatted_questions = []
            for i, q in enumerate(questions):
                formatted_q = {
                    'question_text': q.get('question', ''),
                    'question_type': q.get('type', 'mcq'),
                    'correct_answer': q.get('correct_answer', ''),
                    'options': json.dumps(q.get('options', [])) if q.get('options') else None,
                    'points': 1,
                    'order': i + 1
                }
                formatted_questions.append(formatted_q)
            
            return formatted_questions
            
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Error parsing Gemini response: {str(e)}")
            return []
    
    def _get_fallback_questions(self, topic: str, difficulty: str, num_questions: int, question_type: str = "mixed") -> List[Dict[str, Any]]:
        """Provide fallback questions when API fails"""
        fallback_questions = [
            {
                'question_text': f'What is a key concept in {topic}?',
                'question_type': 'mcq',
                'correct_answer': 'Fundamental principles',
                'options': json.dumps(['Fundamental principles', 'Random facts', 'Unrelated topics', 'None of the above']),
                'points': 1,
                'order': 1
            },
            {
                'question_text': f'{topic} is an important subject to study.',
                'question_type': 'true_false',
                'correct_answer': 'true',
                'options': None,
                'points': 1,
                'order': 2
            },
            {
                'question_text': f'The study of {topic} involves understanding _____ concepts.',
                'question_type': 'fill_blank',
                'correct_answer': 'key',
                'options': None,
                'points': 1,
                'order': 3
            }
        ]
        
        # Repeat and limit to requested number
        questions = (fallback_questions * ((num_questions // 3) + 1))[:num_questions]
        
        # Update order numbers
        for i, q in enumerate(questions):
            q['order'] = i + 1
            
        return questions
