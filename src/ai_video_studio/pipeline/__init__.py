"""Pipeline orchestration and CLI."""

from ai_video_studio.pipeline.render_scenes import render_scene, render_scene_via_cli
from ai_video_studio.pipeline.cli import main

__all__ = [
    "render_scene",
    "render_scene_via_cli",
    "main",
]
