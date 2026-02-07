import os

def get_database_uri():
    url = os.environ.get('DATABASE_URL')
    if not url:
        return 'sqlite:///classroom.db'
    if url.startswith('postgres://'):
        url = 'postgresql+psycopg://' + url[len('postgres://'):]
    else:
        # Ensure the driver is psycopg
        url = url.replace('postgresql://', 'postgresql+psycopg://')
    return url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
