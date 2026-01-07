"""Base scene class for spec-driven Manim scenes."""

from typing import Any

import numpy as np
from manim import (
    BLUE_E, Create, FadeIn, FadeOut, RED, ThreeDAxes, ThreeDScene, 
    YELLOW, WHITE, Text, Write, DEGREES, UP, DOWN, LEFT, RIGHT, ORIGIN,
    TracedPath, rate_functions,
)

from ai_video_studio.core.types import SceneActionSpec, SceneObjectSpec, SceneSpec
from ai_video_studio.manim_scenes.layouts import TitledSceneLayout
from ai_video_studio.manim_scenes.primitives import (
    create_ball,
    create_gradient_arrow,
    create_paraboloid_surface,
)


class SpecDrivenScene(ThreeDScene):
    """
    A Manim scene that constructs itself from a SceneSpec.
    
    This class interprets SceneSpec objects and creates corresponding
    Manim animations automatically.
    """

    def __init__(self, scene_spec: SceneSpec, *args, **kwargs):
        """
        Initialize the scene with a specification.
        
        Args:
            scene_spec: The SceneSpec defining what to render
            *args, **kwargs: Passed to parent Scene class
        """
        super().__init__(*args, **kwargs)
        self.scene_spec = scene_spec
        self.objects: dict[str, Any] = {}  # Maps object IDs to Manim mobjects
        self._traced_paths: dict[str, TracedPath] = {}  # Traced paths for objects

    def construct(self):
        """Build and animate the scene from the specification."""
        # Set up camera for a better viewing angle
        self.set_camera_orientation(phi=70 * DEGREES, theta=-50 * DEGREES, distance=7)
        
        # Use TitledSceneLayout to properly separate title from 3D content
        self._layout = None
        if self.scene_spec.title:
            self._layout = TitledSceneLayout(
                scene=self,
                title=self.scene_spec.title,
                title_font="Menlo",
                title_font_size=42,
            )
            # Setup title (animated) - title is fixed to camera frame
            self._layout.setup(animate_title=True, run_time=0.4)
        
        # Start ambient camera rotation
        self.begin_ambient_camera_rotation(rate=0.08)
        
        # Sort actions by time
        sorted_actions = sorted(self.scene_spec.actions, key=lambda a: a.time)
        
        current_time = 0.0
        
        for action in sorted_actions:
            # Wait until the action's time
            if action.time > current_time:
                wait_time = action.time - current_time
                self.wait(wait_time)
                current_time = action.time
            
            # Execute the action
            self._execute_action(action)
        
        # Wait for remaining duration
        remaining_time = self.scene_spec.duration - current_time
        if remaining_time > 0:
            self.wait(remaining_time)
        
        # Stop camera rotation
        self.stop_ambient_camera_rotation()

    def _execute_action(self, action: SceneActionSpec):
        """Execute a single action from the scene spec."""
        action_type = action.action_type
        target_id = action.target_id
        params = action.params or {}
        
        if action_type == "create":
            if target_id not in self.objects:
                # Create the object if it doesn't exist
                obj_spec = next(
                    (obj for obj in self.scene_spec.objects if obj.id == target_id),
                    None
                )
                if obj_spec:
                    mobject = self._create_object(obj_spec)
                    self.objects[target_id] = mobject
                    # Use FadeIn for smoother appearance (fast)
                    self.play(FadeIn(mobject), run_time=0.5)
                    
                    # Add traced path for points (balls) - shows optimization trajectory
                    if obj_spec.type == "point":
                        traced = TracedPath(
                            mobject.get_center, 
                            stroke_color="#FFFF00",  # Bright yellow
                            stroke_width=5,
                            stroke_opacity=1.0,
                            dissipating_time=None,  # Path persists
                        )
                        self._traced_paths[target_id] = traced
                        self.add(traced)
                        
        elif action_type == "fade_out":
            if target_id in self.objects:
                self.play(FadeOut(self.objects[target_id]), run_time=0.3)
        elif action_type == "move_to":
            if target_id in self.objects:
                new_position = params.get("position")
                if new_position:
                    mobject = self.objects[target_id]
                    # Adjust position for layout offset if we have a titled scene
                    # Shift in Z direction for 3D scenes viewed from above
                    adjusted_position = list(new_position)
                    if self._layout is not None:
                        adjusted_position[2] -= self._layout.CONTENT_SHIFT_DOWN
                    # Smooth movement with ease_out for natural deceleration
                    self.play(
                        mobject.animate.move_to(adjusted_position),
                        run_time=0.6,
                        rate_func=rate_functions.ease_out_cubic,
                    )
        elif action_type == "wait":
            wait_time = params.get("duration", 0.5)
            self.wait(wait_time)

    def _create_object(self, obj_spec: SceneObjectSpec):
        """
        Create a Manim mobject from an object specification.
        
        Args:
            obj_spec: The SceneObjectSpec defining the object
            
        Returns:
            A Manim mobject
        """
        obj_type = obj_spec.type
        params = obj_spec.params or {}
        mobject = None
        
        if obj_type == "axes":
            x_range = params.get("x_range", [-3, 3])
            y_range = params.get("y_range", [-3, 3])
            z_range = params.get("z_range", [0, 9])
            mobject = ThreeDAxes(
                x_range=x_range,
                y_range=y_range,
                z_range=z_range,
                axis_config={"include_numbers": True},
            )
        elif obj_type == "surface":
            function = params.get("function", "paraboloid")
            color_str = params.get("color", "BLUE_E")
            color = self._get_color(color_str)
            x_range = params.get("x_range", (-3, 3))
            y_range = params.get("y_range", (-3, 3))
            
            if function == "paraboloid":
                mobject = create_paraboloid_surface(
                    x_range=x_range,
                    y_range=y_range,
                    color=color
                )
            else:
                raise ValueError(f"Unknown surface function: {function}")
        elif obj_type == "point":
            position = params.get("position", [0, 0, 0])
            color_str = params.get("color", "YELLOW")
            color = self._get_color(color_str)
            mobject = create_ball(position=position, color=color)
        elif obj_type == "arrow":
            start = params.get("start", [0, 0, 0])
            end = params.get("end", [1, 1, 1])
            color_str = params.get("color", "RED")
            color = self._get_color(color_str)
            mobject = create_gradient_arrow(start=start, end=end, color=color)
        else:
            raise ValueError(f"Unknown object type: {obj_type}")
        
        # Shift content down if we have a titled layout to avoid intersection
        if mobject is not None and self._layout is not None:
            self._layout.shift_content_down(mobject)
        
        return mobject

    def _get_color(self, color_str: str):
        """
        Convert a color string to a Manim color constant.
        
        Args:
            color_str: String name of the color (e.g., "BLUE_E", "YELLOW", "RED")
            
        Returns:
            A Manim color constant
        """
        color_map = {
            "BLUE_E": BLUE_E,
            "YELLOW": YELLOW,
            "RED": RED,
        }
        return color_map.get(color_str, color_str)  # Return as-is if not in map

