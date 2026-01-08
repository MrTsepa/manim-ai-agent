"""Function demo scene - a simple animated function graph."""

from manim import (
    Axes,
    Create,
    Dot,
    MoveAlongPath,
    Scene,
    TracedPath,
)

from ai_video_studio.manim_scenes.registry import register_scene


@register_scene(
    id="function_demo_v1",
    title="Function Demo",
    tags=["demo", "simple", "2d", "animation"],
    quality_notes=["Basic demo scene for testing the rendering pipeline."],
)
class FunctionDemoScene(Scene):
    """A simple demo scene showing a function on axes with a point moving along the curve."""

    def construct(self):
        """Create and animate the scene."""
        # Create axes
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            x_length=10,
            y_length=6,
            axis_config={"include_numbers": True},
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")

        # Create a function: f(x) = x^2 / 3 - 1
        def func(x):
            return x**2 / 3 - 1

        # Create the graph
        graph = axes.plot(func, color="BLUE", x_range=[-3, 3])

        # Create a dot that will move along the curve
        dot = Dot(axes.coords_to_point(-3, func(-3)), color="RED")

        # Create a traced path for the dot
        traced_path = TracedPath(dot.get_center, stroke_color="RED", stroke_width=2)

        # Animation sequence
        self.play(Create(axes), Create(axes_labels))
        self.wait(0.5)
        self.play(Create(graph))
        self.wait(0.5)
        self.add(dot, traced_path)
        self.play(
            MoveAlongPath(dot, graph, run_time=3),
            rate_func=lambda t: t,  # linear motion
        )
        self.wait(1)
