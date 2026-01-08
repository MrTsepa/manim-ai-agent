"""Configuration settings for AI Video Studio."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def _get_project_root() -> Path:
    """Get the project root directory."""
    # Assuming this file is at src/ai_video_studio/config/settings.py
    # Project root is 3 levels up
    return Path(__file__).resolve().parent.parent.parent.parent


def _load_env() -> None:
    """Load environment variables from .env file if it exists."""
    project_root = _get_project_root()
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)


class Settings:
    """Application settings."""

    def __init__(self):
        _load_env()
        self.project_root = _get_project_root()
        self.output_dir = Path(
            os.getenv("OUTPUT_DIR", str(self.project_root / "output"))
        )
        self.manim_quality = os.getenv("MANIM_QUALITY", "medium_quality")
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get the cached settings instance.

    Uses lru_cache for thread-safe singleton pattern.
    To reset settings in tests, call: get_settings.cache_clear()
    """
    return Settings()
