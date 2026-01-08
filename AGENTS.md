# Agent Instructions

This document provides instructions for AI coding agents working on this project.

## UV Environment Setup

**Always use the uv-managed environment when working on this project.**

### Initial Setup

1. Sync the environment (creates `.venv` if needed):
   ```bash
   uv sync
   ```

2. Install dev dependencies if needed:
   ```bash
   uv sync --extra dev
   ```

### Working with UV

- **Always use `uv run` for Python commands**
- When installing new dependencies, add them to `pyproject.toml` and run `uv sync`
- The `.venv` directory is already in `.gitignore`, so it won't be committed

### Testing Commands

After syncing, you can test the demo scene:
```bash
uv run python -m ai_video_studio.pipeline.cli render-demo --quality low_quality
```

## Project Structure

See `docs/AGENT_BACKBONE.md` for the complete project specification and roadmap.

### Output Directory

Videos produced by the Manim integration are stored in the `output/videos/` folder:
- `output/videos/480p15/` - Low quality renders (480p at 15fps)
- `output/videos/720p30/` - Medium quality renders (720p at 30fps)
- `output/videos/1080p60/` - High quality renders (1080p at 60fps)

Rendered videos are named after their scene class (e.g., `LossDescentDemoScene.mp4`).

### Agent Workspace

**Use the `agent_scratchpad/` folder for all intermediate and temporary files.**
This folder is ephemeral and should not be relied on across sessions.

This keeps working files separate from the source code repository:
- Store scratch files, experiments, and drafts in `agent_scratchpad/`
- Store generated assets being reviewed in `agent_scratchpad/`
- Store temporary processing outputs in `agent_scratchpad/`
- Never commit `agent_scratchpad/` contents to version control
- Store approved sample artifacts in `samples_artifacts/` (not in the scratchpad)

```bash
# Create workspace if it doesn't exist
mkdir -p agent_scratchpad
```

## Video Review Workflow

When reviewing rendered videos, create a low-resolution GIF to analyze the output:

### Creating Review GIFs

```bash
# Convert video to low-res GIF for review (recommended: 320px width, 10fps)
ffmpeg -i output/videos/480p15/YourScene.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" -y agent_scratchpad/review.gif
```

### What to Review

When processing the GIF for review, evaluate:
- **Animations**: Timing, smoothness, and visual flow
- **Layout**: Element positioning, spacing, and composition
- **Text**: Readability, sizing, and placement
- **Colors**: Contrast, consistency, and visual hierarchy
- **Transitions**: Scene changes and object transformations
- **Overall Quality**: Professional appearance and clarity

### Iterative Improvement

1. Render the scene at low quality (480p15) for fast iteration
2. Generate a review GIF
3. Analyze the output and identify issues
4. Make code adjustments
5. Re-render and review again
6. Once satisfied, stop the process and ask the user if he wants to render higher quality video

## Reference Quality Example (Approved)

The Parabolic Motion scene (trajectory + position/velocity/acceleration plots) is an approved reference
for high-quality layout, alignment, and visual balance. Use it as a style benchmark for future scenes:
- File: `src/ai_video_studio/manim_scenes/demo_scenes.py`
- Scene class: `ParabolicMotionScene`
- Latest low-quality render: `output/videos/480p15/ParabolicMotionScene.mp4`
- Review assets: `samples_artifacts/parabolic_motion_review.gif` and
  `samples_artifacts/parabolic_frame_3s.png`, `samples_artifacts/parabolic_frame_6s.png`,
  `samples_artifacts/parabolic_frame_10s.png`

## Development Workflow

1. Run `uv sync`
2. Make code changes
3. Test using CLI commands
4. Render and review video output (create GIF for analysis)
5. Check for linting errors
6. Commit changes

See `docs/VIDEO_CREATION_SCENARIO.md` for the full end-to-end video creation loop.

## Manim 3D Scene Tips

### Coordinate System in 3D Scenes

When working with `ThreeDScene` and overhead camera angles (phi ~70°):

- **X and Y** form the horizontal plane (the "ground")
- **Z** is the vertical axis pointing upward
- The screen's **vertical direction** aligns more with **Z**, not Y
- `DOWN` constant is `[0, -1, 0]` (negative Y) - this moves things horizontally in 3D space, NOT down on screen!

### Moving Content Down on Screen

**Wrong approach** (shifts horizontally in 3D space):
```python
mobject.shift(DOWN * 2.0)  # DOWN = [0, -1, 0]
```

**Correct approach** (shifts down visually on screen):
```python
import numpy as np
mobject.shift(np.array([0, 0, -2.0]))  # Negative Z = down on screen
```

### Title and 3D Content Separation

Use `TitledSceneLayout` from `ai_video_studio.manim_scenes.layouts` to prevent title/content overlap:

```python
from ai_video_studio.manim_scenes.layouts import TitledSceneLayout

class MyScene(ThreeDScene):
    def construct(self):
        layout = TitledSceneLayout(self, title="My Title")
        layout.setup()
        
        # Create 3D content
        surface = create_surface()
        layout.shift_content_down(surface)  # Shifts in Z direction
        self.play(Create(surface))
```

Key points:
- Title is fixed to camera frame using `add_fixed_in_frame_mobjects()` - it won't rotate
- 3D content is shifted down (negative Z) by `CONTENT_SHIFT_DOWN = 2.0` units
- This creates visual separation throughout camera rotation

### Reviewing 3D Scenes

When reviewing 3D scenes, extract **multiple frames at different timestamps** to verify layout holds throughout camera rotation:

```bash
# Extract frames at 3s, 6s, 10s to check different camera angles
ffmpeg -y -ss 00:00:03 -i video.mp4 -vframes 1 -update 1 frame_3s.png
ffmpeg -y -ss 00:00:06 -i video.mp4 -vframes 1 -update 1 frame_6s.png
ffmpeg -y -ss 00:00:10 -i video.mp4 -vframes 1 -update 1 frame_10s.png
```

Camera rotation can cause 3D objects to appear at different screen positions - what looks separated in one frame may overlap in another.

### Common 3D Scene Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Title overlaps 3D content | Content not shifted in Z | Use `TitledSceneLayout` or shift with `[0, 0, -Z]` |
| `DOWN` shift doesn't move content down visually | `DOWN` is Y-direction, not screen-vertical | Use `np.array([0, 0, -amount])` for Z shift |
| Overlap varies with camera angle | Camera rotation changes apparent positions | Extract multiple frames to verify separation |
| Title rotates with scene | Title added normally | Use `add_fixed_in_frame_mobjects(title)` |
