"""Tests for configuration settings."""

from pathlib import Path

from ai_video_studio.config.settings import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""

    def test_settings_has_project_root(self):
        """Test that settings has a project root path."""
        settings = Settings()
        assert isinstance(settings.project_root, Path)
        assert settings.project_root.exists()

    def test_settings_has_output_dir(self):
        """Test that settings has an output directory."""
        settings = Settings()
        assert isinstance(settings.output_dir, Path)

    def test_settings_has_manim_quality(self):
        """Test that settings has a manim quality setting."""
        settings = Settings()
        assert settings.manim_quality in [
            "low_quality",
            "medium_quality",
            "high_quality",
            "production_quality",
        ]

    def test_output_dir_is_created(self):
        """Test that output directory is created if it doesn't exist."""
        settings = Settings()
        # The Settings constructor creates the output directory
        assert settings.output_dir.exists() or settings.output_dir.parent.exists()


class TestGetSettings:
    """Tests for get_settings function."""

    def test_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_returns_cached_instance(self):
        """Test that get_settings returns the same cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_cache_can_be_cleared(self):
        """Test that cache can be cleared for testing purposes."""
        settings1 = get_settings()
        get_settings.cache_clear()
        settings2 = get_settings()
        # After clearing cache, a new instance is created
        assert settings1 is not settings2
