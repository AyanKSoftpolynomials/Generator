"""Path helpers so lessons can find shared and lesson-specific assets."""

from pathlib import Path

from src.config.video_config import PROJECT_ROOT


def asset_path(*parts: str) -> str:
    """Path to a shared asset, e.g. ``asset_path("images", "logo.png")``.

    Returns a string because Manim classes (``ImageMobject``, ``SVGMobject``)
    accept strings everywhere.
    """
    path = PROJECT_ROOT / "assets" / Path(*parts)
    if not path.exists():
        raise FileNotFoundError(f"Asset not found: {path}")
    return str(path)


def lesson_asset(lesson_file: str, *parts: str) -> str:
    """Path to a file in a lesson's own assets/ folder.

    Call it from a lesson's animation.py with ``__file__``:
    ``lesson_asset(__file__, "apples.png")``.
    """
    path = Path(lesson_file).resolve().parent / "assets" / Path(*parts)
    if not path.exists():
        raise FileNotFoundError(f"Lesson asset not found: {path}")
    return str(path)
