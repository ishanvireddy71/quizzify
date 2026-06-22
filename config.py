import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'quizzify-dev-key-2026')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    
    CATEGORIES_FILE = os.path.join(DATA_DIR, 'categories.json')
    QUIZZES_FILE = os.path.join(DATA_DIR, 'quizzes.json')
    LEADERBOARD_FILE = os.path.join(DATA_DIR, 'leaderboard.json')
    ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, 'achievements.json')
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    
    QUIZ_MODES = ['timed', 'practice', 'survival']
    DIFFICULTIES = ['easy', 'medium', 'hard']
    
    DAILY_CHALLENGE_ID = 'daily_challenge'
    DAILY_CHALLENGE_MULTIPLIER = 2.0
    
    MAX_HINTS_PER_QUIZ = 3
    STREAK_BONUS_MULTIPLIER = 0.1
    TIME_BONUS_MULTIPLIER = 0.05
    ACCURACY_BONUS_THRESHOLD = 80