"""Utilities for loading and querying the scene library registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ReferenceScene:
    """Typed view of a reference scene entry."""

    id: str
    title: str
    scene_class: str
    module: str
    source_file: str
    tags: list[str]
    quality_notes: list[str]
    artifacts: dict[str, Any]


def load_scene_library(path: str | Path) -> list[ReferenceScene]:
    """Load the scene library YAML and return reference scenes."""
    library_path = Path(path)
    data = yaml.safe_load(library_path.read_text())
    scenes: list[ReferenceScene] = []
    for entry in data.get("reference_scenes", []):
        scenes.append(
            ReferenceScene(
                id=entry.get("id", ""),
                title=entry.get("title", ""),
                scene_class=entry.get("scene_class", ""),
                module=entry.get("module", ""),
                source_file=entry.get("source_file", ""),
                tags=list(entry.get("tags", [])),
                quality_notes=list(entry.get("quality_notes", [])),
                artifacts=dict(entry.get("artifacts", {})),
            )
        )
    return scenes


def filter_reference_scenes(
    scenes: list[ReferenceScene], *, tags: list[str] | None = None
) -> list[ReferenceScene]:
    """Filter scenes by tag inclusion (all tags must be present)."""
    if not tags:
        return scenes
    required = set(tags)
    return [scene for scene in scenes if required.issubset(set(scene.tags))]
