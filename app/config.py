
import os
from dotenv import load_dotenv

load_dotenv("data/.env")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:Thisisatest25!@localhost:5432/Project Database')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
    JWT_HEADER_TYPE = ""
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    AUTH0_DOMAIN        = os.getenv('AUTH0_DOMAIN')
    AUTH0_CLIENT_ID     = os.getenv('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
    AUTH0_CALLBACK_URL  = os.getenv('AUTH0_CALLBACK_URL')
    AUTH0_AUDIENCE      = os.getenv('AUTH0_AUDIENCE')
