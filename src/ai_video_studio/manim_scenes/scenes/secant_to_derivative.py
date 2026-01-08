"""Secant to Derivative scene - visualizing the limit definition of derivative."""

import numpy as np
from manim import (
    Axes,
    Create,
    DashedLine,
    Dot,
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    MathTex,
    ParametricFunction,
    RIGHT,
    Scene,
    UP,
    ValueTracker,
    VGroup,
    DecimalNumber,
    always_redraw,
    BLUE,
    GREEN,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
)

from ai_video_studio.manim_scenes.layouts import setup_titled_2d_scene
from ai_video_studio.manim_scenes.registry import register_scene


@register_scene(
    id="secant_to_derivative_v1",
    title="Secant → Derivative",
    tags=["calculus", "derivative", "limit", "mathematics"],
    quality_notes=[
        "Shows secant line shrinking to tangent line as Δx→0.",
        "Visualizes the limit definition of derivative.",
    ],
)
class SecantToDerivativeScene(Scene):
    """
    A scene visualizing how a secant line becomes a tangent line as Δx→0.
    
    This demonstrates the fundamental limit definition of the derivative:
    f'(x) = lim(Δx→0) [f(x+Δx) - f(x)] / Δx
    """

    def construct(self):
        """Create and animate the scene."""
        # Use the standard 2D title layout
        layout = setup_titled_2d_scene(self, "Secant → Derivative", title_font_size=40)

        # Define a function: f(x) = x²/2 + sin(x) (interesting curve)
        def f(x):
            return 0.5 * x**2 + np.sin(x)

        # Derivative: f'(x) = x + cos(x)
        def df(x):
            return x + np.cos(x)

        # Point of interest
        x0 = 1.5
        y0 = f(x0)
        slope = df(x0)  # True derivative at x0

        # Create axes
        axes = Axes(
            x_range=[-1, 4, 1],
            y_range=[-1, 5, 1],
            x_length=6.0,
            y_length=4.6,
            axis_config={"include_numbers": True, "font_size": 26},
        )
        axes_labels = axes.get_axis_labels("x", "y")
        axes_group = VGroup(axes, axes_labels)
        axes_group.shift(DOWN * 0.5)
        axes_group.shift(RIGHT * 2.2)

        # Plot the function
        func_graph = axes.plot(f, x_range=[-0.5, 3.5], color=BLUE, stroke_width=3)
        
        # Fixed point at x0
        fixed_point = Dot(axes.c2p(x0, y0), color=RED, radius=0.08)
        fixed_label = MathTex("(x, f(x))", font_size=26, color=RED)
        fixed_label.next_to(fixed_point, UP + LEFT, buff=0.2)

        # Tracker for the second point (x0 + Δx)
        delta_x_tracker = ValueTracker(2.0)  # Start with large Δx

        # Second point that moves
        def get_second_point():
            x1 = x0 + delta_x_tracker.get_value()
            y1 = f(x1)
            return Dot(axes.c2p(x1, y1), color=GREEN, radius=0.08)

        second_point = always_redraw(get_second_point)
        
        # Label for second point
        def get_second_label():
            x1 = x0 + delta_x_tracker.get_value()
            y1 = f(x1)
            label = MathTex(
                f"(x+\\Delta x, f(x+\\Delta x))",
                font_size=22,
                color=GREEN,
            )
            label.next_to(axes.c2p(x1, y1), RIGHT + DOWN * 0.2, buff=0.25)
            return label

        second_label = always_redraw(get_second_label)

        # Secant line connecting the two points
        def get_secant_line():
            x1 = x0 + delta_x_tracker.get_value()
            y1 = f(x1)
            line = DashedLine(
                axes.c2p(x0, y0),
                axes.c2p(x1, y1),
                color=YELLOW,
                stroke_width=2.5,
            )
            return line

        secant_line = always_redraw(get_secant_line)

        # Full secant line (continuous, extends across the plot)
        def get_secant_full_line():
            x1 = x0 + delta_x_tracker.get_value()
            y1 = f(x1)
            dx = x1 - x0
            if abs(dx) < 1e-6:
                slope_secant = slope
            else:
                slope_secant = (y1 - y0) / dx

            def secant_func(x):
                return y0 + slope_secant * (x - x0)

            line = axes.plot(
                secant_func,
                x_range=[-0.5, 3.5],
                color=YELLOW,
                stroke_width=2,
            )
            line.set_stroke(opacity=0.7)
            return line

        secant_full_line = always_redraw(get_secant_full_line)

        # Δx bracket (anchored to x-axis)
        def get_delta_x_bracket():
            x1 = x0 + delta_x_tracker.get_value()
            delta_x = delta_x_tracker.get_value()
            opacity = 1.0

            start_x = axes.c2p(x0, 0)[0]
            end_x = axes.c2p(x1, 0)[0]
            bracket_y = axes.c2p(0, 0)[1] - 0.25

            line = DashedLine(
                [start_x, bracket_y, 0],
                [end_x, bracket_y, 0],
                color=ORANGE,
                stroke_width=2,
            )

            tick_length = 0.15
            left_tick = DashedLine(
                [start_x, bracket_y - tick_length, 0],
                [start_x, bracket_y + tick_length, 0],
                color=ORANGE,
                stroke_width=2,
            )
            right_tick = DashedLine(
                [end_x, bracket_y - tick_length, 0],
                [end_x, bracket_y + tick_length, 0],
                color=ORANGE,
                stroke_width=2,
            )

            label = MathTex(
                f"\\Delta x",
                font_size=28,
                color=ORANGE,
            )
            label.move_to([(start_x + end_x) / 2, bracket_y - 0.3, 0])

            group = VGroup(line, left_tick, right_tick, label)
            group.set_opacity(opacity)
            return group

        delta_x_bracket = always_redraw(get_delta_x_bracket)

        # Δy bracket (anchored to y-axis)
        def get_delta_y_bracket():
            x1 = x0 + delta_x_tracker.get_value()
            y1 = f(x1)
            delta_x = delta_x_tracker.get_value()
            opacity = 1.0

            bracket_x = axes.c2p(0, 0)[0] - 0.3
            start_y = axes.c2p(0, y0)[1]
            end_y = axes.c2p(0, y1)[1]

            line = DashedLine(
                [bracket_x, start_y, 0],
                [bracket_x, end_y, 0],
                color=GREEN,
                stroke_width=2,
            )

            tick_length = 0.15
            bottom_tick = DashedLine(
                [bracket_x - tick_length, start_y, 0],
                [bracket_x + tick_length, start_y, 0],
                color=GREEN,
                stroke_width=2,
            )
            top_tick = DashedLine(
                [bracket_x - tick_length, end_y, 0],
                [bracket_x + tick_length, end_y, 0],
                color=GREEN,
                stroke_width=2,
            )

            label = MathTex(
                f"\\Delta y",
                font_size=28,
                color=GREEN,
            )
            label.move_to([bracket_x - 0.35, (start_y + end_y) / 2, 0])

            group = VGroup(line, bottom_tick, top_tick, label)
            group.set_opacity(opacity)
            return group

        delta_y_bracket = always_redraw(get_delta_y_bracket)

        # Projection legs that move with the secant
        def get_projection_legs():
            x1 = x0 + delta_x_tracker.get_value()
            y1 = f(x1)
            delta_x = delta_x_tracker.get_value()
            if abs(delta_x) < 0.06:
                opacity = 0.0
            else:
                opacity = min(1.0, abs(delta_x) / 0.4)

            horizontal = DashedLine(
                axes.c2p(x0, y0),
                axes.c2p(x1, y0),
                color=ORANGE,
                stroke_width=2,
            )
            vertical = DashedLine(
                axes.c2p(x1, y0),
                axes.c2p(x1, y1),
                color=GREEN,
                stroke_width=2,
            )
            group = VGroup(horizontal, vertical)
            group.set_opacity(opacity)
            return group

        projection_legs = always_redraw(get_projection_legs)

        # Left panel: explanatory text + dynamic readout
        explanation_line_1 = MathTex(
            "\\text{As } \\Delta x \\text{ shrinks,}",
            font_size=26,
            color=WHITE,
        )

        explanation_line_2 = MathTex(
            "\\text{the secant slope } \\frac{\\Delta y}{\\Delta x} \\text{ approaches } f'(x).",
            font_size=26,
            color=WHITE,
        )

        explanation_block = VGroup(
            explanation_line_1,
            explanation_line_2,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        explanation_block.to_edge(LEFT, buff=0.6)

        def get_delta_y_value():
            delta_x = delta_x_tracker.get_value()
            x1 = x0 + delta_x
            return f(x1) - y0

        def get_secant_slope_value():
            delta_x = delta_x_tracker.get_value()
            delta_y = get_delta_y_value()
            if abs(delta_x) < 1e-6:
                return slope
            return delta_y / delta_x

        dx_label = MathTex("\\Delta x =", font_size=26, color=WHITE)
        dx_value = DecimalNumber(
            delta_x_tracker.get_value(),
            num_decimal_places=2,
            font_size=26,
            color=ORANGE,
        )
        dx_value.add_updater(lambda m: m.set_value(delta_x_tracker.get_value()))
        delta_x_readout = VGroup(dx_label, dx_value).arrange(RIGHT, buff=0.1)
        delta_x_readout.to_edge(LEFT, buff=0.6)

        dy_label = MathTex("\\Delta y =", font_size=26, color=WHITE)
        dy_value = DecimalNumber(
            get_delta_y_value(),
            num_decimal_places=2,
            font_size=26,
            color=GREEN,
        )
        dy_value.add_updater(lambda m: m.set_value(get_delta_y_value()))
        delta_y_readout = VGroup(dy_label, dy_value).arrange(RIGHT, buff=0.1)
        delta_y_readout.to_edge(LEFT, buff=0.6)

        slope_header = MathTex(
            "\\text{secant slope} = \\frac{\\Delta y}{\\Delta x}",
            font_size=26,
            color=WHITE,
        )

        slope_equals = MathTex("=", font_size=26, color=WHITE)
        slope_div = MathTex("/", font_size=26, color=WHITE)
        slope_approx = MathTex("\\approx", font_size=26, color=WHITE)
        slope_dy_value = DecimalNumber(
            get_delta_y_value(),
            num_decimal_places=2,
            font_size=26,
            color=GREEN,
        )
        slope_dx_value = DecimalNumber(
            delta_x_tracker.get_value(),
            num_decimal_places=2,
            font_size=26,
            color=ORANGE,
        )
        slope_m_value = DecimalNumber(
            get_secant_slope_value(),
            num_decimal_places=2,
            font_size=26,
            color=YELLOW,
        )
        slope_dy_value.add_updater(lambda m: m.set_value(get_delta_y_value()))
        slope_dx_value.add_updater(lambda m: m.set_value(delta_x_tracker.get_value()))
        slope_m_value.add_updater(lambda m: m.set_value(get_secant_slope_value()))

        slope_formula = VGroup(
            slope_equals,
            slope_dy_value,
            slope_div,
            slope_dx_value,
            slope_approx,
            slope_m_value,
        ).arrange(RIGHT, buff=0.12)
        slope_formula.to_edge(LEFT, buff=0.6)

        # Limit notation (appears when Δx is small)
        limit_intro = MathTex(
            "\\text{In the limit:}",
            font_size=26,
            color=WHITE,
        )
        limit_label = MathTex(
            "f'(x)=\\lim_{\\Delta x \\to 0} \\frac{f(x+\\Delta x)-f(x)}{\\Delta x}",
            font_size=26,
            color=WHITE,
        )
        limit_intro.set_opacity(0)
        limit_label.set_opacity(0)

        # Tangent line (appears when Δx is very small, use different color to distinguish)
        def get_tangent_line():
            delta_x_val = delta_x_tracker.get_value()
            # Only show if Δx is very small
            if abs(delta_x_val) > 0.15:
                return VGroup()  # Empty group
            
            # Tangent line: y = y0 + slope * (x - x0)
            def tangent_func(x):
                return y0 + slope * (x - x0)
            
            # Extend beyond the point
            x_range = [x0 - 1.5, x0 + 1.5]
            line = axes.plot(
                tangent_func,
                x_range=x_range,
                color=ORANGE,  # Different color from secant (YELLOW)
                stroke_width=4,  # Thicker to distinguish from secant
            )
            # Fade in as Δx approaches 0, fully opaque when very close
            opacity = max(0, 1 - abs(delta_x_val) / 0.15)
            if abs(delta_x_val) < 0.05:
                opacity = 1.0  # Fully visible when very close
            line.set_stroke(opacity=opacity)
            return line

        tangent_line = always_redraw(get_tangent_line)

        # Position everything
        # Animation sequence
        self.play(Create(axes), Create(axes_labels), run_time=1.0)
        self.play(Create(func_graph), run_time=1.2)
        
        self.play(FadeIn(fixed_point), FadeIn(fixed_label), run_time=0.6)
        
        self.add(second_point, second_label)
        self.add(secant_line)
        self.play(
            FadeIn(secant_full_line),
            FadeIn(delta_x_bracket),
            FadeIn(delta_y_bracket),
            FadeIn(projection_legs),
            run_time=0.8,
        )

        left_panel = VGroup(
            explanation_block,
            delta_x_readout,
            delta_y_readout,
            slope_header,
            slope_formula,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        left_panel.to_edge(LEFT, buff=0.6)
        left_panel.shift(DOWN * 0.2)

        limit_intro.next_to(left_panel, DOWN, aligned_edge=LEFT, buff=0.25)
        limit_label.next_to(limit_intro, DOWN, aligned_edge=LEFT, buff=0.2)

        self.play(FadeIn(left_panel), run_time=0.8)
        self.add(tangent_line, limit_intro, limit_label)
        
        # Animate Δx shrinking
        self.wait(0.5)
        self.play(
            delta_x_tracker.animate.set_value(0.01),
            run_time=5.5,
            rate_func=lambda t: 1 - (1 - t)**3,  # Ease out
        )
        
        # Ensure tangent line is visible and add limit notation
        self.wait(0.3)
        # Fade in limit notation smoothly and make it more prominent
        self.play(
            limit_intro.animate.set_opacity(1),
            limit_label.animate.set_opacity(1),
            run_time=1.5,
        )
        
        self.wait(1.5)
