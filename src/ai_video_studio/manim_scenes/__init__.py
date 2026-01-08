"""Manim scene implementations.

This package contains:
- `base_scene`: Base class for spec-driven scenes
- `layouts`: Layout components for title/content separation
- `primitives`: Reusable visual primitives (surfaces, balls, arrows)
- `scenes/`: Individual scene implementations (modular structure)
- `demo_scenes`: Re-exports from scenes/ for backward compatibility
"""

# Base scene class
from ai_video_studio.manim_scenes.base_scene import SpecDrivenScene

# Layout components
from ai_video_studio.manim_scenes.layouts import (
    TitledSceneLayout,
    setup_titled_3d_scene,
)

# Visual primitives
from ai_video_studio.manim_scenes.primitives import (
    create_ball,
    create_gradient_arrow,
    create_paraboloid_surface,
    get_paraboloid_z,
)

# Scene implementations (from scenes/ subpackage)
from ai_video_studio.manim_scenes.scenes import (
    FunctionDemoScene,
    LossDescentDemoScene,
    ParabolicMotionScene,
    PythagoreanTheoremScene,
    get_loss_descent_narration_segment,
    get_loss_descent_scene_spec,
)

__all__ = [
    # Base
    "SpecDrivenScene",
    # Layouts
    "TitledSceneLayout",
    "setup_titled_3d_scene",
    # Primitives
    "create_ball",
    "create_gradient_arrow",
    "create_paraboloid_surface",
    "get_paraboloid_z",
    # Scenes
    "FunctionDemoScene",
    "LossDescentDemoScene",
    "ParabolicMotionScene",
    "PythagoreanTheoremScene",
    "get_loss_descent_narration_segment",
    "get_loss_descent_scene_spec",
]
