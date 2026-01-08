"""Shared pytest fixtures for AI Video Studio tests."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def docs_dir(project_root: Path) -> Path:
    """Return the docs directory."""
    return project_root / "docs"


@pytest.fixture
def scene_library_path(docs_dir: Path) -> Path:
    """Return the path to scene_library.yaml."""
    return docs_dir / "scene_library.yaml"
