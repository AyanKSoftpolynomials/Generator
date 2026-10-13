"""Delete the generated files of ONE finished job, only after a successful download or upload.

Scope (strictly the job's own workspace, cache/jobs/<job id>/):
    deleted: the final MP4, its audio, alignment, subtitles, generated/ files, the
             Manim scenes and every other file the job produced, plus the lesson's
             published copy of the MP4 (lessons/<lesson>/output/) ONLY if it is
             byte-identical to this job's video (i.e. no later job replaced it)
    kept:    state.json / job.json / youtube.json (the small record of what happened),
             lessons/<lesson>/animation.py and the lesson's reusable build, voices,
             templates, caches, settings, preferences and credentials, other jobs

Nothing is ever deleted without a recorded successful download/upload for this job
(see backend/app.py), and a failed cleanup never turns that success into a failure.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import time
from pathlib import Path

from src.config.video_config import PROJECT_ROOT

JOB_ID = re.compile(r"^[0-9a-f]{12}$")
KEEP = {"state.json", "job.json", "youtube.json"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.is_dir() else path.stat().st_size


def job_workspace(jobs_dir: Path, job_id: str) -> Path:
    """The job's folder, refusing anything that is not exactly cache/jobs/<12 hex chars>."""
    if not JOB_ID.match(job_id or ""):
        raise ValueError(f"Refusing to clean up: invalid job id {job_id!r}.")
    root = Path(jobs_dir).resolve()
    folder = (root / job_id).resolve()
    if folder.parent != root:
        raise ValueError("Refusing to clean up outside the jobs folder.")
    return folder


def cleanup_job(jobs_dir: Path, job_id: str, video_relative: str | None, lessons_dir: Path) -> dict:
    """Delete one job's generated files. Returns what was deleted and kept (paths relative to the project)."""
    folder = job_workspace(jobs_dir, job_id)
    if not folder.is_dir():
        raise FileNotFoundError("The job's workspace no longer exists.")
    deleted, freed = [], 0

    video = (PROJECT_ROOT / video_relative).resolve() if video_relative else None
    published = None
    if video and video.is_file() and folder in video.parents:
        lesson_copy = (Path(lessons_dir).resolve() / _lesson_of(folder) / "output" / video.name) \
            if _lesson_of(folder) else None
        if lesson_copy and lesson_copy.is_file() and lesson_copy.stat().st_size == video.stat().st_size \
                and _sha256(lesson_copy) == _sha256(video):
            published = lesson_copy                        # this job's own video, not replaced since

    for entry in sorted(folder.iterdir()):
        if entry.name in KEEP:
            continue
        freed += _size(entry)
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()
        deleted.append(_rel(entry))
    if published is not None:
        freed += published.stat().st_size
        published.unlink()
        deleted.append(_rel(published))
    return {"deleted": deleted, "freedBytes": freed, "kept": sorted(_rel(folder / k) for k in KEEP
                                                                     if (folder / k).exists()),
            "at": time.strftime("%Y-%m-%d %H:%M:%S")}


def _lesson_of(folder: Path) -> str | None:
    import json

    try:
        lesson = json.loads((folder / "job.json").read_text(encoding="utf-8")).get("lessonId")
    except (OSError, ValueError):
        return None
    return lesson if lesson and re.fullmatch(r"[a-z0-9][a-z0-9_]{0,59}", lesson) else None


def _rel(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)
