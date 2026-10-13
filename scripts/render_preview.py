"""Render a quick preview of a lesson (480p by default).

Usage (from the project root, with .venv active):

    python scripts/render_preview.py lessons/whole_numbers/animation.py
    python scripts/render_preview.py lessons/whole_numbers/animation.py --quality medium
    python scripts/render_preview.py lessons/whole_numbers/animation.py WholeNumbersVideo -p

Videos are copied to output/preview/<lesson_name>/. See scripts/render.py for
how the wrapper works; extra arguments after ``--`` go straight to manim.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.render import build_parser, run_render, split_extra  # noqa: E402
from src.config.video_config import PREVIEW_DIR, PREVIEW_QUALITIES  # noqa: E402


def main() -> None:
    ours, extra = split_extra(sys.argv[1:])
    args = build_parser("Render a quick preview of a lesson.", PREVIEW_QUALITIES, "low").parse_args(ours)
    run_render(args.file, args.scenes, args.quality, PREVIEW_DIR, args.open, extra)


if __name__ == "__main__":
    main()
