"""
Shared MinIO Configuration
==========================
Central MinIO client configuration used across the application.
Import this in any module that needs MinIO access.

Usage:
    from minio_config import get_minio_client, BUCKETS
    
    client = get_minio_client()
    client.list_objects(BUCKETS['RAW_CROPS'], ...)
"""

import os
from minio import Minio
from flask import current_app


# =========================
# BUCKET NAMES
# =========================
BUCKETS = {
    'RAW_CROPS': 'raw-crops',
    'LABELED_DATA': 'labeled-data',
    'LABELING_JOBS': 'labeling-jobs',
    'PROCESSED': 'tastelab-videos-processed',
}


# =========================
# DEFAULT CONFIGURATIONS
# =========================
# Production defaults (TasteLab server)
PRODUCTION_DEFAULTS = {
    'endpoint': '194.171.191.226:3135',
    'access_key': 'tastelab_admin',
    'secret_key': 'tastelabpassword123',
    'secure': False
}

# Local development defaults
LOCAL_DEFAULTS = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False
}


def get_minio_client(use_local=False):
    """
    Get MinIO client with automatic configuration detection.
    
    Priority order:
    1. Flask app.config (if in app context)
    2. Environment variables
    3. Production defaults (or local defaults if use_local=True)
    
    Args:
        use_local: If True, use local defaults instead of production defaults
                   when no other config is found
    
    Returns:
        Minio: Configured MinIO client
    """
    defaults = LOCAL_DEFAULTS if use_local else PRODUCTION_DEFAULTS
    
    # Try to get config from Flask app context first
    try:
        endpoint = (
            current_app.config.get('MINIO_ENDPOINT') or 
            os.environ.get('MINIO_ENDPOINT') or 
            defaults['endpoint']
        )
        access_key = (
            current_app.config.get('MINIO_ACCESS_KEY') or 
            os.environ.get('MINIO_ACCESS_KEY') or 
            defaults['access_key']
        )
        secret_key = (
            current_app.config.get('MINIO_SECRET_KEY') or 
            os.environ.get('MINIO_SECRET_KEY') or 
            defaults['secret_key']
        )
        secure = current_app.config.get('MINIO_SECURE')
        if secure is None:
            secure_env = os.environ.get('MINIO_SECURE')
            if secure_env is not None:
                secure = secure_env.lower() == 'true'
            else:
                secure = defaults['secure']
        elif isinstance(secure, str):
            secure = secure.lower() == 'true'
            
    except RuntimeError:
        # Outside Flask application context - use env vars or defaults
        endpoint = os.environ.get('MINIO_ENDPOINT', defaults['endpoint'])
        access_key = os.environ.get('MINIO_ACCESS_KEY', defaults['access_key'])
        secret_key = os.environ.get('MINIO_SECRET_KEY', defaults['secret_key'])
        secure_env = os.environ.get('MINIO_SECURE')
        secure = secure_env.lower() == 'true' if secure_env else defaults['secure']
    
    return Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )


def ensure_buckets(bucket_names=None):
    """
    Ensure specified buckets exist, create if they don't.
    
    Args:
        bucket_names: List of bucket names to ensure. 
                      If None, ensures all buckets in BUCKETS dict.
    """
    client = get_minio_client()
    
    if bucket_names is None:
        bucket_names = BUCKETS.values()
    
    for bucket in bucket_names:
        try:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                print(f"Created bucket: {bucket}")
        except Exception as e:
            print(f"Error ensuring bucket {bucket}: {e}")
