# Loss Descent Demo

A simple, elegant one-scene demo that visualizes the core intuition: **optimizing loss = moving downhill on a landscape**.

## Overview

This demo shows a ball rolling down a smooth bowl surface (paraboloid), representing how model parameters move downhill during loss optimization. Lower loss is simply lower height.

## Components Created

### 1. Micro-Script (Narration)

**Text:**
> "When we optimize a model's loss, we're really trying to move its parameters downhill on a surface. Lower loss is simply lower height."

**Location:** `src/ai_video_studio/manim_scenes/demo_scenes.py` → `get_loss_descent_narration_segment()`

**JSON Reference:** `docs/loss_descent_narration.json`

### 2. Scene Specification

A complete `SceneSpec` defining:
- **3D Axes**: Spatial reference frame
- **Paraboloid Surface**: The loss landscape (bowl shape)
- **Ball**: Represents model parameters (starts high, rolls down)
- **Gradient Arrow**: Briefly shows direction of steepest descent

**Location:** `src/ai_video_studio/manim_scenes/demo_scenes.py` → `get_loss_descent_scene_spec()`

**JSON Reference:** `docs/loss_descent_scene_spec.json`

### 3. Manim Primitives

Reusable 3D visualization functions in `src/ai_video_studio/manim_scenes/primitives.py`:

- `create_paraboloid_surface()` - Creates the bowl-shaped loss landscape
- `create_ball()` - Creates a sphere representing the model state
- `create_gradient_arrow()` - Creates a 3D arrow showing gradient direction

### 4. Spec-Driven Scene System

- **`SpecDrivenScene`** (`src/ai_video_studio/manim_scenes/base_scene.py`): Base class that interprets `SceneSpec` objects and automatically creates Manim animations
- **`LossDescentDemoScene`** (`src/ai_video_studio/manim_scenes/demo_scenes.py`): The actual demo scene class

## Animation Sequence

1. **0.0s**: Axes appear
2. **0.3s**: Surface (bowl) appears
3. **0.8s**: Ball appears at high point `[2.2, 1.4, 6.8]`
4. **1.0s**: Red gradient arrow appears, pointing downhill
5. **1.5s**: Arrow fades out
6. **1.6s**: Ball moves to intermediate position `[1.2, 0.9, 2.2]`
7. **3.0s**: Ball moves to final low position `[0.4, 0.3, 0.24]`
8. **8.0s**: Scene ends

## Usage

### Render the Scene

```bash
# Using the CLI
python -m ai_video_studio.pipeline.cli render-loss-descent

# With options
python -m ai_video_studio.pipeline.cli render-loss-descent --quality low_quality --preview
```

### Programmatic Usage

```python
from ai_video_studio.manim_scenes.demo_scenes import LossDescentDemoScene
from ai_video_studio.pipeline.render_scenes import render_scene

# Render the scene
video_path = render_scene(
    LossDescentDemoScene,
    quality="low_quality",
    preview=True
)
print(f"Rendered to: {video_path}")
```

### Access the Spec and Narration

```python
from ai_video_studio.manim_scenes.demo_scenes import (
    get_loss_descent_scene_spec,
    get_loss_descent_narration_segment
)

# Get the scene specification
spec = get_loss_descent_scene_spec()

# Get the narration
narration = get_loss_descent_narration_segment()
print(narration.text)
```

## Files Created/Modified

- ✅ `src/ai_video_studio/manim_scenes/primitives.py` - 3D visualization primitives
- ✅ `src/ai_video_studio/manim_scenes/base_scene.py` - SpecDrivenScene base class
- ✅ `src/ai_video_studio/manim_scenes/demo_scenes.py` - LossDescentDemoScene and helpers
- ✅ `src/ai_video_studio/pipeline/cli.py` - Added `render-loss-descent` command
- ✅ `docs/loss_descent_scene_spec.json` - JSON reference for the scene spec
- ✅ `docs/loss_descent_narration.json` - JSON reference for the narration

## Next Steps

This demo proves the core system works. You can now:

1. **Extend primitives**: Add more 3D shapes, surfaces, and visual elements
2. **Add more scenes**: Create additional demos using the same spec-driven approach
3. **Load from JSON**: Implement JSON loading to create scenes from external specs
4. **Add voiceover**: Integrate narration timing with `manim-voiceover`

## Design Notes

- Uses `ThreeDScene` for proper 3D rendering in Manim CE
- Color strings in specs are automatically converted to Manim color constants
- The spec-driven approach makes it easy for LLM agents to generate new scenes
- All timing is explicit in the `SceneActionSpec` objects

