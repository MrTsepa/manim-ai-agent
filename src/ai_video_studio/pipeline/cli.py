"""CLI entrypoints for the AI Video Studio pipeline."""

import argparse
import sys
from pathlib import Path
from typing import Type

from manim import Scene

from ai_video_studio.config import get_settings
from ai_video_studio.core.agent_utils import get_agent_id, print_agent_info
from ai_video_studio.manim_scenes.demo_scenes import (
    FunctionDemoScene,
    LossDescentDemoScene,
    ParabolicMotionScene,
    PythagoreanTheoremScene,
)
from ai_video_studio.manim_scenes.registry import (
    discover_scenes,
    get_registered_scenes,
    get_scene_by_class_name,
    get_scene_by_command,
    load_metadata_files,
)
from ai_video_studio.pipeline.render_scenes import render_scene
from ai_video_studio.core.scene_library import (
    filter_reference_scenes,
    load_scene_library,
)


def _render_scene_command(
    scene_class: Type[Scene],
    scene_name: str,
    args: argparse.Namespace,
) -> int:
    """
    Generic render command handler.

    Args:
        scene_class: The Manim Scene class to render
        scene_name: Human-readable name for logging
        args: Parsed CLI arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        output_dir = Path(args.output_dir) if args.output_dir else None
        quality = args.quality if args.quality else None
        settings = get_settings()

        print(f"Rendering {scene_name}...")
        print(f"Output directory: {output_dir or settings.output_dir}")
        print(f"Quality: {quality or settings.manim_quality}")

        video_path = render_scene(
            scene_class,
            output_dir=output_dir,
            quality=quality,
            preview=args.preview,
        )

        print(f"✓ Successfully rendered to: {video_path}")
        return 0

    except Exception as e:
        print(f"✗ Error rendering scene: {e}", file=sys.stderr)
        return 1


def render_demo(args: argparse.Namespace) -> int:
    """Render the demo scene."""
    return _render_scene_command(FunctionDemoScene, "demo scene", args)


def render_loss_descent(args: argparse.Namespace) -> int:
    """Render the loss descent demo scene."""
    return _render_scene_command(LossDescentDemoScene, "loss descent demo scene", args)


def render_parabolic_motion(args: argparse.Namespace) -> int:
    """Render the parabolic motion scene with kinematics plots."""
    return _render_scene_command(ParabolicMotionScene, "parabolic motion scene", args)


def render_pythagorean_theorem(args: argparse.Namespace) -> int:
    """Render the Pythagorean theorem scene."""
    return _render_scene_command(PythagoreanTheoremScene, "Pythagorean theorem scene", args)


def list_reference_scenes(args: argparse.Namespace) -> int:
    """List reference scenes from the scene library."""
    try:
        scenes = load_scene_library(args.library)
        if args.tag:
            scenes = filter_reference_scenes(scenes, tags=args.tag)

        if not scenes:
            print("No reference scenes found.")
            return 0

        for scene in scenes:
            print(f"- {scene.id}: {scene.title}")
            print(f"  class: {scene.scene_class}")
            print(f"  module: {scene.module}")
            if scene.tags:
                print(f"  tags: {', '.join(scene.tags)}")
            if args.verbose:
                if scene.quality_notes:
                    print("  notes:")
                    for note in scene.quality_notes:
                        print(f"    - {note}")
                if scene.artifacts:
                    print("  artifacts:")
                    for key, value in scene.artifacts.items():
                        print(f"    - {key}: {value}")
        return 0

    except Exception as e:
        print(f"✗ Error loading scene library: {e}", file=sys.stderr)
        return 1


def render_dynamic_scene(args: argparse.Namespace) -> int:
    """Render a scene using dynamic discovery (no central registration needed).

    This command finds scenes by class name or CLI command without requiring
    them to be imported in cli.py. Perfect for multiagent workflows.
    """
    try:
        # Discover all registered scenes
        discover_scenes()
        load_metadata_files()

        scene_name = args.scene

        # Try to find by class name first
        metadata = get_scene_by_class_name(scene_name)

        # Then try by CLI command
        if metadata is None:
            metadata = get_scene_by_command(scene_name)

        if metadata is None:
            # List available scenes to help the user
            all_scenes = get_registered_scenes()
            print(f"✗ Scene '{scene_name}' not found.", file=sys.stderr)
            if all_scenes:
                print("\nAvailable scenes:", file=sys.stderr)
                for meta in all_scenes.values():
                    print(
                        f"  - {meta.scene_class.__name__} (command: {meta.cli_command})",
                        file=sys.stderr,
                    )
            else:
                print(
                    "\nNo scenes registered. Use @register_scene decorator or .meta.yaml files.",
                    file=sys.stderr,
                )
            return 1

        output_dir = Path(args.output_dir) if args.output_dir else None
        quality = args.quality if args.quality else None
        settings = get_settings()

        print(f"Rendering {metadata.title} ({metadata.scene_class.__name__})...")
        print(f"Output directory: {output_dir or settings.output_dir}")
        print(f"Quality: {quality or settings.manim_quality}")

        video_path = render_scene(
            metadata.scene_class,
            output_dir=output_dir,
            quality=quality,
            preview=args.preview,
        )

        print(f"✓ Successfully rendered to: {video_path}")
        return 0

    except Exception as e:
        print(f"✗ Error rendering scene: {e}", file=sys.stderr)
        return 1


def list_available_scenes(args: argparse.Namespace) -> int:
    """List all available scenes from dynamic discovery."""
    try:
        # Discover all registered scenes
        discover_scenes()
        load_metadata_files()

        all_scenes = get_registered_scenes()

        if not all_scenes:
            print("No scenes registered.")
            print("\nTo register scenes, use the @register_scene decorator:")
            print("  from ai_video_studio.manim_scenes.registry import register_scene")
            print()
            print('  @register_scene(id="my_scene", title="My Scene")')
            print("  class MyScene(Scene):")
            print("      ...")
            return 0

        print(f"Found {len(all_scenes)} registered scene(s):\n")
        for metadata in all_scenes.values():
            print(f"  {metadata.scene_class.__name__}")
            print(f"    ID: {metadata.id}")
            print(f"    Title: {metadata.title}")
            print(f"    Command: render-scene {metadata.cli_command}")
            if metadata.tags:
                print(f"    Tags: {', '.join(metadata.tags)}")
            print()

        return 0

    except Exception as e:
        print(f"✗ Error discovering scenes: {e}", file=sys.stderr)
        return 1


def agent_info_command(args: argparse.Namespace) -> int:
    """Print agent context information for debugging."""
    print_agent_info()
    return 0


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="AI Video Studio - Render educational videos with Manim"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # render-demo command
    render_demo_parser = subparsers.add_parser(
        "render-demo", help="Render a simple demo scene"
    )
    render_demo_parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for rendered videos (default: from settings)",
    )
    render_demo_parser.add_argument(
        "--quality",
        type=str,
        choices=["low_quality", "medium_quality", "high_quality", "production_quality"],
        help="Manim quality preset (default: from settings)",
    )
    render_demo_parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the video after rendering",
    )

    # render-loss-descent command
    render_loss_descent_parser = subparsers.add_parser(
        "render-loss-descent", help="Render the loss descent demo scene (ball rolling downhill)"
    )
    render_loss_descent_parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for rendered videos (default: from settings)",
    )
    render_loss_descent_parser.add_argument(
        "--quality",
        type=str,
        choices=["low_quality", "medium_quality", "high_quality", "production_quality"],
        help="Manim quality preset (default: from settings)",
    )
    render_loss_descent_parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the video after rendering",
    )

    # render-parabolic-motion command
    render_parabolic_motion_parser = subparsers.add_parser(
        "render-parabolic-motion",
        help="Render the parabolic motion scene with position, velocity, and acceleration plots",
    )
    render_parabolic_motion_parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for rendered videos (default: from settings)",
    )
    render_parabolic_motion_parser.add_argument(
        "--quality",
        type=str,
        choices=["low_quality", "medium_quality", "high_quality", "production_quality"],
        help="Manim quality preset (default: from settings)",
    )
    render_parabolic_motion_parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the video after rendering",
    )

    # render-pythagorean-theorem command
    render_pythagorean_parser = subparsers.add_parser(
        "render-pythagorean-theorem",
        help="Render the Pythagorean theorem scene with squares on a right triangle",
    )
    render_pythagorean_parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for rendered videos (default: from settings)",
    )
    render_pythagorean_parser.add_argument(
        "--quality",
        type=str,
        choices=["low_quality", "medium_quality", "high_quality", "production_quality"],
        help="Manim quality preset (default: from settings)",
    )
    render_pythagorean_parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the video after rendering",
    )

    # list-reference-scenes command
    list_reference_scenes_parser = subparsers.add_parser(
        "list-reference-scenes",
        help="List reference scenes from the scene library",
    )
    list_reference_scenes_parser.add_argument(
        "--library",
        type=str,
        default="docs/scene_library.yaml",
        help="Path to scene_library.yaml (default: docs/scene_library.yaml)",
    )
    list_reference_scenes_parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Filter by tag (can be repeated)",
    )
    list_reference_scenes_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show notes and artifacts",
    )

    # render-scene command (dynamic discovery - multiagent friendly)
    render_scene_parser = subparsers.add_parser(
        "render-scene",
        help="Render a scene by name using dynamic discovery (multiagent-friendly)",
    )
    render_scene_parser.add_argument(
        "scene",
        type=str,
        help="Scene class name or CLI command (e.g., ParabolicMotionScene or parabolic-motion)",
    )
    render_scene_parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for rendered videos (default: from settings)",
    )
    render_scene_parser.add_argument(
        "--quality",
        type=str,
        choices=["low_quality", "medium_quality", "high_quality", "production_quality"],
        help="Manim quality preset (default: from settings)",
    )
    render_scene_parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the video after rendering",
    )

    # list-scenes command (dynamic discovery)
    list_scenes_parser = subparsers.add_parser(
        "list-scenes",
        help="List all available scenes from dynamic discovery",
    )

    # agent-info command
    agent_info_parser = subparsers.add_parser(
        "agent-info",
        help="Print agent context information (ID, scratchpad path, etc.)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "render-demo":
        return render_demo(args)
    elif args.command == "render-loss-descent":
        return render_loss_descent(args)
    elif args.command == "render-parabolic-motion":
        return render_parabolic_motion(args)
    elif args.command == "render-pythagorean-theorem":
        return render_pythagorean_theorem(args)
    elif args.command == "list-reference-scenes":
        return list_reference_scenes(args)
    elif args.command == "render-scene":
        return render_dynamic_scene(args)
    elif args.command == "list-scenes":
        return list_available_scenes(args)
    elif args.command == "agent-info":
        return agent_info_command(args)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
