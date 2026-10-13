"""Lesson folders for web-created lessons: ``lessons/<slug>/animation.py``.

A lesson generated from the browser lands in exactly the same place as a
hand-made one, so ``python generate.py lessons/<slug>/animation.py`` works
on it too, and both share the same caches.
"""

from __future__ import annotations

import ast
import json
import re
import shutil
from pathlib import Path

from src.animation.manim_engine import NARRATED_BASES
from src.config.video_config import PROJECT_ROOT

LESSONS_DIR = PROJECT_ROOT / "lessons"
MAX_SOURCE_BYTES = 1_000_000
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]{0,59}$")


class InputError(ValueError):
    """Bad input from the browser (reported as HTTP 400 with ``detail``)."""

    def __init__(self, message: str, detail: str | None = None, line: int | None = None):
        super().__init__(message)
        self.message, self.detail, self.line = message, detail, line


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")[:60].strip("_")
    if not slug or not SLUG_PATTERN.match(slug):
        raise InputError("Enter a lesson name (letters or digits).")
    return slug


def lesson_dir(slug: str) -> Path:
    if not SLUG_PATTERN.match(slug):
        raise InputError(f"Invalid lesson id '{slug}'.")
    return LESSONS_DIR / slug


def normalise_source(source: str) -> str:
    return source.lstrip("﻿").replace("\r\n", "\n")


def check_source(source: str) -> str:
    """Static checks before any code runs. Returns the narrated class name."""
    if not source or not source.strip():
        raise InputError("animation.py is empty.")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise InputError("animation.py is larger than 1 MB.")
    try:
        tree = ast.parse(source)
    except SyntaxError as err:
        raise InputError(f"Python syntax error on line {err.lineno}: {err.msg}",
                         (err.text or "").rstrip() or None, err.lineno) from err
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    narrated = [c.name for c in classes
                if {getattr(b, "id", getattr(b, "attr", "")) for b in c.bases} & NARRATED_BASES]
    if not narrated:
        raise InputError(
            "No narrated scene found.",
            "animation.py needs a class that extends LMSScene, LMS3DScene or LMSMovingCameraScene:\n\n"
            "    from src.animation import LMSScene\n\n    class MyLessonVideo(LMSScene):\n        ...")
    if len(narrated) > 1:
        raise InputError(f"Several narrated scenes found: {', '.join(narrated)}.", "Keep one narrated scene per lesson.")
    return narrated[0]


def write_animation(slug: str, source: str) -> Path:
    """Save animation.py for a lesson. Unchanged content is not rewritten
    (so every cache stays valid); a changed file's previous version is kept
    in generated/animation.previous.py."""
    folder = lesson_dir(slug)
    target = folder / "animation.py"
    source = normalise_source(source)
    if target.exists():
        current = normalise_source(target.read_text(encoding="utf-8-sig"))
        if current == source:
            return target
        backup = folder / "generated" / "animation.previous.py"
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)
    folder.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.encode("utf-8"))
    return target


def read_animation(slug: str) -> str:
    path = lesson_dir(slug) / "animation.py"
    if not path.exists():
        raise FileNotFoundError(slug)
    return normalise_source(path.read_text(encoding="utf-8-sig"))


def list_lessons() -> list[dict]:
    lessons = []
    for path in sorted(LESSONS_DIR.glob("*/animation.py")):
        folder = path.parent
        if not SLUG_PATTERN.match(folder.name):
            continue
        title = folder.name.replace("_", " ").title()
        try:
            title = json.loads((folder / "generated" / "script.json").read_text(encoding="utf-8"))["lesson"]["title"] or title
        except (OSError, ValueError, KeyError, TypeError):
            pass
        videos = sorted((folder / "output").glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        lessons.append({
            "id": folder.name,
            "title": title,
            "hasVideo": bool(videos),
            "updated": max([path.stat().st_mtime] + [v.stat().st_mtime for v in videos]),
        })
    return sorted(lessons, key=lambda l: l["updated"], reverse=True)


def last_clip_info(slug: str, narration_id: str) -> dict:
    """Duration/voice/text of the lesson's last generated clip for a block (or {})."""
    try:
        meta = json.loads((lesson_dir(slug) / "audio" / f"{narration_id}.meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, InputError):
        return {}
    return {k: meta.get(k) for k in ("duration", "voice", "text")}
