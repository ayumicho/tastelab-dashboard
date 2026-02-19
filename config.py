import os

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:password@localhost:5432/tastelab'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False