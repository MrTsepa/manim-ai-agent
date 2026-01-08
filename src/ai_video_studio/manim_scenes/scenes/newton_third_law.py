"""Newton's third law scene - action and reaction forces."""

from manim import (
    Arrow,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    GrowArrow,
    LEFT,
    MathTex,
    ORIGIN,
    RIGHT,
    Scene,
    Text,
    UP,
    YELLOW,
    BLUE,
    GREEN,
    Write,
    smooth,
    always_redraw,
)

from ai_video_studio.manim_scenes.layouts import setup_titled_2d_scene
from ai_video_studio.manim_scenes.primitives import create_ground_line, create_labeled_block
from ai_video_studio.manim_scenes.registry import register_scene


@register_scene(
    id="newton_third_law_v1",
    title="Newton's Third Law",
    tags=["physics", "mechanics", "newton", "action-reaction"],
    quality_notes=[
        "Balanced central interaction with equal force arrows.",
        "Equation lands after the push to reinforce the law.",
        "Clean spacing between title, interaction, and formula.",
    ],
)
class NewtonThirdLawScene(Scene):
    """A scene showing equal and opposite forces during a push."""

    def construct(self):
        """Create and animate the Newton's third law scene."""
        # Use the standard 2D title layout
        setup_titled_2d_scene(self, "Newton's Third Law")

        center_y = 0.2
        arrow_y_offset = 0.3

        # Use primitives for ground and blocks
        ground = create_ground_line(width=12.4, y_position=0.35)

        left_group = create_labeled_block("A", color=BLUE)
        right_group = create_labeled_block("B", color=GREEN)

        left_group.move_to(LEFT * 1.1 + UP * center_y)
        right_group.move_to(RIGHT * 1.1 + UP * center_y)

        contact_label = Text("Push", font="Menlo", font_size=26)
        contact_label.move_to(ORIGIN + UP * 0.95)

        self.play(Create(ground), FadeIn(left_group), FadeIn(right_group), run_time=0.8)
        self.play(FadeIn(contact_label), run_time=0.4)

        force_length = 1.9

        def contact_point():
            return (left_group.get_right() + right_group.get_left()) / 2 + UP * arrow_y_offset

        action_arrow = always_redraw(
            lambda: Arrow(
                start=contact_point(),
                end=contact_point() + RIGHT * force_length,
                buff=0.05,
                color=YELLOW,
                max_tip_length_to_length_ratio=0.25,
            )
        )
        reaction_arrow = always_redraw(
            lambda: Arrow(
                start=contact_point(),
                end=contact_point() + LEFT * force_length,
                buff=0.05,
                color=YELLOW,
                max_tip_length_to_length_ratio=0.25,
            )
        )

        action_label = always_redraw(
            lambda: MathTex("F_{A\\to B}", font_size=26, color=YELLOW).next_to(
                action_arrow, UP, buff=0.2
            )
        )
        reaction_label = always_redraw(
            lambda: MathTex("F_{B\\to A}", font_size=26, color=YELLOW).next_to(
                reaction_arrow, UP, buff=0.2
            )
        )

        self.play(GrowArrow(action_arrow), GrowArrow(reaction_arrow), run_time=0.6)
        self.play(FadeIn(action_label), FadeIn(reaction_label), run_time=0.4)

        self.play(
            left_group.animate.shift(LEFT * 2.0),
            right_group.animate.shift(RIGHT * 2.0),
            run_time=1.6,
            rate_func=smooth,
        )

        equation = MathTex("\\vec{F}_{A\\to B} = -\\vec{F}_{B\\to A}", font_size=38)
        equation.move_to(DOWN * 2.3)

        self.play(Write(equation), run_time=0.7)
        self.play(FadeOut(contact_label), FadeOut(action_label), FadeOut(reaction_label), run_time=0.4)
        self.wait(0.8)
