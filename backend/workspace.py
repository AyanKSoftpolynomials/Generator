"""Isolated job workspaces, so several generations can run at once.

Every web generation builds in its own folder, never in ``lessons/<name>/``:

    cache/jobs/<jobId>/
        animation.py                 this job's code (as submitted)
        generated/ audio/ alignment/ subtitles/ output/
        scenes/                      this job's Manim media folder
        job.json  output.log  state.json

``seed()`` copies the lesson's last successful build in (small files are
copied; Manim's write-once, content-hashed files — partial movies, compiled
LaTeX — are hard-linked, so nothing large is duplicated and every cache still
hits). ``publish()`` copies the finished result back to ``lessons/<name>/``
and the lesson's Manim folder, so the next job (or ``python generate.py``)
starts from it. Both hold a per-lesson lock, briefly; the generation itself
runs without any lock, so jobs never block each other.

Files a job may rewrite in place are always real copies, never links, so one
job can never modify another job's (or the lesson's) files.
"""

from __future__ import annotations

import json
import os
import shutil
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path

from src.config.video_config import MEDIA_DIR

from backend.lessons import lesson_dir, write_animation

LESSON_FOLDERS = ("generated", "audio", "alignment", "subtitles", "output", "assets")
SKIP = {"logs", "animation.previous.py"}

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


@contextmanager
def lesson_lock(lesson_id: str):
    with _locks_guard:
        lock = _locks.setdefault(lesson_id, threading.Lock())
    with lock:
        yield


def lesson_media_dir(lesson_id: str) -> Path:
    return MEDIA_DIR / f"{lesson_id}_narrated"


def _write_once(relative: Path) -> bool:
    """Manim files named by content hash and never rewritten: safe to hard-link."""
    parts = relative.parts
    if "partial_movie_files" in parts:
        return relative.suffix != ".txt"          # the file list is rewritten every render
    return bool(parts) and parts[0] in ("Tex", "texts", "images")


def _link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def _atomic_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    staged = dst.with_name(f".{dst.name}.{uuid.uuid4().hex[:8]}.tmp")
    shutil.copy2(src, staged)
    os.replace(staged, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        if path.is_file() and not (set(rel.parts) & SKIP):
            _atomic_copy(path, dst / rel)


def _rewrite_render_meta(generated: Path, old_media: Path, new_media: Path, copy_video: bool,
                         preset: str | None = None) -> None:
    """render.meta.json stores the rendered scene video's absolute path; point it at ``new_media``.
    With ``preset``, other quality presets' records are dropped (this job does not render them)."""
    for meta_path in generated.glob("manim/*/render.meta.json"):
        if preset and meta_path.parent.name != preset:
            meta_path.unlink(missing_ok=True)
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            video = Path(meta.get("video") or "")
            rel = video.resolve().relative_to(old_media.resolve())
        except (OSError, ValueError):
            meta_path.unlink(missing_ok=True)       # unknown origin: the job re-checks the render (cache hits)
            continue
        target = new_media / rel
        if copy_video:
            if not video.exists():
                meta_path.unlink(missing_ok=True)
                continue
            _atomic_copy(video, target)             # a real copy: Manim may rewrite this file
        meta["video"] = str(target)
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def seed(workspace: Path, lesson_id: str, source: str, preset: str) -> Path:
    """Create the job's workspace from the lesson's last build. Returns its Manim media folder."""
    scenes = workspace / "scenes"
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "animation.py").write_bytes(source.encode("utf-8"))
    lesson = lesson_dir(lesson_id)
    media = lesson_media_dir(lesson_id)
    with lesson_lock(lesson_id):
        for name in LESSON_FOLDERS:
            if (lesson / name).is_dir():
                _copy_tree(lesson / name, workspace / name)
        if media.is_dir():
            for path in media.rglob("*"):
                rel = path.relative_to(media)
                if path.is_file() and _write_once(rel):
                    _link_or_copy(path, scenes / rel)
        _rewrite_render_meta(workspace / "generated", media, scenes, copy_video=True, preset=preset)
    scenes.mkdir(parents=True, exist_ok=True)
    return scenes


def publish(workspace: Path, lesson_id: str, source: str) -> None:
    """Make a finished job the lesson's current build (lessons/<id>/ + its Manim cache)."""
    lesson = lesson_dir(lesson_id)
    media = lesson_media_dir(lesson_id)
    scenes = workspace / "scenes"
    with lesson_lock(lesson_id):
        write_animation(lesson_id, source)
        for name in LESSON_FOLDERS:
            if (workspace / name).is_dir():
                _copy_tree(workspace / name, lesson / name)
        if scenes.is_dir():
            for path in scenes.rglob("*"):
                rel = path.relative_to(scenes)
                if not path.is_file():
                    continue
                if _write_once(rel):
                    if not (media / rel).exists():
                        _link_or_copy(path, media / rel)
                elif rel.parts and rel.parts[0] == "videos":
                    _atomic_copy(path, media / rel)
        _rewrite_render_meta(lesson / "generated", scenes, media, copy_video=False)
