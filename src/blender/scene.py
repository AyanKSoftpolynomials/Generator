"""Authoring API for 3D sections: subclass ``BlenderScene`` in animation.py.

    from src.blender import BlenderScene

    class Coordinates3D(BlenderScene):
        def construct(self, b, t):
            axes = b.axes(length=4)
            p = b.sphere(radius=0.15, location=(0, 0, 0), color="#FFD166")
            b.move(p, to=(2, 0, 0), start=t.word("x"), duration=1.5)
            b.orbit_camera(radius=11, height=5, start=0, end=t.duration)

``b`` is the Toolkit (src/blender/toolkit.py: objects, materials, cameras,
lights, animation helpers); ``t`` is the segment's ``Timing`` (its length and
the narration's word timings, in seconds from the start of the clip).

This module is plain Python (no ``bpy``), so animation.py can import it in the
normal Manim process; ``construct()`` only ever runs inside Blender.
"""

from __future__ import annotations

import re


def normalise_word(word: str) -> str:
    """Same rule as src.animation.timing (kept here: this module also runs inside Blender)."""
    return re.sub(r"[^\w]", "", word.lower())


class Timing:
    """Time information of one Blender segment. All times are seconds from the clip's start."""

    def __init__(self, duration: float, fps: float, frames: int, narrations: list[dict], params: dict):
        self.duration = duration
        self.fps = fps
        self.frames = frames
        self.narrations = narrations
        self.params = params

    @property
    def words(self) -> list[dict]:
        return [w for n in self.narrations for w in n.get("words", [])]

    def word(self, phrase: str, occurrence: int = 1, default: float | None = None) -> float:
        """When ``phrase`` (one or more words) starts being spoken in this clip."""
        target = [normalise_word(w) for w in phrase.split()]
        spoken = [(normalise_word(w["text"]), w["start"]) for w in self.words]
        seen = 0
        for i in range(len(spoken) - len(target) + 1):
            if [s for s, _ in spoken[i:i + len(target)]] == target:
                seen += 1
                if seen == occurrence:
                    return max(0.0, spoken[i][1])
        if default is not None:
            return default
        raise ValueError(f"'{phrase}' is not spoken during this Blender clip "
                         f"(words: {' '.join(w['text'] for w in self.words)[:200]})")

    def narration(self, narration_id: str) -> dict:
        for n in self.narrations:
            if n["id"] == narration_id:
                return n
        raise ValueError(f"Narration '{narration_id}' is not part of this Blender clip.")

    def frame(self, seconds: float) -> int:
        """Blender frame number (1-based) shown at ``seconds``."""
        return 1 + int(round(max(0.0, seconds) * self.fps))


class BlenderScene:
    """Base class of a 3D clip. Override ``construct(self, b, t)``."""

    background: str = "#0E1726"        # same as manim.cfg, so cuts between engines are seamless

    def construct(self, b, t: Timing) -> None:  # pragma: no cover - implemented by lessons
        raise NotImplementedError("Implement construct(self, b, t) in your BlenderScene subclass.")
