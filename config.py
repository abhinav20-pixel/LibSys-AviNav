import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_key_library'
    DATABASE_URI = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'library.db')
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max for file uploads
