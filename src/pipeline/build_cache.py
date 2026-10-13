"""Deterministic content hashes and the per-lesson build manifest.

Every pipeline stage computes an *input hash* from exactly the things that
affect its output. If the hash matches the one stored after the last
successful build (and the output still exists), the stage is skipped.

Stage keys live in ``generated/build_cache.json``; per-artifact metadata the
user asked for sits next to the artifacts (``audio/<id>.meta.json``,
``alignment/alignment.meta.json``, ``generated/manim/<quality>/*.meta.json``).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.config.video_config import PROJECT_ROOT

_file_hash_memo: dict[tuple[str, int, int], str] = {}


def hash_value(value) -> str:
    """Stable hash of any JSON-serialisable value."""
    payload = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def hash_file(path: Path) -> str:
    """Content hash of a file (memoised on path + size + mtime within one run)."""
    path = Path(path)
    stat = path.stat()
    memo_key = (str(path.resolve()), stat.st_size, stat.st_mtime_ns)
    if memo_key not in _file_hash_memo:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        _file_hash_memo[memo_key] = digest.hexdigest()[:24]
    return _file_hash_memo[memo_key]


def hash_files(paths) -> str:
    """Hash of several files (names relative to the project + contents)."""
    entries = []
    for p in sorted(Path(x) for x in paths):
        try:
            name = p.resolve().relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            name = p.name
        entries.append((name, hash_file(p)))
    return hash_value(entries)


def framework_hash() -> str:
    """Everything in src/ (and the lms_video_generator/ import alias) plus manim.cfg:
    code any lesson's visuals can depend on."""
    files = [p for folder in ("src", "lms_video_generator") for p in (PROJECT_ROOT / folder).rglob("*.py")
             if "__pycache__" not in p.parts]
    return hash_files([*files, PROJECT_ROOT / "manim.cfg"])


def lesson_asset_files(lesson_dir: Path) -> list[Path]:
    """Assets a lesson may draw: its own assets/ folder and the shared assets/ (not voices)."""
    folders = [lesson_dir / "assets", PROJECT_ROOT / "assets"]
    found = []
    for folder in folders:
        if folder.exists():
            found += [p for p in folder.rglob("*") if p.is_file() and "voices" not in p.parts and p.name != ".gitkeep"]
    return found


class BuildManifest:
    """``generated/build_cache.json``: last successful input hash per stage."""

    def __init__(self, path: Path):
        self.path = Path(path)
        try:
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

    def get(self, stage: str) -> dict | None:
        return self.data.get(stage)

    def matches(self, stage: str, input_hash: str, *outputs: Path) -> bool:
        entry = self.data.get(stage)
        return bool(entry) and entry.get("input_hash") == input_hash and all(Path(o).exists() for o in outputs)

    def record(self, stage: str, input_hash: str, **extra) -> None:
        self.data[stage] = {"input_hash": input_hash, **extra}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def forget(self, stage: str) -> None:
        if self.data.pop(stage, None) is not None:
            self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
