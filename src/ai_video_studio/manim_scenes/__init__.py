"""Manim scene implementations."""

from ai_video_studio.manim_scenes.base_scene import SpecDrivenScene
from ai_video_studio.manim_scenes.demo_scenes import (
    FunctionDemoScene,
    LossDescentDemoScene,
    get_loss_descent_narration_segment,
    get_loss_descent_scene_spec,
)
from ai_video_studio.manim_scenes.layouts import (
    TitledSceneLayout,
    setup_titled_3d_scene,
)

__all__ = [
    "SpecDrivenScene",
    "FunctionDemoScene",
    "LossDescentDemoScene",
    "get_loss_descent_scene_spec",
    "get_loss_descent_narration_segment",
    "TitledSceneLayout",
    "setup_titled_3d_scene",
]
