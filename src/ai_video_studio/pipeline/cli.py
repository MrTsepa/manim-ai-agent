"""CLI entrypoints for the AI Video Studio pipeline."""

import argparse
import sys
from pathlib import Path

from ai_video_studio.config import get_settings
from ai_video_studio.manim_scenes.demo_scenes import FunctionDemoScene, LossDescentDemoScene
from ai_video_studio.pipeline.render_scenes import render_scene


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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "render-demo":
        return render_demo(args)
    elif args.command == "render-loss-descent":
        return render_loss_descent(args)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

