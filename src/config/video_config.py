"""Render quality presets and output locations used by scripts/render*.py.

Each preset maps to one of Manim's built-in quality flags, so the scripts
stay a thin wrapper around the normal ``manim`` command line.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "output"
MEDIA_DIR = OUTPUT_DIR / "media"            # Manim's working files (per lesson)
PREVIEW_DIR = OUTPUT_DIR / "preview"        # finished preview MP4s
FINAL_DIR = OUTPUT_DIR / "final"            # finished final MP4s
THUMBNAILS_DIR = OUTPUT_DIR / "thumbnails"  # still images (PNG)

# name -> (manim flag, human description). All presets are 16:9.
QUALITY_PRESETS = {
    "low": ("-ql", "854x480 @ 15 fps (fast preview)"),
    "medium": ("-qm", "1280x720 @ 30 fps (detailed preview)"),
    "high": ("-qh", "1920x1080 @ 60 fps (Full HD final)"),
    "4k": ("-qk", "3840x2160 @ 60 fps (only if you really need it)"),
}

PREVIEW_QUALITIES = ("low", "medium")
FINAL_QUALITIES = ("high", "4k")
