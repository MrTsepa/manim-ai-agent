"""Tests for scene library loading and filtering."""

from pathlib import Path

import pytest

from ai_video_studio.core.scene_library import (
    ReferenceScene,
    filter_reference_scenes,
    load_scene_library,
)


class TestLoadSceneLibrary:
    """Tests for load_scene_library function."""

    def test_load_existing_library(self, scene_library_path: Path):
        """Test loading the actual scene library file."""
        scenes = load_scene_library(scene_library_path)
        assert isinstance(scenes, list)
        assert len(scenes) > 0
        assert all(isinstance(s, ReferenceScene) for s in scenes)

    def test_loaded_scenes_have_required_fields(self, scene_library_path: Path):
        """Test that loaded scenes have all required fields populated."""
        scenes = load_scene_library(scene_library_path)
        for scene in scenes:
            assert scene.id, "Scene should have an id"
            assert scene.title, "Scene should have a title"
            assert scene.scene_class, "Scene should have a scene_class"
            assert scene.module, "Scene should have a module"
            assert scene.source_file, "Scene should have a source_file"

    def test_reference_scene_is_frozen(self):
        """Test that ReferenceScene is immutable (frozen dataclass)."""
        scene = ReferenceScene(
            id="test",
            title="Test",
            scene_class="TestScene",
            module="test.module",
            source_file="test.py",
            tags=["test"],
            quality_notes=[],
            artifacts={},
        )
        with pytest.raises(AttributeError):
            scene.id = "modified"  # type: ignore


class TestFilterReferenceScenes:
    """Tests for filter_reference_scenes function."""

    @pytest.fixture
    def sample_scenes(self) -> list[ReferenceScene]:
        """Create sample scenes for testing."""
        return [
            ReferenceScene(
                id="scene1",
                title="Scene 1",
                scene_class="Scene1",
                module="mod",
                source_file="s1.py",
                tags=["reference", "layout:side-by-side"],
                quality_notes=[],
                artifacts={},
            ),
            ReferenceScene(
                id="scene2",
                title="Scene 2",
                scene_class="Scene2",
                module="mod",
                source_file="s2.py",
                tags=["sample", "geometry"],
                quality_notes=[],
                artifacts={},
            ),
            ReferenceScene(
                id="scene3",
                title="Scene 3",
                scene_class="Scene3",
                module="mod",
                source_file="s3.py",
                tags=["reference", "geometry"],
                quality_notes=[],
                artifacts={},
            ),
        ]

    def test_filter_no_tags_returns_all(self, sample_scenes: list[ReferenceScene]):
        """Test that filtering with no tags returns all scenes."""
        result = filter_reference_scenes(sample_scenes, tags=None)
        assert len(result) == 3

    def test_filter_empty_tags_returns_all(self, sample_scenes: list[ReferenceScene]):
        """Test that filtering with empty tags list returns all scenes."""
        result = filter_reference_scenes(sample_scenes, tags=[])
        assert len(result) == 3

    def test_filter_single_tag(self, sample_scenes: list[ReferenceScene]):
        """Test filtering by a single tag."""
        result = filter_reference_scenes(sample_scenes, tags=["reference"])
        assert len(result) == 2
        assert all("reference" in s.tags for s in result)

    def test_filter_multiple_tags_requires_all(self, sample_scenes: list[ReferenceScene]):
        """Test that filtering with multiple tags requires all tags to be present."""
        result = filter_reference_scenes(sample_scenes, tags=["reference", "geometry"])
        assert len(result) == 1
        assert result[0].id == "scene3"

    def test_filter_nonexistent_tag_returns_empty(self, sample_scenes: list[ReferenceScene]):
        """Test that filtering by nonexistent tag returns empty list."""
        result = filter_reference_scenes(sample_scenes, tags=["nonexistent"])
        assert len(result) == 0
