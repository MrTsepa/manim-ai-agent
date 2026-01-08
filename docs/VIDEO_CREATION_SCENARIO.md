# Video Creation Scenario (Agent Workflow)

This document defines the expected end-to-end workflow for creating and refining
Manim videos in this repository. Agents should follow this loop eagerly, without
stopping after a single iteration, until the output is high-quality and stable.

## Core Principles

- Always use the UV-managed environment (`uv run`).
- Use `agent_scratchpad/` for intermediate artifacts (GIFs, frames, scratch files).
- Follow a strict render → review → critique → adjust loop.
- Do not stop after one iteration; continue until satisfied with the result.
- Once satisfied, ask the user whether to render a higher-quality version.

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
   - Make a low-res GIF for fast review:
     - `ffmpeg -i output/videos/480p15/<Scene>.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" -y agent_scratchpad/review.gif`
   - Extract key frames (e.g., 3s, 6s, 10s) when camera or motion changes:
     - `ffmpeg -y -ss 00:00:03 -i output/videos/480p15/<Scene>.mp4 -vframes 1 -update 1 agent_scratchpad/frame_3s.png`
     - `ffmpeg -y -ss 00:00:06 -i output/videos/480p15/<Scene>.mp4 -vframes 1 -update 1 agent_scratchpad/frame_6s.png`
     - `ffmpeg -y -ss 00:00:10 -i output/videos/480p15/<Scene>.mp4 -vframes 1 -update 1 agent_scratchpad/frame_10s.png`

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
   - Ask the user if they want a higher-quality render.

## Notes

- Store all review artifacts in `agent_scratchpad/` (never in source).
- Copy any artifacts intended for the samples library into `samples_artifacts/`.
- Use reference scenes as quality benchmarks; see `docs/scene_library.yaml`.
- For 3D scenes, verify multiple timestamps because camera motion can shift layout.
