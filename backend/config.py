from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://neondb_owner:npg_rnBE4HWjSia6@ep-young-band-b30x3m8i-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    # JWT Authentication
    SECRET_KEY: str = "Vj8mQ2xL9pR4tN7wK6zY3cH1sF5aD8eG0uB2nM4qW7xP9rT6vC3jL5kZ8sX1ALGORITHM=HS256"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # File Storage
    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"
    GENERATED_DIR: str = "generated"

    # OCR Configuration
    OCR_ENGINE: str = "auto"
    TESSERACT_PATH: str = ""
    GEMINI_API_KEY: str = ""

    # Application
    APP_NAME: str = "Intelligent Land Record Digitization System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # URLs
    FRONTEND_URL: str = "land-record-frontend07-sage.vercel.app"
    BACKEND_URL: str = "https://land-record.onrender.com"

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()

# Create required directories on startup
for dir_path in [settings.UPLOAD_DIR, settings.PROCESSED_DIR, settings.GENERATED_DIR]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
