import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'normakorm-dev-secret-key-2026')
    DATABASE = os.path.join(BASE_DIR, 'normakorm.db')
    DEBUG = True
