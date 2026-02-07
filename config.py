import os

def _database_uri():
    url = os.environ.get('DATABASE_URL')
    if not url:
        return 'sqlite:///classroom.db'
    # Heroku/Render use postgres://; SQLAlchemy 1.4+ needs postgresql://
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    return url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg://classroom_yvom_user:9ZUY5CGlKnXfGE7TIx1SqT9D0d7XmRVs@dpg-d63j22ngi27c739h3qag-a.postgres-render.com:5432/classroom_yvom"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
