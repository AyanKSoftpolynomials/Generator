"""Narration timing as seen from inside a Manim scene.

The same ``animation.py`` runs in three modes, chosen by environment
variables that the generator sets (you never set them yourself):

* **standalone** (no variables): plain ``manim``/``render.py`` runs. Durations
  are estimated from the text so the animation still plays sensibly, silently.
* **extract**: fast dry run. Every ``narrate()`` call is recorded and written
  to ``generated/script.json``. Durations are estimates.
* **render**: real render. Durations and word timings come from the generated
  audio (``generated/timing.json``). The start time of every narration in the
  video is written to ``generated/timeline.json``.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

MODE_ENV = "LMS_MODE"
TIMING_ENV = "LMS_TIMING_FILE"
OUTPUT_ENV = "LMS_OUTPUT_FILE"
PAUSE_ENV = "LMS_DEFAULT_PAUSE"
VALIDATION_ENV = "LMS_VALIDATION"   # settings.json > validation, as JSON (layout checks)
SCENE_MARKER = "[LMS] scene "   # printed by scene_start() while rendering (progress reporting)

DEFAULT_PAUSE_AFTER = 0.25

STANDALONE, EXTRACT, RENDER, PLAN = "standalone", "extract", "render", "plan"

# Typical narration speed used for estimates (words per second).
WORDS_PER_SECOND = 2.6


@dataclass
class Word:
    """One spoken word; times are seconds from the start of its narration clip."""

    text: str
    start: float
    end: float


def normalise_word(word: str) -> str:
    """Lower-case and strip punctuation so "zero," matches "Zero"."""
    return re.sub(r"[^\w]", "", word.lower())


def estimate_duration(text: str) -> float:
    """Rough spoken length of ``text`` in seconds (used before audio exists)."""
    return round(max(1.0, len(text.split()) / WORDS_PER_SECOND + 0.4), 3)


def estimate_words(text: str, duration: float) -> list[Word]:
    """Spread the words of ``text`` over ``duration`` in proportion to their length."""
    tokens = text.split()
    total = sum(len(t) + 1 for t in tokens) or 1
    words, cursor = [], 0.0
    for token in tokens:
        span = duration * (len(token) + 1) / total
        words.append(Word(token, round(cursor, 3), round(cursor + span, 3)))
        cursor += span
    return words


class NarrationTimingStore:
    """Answers "how long is narration X and when is each word spoken?"."""

    def __init__(
        self,
        mode: str = STANDALONE,
        timing: dict | None = None,
        output: Path | None = None,
        default_pause: float = DEFAULT_PAUSE_AFTER,
    ):
        self.mode = mode
        self.timing = timing or {}
        self.output = output
        self.default_pause = default_pause

    @classmethod
    def from_environment(cls) -> "NarrationTimingStore":
        mode = os.environ.get(MODE_ENV, STANDALONE)
        output = Path(os.environ[OUTPUT_ENV]) if os.environ.get(OUTPUT_ENV) else None
        timing = {}
        timing_file = os.environ.get(TIMING_ENV)
        if timing_file and Path(timing_file).exists():
            timing = json.loads(Path(timing_file).read_text(encoding="utf-8")).get("narrations", {})
        pause = float(os.environ.get(PAUSE_ENV, DEFAULT_PAUSE_AFTER))
        return cls(mode, timing, output, pause)

    def lookup(self, narration_id: str, text: str) -> tuple[float, list[Word], bool]:
        """Return ``(duration, words, estimated)`` for a narration block."""
        entry = self.timing.get(narration_id)
        if entry is None:
            if self.mode == RENDER and self.timing:
                raise RuntimeError(
                    f"Narration '{narration_id}' has no generated audio. "
                    "Run scripts/generate_video.py again so the audio is regenerated."
                )
            duration = estimate_duration(text)
            return duration, estimate_words(text, duration), True
        duration = float(entry["duration"])
        words = [Word(w["word"], w["start"], w["end"]) for w in entry.get("words", [])]
        return duration, words or estimate_words(text, duration), not entry.get("words")
