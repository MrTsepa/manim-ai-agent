# Agent Instructions

This document provides instructions for AI coding agents working on this project.

## Environment Setup

**Always use the uv-managed environment.**

```bash
uv sync                    # Install dependencies
uv sync --extra dev        # Install dev dependencies
uv run <command>           # Run any Python command
```

## Creating Scenes

Register new scenes with the `@register_scene` decorator — no central file edits needed:

```python
from ai_video_studio.manim_scenes.registry import register_scene

@register_scene(id="my_scene_v1", title="My Scene", tags=["geometry"])
class MyScene(Scene):
    ...
```

Render with:
```bash
uv run python -m ai_video_studio.pipeline.cli render-scene MyScene --quality low_quality
```

## Project Structure

See `docs/AGENT_BACKBONE.md` for the complete project specification and roadmap.

### Output Directory

Videos are stored in `output/videos/`:
- `output/videos/480p15/` — Low quality (480p at 15fps)
- `output/videos/720p30/` — Medium quality (720p at 30fps)
- `output/videos/1080p60/` — High quality (1080p at 60fps)

### Agent Workspace

Use `agent_scratchpad/` for all intermediate and temporary files.
This folder is ephemeral and gitignored.

```bash
mkdir -p agent_scratchpad
```

## Video Review Workflow

Render at low quality, convert to GIF, review, iterate:

```bash
# Render
uv run python -m ai_video_studio.pipeline.cli render-scene MyScene --quality low_quality

# Convert to review GIF
ffmpeg -loglevel error -i output/videos/480p15/MyScene.mp4 \
  -vf "fps=10,scale=320:-1:flags=lanczos" -y agent_scratchpad/review.gif
```

### What to Review

- **Animations**: Timing, smoothness, visual flow
- **Layout**: Positioning, spacing, composition
- **Text**: Readability, sizing, placement
- **Colors**: Contrast, consistency, hierarchy
- **Transitions**: Scene changes and transformations

### Iterative Improvement

1. Render at low quality (480p15)
2. Generate a review GIF
3. Analyze and identify issues
4. Fix code
5. Re-render and review
6. Once satisfied, ask the user if they want a higher quality render

See `docs/VIDEO_CREATION_SCENARIO.md` for the full end-to-end video creation loop.

## Reference Example

The `ParabolicMotionScene` is an approved reference for layout and visual quality:
- File: `src/ai_video_studio/manim_scenes/demo_scenes.py`
- Artifacts: `samples_artifacts/parabolic_motion_review.gif`

## Manim 3D Tips

### Coordinate System

With `ThreeDScene` and overhead camera (phi ~70°):
- X and Y form the horizontal plane
- Z is vertical (screen up/down)
- `DOWN` = `[0, -1, 0]` moves horizontally, NOT down on screen

**Move content down on screen:**
```python
import numpy as np
mobject.shift(np.array([0, 0, -2.0]))  # Negative Z = down on screen
```

### Title + 3D Content Separation

```python
from ai_video_studio.manim_scenes.layouts import TitledSceneLayout

class MyScene(ThreeDScene):
    def construct(self):
        layout = TitledSceneLayout(self, title="My Title")
        layout.setup()
        surface = create_surface()
        layout.shift_content_down(surface)
        self.play(Create(surface))
```

### Reviewing 3D Scenes

Extract multiple frames to verify layout across camera angles:
```bash
ffmpeg -loglevel error -y -ss 00:00:03 -i video.mp4 -vframes 1 -update 1 frame_3s.png
ffmpeg -loglevel error -y -ss 00:00:06 -i video.mp4 -vframes 1 -update 1 frame_6s.png
ffmpeg -loglevel error -y -ss 00:00:10 -i video.mp4 -vframes 1 -update 1 frame_10s.png
```

## Development Workflow

1. `uv sync`
2. Make code changes
3. Render and review (create GIF)
4. Check for linting errors
5. Commit
