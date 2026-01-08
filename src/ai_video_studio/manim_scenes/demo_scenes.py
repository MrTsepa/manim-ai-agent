"""Demo scenes for testing Manim integration."""

import numpy as np
from manim import (
    Axes,
    AnimationGroup,
    Create,
    Dot,
    FadeIn,
    Indicate,
    Line,
    MathTex,
    MoveAlongPath,
    ORIGIN,
    ParametricFunction,
    Polygon,
    RightAngle,
    Scene,
    Square,
    Text,
    TracedPath,
    VGroup,
    ValueTracker,
    Write,
    always_redraw,
    DEGREES,
    LEFT,
    RIGHT,
    UP,
    DOWN,
    BLUE,
    GREEN,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
)

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


class ParabolicMotionScene(Scene):
    """A demo scene showing a projectile following a parabolic arc with kinematics plots."""

    def construct(self):
        """Create and animate the scene."""
        title = Text("Parabolic Motion", font="Menlo", font_size=40)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=UP * 0.2), run_time=0.6)

        g = 9.8
        v0 = 6.5
        angle = 50 * DEGREES
        t_end = 2 * v0 * np.sin(angle) / g

        def x_pos(t):
            return v0 * np.cos(angle) * t

        def y_pos(t):
            return v0 * np.sin(angle) * t - 0.5 * g * t**2

        def vy(t):
            return v0 * np.sin(angle) - g * t

        def ay(_t):
            return -g

        max_y = (v0 * np.sin(angle)) ** 2 / (2 * g)

        traj_axes = Axes(
            x_range=[0, max(4, x_pos(t_end)), 1],
            y_range=[0, max(3, max_y * 1.2), 1],
            x_length=6.2,
            y_length=4.2,
            axis_config={"include_numbers": True},
        )
        traj_labels = traj_axes.get_axis_labels("x", "y")
        trajectory = ParametricFunction(
            lambda t: traj_axes.c2p(x_pos(t), y_pos(t)),
            t_range=[0, t_end],
            color=BLUE,
        )

        time_tracker = ValueTracker(0.0)
        ball = always_redraw(
            lambda: Dot(traj_axes.c2p(x_pos(time_tracker.get_value()), y_pos(time_tracker.get_value())), color=RED)
        )
        trail = TracedPath(ball.get_center, stroke_color=YELLOW, stroke_width=4)

        traj_group = VGroup(traj_axes, traj_labels, trajectory, trail, ball)

        plot_width = 4.0
        plot_height = 1.7
        time_ticks = max(1, int(np.ceil(t_end)))

        pos_axes = Axes(
            x_range=[0, t_end, time_ticks],
            y_range=[0, max(2, max_y * 1.2), 1],
            x_length=plot_width,
            y_length=plot_height,
            axis_config={"include_numbers": True, "font_size": 28},
        )
        vel_axes = Axes(
            x_range=[0, t_end, time_ticks],
            y_range=[-v0, v0, 2],
            x_length=plot_width,
            y_length=plot_height,
            axis_config={"include_numbers": True, "font_size": 28},
        )
        acc_axes = Axes(
            x_range=[0, t_end, time_ticks],
            y_range=[-g * 1.3, g * 0.3, 2],
            x_length=plot_width,
            y_length=plot_height,
            axis_config={"include_numbers": True, "font_size": 28},
        )

        pos_graph = pos_axes.plot(y_pos, x_range=[0, t_end], color=GREEN)
        vel_graph = vel_axes.plot(vy, x_range=[0, t_end], color=ORANGE)
        acc_graph = acc_axes.plot(ay, x_range=[0, t_end], color=RED)

        pos_label = MathTex("y(t)", font_size=32)
        vel_label = MathTex("v_y(t)", font_size=32)
        acc_label = MathTex("a_y(t)", font_size=32)

        pos_dot = always_redraw(
            lambda: Dot(pos_axes.c2p(time_tracker.get_value(), y_pos(time_tracker.get_value())), color=GREEN)
        )
        vel_dot = always_redraw(
            lambda: Dot(vel_axes.c2p(time_tracker.get_value(), vy(time_tracker.get_value())), color=ORANGE)
        )
        acc_dot = always_redraw(
            lambda: Dot(acc_axes.c2p(time_tracker.get_value(), ay(time_tracker.get_value())), color=RED)
        )

        pos_plot = VGroup(pos_axes, pos_graph, pos_dot)
        vel_plot = VGroup(vel_axes, vel_graph, vel_dot)
        acc_plot = VGroup(acc_axes, acc_graph, acc_dot)

        plots_group = VGroup(pos_plot, vel_plot, acc_plot).arrange(
            DOWN, buff=0.5, aligned_edge=LEFT
        )

        # Align y-axes of the three plots to the same x-position.
        reference_x = pos_axes.c2p(0, 0)[0]
        for axes, plot in ((vel_axes, vel_plot), (acc_axes, acc_plot)):
            delta_x = reference_x - axes.c2p(0, 0)[0]
            plot.shift(RIGHT * delta_x)

        pos_label.next_to(pos_axes, LEFT, buff=0.3)
        vel_label.next_to(vel_axes, LEFT, buff=0.3)
        acc_label.next_to(acc_axes, LEFT, buff=0.3)

        labels_group = VGroup(pos_label, vel_label, acc_label)
        target_label_x = np.mean([label.get_center()[0] for label in labels_group])
        for label in labels_group:
            label.shift(RIGHT * (target_label_x - label.get_center()[0]))

        right_stack = VGroup(plots_group, labels_group)
        content_group = VGroup(traj_group, right_stack).arrange(
            RIGHT, buff=0.8, aligned_edge=UP
        )
        right_stack.shift(DOWN * 0.3)
        traj_group.shift(UP * (right_stack.get_center()[1] - traj_group.get_center()[1]))
        content_group.shift(DOWN * 0.2)

        self.play(Create(traj_axes), Create(traj_labels), run_time=1.0)
        self.play(Create(trajectory), run_time=1.0)
        self.add(trail, ball)

        self.play(
            Create(pos_axes),
            Create(vel_axes),
            Create(acc_axes),
            run_time=1.2,
        )
        self.play(
            Create(pos_graph),
            Create(vel_graph),
            Create(acc_graph),
            FadeIn(pos_label),
            FadeIn(vel_label),
            FadeIn(acc_label),
            run_time=1.2,
        )

        self.add(pos_dot, vel_dot, acc_dot)
        self.play(time_tracker.animate.set_value(t_end), run_time=6, rate_func=lambda t: t)
        self.wait(0.6)


