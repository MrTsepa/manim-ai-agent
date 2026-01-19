#!/usr/bin/env python3
"""Helper script to critique a rendered video with GPT-5.2 (vision)."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _encode_image(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0]
    if not mime or not mime.startswith("image/"):
        raise ValueError(f"Unsupported image type for {path}")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_state(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _extract_score(text: str) -> float | None:
    text = text.strip()
    if text.startswith("{"):
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "score" in obj:
                return float(obj["score"])
        except json.JSONDecodeError:
            pass
    match = re.search(r"score\\s*[:=]\\s*([0-9]+(?:\\.[0-9]+)?)", text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def _build_prompt(min_score: float, notes: str | None) -> str:
    base = (
        "You are a strict Manim video reviewer. Critique the video and provide actionable fixes. "
        "Return JSON only with keys: score (0-10), strengths (list), issues (list), fixes (list). "
        f"Score must be a number from 0 to 10. If score is below {min_score}, "
        "list the top fixes required to reach at least that score."
    )
    if notes:
        return f"{base}\nAdditional context:\n{notes}"
    return base


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Critique video with GPT-5.2.")
    parser.add_argument("--gif", required=True, help="Path to review GIF.")
    parser.add_argument("--frames", nargs="*", default=[], help="Paths to frame PNG/JPGs.")
    parser.add_argument("--notes", default=None, help="Extra context for the reviewer.")
    parser.add_argument(
        "--state",
        default=None,
        help="Path to state file for conversation continuity.",
    )
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-5.2"))
    parser.add_argument("--min-score", type=float, default=9.0)
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a brief score/issues summary for quick monitoring.",
    )

    args = parser.parse_args()

    gif_path = Path(args.gif)
    if not gif_path.exists():
        print(f"GIF not found: {gif_path}", file=sys.stderr)
        return 2

    frame_paths = [Path(p) for p in args.frames]
    for path in frame_paths:
        if not path.exists():
            print(f"Frame not found: {path}", file=sys.stderr)
            return 2

    for path in [gif_path, *frame_paths]:
        if path.suffix.lower() not in SUPPORTED_IMAGE_EXTS:
            print(f"Unsupported image extension: {path}", file=sys.stderr)
            return 2

    agent_id = os.getenv("AGENT_ID", "default")
    default_state = Path("agent_scratchpad") / agent_id / "gpt52_critique_state.json"
    state_path = Path(args.state) if args.state else default_state

    state = _load_state(state_path)
    previous_response_id = state.get("last_response_id")

    content = [{"type": "input_text", "text": _build_prompt(args.min_score, args.notes)}]
    content.append(
        {"type": "input_image", "image_url": _encode_image(gif_path), "detail": "high"}
    )
    for frame_path in frame_paths:
        content.append(
            {
                "type": "input_image",
                "image_url": _encode_image(frame_path),
                "detail": "high",
            }
        )

    client = OpenAI()
    response = client.responses.create(
        model=args.model,
        reasoning={"effort": "high"},
        input=[{"role": "user", "content": content}],
        previous_response_id=previous_response_id,
    )

    output_text = response.output_text.strip()
    score = _extract_score(output_text)
    summary_text = None
    if args.summary and output_text.startswith("{"):
        try:
            payload = json.loads(output_text)
            issues = payload.get("issues") or []
            fixes = payload.get("fixes") or []
            top_issues = "; ".join(issues[:3]) if isinstance(issues, list) else ""
            top_fixes = "; ".join(fixes[:2]) if isinstance(fixes, list) else ""
            summary_text = f"score={payload.get('score')} issues={top_issues} fixes={top_fixes}"
        except json.JSONDecodeError:
            summary_text = None

    state_payload = {
        "last_response_id": response.id,
        "previous_response_id": previous_response_id,
        "last_score": score,
        "model": args.model,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_state(state_path, state_payload)

    if summary_text:
        print(summary_text, file=sys.stderr)
    print(output_text)
    if score is not None and score >= args.min_score:
        return 0
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
