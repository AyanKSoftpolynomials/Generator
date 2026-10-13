"""Subtitle settings and cue building (shared by the SRT and VTT writers)."""

from __future__ import annotations

from dataclasses import dataclass, field

MODES = ("sentence", "word")
FORMATS = ("srt", "vtt")


@dataclass
class SubtitleSettings:
    enabled: bool = True
    mode: str = "sentence"
    formats: list[str] = field(default_factory=lambda: ["srt", "vtt"])
    max_chars: int = 84
    embed_in_mp4: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "SubtitleSettings":
        formats = data.get("formats", data.get("format", ["srt", "vtt"]))
        if isinstance(formats, str):
            formats = [formats]
        settings = cls(
            enabled=bool(data.get("enabled", True)),
            mode=data.get("mode", "sentence"),
            formats=[f.lower() for f in formats],
            max_chars=int(data.get("max_chars", 84)),
            embed_in_mp4=bool(data.get("embed_in_mp4", True)),
        )
        if settings.mode not in MODES:
            raise ValueError(f"subtitle mode must be one of {MODES}, not '{settings.mode}'")
        unknown = [f for f in settings.formats if f not in FORMATS]
        if unknown:
            raise ValueError(f"unsupported subtitle format(s) {unknown}; use {FORMATS}")
        return settings


@dataclass
class Cue:
    start: float
    end: float
    text: str


def build_cues(timeline: list[dict], timing: dict[str, dict], script: dict[str, dict], settings: SubtitleSettings) -> list[Cue]:
    """Turn narration placement + word timings into subtitle cues.

    ``timeline``: [{"id", "start"}] from the render; ``timing``: timing.json
    entries; ``script``: narration id -> script entry (for the subtitle flag).
    """
    cues: list[Cue] = []
    for placed in timeline:
        entry = timing.get(placed["id"])
        if entry is None or not script.get(placed["id"], {}).get("subtitle", True):
            continue
        offset = placed["start"]
        words = entry.get("words", [])
        if settings.mode == "word":
            for i, w in enumerate(words):
                end = words[i + 1]["start"] if i + 1 < len(words) else w["end"]
                cues.append(Cue(offset + w["start"], offset + max(end, w["end"]), w["word"]))
        else:
            cues += _sentence_cues(entry, offset, settings.max_chars)
    return cues


def _sentence_cues(entry: dict, offset: float, max_chars: int) -> list[Cue]:
    cues, words, index = [], entry.get("words", []), 0
    for sentence in entry.get("sentences", []):
        count = len(sentence["text"].split())
        chunk = words[index:index + count]
        index += count
        # Split long sentences at word boundaries so a cue fits on two lines.
        line: list[dict] = []
        for w in chunk:
            if line and len(" ".join(x["word"] for x in line + [w])) > max_chars:
                cues.append(Cue(offset + line[0]["start"], offset + line[-1]["end"], " ".join(x["word"] for x in line)))
                line = []
            line.append(w)
        if line:
            cues.append(Cue(offset + line[0]["start"], offset + line[-1]["end"], " ".join(x["word"] for x in line)))
    return cues
