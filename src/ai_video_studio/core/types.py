"""Core data models for scripts and scene specifications."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ScriptSegment:
    """A segment of narration text in a script."""

    id: str
    text: str
    start_time: float | None = None  # optional
    end_time: float | None = None  # optional


@dataclass
class SceneObjectSpec:
    """Specification for an object that appears in a scene."""

    id: str
    type: str  # e.g. "text", "vector", "point_cloud", "matrix", etc.
    content: str | None = None
    params: dict[str, Any] | None = None


@dataclass
class SceneActionSpec:
    """Specification for an action that occurs in a scene."""

    time: float  # seconds from scene start
    action_type: str  # e.g. "create", "fade_out", "move_to", "transform", "highlight"
    target_id: str  # object id
    params: dict[str, Any] | None = None


@dataclass
class SceneSpec:
    """Complete specification for a scene."""

    id: str
    title: str
    duration: float
    narration_segment_ids: list[str]
    objects: list[SceneObjectSpec]
    actions: list[SceneActionSpec]

