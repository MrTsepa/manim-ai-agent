"""Softmax bars scene - logits transforming into softmax probabilities."""

from __future__ import annotations

import numpy as np
from manim import (
    Create,
    DecimalNumber,
    Dot,
    FadeIn,
    LaggedStart,
    Line,
    LEFT,
    Rectangle,
    RIGHT,
    Scene,
    Text,
    Transform,
    DOWN,
    UP,
    VGroup,
    ValueTracker,
    BLACK,
    BLUE,
    GREY_B,
    WHITE,
)
from ai_video_studio.manim_scenes.registry import register_scene


@register_scene(
    id="softmax_bars_v1",
    title="Softmax Bars",
    tags=["probability", "softmax", "bars", "ml"],
    quality_notes=[
        "Logits bars morph into softmax probabilities.",
        "Temperature slider shows sharpening vs. flattening.",
    ],
)
class SoftmaxBarsScene(Scene):
    """Animate logits bars transforming into softmax probabilities with temperature."""

    def construct(self) -> None:
        logits = np.array([2.6, 1.4, 0.9, 0.4], dtype=float)
        labels = ["A", "B", "C", "D"]

        bar_width = 0.8
        spacing = 0.35
        max_bar_height = 3.6
        baseline_y = -1.3
        target_max = 0.75

        total_width = len(logits) * bar_width + (len(logits) - 1) * spacing
        start_x = -total_width / 2 + bar_width / 2
        x_positions = [
            start_x + i * (bar_width + spacing) for i in range(len(logits))
        ]

        def softmax(values: np.ndarray, temperature: float = 1.0) -> np.ndarray:
            scaled = values / max(temperature, 1e-6)
            exps = np.exp(scaled - np.max(scaled))
            return exps / np.sum(exps)

        def make_bar_group(values: np.ndarray, color=BLUE) -> VGroup:
            bars = VGroup()
            for i, value in enumerate(values):
                height = max_bar_height * value
                bar = Rectangle(
                    width=bar_width,
                    height=max(height, 0.05),
                    stroke_width=2,
                )
                bar.set_fill(color, opacity=0.95)
                bar.set_stroke(WHITE, opacity=0.9)
                bar.move_to([x_positions[i], baseline_y + height / 2, 0])
                bars.add(bar)
            return bars

        baseline = Line(
            [start_x - bar_width / 2, baseline_y, 0],
            [start_x + total_width - bar_width / 2, baseline_y, 0],
            color=GREY_B,
            stroke_width=4,
        )
        baseline.set_opacity(0.6)

        logit_heights = (logits / np.max(logits)) * target_max
        softmax_base = softmax(logits, temperature=1.0)
        softmax_scale = target_max / softmax_base.max()
        logit_bars = make_bar_group(logit_heights, color=BLUE)
        for bar in logit_bars:
            bar.set_z_index(1)

        bar_labels = VGroup()
        for i, label in enumerate(labels):
            text = Text(label, font="Menlo", font_size=26, color=WHITE)
            text.move_to([x_positions[i], baseline_y - 0.4, 0])
            text.set_z_index(2)
            bar_labels.add(text)

        title = Text("Softmax Bars", font="Menlo", font_size=40, color=WHITE)
        title.to_edge(UP)
        subtitle = Text("Logits", font="Menlo", font_size=26, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.2)

        self.play(FadeIn(title), FadeIn(subtitle), run_time=0.6)
        self.play(Create(baseline), FadeIn(bar_labels), run_time=0.4)
        self.play(
            LaggedStart(*[Create(bar) for bar in logit_bars], lag_ratio=0.12),
            run_time=0.9,
        )

        temp_tracker = ValueTracker(1.0)
        slider_line = Line([-2.0, 0, 0], [2.0, 0, 0], color=GREY_B, stroke_width=4)
        slider_line.set_opacity(0.6)
        slider_label = Text("Temperature", font="Menlo", font_size=22, color=GREY_B)
        slider_label.next_to(slider_line, LEFT, buff=0.35)
        slider_label.set_y(slider_line.get_center()[1])

        knob = Dot(color=WHITE, radius=0.06)
        knob.add_updater(
            lambda m: m.move_to(
                [
                    np.interp(
                        temp_tracker.get_value(),
                        [0.5, 2.0],
                        [slider_line.get_start()[0], slider_line.get_end()[0]],
                    ),
                    slider_line.get_center()[1],
                    0,
                ]
            )
        )

        temp_value = DecimalNumber(1.0, num_decimal_places=2, font_size=28)
        temp_value.set_color(WHITE)

        def update_temp_value(mobj) -> None:
            mobj.set_value(temp_tracker.get_value())
            mobj.next_to(knob, UP, buff=0.45)

        temp_value.add_updater(update_temp_value)

        slider_group = VGroup(slider_label, slider_line, knob, temp_value)
        slider_group.shift(DOWN * 3.0)
        slider_group.set_opacity(0.75)

        self.play(FadeIn(slider_group), run_time=0.6)
        self.wait(0.4)

        blend_tracker = ValueTracker(0.0)
        softmax_label = Text("Softmax", font="Menlo", font_size=26, color=GREY_B)
        softmax_label.move_to(subtitle.get_center())

        def update_blend_bar(bar, index: int) -> None:
            blend = blend_tracker.get_value()
            target = softmax(logits, temperature=1.0) * softmax_scale
            blended = logit_heights[index] * (1 - blend) + target[index] * blend
            height = max_bar_height * blended
            max_blended = max(
                logit_heights.max() * (1 - blend) + target.max() * blend,
                1e-6,
            )
            bar.set_height(max(height, 0.05))
            bar.move_to([x_positions[index], baseline_y + height / 2, 0])
            bar.set_fill(BLUE, opacity=0.6 + 0.35 * (blended / max_blended))

        for i, bar in enumerate(logit_bars):
            bar.add_updater(lambda m, idx=i: update_blend_bar(m, idx))

        self.play(blend_tracker.animate.set_value(1.0), run_time=1.2)
        self.play(Transform(subtitle, softmax_label), run_time=0.4)
        self.wait(0.2)

        for bar in logit_bars:
            bar.clear_updaters()

        value_labels = VGroup()
        softmax_probs = softmax(logits, temperature=1.0)
        for i in range(len(logits)):
            label = DecimalNumber(
                softmax_probs[i],
                num_decimal_places=2,
                include_sign=False,
                font_size=28,
                color=WHITE,
            )
            label.set_color(WHITE)
            label.set_stroke(BLACK, width=3, opacity=1.0)
            label.add_background_rectangle(color=BLACK, opacity=0.8, buff=0.06)
            label.set_z_index(20)
            if hasattr(label, "background_rectangle"):
                label.background_rectangle.set_z_index(19)
            label.next_to(logit_bars[i], UP, buff=0.12)
            value_labels.add(label)

        self.play(FadeIn(value_labels), run_time=0.3)

        def update_bar(bar, index: int) -> None:
            probs = softmax(logits, temperature=temp_tracker.get_value()) * softmax_scale
            height = max_bar_height * probs[index]
            bar.set_height(max(height, 0.05))
            bar.set_width(bar_width)
            bar.move_to([x_positions[index], baseline_y + height / 2, 0])
            bar.set_fill(BLUE, opacity=0.6 + 0.35 * (probs[index] / probs.max()))

        for i, bar in enumerate(logit_bars):
            bar.add_updater(lambda m, idx=i: update_bar(m, idx))

        self.play(slider_group.animate.set_opacity(0.75), run_time=0.2)
        self.play(temp_tracker.animate.set_value(2.0), run_time=1.4)
        self.play(temp_tracker.animate.set_value(0.5), run_time=1.4)
        self.wait(0.6)
