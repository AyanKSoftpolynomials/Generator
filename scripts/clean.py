"""Delete generated files to free disk space.

Usage (from the project root):

    python scripts/clean.py          # Manim working files + Python caches
    python scripts/clean.py --all    # ...and ALSO preview/final videos and thumbnails
    python scripts/clean.py --cache  # ...and cached narration audio (regenerated on next run)

By default your finished videos in output/preview and output/final are kept.
"""

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config.video_config import (  # noqa: E402
    FINAL_DIR,
    MEDIA_DIR,
    PREVIEW_DIR,
    PROJECT_ROOT,
    THUMBNAILS_DIR,
)


def remove(path: Path) -> None:
    """Delete a folder if it exists and say so."""
    if path.exists():
        shutil.rmtree(path)
        print(f"removed {path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete generated files.")
    parser.add_argument("--all", action="store_true", help="also delete rendered preview/final videos and thumbnails")
    parser.add_argument("--cache", action="store_true", help="also delete cached narration audio and alignments (forces regeneration)")
    args = parser.parse_args()

    if args.cache:
        remove(PROJECT_ROOT / "cache")

    remove(MEDIA_DIR)
    remove(PROJECT_ROOT / "media")  # created if manim was run with a different config
    for cache in PROJECT_ROOT.rglob("__pycache__"):
        if ".venv" not in cache.parts:
            remove(cache)
    remove(PROJECT_ROOT / ".pytest_cache")

    if args.all:
        for folder in (PREVIEW_DIR, FINAL_DIR, THUMBNAILS_DIR):
            remove(folder)
            folder.mkdir(parents=True, exist_ok=True)

    print("Clean complete.")


if __name__ == "__main__":
    main()
