import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey_change_in_prod")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///recipes.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt_secret_change_in_prod")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://delcom.org/api")
    LLM_TOKEN = os.environ.get("LLM_TOKEN", "")
    LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

    # Rate limiting
    # ⚠️  PENTING untuk production multi-worker (Gunicorn):
    #     Gunakan Redis agar rate limit berlaku di semua worker.
    #     Set environment variable: RATELIMIT_STORAGE_URL=redis://localhost:6379/0
    #     "memory://" hanya aman untuk development single-process.
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")

    @staticmethod
    def validate():
        """Periksa konfigurasi kritis — panggil saat startup production."""
        warnings = []
        if os.environ.get("SECRET_KEY", "") in ("", "supersecretkey_change_in_prod"):
            warnings.append("SECRET_KEY masih menggunakan nilai default — ganti sebelum deploy!")
        if os.environ.get("JWT_SECRET_KEY", "") in ("", "jwt_secret_change_in_prod"):
            warnings.append("JWT_SECRET_KEY masih menggunakan nilai default — ganti sebelum deploy!")
        if not os.environ.get("LLM_TOKEN", ""):
            warnings.append("LLM_TOKEN belum diisi — endpoint /recipes/generate tidak akan berfungsi.")
        storage = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
        if storage == "memory://":
            warnings.append(
                "RATELIMIT_STORAGE_URL=memory:// — rate limiting tidak akurat "
                "pada deployment multi-worker. Gunakan Redis untuk production."
            )
        return warnings