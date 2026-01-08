"""Scene registry for auto-discovery and multiagent-friendly registration.

This module provides a decorator-based scene registration system that avoids
the need to edit central files (cli.py, demo_scenes.py) when adding new scenes.
This makes parallel agent development more merge-friendly.

Usage:
    from ai_video_studio.manim_scenes.registry import register_scene

    @register_scene(
        id="my_scene_v1",
        title="My Scene Title",
        tags=["geometry", "animation"],
    )
    class MyScene(Scene):
        def construct(self):
            ...
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from manim import Scene


@dataclass
class SceneMetadata:
    """Metadata for a registered scene."""

    id: str
    title: str
    scene_class: Type[Scene]
    module: str
    tags: List[str] = field(default_factory=list)
    quality_notes: List[str] = field(default_factory=list)
    cli_command: Optional[str] = None  # Auto-generated if not provided

    def __post_init__(self) -> None:
        """Generate CLI command from scene class name if not provided."""
        if self.cli_command is None:
            # Convert CamelCase to kebab-case: MyNewScene -> my-new-scene
            name = self.scene_class.__name__
            # Remove 'Scene' suffix if present
            if name.endswith("Scene"):
                name = name[:-5]
            # Convert to kebab-case
            import re

            self.cli_command = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


# Global registry of scenes
_SCENE_REGISTRY: Dict[str, SceneMetadata] = {}


T = TypeVar("T", bound=Type[Scene])


def register_scene(
    id: str,
    title: str,
    tags: Optional[List[str]] = None,
    quality_notes: Optional[List[str]] = None,
    cli_command: Optional[str] = None,
) -> Callable[[T], T]:
    """Decorator to register a scene class for auto-discovery.

    This decorator adds the scene to a global registry that can be queried
    by the CLI and other tools without modifying central files.

    Args:
        id: Unique identifier for the scene (e.g., "parabolic_motion_v1")
        title: Human-readable title for display
        tags: Optional list of tags for filtering
        quality_notes: Optional notes about quality/style
        cli_command: Optional CLI command name (auto-generated from class name if not provided)

    Returns:
        Decorator function that registers the scene class

    Example:
        @register_scene(
            id="my_scene_v1",
            title="My Amazing Scene",
            tags=["physics", "animation"],
        )
        class MyScene(Scene):
            def construct(self):
                ...
    """

    def decorator(cls: T) -> T:
        metadata = SceneMetadata(
            id=id,
            title=title,
            scene_class=cls,
            module=cls.__module__,
            tags=tags or [],
            quality_notes=quality_notes or [],
            cli_command=cli_command,
        )
        _SCENE_REGISTRY[id] = metadata
        # Also store metadata on the class for introspection
        cls._scene_metadata = metadata  # type: ignore[attr-defined]
        return cls

    return decorator


def get_registered_scenes() -> Dict[str, SceneMetadata]:
    """Get all registered scenes.

    Returns:
        Dictionary mapping scene IDs to their metadata
    """
    return _SCENE_REGISTRY.copy()


def get_scene_by_id(scene_id: str) -> Optional[SceneMetadata]:
    """Get a scene by its ID.

    Args:
        scene_id: The unique scene identifier

    Returns:
        SceneMetadata if found, None otherwise
    """
    return _SCENE_REGISTRY.get(scene_id)


def get_scene_by_command(command: str) -> Optional[SceneMetadata]:
    """Get a scene by its CLI command name.

    Args:
        command: The CLI command (e.g., "parabolic-motion")

    Returns:
        SceneMetadata if found, None otherwise
    """
    for metadata in _SCENE_REGISTRY.values():
        if metadata.cli_command == command:
            return metadata
    return None


def get_scene_by_class_name(class_name: str) -> Optional[SceneMetadata]:
    """Get a scene by its class name.

    Args:
        class_name: The scene class name (e.g., "ParabolicMotionScene")

    Returns:
        SceneMetadata if found, None otherwise
    """
    for metadata in _SCENE_REGISTRY.values():
        if metadata.scene_class.__name__ == class_name:
            return metadata
    return None


def filter_scenes_by_tags(tags: List[str]) -> List[SceneMetadata]:
    """Filter registered scenes by tags.

    Args:
        tags: List of tags to filter by (scenes must have all tags)

    Returns:
        List of matching SceneMetadata
    """
    return [
        metadata
        for metadata in _SCENE_REGISTRY.values()
        if all(tag in metadata.tags for tag in tags)
    ]


def discover_scenes() -> None:
    """Import all scene modules to trigger registration.

    This function imports all Python files in the scenes/ directory,
    which triggers the @register_scene decorators to run.
    """
    import importlib
    import pkgutil
    from pathlib import Path

    # Get the scenes package path
    scenes_dir = Path(__file__).parent / "scenes"
    if not scenes_dir.exists():
        return

    # Import each module in the scenes directory
    for module_info in pkgutil.iter_modules([str(scenes_dir)]):
        if not module_info.name.startswith("_"):
            module_name = f"ai_video_studio.manim_scenes.scenes.{module_info.name}"
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                # Log but don't fail - allows partial discovery
                import sys

                print(f"Warning: Could not import {module_name}: {e}", file=sys.stderr)


def load_metadata_files() -> List[SceneMetadata]:
    """Load scene metadata from .meta.yaml files.

    This provides an alternative to the decorator approach - scenes can
    define their metadata in separate YAML files.

    Returns:
        List of SceneMetadata loaded from files
    """
    from pathlib import Path

    import yaml

    scenes_dir = Path(__file__).parent / "scenes"
    if not scenes_dir.exists():
        return []

    metadata_list: List[SceneMetadata] = []

    for meta_file in scenes_dir.glob("*.meta.yaml"):
        try:
            with open(meta_file) as f:
                data = yaml.safe_load(f)

            if not data:
                continue

            # Get the corresponding module and class
            module_name = meta_file.stem.replace(".meta", "")
            full_module = f"ai_video_studio.manim_scenes.scenes.{module_name}"

            # Try to import and get the class
            import importlib

            try:
                module = importlib.import_module(full_module)
                scene_class = getattr(module, data["scene_class"])
            except (ImportError, AttributeError):
                continue

            metadata = SceneMetadata(
                id=data["id"],
                title=data["title"],
                scene_class=scene_class,
                module=full_module,
                tags=data.get("tags", []),
                quality_notes=data.get("quality_notes", []),
                cli_command=data.get("cli_command"),
            )

            # Register it
            _SCENE_REGISTRY[metadata.id] = metadata
            metadata_list.append(metadata)

        except Exception as e:
            import sys

            print(f"Warning: Could not load {meta_file}: {e}", file=sys.stderr)

    return metadata_list

