import os
from pathlib import Path

API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.getenv('DHURANDHAR_ROOT', API_DIR.parent.parent)).resolve()


class Config:
    HOST = os.getenv('API_HOST', '0.0.0.0')
    PORT = int(os.getenv('API_PORT', '5003'))
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    THREADED = True
    MAX_FILE_SIZE = 8 * 1024 * 1024  # 8 MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    CONFIDENCE_THRESHOLD = 0.70
    IMAGE_SIZE = (224, 224)
    LOG_DIR = API_DIR / 'logs'
    PROJECT_ROOT = PROJECT_ROOT

    @staticmethod
    def ensure_dirs():
        Config.LOG_DIR.mkdir(parents=True, exist_ok=True)
