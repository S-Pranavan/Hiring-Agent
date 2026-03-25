"""
core/config.py - Central configuration using environment variables
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Hiring Agent System"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/hiring_db"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_CVS: str = "hiring-cvs"
    S3_BUCKET_VIDEOS: str = "hiring-videos"

    # AI / LLM
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    # Vector DB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_MONITOR_ADDRESS: str = ""  # inbox for CV email submissions

    # Twilio (calls)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # Matching threshold
    CV_MATCH_THRESHOLD: float = 85.0

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://your-domain.com"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
