"""Word- and sentence-level timestamps for generated narration (WhisperX).

We already know what was said, so WhisperX *forced alignment* (wav2vec2) is
used instead of speech recognition: it is faster and matches the script
exactly. Results are cached per audio file in ``cache/alignment/``.
If WhisperX is unavailable, timings are estimated from the text instead.
"""

from __future__ import annotations

import hashlib
import os
import uuid
import json
import re
from pathlib import Path

from src.animation.timing import estimate_words
from src.config.video_config import PROJECT_ROOT

CACHE_DIR = PROJECT_ROOT / "cache" / "alignment"
ALIGN_VERSION = "wav2vec2-forced-v1"  # bump to invalidate cached alignments


def audio_hash(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:24]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


class Aligner:
    def __init__(self, language: str = "en", device: str = "cpu", cache_dir: Path = CACHE_DIR):
        self.language = language
        self.device = device
        self.cache_dir = Path(cache_dir)
        self._model = None
        self._meta = None

    @staticmethod
    def available() -> bool:
        try:
            import whisperx  # noqa: F401
        except Exception:
            return False
        return True

    def _load(self):
        if self._model is None:
            import whisperx

            self._model, self._meta = whisperx.load_align_model(language_code=self.language, device=self.device)
        return self._model, self._meta

    def align(self, wav: Path, text: str, duration: float, force: bool = False) -> tuple[dict | None, bool]:
        """Return ``({"words": [...], "sentences": [...], "method": ...}, from_cache)``.

        Returns ``(None, False)`` if WhisperX is needed but not installed.
        WhisperX is imported (and its model loaded) only on a cache miss.
        """
        key = f"{audio_hash(wav)}-{hashlib.sha256(text.encode()).hexdigest()[:8]}-{self.language}-{ALIGN_VERSION}"
        cached = self.cache_dir / f"{key}.json"
        if cached.exists() and not force:
            return json.loads(cached.read_text(encoding="utf-8")), True

        if not self.available():
            return None, False
        import whisperx

        model, meta = self._load()
        audio = whisperx.load_audio(str(wav))
        result = whisperx.align(
            [{"text": text, "start": 0.0, "end": duration}], model, meta, audio, self.device,
            return_char_alignments=False,
        )
        words = fill_missing_times([
            {"word": w["word"], "start": w.get("start"), "end": w.get("end")} for w in result.get("word_segments", [])
        ], duration)
        data = {"method": "whisperx", "words": words, "sentences": sentences_from_words(text, words)}
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Unique temp name + atomic rename: concurrent jobs may align the same clip.
        staged = cached.with_name(f"{cached.stem}.{os.getpid()}.{uuid.uuid4().hex[:8]}.tmp")
        staged.write_text(json.dumps(data, indent=1), encoding="utf-8")
        os.replace(staged, cached)
        return data, False


def estimated_alignment(text: str, duration: float) -> dict:
    """Fallback when WhisperX is disabled or unavailable."""
    words = [{"word": w.text, "start": w.start, "end": w.end} for w in estimate_words(text, duration)]
    return {"method": "estimated", "words": words, "sentences": sentences_from_words(text, words)}


def fill_missing_times(words: list[dict], duration: float) -> list[dict]:
    """Some tokens (digits, symbols) get no timestamp; interpolate between neighbours."""
    for i, w in enumerate(words):
        if w["start"] is None:
            prev_end = next((words[j]["end"] for j in range(i - 1, -1, -1) if words[j]["end"] is not None), 0.0)
            next_start = next((words[j]["start"] for j in range(i + 1, len(words)) if words[j]["start"] is not None), duration)
            w["start"], w["end"] = prev_end, max(prev_end, next_start)
        w["start"], w["end"] = round(float(w["start"]), 3), round(float(w["end"]), 3)
    return words


def sentences_from_words(text: str, words: list[dict]) -> list[dict]:
    """Group aligned words back into the script's sentences."""
    sentences, index = [], 0
    for sentence in split_sentences(text):
        count = len(sentence.split())
        chunk = words[index:index + count]
        index += count
        if chunk:
            sentences.append({"text": sentence, "start": chunk[0]["start"], "end": chunk[-1]["end"]})
    return sentences
