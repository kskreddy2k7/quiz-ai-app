from functools import lru_cache
from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env files."""

    app_name: str = "QuizAI Academy"
    environment: str = Field("development", env="ENVIRONMENT")
    api_v1_prefix: str = "/api"
    cors_origins: str = Field("*", env="CORS_ORIGINS")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_upload_mb: int = Field(10, env="MAX_UPLOAD_MB")

    ai_provider: str = Field("stub", env="AI_PROVIDER")
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings(_env_file=Path(".env") if Path(".env").exists() else None)
