"""Pythagorean theorem scene - geometric proof visualization."""

import numpy as np
from manim import (
    AnimationGroup,
    BLUE,
    Create,
    DOWN,
    FadeIn,
    GREEN,
    Indicate,
    LEFT,
    Line,
    MathTex,
    ORANGE,
    ORIGIN,
    Polygon,
    RIGHT,
    RightAngle,
    Scene,
    Square,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
)

from ai_video_studio.manim_scenes.registry import register_scene


@register_scene(
    id="pythagorean_theorem_v1",
    title="Pythagorean Theorem",
    tags=["sample", "geometry", "layout:split", "equation", "highlight"],
    quality_notes=[
        "Centered layout with title clearance.",
        "Squares and equation highlight in sync.",
        "Diagram labels sized to match equation.",
    ],
)
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
        square_c = Polygon(
            B, C, C + perp, B + perp, color=ORANGE, fill_opacity=0.18, stroke_width=3
        )

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
