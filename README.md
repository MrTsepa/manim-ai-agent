# AI Video Studio

A self-improving harness for AI video editing agents. Point an AI agent at this repo, and it can autonomously create, render, review, and iterate on high-quality educational math animations using [Manim](https://www.manim.community/).

> The core loop — autonomous scene generation with render-review-improve cycles — is fully working. Multi-scene stitching with narration and transitions is on the roadmap.

## How It Works

The core loop is: **plan → implement → render → review → critique → improve → repeat**.

An AI agent working in this repo can:
1. **Create** a new Manim scene using the `@register_scene` decorator
2. **Render** it via CLI (`render-scene MyScene --quality low_quality`)
3. **Review** by generating a GIF and extracting key frames
4. **Self-critique** the output for layout, timing, colors, and readability
5. **Get external critique** via GPT with vision (score 0-10)
6. **Iterate** until the score hits 9+, then ask the user about higher quality

The codebase is designed for extensibility — agents learn from past examples in the scene library, reuse proven layout helpers and primitives, and can refactor or extend shared code (layouts, primitives, registry) when existing abstractions don't fit a new scene. Each new scene makes the next one easier to build.

See [`docs/VIDEO_CREATION_SCENARIO.md`](docs/VIDEO_CREATION_SCENARIO.md) for the full autonomous workflow, and [`AGENTS.md`](AGENTS.md) for agent instructions.

## Examples

All scenes below were generated and refined autonomously by AI agents using this harness.

| Parabolic Motion | Pythagorean Theorem | Secant to Derivative |
|:---:|:---:|:---:|
| ![Parabolic Motion](samples_artifacts/parabolic_motion_review.gif) | ![Pythagorean Theorem](samples_artifacts/pythagorean_review.gif) | ![Secant to Derivative](samples_artifacts/secant_to_derivative_review.gif) |

## Quick Start

```bash
git clone https://github.com/MrTsepa/manim-ai-agent.git
cd manim-ai-agent
uv sync
```

Open the repo in a coding agent (Claude Code, Cursor, Windsurf, etc.) and ask it to create a video:

```
Create an animation showing how a Fourier series approximates a square wave.
Use @docs/VIDEO_CREATION_SCENARIO.md as your workflow guide.
```

The agent reads `AGENTS.md`, writes a Manim scene, renders a preview, critiques the output, and iterates until the result looks good. No Manim or Python knowledge needed.

Output videos are saved to `output/videos/`.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- LaTeX distribution (for Manim math rendering)
- ffmpeg

On macOS:
```bash
brew install --cask mactex
brew install ffmpeg
```

## Creating a New Scene

Register scenes with the `@register_scene` decorator — no central file edits needed:

```python
from manim import *
from ai_video_studio.manim_scenes.registry import register_scene

@register_scene(id="my_scene_v1", title="My Scene", tags=["geometry"])
class MyScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
```

Then render:
```bash
uv run python -m ai_video_studio.pipeline.cli render-scene MyScene --quality low_quality
```

## Project Structure

```
AGENTS.md                    # Agent instructions (start here)
docs/
    AGENT_BACKBONE.md        # Project spec and roadmap
    VIDEO_CREATION_SCENARIO.md  # Autonomous video creation workflow
    scene_library.yaml       # Catalog of approved reference scenes
src/ai_video_studio/
    config/                  # Settings and environment config
    core/                    # Data models and utilities
    manim_scenes/
        scenes/              # Individual scene implementations
        layouts.py           # Reusable layout helpers
        primitives.py        # Physics and math primitives
        registry.py          # Scene auto-discovery and registration
    pipeline/
        cli.py               # CLI entrypoint
        render_scenes.py     # Manim rendering wrapper
```

## Available Scenes

| Scene | Description |
|-------|-------------|
| `FunctionDemoScene` | Simple function plot with a moving point |
| `ParabolicMotionScene` | Projectile trajectory with position/velocity/acceleration plots |
| `PythagoreanTheoremScene` | Visual proof with squares on a right triangle |
| `LossDescentDemoScene` | 3D loss surface with gradient descent ball |
| `SecantToDerivativeScene` | Secant line converging to tangent |
| `SoftmaxBarsScene` | Animated softmax probability distribution |
| `NewtonThirdLawScene` | Newton's third law force visualization |

## Quality Presets

| Preset | Resolution | FPS |
|--------|-----------|-----|
| `low_quality` | 480p | 15 |
| `medium_quality` | 720p | 30 |
| `high_quality` | 1080p | 60 |
| `production_quality` | 1440p | 60 |

## Configuration

```bash
cp .env.example .env
# Add your OpenAI API key for GPT video critique
```

## Acknowledgements

This project was heavily inspired by [TheoremExplainAgent](https://tiger-ai-lab.github.io/TheoremExplainAgent/) from TIGER-AI-Lab — a multimodal AI agent that autonomously generates Manim videos to explain mathematical theorems.

## License

MIT
