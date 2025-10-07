"""Configuration management for OpenGov-EarlyMathematics."""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")
    api_title: str = Field(default="OpenGov-EarlyMathematics API")
    api_version: str = Field(default="0.1.0")

    # Security
    secret_key: SecretStr = Field(default=SecretStr("change-me-in-production"))
    jwt_secret: SecretStr = Field(default=SecretStr("jwt-secret-change-me"))
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)

    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/mathdb")
    redis_url: str = Field(default="redis://localhost:6379/0")

    # OpenAI Configuration
    openai_api_key: SecretStr = Field(default=SecretStr("sk-..."))
    openai_model: str = Field(default="gpt-4-turbo-preview")
    openai_temperature: float = Field(default=0.7)
    openai_max_tokens: int = Field(default=500)

    # Educational Settings
    max_daily_practice_time: int = Field(default=120)  # minutes
    break_reminder_interval: int = Field(default=30)  # minutes
    min_accuracy_for_advancement: float = Field(default=0.8)
    max_hints_per_problem: int = Field(default=3)
    points_per_correct_answer: int = Field(default=10)
    streak_bonus_threshold: int = Field(default=5)

    # Curriculum Settings
    grade_levels: List[str] = Field(
        default=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    )
    difficulty_levels: List[str] = Field(default=["beginner", "intermediate", "advanced", "expert"])
    learning_styles: List[str] = Field(
        default=["visual", "auditory", "kinesthetic", "reading_writing"]
    )

    # Session Configuration
    session_timeout_minutes: int = Field(default=60)
    max_concurrent_sessions: int = Field(default=3)
    session_recording_enabled: bool = Field(default=True)

    # Content Delivery
    cdn_url: Optional[str] = Field(default=None)
    media_storage_path: Path = Field(default=Path("./data/media"))
    cache_ttl: int = Field(default=3600)  # seconds

    # ML Model Settings
    model_path: Path = Field(default=Path("./data/models"))
    model_update_interval: int = Field(default=86400)  # daily
    min_data_for_personalization: int = Field(default=20)  # problems

    # Gamification
    enable_gamification: bool = Field(default=True)
    enable_leaderboards: bool = Field(default=True)
    enable_achievements: bool = Field(default=True)
    enable_virtual_rewards: bool = Field(default=True)

    # Parent Controls
    require_parent_consent: bool = Field(default=True)
    enable_time_limits: bool = Field(default=True)
    enable_content_filtering: bool = Field(default=True)

    # Analytics
    enable_analytics: bool = Field(default=True)
    analytics_batch_size: int = Field(default=100)
    analytics_flush_interval: int = Field(default=60)  # seconds

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    enable_metrics: bool = Field(default=True)

    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8501"])

    @field_validator("model_path", "media_storage_path")
    @classmethod
    def create_directories(cls, v: Path) -> Path:
        """Ensure directories exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