class PythagoreanTheoremScene(Scene):
    """A scene illustrating the Pythagorean theorem with squares on a right triangle."""

    def construct(self):
        """Create and animate the Pythagorean theorem scene."""
        show_guides = False
        title = Text("Pythagorean Theorem", font="Menlo", font_size=42)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=UP * 0.2), run_time=0.6)

        a_len = 2.6
        b_len = 3.4
        A = np.array([0.0, 0.0, 0.0])
        B = np.array([a_len, 0.0, 0.0])
        C = np.array([0.0, b_len, 0.0])

        triangle = Polygon(A, B, C, color=WHITE, stroke_width=4)

        leg_a = Line(A, B)
        leg_b = Line(A, C)
        hypotenuse = Line(B, C)

        right_angle = RightAngle(leg_a, leg_b, length=0.3, color=WHITE)

        square_a = Square(side_length=a_len, color=BLUE, fill_opacity=0.18, stroke_width=3)
        square_a.move_to(np.array([a_len / 2, -a_len / 2, 0.0]))

        square_b = Square(side_length=b_len, color=GREEN, fill_opacity=0.18, stroke_width=3)
        square_b.move_to(np.array([-b_len / 2, b_len / 2, 0.0]))

        v = C - B
        perp = np.array([-v[1], v[0], 0.0])
        midpoint = (B + C) / 2
        candidate = midpoint + perp / 2
        if np.linalg.norm(candidate - A) < np.linalg.norm(midpoint - perp / 2 - A):
            perp *= -1
        square_c = Polygon(B, C, C + perp, B + perp, color=ORANGE, fill_opacity=0.18, stroke_width=3)

        label_a = MathTex("a", font_size=42, color=BLUE)
        label_b = MathTex("b", font_size=42, color=GREEN)
        label_c = MathTex("c", font_size=42, color=ORANGE)

        label_a.next_to(leg_a, DOWN, buff=0.2)
        label_b.next_to(leg_b, LEFT, buff=0.2)
        label_c.next_to(hypotenuse, UP, buff=0.2)

        diagram = VGroup(
            triangle,
            right_angle,
            square_a,
            square_b,
            square_c,
            label_a,
            label_b,
            label_c,
        )

        equation = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=48)
        equation.set_color_by_tex("a^2", BLUE)
        equation.set_color_by_tex("b^2", GREEN)
        equation.set_color_by_tex("c^2", ORANGE)

        diagram.scale(0.62)
        equation.scale(0.9)
        equation.next_to(diagram, RIGHT, buff=0.7)
        equation.shift(UP * 0.05)
        layout = VGroup(diagram, equation)
        layout.move_to(ORIGIN)
        layout.shift(LEFT * 1.35 + DOWN * 0.5)

        if show_guides:
            guide = Line(LEFT * 7, RIGHT * 7, color=WHITE, stroke_opacity=0.2, stroke_width=2)
            self.add(guide)

        self.play(Create(triangle), Create(right_angle), run_time=0.9)
        self.play(FadeIn(label_a), FadeIn(label_b), FadeIn(label_c), run_time=0.6)
        self.play(Create(square_a), Create(square_b), run_time=0.9)
        self.play(Create(square_c), run_time=0.9)
        self.play(Write(equation), run_time=0.8)

        self.play(
            AnimationGroup(
                Indicate(square_a),
                Indicate(equation.get_part_by_tex("a^2")),
                lag_ratio=0.0,
            ),
            run_time=0.6,
        )
        self.play(
            AnimationGroup(
                Indicate(square_b),
                Indicate(equation.get_part_by_tex("b^2")),
                lag_ratio=0.0,
            ),
            run_time=0.6,
        )
        self.play(
            AnimationGroup(
                Indicate(square_c),
                Indicate(equation.get_part_by_tex("c^2")),
                lag_ratio=0.0,
            ),
            run_time=0.6,
        )
        self.wait(0.6)
