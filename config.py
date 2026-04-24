import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey_change_in_prod")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///recipes.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt_secret_change_in_prod")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # Token expired setelah 7 hari

    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://delcom.org/api")
    LLM_TOKEN = os.environ.get("LLM_TOKEN", "")
    LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

    # Rate limiting
    # Untuk production multi-worker, ganti ke Redis: "redis://localhost:6379/0"
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")