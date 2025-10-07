"""Unit tests for configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from opengov_earlymathematics.config import Settings, get_settings


class TestSettings:
    """Test Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.api_prefix == "/api/v1"

    def test_openai_config(self):
        """Test OpenAI configuration."""
        settings = Settings()
        assert settings.openai_model == "gpt-4-turbo-preview"
        assert settings.openai_temperature == 0.7
        assert settings.openai_max_tokens == 500

    def test_educational_settings(self):
        """Test educational settings."""
        settings = Settings()
        assert settings.max_daily_practice_time == 120
        assert settings.break_reminder_interval == 30
        assert settings.min_accuracy_for_advancement == 0.8
        assert settings.max_hints_per_problem == 3

    def test_curriculum_settings(self):
        """Test curriculum settings."""
        settings = Settings()
        assert "K" in settings.grade_levels
        assert "12" in settings.grade_levels
        assert "beginner" in settings.difficulty_levels
        assert "visual" in settings.learning_styles

    def test_gamification_settings(self):
        """Test gamification settings."""
        settings = Settings()
        assert settings.enable_gamification is True
        assert settings.enable_leaderboards is True
        assert settings.enable_achievements is True
        assert settings.points_per_correct_answer == 10

    def test_session_settings(self):
        """Test session configuration."""
        settings = Settings()
        assert settings.session_timeout_minutes == 60
        assert settings.max_concurrent_sessions == 3
        assert settings.session_recording_enabled is True

    def test_cors_origins(self):
        """Test CORS origins configuration."""
        settings = Settings()
        assert len(settings.cors_origins) > 0
        assert any("localhost" in origin for origin in settings.cors_origins)

    def test_get_settings_cached(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_parent_controls(self):
        """Test parent control settings."""
        settings = Settings()
        assert settings.require_parent_consent is True
        assert settings.enable_time_limits is True
        assert settings.enable_content_filtering is True

    def test_analytics_settings(self):
        """Test analytics settings."""
        settings = Settings()
        assert settings.enable_analytics is True
        assert settings.analytics_batch_size == 100
        assert settings.analytics_flush_interval == 60

    def test_logging_settings(self):
        """Test logging configuration."""
        settings = Settings()
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert settings.enable_metrics is True

    def test_cache_ttl(self):
        """Test cache configuration."""
        settings = Settings()
        assert settings.cache_ttl == 3600

    def test_ml_model_settings(self):
        """Test ML model settings."""
        settings = Settings()
        assert settings.model_update_interval == 86400
        assert settings.min_data_for_personalization == 20
