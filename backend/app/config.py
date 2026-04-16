import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Ruta absoluta al .env — funciona sin importar desde dónde se ejecute
load_dotenv(Path(__file__).resolve().parent.parent / '.env', override=True)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
        f"/{os.getenv('DB_NAME', 'AWGPMCESE')}?charset=utf8mb4"
    )

    LOGIN_MAX_INTENTOS = int(os.getenv('LOGIN_MAX_INTENTOS', 5))
    LOGIN_BLOQUEO_MINUTOS = int(os.getenv('LOGIN_BLOQUEO_MINUTOS', 15))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
