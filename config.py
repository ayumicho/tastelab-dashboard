import os

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:password@localhost:5432/tastelab'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MinIO Configuration
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', "194.171.191.226:3135")
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', "tastelab_admin")
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', "tastelabpassword123")
    MINIO_SECURE = os.getenv('MINIO_SECURE', 'False').lower() in ('true', '1', 't')
    MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'tastelab-videos-processed')
    
    # Scheduler Configuration
    SCHEDULER_API_ENABLED = True
    SCHEDULER_ENABLED = True  # Set to False to disable background sync