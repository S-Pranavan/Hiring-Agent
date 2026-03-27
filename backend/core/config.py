from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Hiring Agent System API"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "local-dev-backend-secret-change-me"
    database_path: str = "backend/data/hiring_agent.db"
    local_upload_dir: str = "backend/data/uploads"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_cvs: str = ""
    s3_bucket_videos: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
