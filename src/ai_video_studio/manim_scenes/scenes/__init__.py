"""Individual scene implementations.

This module contains all scene classes organized by topic/functionality.
Each scene is in its own module for better maintainability.
"""

from ai_video_studio.manim_scenes.scenes.function_demo import FunctionDemoScene
from ai_video_studio.manim_scenes.scenes.loss_descent import (
    LossDescentDemoScene,
    get_loss_descent_narration_segment,
    get_loss_descent_scene_spec,
)
from ai_video_studio.manim_scenes.scenes.parabolic_motion import ParabolicMotionScene
from ai_video_studio.manim_scenes.scenes.pythagorean_theorem import PythagoreanTheoremScene

__all__ = [
    "FunctionDemoScene",
    "LossDescentDemoScene",
    "get_loss_descent_narration_segment",
    "get_loss_descent_scene_spec",
    "ParabolicMotionScene",
    "PythagoreanTheoremScene",
]
