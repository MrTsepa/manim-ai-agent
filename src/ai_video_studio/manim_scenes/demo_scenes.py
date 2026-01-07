"""Demo scenes for testing Manim integration."""

from manim import Axes, Create, Dot, MoveAlongPath, Scene, TracedPath

from ai_video_studio.core.types import SceneActionSpec, SceneObjectSpec, SceneSpec, ScriptSegment
from ai_video_studio.manim_scenes.base_scene import SpecDrivenScene


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


def get_loss_descent_narration_segment() -> ScriptSegment:
    """
    Get the narration segment for the loss descent demo.
    
    Returns:
        ScriptSegment with the narration text
    """
    return ScriptSegment(
        id="segment_loss_equals_height",
        text="When we optimize a model's loss, we're really trying to move its parameters downhill on a surface. Lower loss is simply lower height."
    )


def get_loss_descent_scene_spec() -> SceneSpec:
    """
    Create the SceneSpec for the loss descent demo.
    
    This scene visualizes loss optimization as a ball rolling downhill
    on a smooth bowl surface (paraboloid).
    
    Z values are calculated using: z = (x² + y²) * 0.35
    """
    # Helper to calculate z on the paraboloid surface
    # Ball offset ensures it sits visibly above the surface
    ball_offset = 0.22
    
    def surface_z(x, y):
        return (x * x + y * y) * 0.35 + ball_offset
    
    # Descent trajectory - more points for smoother animation
    trajectory = [
        (2.2, 1.8),    # Start: high on the rim
        (1.8, 1.5),    # Step 1
        (1.4, 1.2),    # Step 2
        (1.0, 0.85),   # Step 3
        (0.65, 0.55),  # Step 4
        (0.35, 0.3),   # Step 5
        (0.12, 0.1),   # End: near minimum
    ]
    
    # Calculate z for each point
    positions = [(x, y, surface_z(x, y)) for x, y in trajectory]
    
    # Starting position
    start_x, start_y, start_z = positions[0]
    
    # Gradient arrow pointing towards the minimum (downhill direction)
    arrow_end_x, arrow_end_y = 1.6, 1.3
    arrow_end_z = surface_z(arrow_end_x, arrow_end_y)
    
    # Build actions with tighter timing
    actions = [
        SceneActionSpec(time=0.0, action_type="create", target_id="axes"),
        SceneActionSpec(time=0.3, action_type="create", target_id="surface"),
        SceneActionSpec(time=0.8, action_type="create", target_id="ball"),
        SceneActionSpec(time=1.0, action_type="create", target_id="gradient_arrow"),
        SceneActionSpec(time=1.8, action_type="fade_out", target_id="gradient_arrow"),
    ]
    
    # Add movement actions with quick succession
    move_start_time = 2.0
    move_interval = 0.8  # Faster transitions
    
    for i, (x, y, z) in enumerate(positions[1:], start=1):
        actions.append(
            SceneActionSpec(
                time=move_start_time + (i - 1) * move_interval,
                action_type="move_to",
                target_id="ball",
                params={"position": [x, y, z]},
            )
        )
    
    return SceneSpec(
        id="loss_descent_demo",
        title="Loss = Height",
        duration=8.0,  # Shorter, snappier
        narration_segment_ids=["segment_loss_equals_height"],
        objects=[
            SceneObjectSpec(
                id="axes",
                type="axes",
                params={
                    "x_range": [-3, 3, 1],
                    "y_range": [-3, 3, 1],
                    "z_range": [0, 4, 1],
                },
            ),
            SceneObjectSpec(
                id="surface",
                type="surface",
                params={
                    "function": "paraboloid",
                    "color": "BLUE_E",
                    "x_range": [-2.8, 2.8],
                    "y_range": [-2.8, 2.8],
                },
            ),
            SceneObjectSpec(
                id="ball",
                type="point",
                params={
                    "position": [start_x, start_y, start_z],
                    "color": "ORANGE",
                },
            ),
            SceneObjectSpec(
                id="gradient_arrow",
                type="arrow",
                params={
                    "start": [start_x, start_y, start_z],
                    "end": [arrow_end_x, arrow_end_y, arrow_end_z],
                    "color": "RED",
                },
            ),
        ],
        actions=actions,
    )


class LossDescentDemoScene(SpecDrivenScene):
    """
    A demo scene showing loss optimization as a ball rolling downhill.
    
    This visualizes the core intuition: optimizing loss = moving downhill
    on a landscape. Lower loss is simply lower height.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with the loss descent scene specification."""
        scene_spec = get_loss_descent_scene_spec()
        super().__init__(scene_spec, *args, **kwargs)

