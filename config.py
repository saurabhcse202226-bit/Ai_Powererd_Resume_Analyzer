import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod-pls')
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5mb max - pdfs are usually small
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

    # session stuff
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # set to True in prod with HTTPS

    # anthropic api key - put yours in .env
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

    # score weights - tweak these if needed
    SKILL_MATCH_WEIGHT = 0.35
    EXPERIENCE_WEIGHT = 0.25
    EDUCATION_WEIGHT = 0.20
    KEYWORD_WEIGHT = 0.20
