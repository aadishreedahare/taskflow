import os
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central app configuration. Reads from environment variables / .env file.
    Swap DATABASE_URL to a Postgres/MySQL DSN in production without touching
    any other code (SQLAlchemy handles the dialect differences).
    """

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_upload_size_mb: int = 10
    # Comma-separated list of allowed frontend origins, e.g.
    # CORS_ORIGINS=https://taskflow.vercel.app,https://taskflow-git-main.vercel.app
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, v):
        # pydantic-settings normally expects a JSON array for list-typed env
        # vars; this lets CORS_ORIGINS be a plain comma-separated string instead.
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file = ".env"


settings = Settings()
