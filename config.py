import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'daa-exam-generator-super-secret-key-2026')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'exam_generator.db')
    DEBUG = True
    
    # File Storage Paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    GENERATED_PAPERS_FOLDER = os.path.join(BASE_DIR, 'generated_papers')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    
    # AI / LLM Integration Configuration
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'local') # 'local', 'openai', 'gemini'
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_MODEL = os.environ.get('AI_MODEL', 'gemini-1.5-pro')

    # Paper Generation Defaults
    DEFAULT_TOTAL_MARKS = 100
    DEFAULT_QUESTION_COUNT = 10
    DEFAULT_DIFFICULTY_RATIO = {'Easy': 0.30, 'Medium': 0.50, 'Hard': 0.20}
    DEFAULT_UNIT_RATIO = {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20}
    
    # Scoring weights for objective function (sum = 100)
    SCORE_WEIGHTS = {
        'difficulty': 25.0,
        'unit': 25.0,
        'topic': 20.0,
        'marks_fit': 15.0,
        'novelty': 15.0
    }
