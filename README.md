# AI Video Studio

A self-improving harness for AI video editing agents. Point an AI agent at this repo, and it can autonomously create, render, review, and iterate on [3Blue1Brown](https://www.3blue1brown.com/)-style educational animations using [Manim](https://www.manim.community/).

> **Status:** Currently supports individual scene generation with autonomous render-review-improve loops. Full multi-scene video generation with narration, transitions, and end-to-end pipeline is coming soon.

## How It Works

The core loop is: **plan → implement → render → review → critique → improve → repeat**.

An AI agent working in this repo can:
1. **Create** a new Manim scene using the `@register_scene` decorator
2. **Render** it via CLI (`render-scene MyScene --quality low_quality`)
3. **Review** by generating a GIF and extracting key frames
4. **Self-critique** the output for layout, timing, colors, and readability
5. **Get external critique** via GPT with vision (score 0-10)
6. **Iterate** until the score hits 9+, then ask the user about higher quality

See [`docs/VIDEO_CREATION_SCENARIO.md`](docs/VIDEO_CREATION_SCENARIO.md) for the full autonomous workflow, and [`AGENTS.md`](AGENTS.md) for agent instructions.

## Quick Start

```bash
# Install
git clone https://github.com/MrTsepa/manim-ai-agent.git
cd manim-ai-agent
uv sync

# Render a demo scene
uv run python -m ai_video_studio.pipeline.cli render-demo --quality low_quality

# List all available scenes
uv run python -m ai_video_studio.pipeline.cli list-scenes

# Render any scene by name
uv run python -m ai_video_studio.pipeline.cli render-scene ParabolicMotionScene --quality low_quality
```

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

## License

MIT
