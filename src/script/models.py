"""In-memory form of the generated ``script.json``."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class NarrationBlock:
    id: str
    text: str
    voice: str | None          # resolved voice (after the global default is applied)
    scene: str | None
    subtitle: bool = True
    pause_after: float = 0.25
    estimated_duration: float = 0.0
    voice_source: str = ""     # "narration", "scene", "lesson" or "global"


@dataclass
class LessonScript:
    lesson_id: str
    title: str | None
    language: str
    default_voice: str | None
    scene_class: str
    subtitles: dict | None
    scenes: list[dict] = field(default_factory=list)
    narration: list[NarrationBlock] = field(default_factory=list)

    @property
    def voices_used(self) -> list[str]:
        return sorted({n.voice for n in self.narration if n.voice})

    def by_id(self) -> dict[str, NarrationBlock]:
        return {n.id: n for n in self.narration}

    def to_dict(self) -> dict:
        return {
            "lesson": {
                "id": self.lesson_id, "title": self.title, "language": self.language,
                "default_voice": self.default_voice, "scene_class": self.scene_class, "subtitles": self.subtitles,
            },
            "scenes": self.scenes,
            "narration": [asdict(n) for n in self.narration],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
