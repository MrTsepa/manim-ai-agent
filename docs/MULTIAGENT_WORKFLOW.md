# Multiagent Workflow Guide

This document provides guidelines for running multiple AI agents simultaneously on
this codebase and merging their work cleanly.

## Agent Identity

Each agent session should set a unique `AGENT_ID` environment variable at the start
of its session. This ID is used to namespace scratchpad files and avoid collisions.

```bash
# At the start of every agent session, set a unique ID
export AGENT_ID="agent-$(date +%s)-$$"
# or use a descriptive name
export AGENT_ID="newton-scene"
```

If `AGENT_ID` is not set, agents share the default namespace which may cause conflicts.

## Directory Structure for Multiagent Work

### Agent-Namespaced Scratchpad

Instead of writing directly to `agent_scratchpad/`, use:

```bash
# Create your namespaced workspace
mkdir -p agent_scratchpad/${AGENT_ID:-default}

# Write review artifacts to your namespace
ffmpeg -i output/videos/480p15/MyScene.mp4 \
  -vf "fps=10,scale=320:-1:flags=lanczos" \
  -y agent_scratchpad/${AGENT_ID:-default}/review.gif

# Extract frames to your namespace
ffmpeg -y -ss 00:00:03 -i output/videos/480p15/MyScene.mp4 \
  -vframes 1 -update 1 agent_scratchpad/${AGENT_ID:-default}/frame_3s.png
```

### Video Output Isolation

When multiple agents might render the same scene class, use custom output directories:

```bash
uv run python -m ai_video_studio.pipeline.cli render-scene MyScene \
  --output-dir output/videos-${AGENT_ID:-default}
```

## Merge-Friendly Development Patterns

### Pattern 1: One Scene = One File

Each scene lives in its own file under `src/ai_video_studio/manim_scenes/scenes/`:

```
scenes/
├── my_new_scene.py      # Agent A's work
├── another_scene.py     # Agent B's work
└── third_scene.py       # Agent C's work
```

This is already the pattern in this codebase. **Do not add multiple scenes per file.**

### Pattern 2: Auto-Discovery Instead of Central Registration

Use the `@register_scene` decorator (see Scene Registration below) instead of manually
editing `cli.py` or `demo_scenes.py`. This avoids merge conflicts in central files.

### Pattern 3: Per-Scene Metadata Files

Instead of adding to `docs/scene_library.yaml`, create a metadata file alongside your scene:

```
scenes/
├── my_new_scene.py
├── my_new_scene.meta.yaml    # Scene metadata lives with the scene
```

The scene library loader will auto-discover these files.

## Files to Avoid Editing (Merge Conflict Hotspots)

| File | Risk | Alternative |
|------|------|-------------|
| `cli.py` | High - every scene adds imports + subparsers | Use `render-scene` with auto-discovery |
| `demo_scenes.py` | High - central `__all__` list | Use `@register_scene` decorator |
| `scene_library.yaml` | High - single registry file | Use per-scene `.meta.yaml` files |
| `pyproject.toml` | Medium - dependency additions | Coordinate via PR comments |
| `uv.lock` | Medium - auto-generated | Run `uv sync` after merge |

## Branch Strategy Recommendations

### Naming Convention

```
scene/{scene-name}        # For new scene development
fix/{scene-name}/{issue}  # For scene fixes
refactor/{component}      # For structural changes
```

### Merge Order

1. **Merge structural changes first** (refactors, new utilities)
2. **Merge scene branches in any order** (isolated by design)
3. **Run `uv sync`** after merging to regenerate lock file
4. **Run tests** to verify nothing broke

### Resolving Conflicts

If conflicts occur in central files:

1. **`uv.lock`**: Delete the file and run `uv sync` to regenerate
2. **`cli.py`**: Accept both changes (additive) then verify imports
3. **`demo_scenes.py`**: Accept both changes to `__all__` list
4. **`scene_library.yaml`**: Accept both scene entries

## Scene Registration

### Using the `@register_scene` Decorator

```python
from ai_video_studio.manim_scenes.registry import register_scene

@register_scene(
    id="my_scene_v1",
    title="My New Scene",
    tags=["geometry", "animation"],
)
class MyNewScene(Scene):
    def construct(self):
        ...
```

The decorator auto-registers the scene without touching central files.

### Per-Scene Metadata File

Create `my_scene.meta.yaml` alongside `my_scene.py`:

```yaml
id: my_scene_v1
title: "My New Scene"
scene_class: "MyNewScene"
tags:
  - geometry
  - animation
quality_notes:
  - "Clean layout with proper spacing"
```

## Pre-Merge Checklist

Before merging your branch:

- [ ] Scene is in its own file under `scenes/`
- [ ] Review artifacts are in namespaced scratchpad (or cleaned up)
- [ ] No edits to central registry files (or coordinated with other agents)
- [ ] Tests pass: `uv run pytest`
- [ ] Linting clean: `uv run ruff check`
- [ ] Scene renders successfully at low quality

## Troubleshooting

### "Another agent's artifacts are in my scratchpad"

You're using the shared namespace. Set `AGENT_ID`:
```bash
export AGENT_ID="my-unique-id"
```

### "Merge conflict in cli.py"

Both agents added scenes. Accept both sets of changes (imports + handlers + subparsers).
Consider using dynamic scene discovery to avoid future conflicts.

### "uv.lock has conflicts"

```bash
# Delete and regenerate
rm uv.lock
uv sync
```

### "Scene not found in CLI"

If using auto-discovery, ensure your scene has the `@register_scene` decorator or a
`.meta.yaml` file.

