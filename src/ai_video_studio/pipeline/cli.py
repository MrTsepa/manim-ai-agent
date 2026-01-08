"""CLI entrypoints for the AI Video Studio pipeline."""

import argparse
import sys
from pathlib import Path

from ai_video_studio.config import get_settings
from ai_video_studio.manim_scenes.demo_scenes import (
    FunctionDemoScene,
    LossDescentDemoScene,
    ParabolicMotionScene,
    PythagoreanTheoremScene,
)
from ai_video_studio.pipeline.render_scenes import render_scene
from ai_video_studio.core.scene_library import (
    filter_reference_scenes,
    load_scene_library,
)


def render_demo(args: argparse.Namespace) -> int:
    """Render the demo scene."""
    try:
        output_dir = Path(args.output_dir) if args.output_dir else None
        quality = args.quality if args.quality else None

        print(f"Rendering demo scene...")
        print(f"Output directory: {output_dir or get_settings().output_dir}")
        print(f"Quality: {quality or get_settings().manim_quality}")

        video_path = render_scene(
            FunctionDemoScene,
            output_dir=output_dir,
            quality=quality,
            preview=args.preview,
        )

        print(f"✓ Successfully rendered to: {video_path}")
        return 0

    except Exception as e:
        print(f"✗ Error rendering scene: {e}", file=sys.stderr)
        return 1


def render_loss_descent(args: argparse.Namespace) -> int:
    """Render the loss descent demo scene."""
    try:
        output_dir = Path(args.output_dir) if args.output_dir else None
        quality = args.quality if args.quality else None

        print(f"Rendering loss descent demo scene...")
        print(f"Output directory: {output_dir or get_settings().output_dir}")
        print(f"Quality: {quality or get_settings().manim_quality}")

        video_path = render_scene(
            LossDescentDemoScene,
            output_dir=output_dir,
            quality=quality,
            preview=args.preview,
        )

        print(f"✓ Successfully rendered to: {video_path}")
        return 0

    except Exception as e:
        print(f"✗ Error rendering scene: {e}", file=sys.stderr)
        return 1


def render_parabolic_motion(args: argparse.Namespace) -> int:
    """Render the parabolic motion scene with kinematics plots."""
    try:
        output_dir = Path(args.output_dir) if args.output_dir else None
        quality = args.quality if args.quality else None

        print("Rendering parabolic motion scene...")
        print(f"Output directory: {output_dir or get_settings().output_dir}")
        print(f"Quality: {quality or get_settings().manim_quality}")

        video_path = render_scene(
            ParabolicMotionScene,
            output_dir=output_dir,
            quality=quality,
            preview=args.preview,
        )

        print(f"✓ Successfully rendered to: {video_path}")
        return 0

    except Exception as e:
        print(f"✗ Error rendering scene: {e}", file=sys.stderr)
        return 1


def render_pythagorean_theorem(args: argparse.Namespace) -> int:
    """Render the Pythagorean theorem scene."""
    try:
        output_dir = Path(args.output_dir) if args.output_dir else None
        quality = args.quality if args.quality else None

        print("Rendering Pythagorean theorem scene...")
        print(f"Output directory: {output_dir or get_settings().output_dir}")
        print(f"Quality: {quality or get_settings().manim_quality}")

        video_path = render_scene(
            PythagoreanTheoremScene,
            output_dir=output_dir,
            quality=quality,
            preview=args.preview,
        )

        print(f"✓ Successfully rendered to: {video_path}")
        return 0

    except Exception as e:
        print(f"✗ Error rendering scene: {e}", file=sys.stderr)
        return 1


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

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
