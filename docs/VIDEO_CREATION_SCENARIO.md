# Video Creation Scenario (Agent Workflow)

This document defines the expected end-to-end workflow for creating and refining
Manim videos in this repository. Agents should follow this loop eagerly, without
stopping after a single iteration, until the output is high-quality and stable.

## Core Principles

- Always use the UV-managed environment (`uv run`).
- **Multiagent-aware**: Use `agent_scratchpad/${AGENT_ID:-default}/` for artifacts.
- **Merge-friendly**: Use `@register_scene` decorator, avoid editing central files.
- Follow a strict render → review → critique → adjust loop.
- Do not stop after one iteration; continue until satisfied with the result.
- Once satisfied, ask the user whether to render a higher-quality version.

## Multiagent Setup (First Step)

Before starting work, set up your agent namespace:

```bash
# Set unique agent ID (optional but recommended for parallel work)
export AGENT_ID="$(echo $PWD | md5 | head -c 8)"  # or use a descriptive name

# Create namespaced scratchpad
mkdir -p agent_scratchpad/${AGENT_ID:-default}
```

## Video Creation Loop

1) **Plan the scene**
   - Decide the scene structure, timing, layout, and visual hierarchy.
   - Reuse known-good patterns from `docs/scene_library.yaml`.

2) **Implement / update the scene**
   - Modify or create the Manim scene code.
   - Keep edits focused and incremental.

3) **Render (low quality)**
   - Use low quality for fast iteration:
     - `uv run python -m ai_video_studio.pipeline.cli render-<scene> --quality low_quality`
   - Confirm the output file path.

4) **Create review artifacts**
   - Use namespaced paths (set `SCRATCH=agent_scratchpad/${AGENT_ID:-default}`):
   - Make a low-res GIF for fast review:
     - `ffmpeg -i output/videos/480p15/<Scene>.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" -y $SCRATCH/review.gif`
   - Extract key frames (e.g., 3s, 6s, 10s) when camera or motion changes:
     - `ffmpeg -y -ss 00:00:03 -i output/videos/480p15/<Scene>.mp4 -vframes 1 -update 1 $SCRATCH/frame_3s.png`
     - `ffmpeg -y -ss 00:00:06 -i output/videos/480p15/<Scene>.mp4 -vframes 1 -update 1 $SCRATCH/frame_6s.png`
     - `ffmpeg -y -ss 00:00:10 -i output/videos/480p15/<Scene>.mp4 -vframes 1 -update 1 $SCRATCH/frame_10s.png`

5) **Self-critique**
   - Review the GIF and frames carefully for:
     - Animations (timing, smoothness, flow)
     - Layout (alignment, spacing, balance)
     - Text (readability, size, placement)
     - Colors (contrast, consistency, hierarchy)
     - Transitions (clarity of changes)
   - Be specific about issues and improvements.

6) **Adjust and improve**
   - Make targeted changes based on the critique.
   - Repeat steps 3–6 until the result is clean and balanced.
   - Do not stop after a single iteration—keep improving.

7) **Conclude the loop**
   - When satisfied, summarize the improvements.
   - **Provide final deliverables** to the user:
     - **Video**: Link to the rendered video (e.g., `output/videos/480p15/<Scene>.mp4`)
     - **GIF**: Link to the review GIF (e.g., `agent_scratchpad/${AGENT_ID}/review.gif`)
     - **Reference frames**: Links to key frame images showing important moments
     - **Merge-ready change**: Ensure the code change is clean, tested, and ready to merge
   - Ask the user if they want a higher-quality render.

## Final Deliverables Checklist

Before presenting work to the user, verify you have:

- [ ] Video file path (low-quality render)
- [ ] Review GIF for quick preview
- [ ] Reference frames at key timestamps (especially for 3D/animated scenes)
- [ ] Clean, focused code changes using `@register_scene` decorator
- [ ] No edits to central files (`cli.py`, `demo_scenes.py`) unless absolutely necessary
- [ ] Scene file in the correct location (`src/ai_video_studio/manim_scenes/scenes/`)

## Notes

- Store all review artifacts in `agent_scratchpad/${AGENT_ID:-default}/` (never in source).
- Copy any artifacts intended for the samples library into `samples_artifacts/`.
- Use reference scenes as quality benchmarks; see `docs/scene_library.yaml`.
- For 3D scenes, verify multiple timestamps because camera motion can shift layout.

## Multiagent Tips

- **Use `@register_scene` decorator** to avoid editing `cli.py` or `demo_scenes.py`.
- **One scene per file** under `src/ai_video_studio/manim_scenes/scenes/`.
- **Dynamic rendering**: `uv run python -m ai_video_studio.pipeline.cli render-scene <ClassName>`
- **Check agent info**: `uv run python -m ai_video_studio.pipeline.cli agent-info`
- **List discovered scenes**: `uv run python -m ai_video_studio.pipeline.cli list-scenes`

See `docs/MULTIAGENT_WORKFLOW.md` for complete guidelines.
