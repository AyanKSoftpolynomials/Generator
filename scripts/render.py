"""Render a lesson at final quality (Full HD by default).

Usage (from the project root, with .venv active):

    python scripts/render.py lessons/whole_numbers/animation.py
    python scripts/render.py lessons/whole_numbers/animation.py WholeNumbersVideo
    python scripts/render.py lessons/whole_numbers/animation.py --quality 4k

Any extra arguments after ``--`` go straight to the ``manim`` CLI, e.g.
``-- --fps 30``.

This is a thin wrapper around ``manim render``. It:
  1. runs Manim from the project root (so manim.cfg is used) with the
     project root on PYTHONPATH (so ``from src.components import ...`` works),
  2. keeps Manim's working files in output/media/<lesson_name>/,
  3. copies the finished MP4s to output/final/<lesson_name>/.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config.video_config import (  # noqa: E402
    FINAL_DIR,
    FINAL_QUALITIES,
    MEDIA_DIR,
    PROJECT_ROOT,
    QUALITY_PRESETS,
)


def run_render(scene_file: str, scenes: list[str], quality: str, dest_root: Path, open_after: bool, extra: list[str]) -> list[Path]:
    """Render ``scene_file`` with Manim and copy the resulting MP4s to ``dest_root/<lesson>/``.

    Returns the copied video paths. Exits the process if Manim fails.
    """
    source = Path(scene_file).resolve()
    if not source.is_file():
        sys.exit(f"Scene file not found: {scene_file}")

    lesson = source.parent.name  # e.g. "whole_numbers"
    media_dir = MEDIA_DIR / lesson
    flag, description = QUALITY_PRESETS[quality]

    cmd = [sys.executable, "-m", "manim", "render", str(source), *scenes, flag, "--media_dir", str(media_dir)]
    if not scenes:
        cmd.append("-a")  # render every scene in the file instead of prompting
    if open_after:
        cmd.append("-p")
    cmd.extend(extra)

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(PROJECT_ROOT), env.get("PYTHONPATH")]))

    print(f"Rendering {source.relative_to(PROJECT_ROOT) if source.is_relative_to(PROJECT_ROOT) else source}")
    print(f"Quality:  {quality} - {description}")
    print("Command: ", " ".join(cmd), flush=True)

    started = time.time()
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
    if result.returncode != 0:
        sys.exit(f"\nManim failed (exit code {result.returncode}). See the error above.")

    # Pick up the videos written by this run (ignore Manim's partial clips).
    videos = [
        p for p in (media_dir / "videos").rglob("*.mp4")
        if "partial_movie_files" not in p.parts and p.stat().st_mtime >= started - 1
    ]
    if not videos:
        print("\nManim finished but produced no MP4 (does the file contain a Scene with animations?).")
        return []

    dest = dest_root / lesson
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    for video in videos:
        target = dest / video.name
        shutil.copy2(video, target)
        copied.append(target)

    print("\nDone. Videos:")
    for path in copied:
        print(f"  {path}")
    return copied


def build_parser(description: str, qualities: tuple[str, ...], default: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("file", help="path to the lesson's animation.py")
    parser.add_argument("scenes", nargs="*", help="scene class names to render (default: all scenes in the file)")
    parser.add_argument("-q", "--quality", choices=qualities, default=default, help=f"default: {default}")
    parser.add_argument("-p", "--open", action="store_true", help="open the video when rendering finishes")
    return parser


def split_extra(argv: list[str]) -> tuple[list[str], list[str]]:
    """Split ``argv`` at ``--``: (our arguments, arguments passed through to manim)."""
    if "--" in argv:
        i = argv.index("--")
        return argv[:i], argv[i + 1:]
    return argv, []


def main() -> None:
    ours, extra = split_extra(sys.argv[1:])
    args = build_parser("Render a lesson at final quality.", FINAL_QUALITIES, "high").parse_args(ours)
    run_render(args.file, args.scenes, args.quality, FINAL_DIR, args.open, extra)


if __name__ == "__main__":
    main()
