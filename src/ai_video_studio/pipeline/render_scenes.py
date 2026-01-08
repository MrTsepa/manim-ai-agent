"""Rendering utilities for Manim scenes."""

import contextlib
import io
import logging
import subprocess
import sys
from pathlib import Path
from typing import Type

from manim import Scene, config

from ai_video_studio.config import get_settings


def render_scene(
    scene_class: Type[Scene],
    output_dir: Path | None = None,
    quality: str | None = None,
    preview: bool = False,
) -> Path:
    """
    Render a Manim scene to a video file.

    Args:
        scene_class: The Scene class to render
        output_dir: Directory to save the output (defaults to settings.output_dir)
        quality: Manim quality preset (low_quality, medium_quality, high_quality, production_quality)
        preview: If True, open the video after rendering

    Returns:
        Path to the rendered video file
    """
    settings = get_settings()

    if output_dir is None:
        output_dir = settings.output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if quality is None:
        quality = settings.manim_quality

    # Configure Manim
    config.output_file = scene_class.__name__
    config.quality = quality
    config.preview = preview

    # Set media directory
    config.media_dir = str(output_dir)

    # Suppress Manim's verbose output
    # Configure logging to suppress INFO/DEBUG messages from Manim
    manim_logger = logging.getLogger("manim")
    original_level = manim_logger.level
    manim_logger.setLevel(logging.ERROR)
    
    # Also try to set config verbosity if available
    original_verbosity = getattr(config, "verbosity", None)
    try:
        config.verbosity = "ERROR"
    except (AttributeError, ValueError):
        pass

    # Render the scene with suppressed output
    # Redirect stdout to suppress print statements, but keep stderr for critical errors
    scene = scene_class()
    stdout_capture = io.StringIO()
    with contextlib.redirect_stdout(stdout_capture):
        scene.render()
    
    # Restore original logging level
    manim_logger.setLevel(original_level)
    
    # Restore original verbosity if it was set
    if original_verbosity is not None:
        try:
            config.verbosity = original_verbosity
        except (AttributeError, ValueError):
            pass

    # Find the output file
    # Manim creates files in output_dir/videos/<resolution>/<scene_name>.mp4
    # Quality strings map to resolutions like: low_quality -> 480p15, medium_quality -> 720p30, etc.
    videos_dir = output_dir / "videos"
    
    # Search for the video file in the videos directory
    # Manim creates subdirectories with resolution names (e.g., 480p15, 720p30)
    video_path = None
    if videos_dir.exists():
        for resolution_dir in videos_dir.iterdir():
            if resolution_dir.is_dir():
                potential_path = resolution_dir / f"{scene_class.__name__}.mp4"
                if potential_path.exists():
                    video_path = potential_path
                    break
    
    if video_path is None or not video_path.exists():
        # Try the direct path as fallback
        video_path = output_dir / "videos" / quality / f"{scene_class.__name__}.mp4"
        if not video_path.exists():
            raise RuntimeError(
                f"Expected video file not found. Searched in {videos_dir}. "
                f"Manim may have saved it to a different location."
            )

    return video_path


def render_scene_via_cli(
    scene_class: Type[Scene],
    output_dir: Path | None = None,
    quality: str | None = None,
) -> Path:
    """
    Render a Manim scene using the CLI (alternative method).

    This method uses subprocess to call manim CLI, which can be more reliable
    in some environments.

    Args:
        scene_class: The Scene class to render
        output_dir: Directory to save the output (defaults to settings.output_dir)
        quality: Manim quality preset

    Returns:
        Path to the rendered video file
    """
    settings = get_settings()

    if output_dir is None:
        output_dir = settings.output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if quality is None:
        quality = settings.manim_quality

    # Get the module path for the scene class
    module = scene_class.__module__
    scene_name = scene_class.__name__

    # Build manim command
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "-ql" if quality == "low_quality" else f"-q{quality[0]}",
        "-o",
        scene_name,
        module,
        scene_name,
    ]

    # Run manim
    result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"Manim CLI failed with return code {result.returncode}:\n{result.stderr}"
        )

    # Find the output file
    video_path = output_dir / "media" / "videos" / module / quality / f"{scene_name}.mp4"

    if not video_path.exists():
        # Try alternative path structure
        video_path = output_dir / "media" / "videos" / quality / f"{scene_name}.mp4"

    if not video_path.exists():
        raise RuntimeError(f"Expected video file not found. Searched: {video_path}")

    return video_path

