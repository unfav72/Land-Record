from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./land_records.db"

    # JWT Authentication
    SECRET_KEY: str = "change-this-to-a-strong-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # File Storage
    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"
    GENERATED_DIR: str = "generated"

    # OCR Configuration
    OCR_ENGINE: str = "auto"
    TESSERACT_PATH: str = ""
    OCR_SPACE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Application
    APP_NAME: str = "Intelligent Land Record Digitization System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # URLs
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()

# Create required directories on startup
for dir_path in [settings.UPLOAD_DIR, settings.PROCESSED_DIR, settings.GENERATED_DIR]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
