# AI Video Studio

An AI-first video studio for creating 3blue1brown-style educational videos focused on AI topics.

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd ai-video-studio
   ```

2. Sync the environment with uv:
   ```bash
   uv sync
   ```

3. (Optional) Install dev dependencies:
   ```bash
   uv sync --extra dev
   ```

4. (Optional) Copy `.env.example` to `.env` and configure any needed environment variables:
   ```bash
   cp .env.example .env
   ```

## Quick Start

**Make sure the uv environment is synced** (see Installation step 2).

Render a demo scene:
```bash
uv run python -m ai_video_studio.pipeline.cli render-demo
```

Or with low quality for faster rendering:
```bash
uv run python -m ai_video_studio.pipeline.cli render-demo --quality low_quality
```

This will create a simple Manim animation showing a function on axes with a point moving along the curve. The output will be saved to `output/videos/` directory.

## Project Structure

```
ai_video_studio/
  src/
    ai_video_studio/
      config/          # Configuration and settings
      core/            # Core data models and utilities
      manim_scenes/    # Manim scene implementations
      pipeline/        # Pipeline orchestration and CLI
```

## Development

- **Always use the uv-managed environment** when working on this project. See `docs/AGENTS.md` for detailed instructions.
- See `docs/AGENT_BACKBONE.md` for the full project specification and roadmap.
