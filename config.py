import os
from dotenv import load_dotenv

load_dotenv()

_secret_key = os.getenv('SECRET_KEY')
if not _secret_key:
    raise RuntimeError('SECRET_KEY environment variable must be set. Generate one with: python -c "import secrets; print(secrets.token_hex(32))"')

class Config:
    SECRET_KEY = _secret_key

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'rural_health_db')
    MYSQL_CURSORCLASS = 'DictCursor'

    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), '.flask_sessions')
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    OTP_ISSUER = 'Anvaya Vistara'
    OTP_VALIDITY_SECONDS = 300

class DevConfig(Config):
    DEBUG = True
    TESTING = False

class ProdConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestConfig(Config):
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False

config_map = {
    'development': DevConfig,
    'production': ProdConfig,
    'testing': TestConfig,
    'default': DevConfig,
}
