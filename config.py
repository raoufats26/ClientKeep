import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Fix for Render: postgres:// -> postgresql://
    _db_url = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/clientkeep'
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI    = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
