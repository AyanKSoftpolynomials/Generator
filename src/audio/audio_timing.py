"""``generated/timing.json``: per-narration audio duration and word timings.

This is what the Manim render reads (through ``NarrationTimingStore``) so
that animation timing follows the real audio.
"""

from __future__ import annotations

import json
from pathlib import Path


def write_timing(path: Path, entries: dict[str, dict]) -> None:
    """``entries`` maps narration id -> {"duration", "audio", "voice", "words", "sentences", "alignment"}."""
    path.parent.mkdir(parents=True, exist_ok=True)
    total = sum(e["duration"] for e in entries.values())
    path.write_text(json.dumps({"total_speech_seconds": round(total, 3), "narrations": entries}, indent=1), encoding="utf-8")


def read_timing(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("narrations", {})


def format_duration(seconds: float) -> str:
    minutes, secs = divmod(int(round(seconds)), 60)
    return f"{minutes}m {secs:02d}s" if minutes else f"{secs}s"
