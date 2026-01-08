"""Parabolic motion scene - projectile trajectory with kinematics plots."""

import numpy as np
from manim import (
    Axes,
    Create,
    DEGREES,
    Dot,
    DOWN,
    FadeIn,
    LEFT,
    MathTex,
    ParametricFunction,
    RIGHT,
    Scene,
    Text,
    TracedPath,
    UP,
    ValueTracker,
    VGroup,
    always_redraw,
    BLUE,
    GREEN,
    ORANGE,
    RED,
    YELLOW,
)


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
            lambda: Dot(
                traj_axes.c2p(x_pos(time_tracker.get_value()), y_pos(time_tracker.get_value())),
                color=RED,
            )
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
            lambda: Dot(
                pos_axes.c2p(time_tracker.get_value(), y_pos(time_tracker.get_value())),
                color=GREEN,
            )
        )
        vel_dot = always_redraw(
            lambda: Dot(
                vel_axes.c2p(time_tracker.get_value(), vy(time_tracker.get_value())),
                color=ORANGE,
            )
        )
        acc_dot = always_redraw(
            lambda: Dot(
                acc_axes.c2p(time_tracker.get_value(), ay(time_tracker.get_value())),
                color=RED,
            )
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
