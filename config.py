import os

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres.zuhfvnelpteuhqnbyzfc:[+6F&U/8U2jfPw5d]@aws-1-eu-west-1.pooler.supabase.com:5432/postgres'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', "194.171.191.226:3135")
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', "tastelab_admin")
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', "tastelabpassword123")
    MINIO_SECURE = os.getenv('MINIO_SECURE', 'False').lower() in ('true', '1', 't')
    MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'tastelab-videos-processed')
