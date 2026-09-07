import os
from pydantic import Field
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
    # Kept as a plain string field (not list[str]) because pydantic-settings
    # tries to JSON-decode list-typed env vars, which breaks on a plain
    # comma-separated value. cors_origins below exposes it as a real list.
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="CORS_ORIGINS",
    )

    class Config:
        env_file = ".env"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = Settings()
