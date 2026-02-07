import os

def get_database_uri():
    """
    Returns the database URI from environment variables, 
    with fallback to SQLite for local development.
    """
    url = os.environ.get('DATABASE_URL')
    if not url:
        # Local fallback
        return 'sqlite:///classroom.db'
    # If URL starts with legacy postgres://, fix it for SQLAlchemy
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    return url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')  # fallback for local dev
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
