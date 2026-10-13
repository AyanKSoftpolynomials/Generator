"""Checks that a generated clip says what its script says.

XTTS v2 sometimes speaks words that are not in the text, mostly on very short
lines ("No." -> "No, I am not.") and around unusual punctuation. Each new clip
is therefore transcribed with a local Whisper model (faster-whisper, already a
dependency of WhisperX) and compared with its text; the engine regenerates a
clip that does not match (``XTTSEngine.synthesize``).

Everything runs locally. The Whisper model (~460 MB) is downloaded once on
first use, like the other speech models.
"""

from __future__ import annotations

import difflib
import logging
import re
from pathlib import Path

WHISPER_MODEL = "small"
CHECK_LANGUAGES = {"en"}      # the number handling below is English-only; other languages are not checked

_UNITS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
          "sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety "
          "hundred thousand million").split()
_ORDINALS = ("first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth "
             "fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth twentieth thirtieth fortieth "
             "fiftieth sixtieth seventieth eightieth ninetieth hundredth thousandth millionth").split()
_NUMBER_WORDS = set(_UNITS) | set(_ORDINALS) | {word + "s" for word in _ORDINALS}
_NUMBER_JOINERS = {"and", "to", "point", "minus", "plus", "times", "divided", "by", "over", "into"}
NUMBER = "#"


def _tokens(text: str) -> list[str]:
    """Words of ``text`` for comparison.

    Whisper writes numbers and maths its own way ("forty minus twelve" ->
    "40-12", "five twentieths" -> "5/20ths", "u ten" -> "U10"), so every run of
    numbers, with the words that join them, becomes one ``#``, and single
    letters are dropped. What is left is the wording itself.
    """
    words = re.findall(r"[a-z0-9]+", text.lower().replace("'", "").replace("’", ""))
    marked = [NUMBER if word in _NUMBER_WORDS or any(ch.isdigit() for ch in word) else word
              for word in words if len(word) > 1 or word.isdigit()]
    out: list[str] = []
    for index, word in enumerate(marked):
        if word in _NUMBER_JOINERS and NUMBER in marked[max(0, index - 2):index + 3]:
            continue
        if word == NUMBER and out and out[-1] == NUMBER:
            continue
        out.append(word)
    return out


def _similar(a: str, b: str) -> bool:
    """Spelling variants of one word ("favourable" / "favorable")."""
    return len(a) > 3 and len(b) > 3 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.8


def compare(text: str, heard: str) -> dict:
    """Compare the script ``text`` with what was ``heard`` in the clip.

    Returns ``{"ok", "errors", "allowed", "words"}``: ``errors`` counts words
    that were added, dropped or replaced. Lines of up to three words must match
    exactly (that is where XTTS invents speech); longer ones may differ in
    about one word in seven, which covers Whisper's own mistakes.
    """
    want, got = _tokens(text), _tokens(heard)
    errors = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, want, got, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        a, b = want[i1:i2], got[j1:j2]
        if tag == "replace":
            pairs = min(len(a), len(b))
            errors += sum(not _similar(x, y) for x, y in zip(a, b)) + max(len(a), len(b)) - pairs
        else:
            errors += len(a) + len(b)
    allowed = 0 if len(want) <= 3 else max(1, round(len(want) / 7))
    return {"ok": bool(got) and errors <= allowed, "errors": errors, "allowed": allowed, "words": len(want)}


class SpeechChecker:
    """Transcribes clips with a local Whisper model (loaded once, on first use)."""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self._model = None
        self.unavailable: str | None = None     # why checking is off (model could not be loaded)

    def _whisper(self):
        if self._model is None and self.unavailable is None:
            try:
                from faster_whisper import WhisperModel

                logging.getLogger("faster_whisper").setLevel(logging.WARNING)
                self._model = WhisperModel(WHISPER_MODEL, device=self.device,
                                           compute_type="float16" if self.device == "cuda" else "int8")
            except Exception as exc:       # not installed / no network for the first download
                self.unavailable = f"{type(exc).__name__}: {exc}"
        return self._model

    def check(self, wav: Path, text: str, language: str) -> dict | None:
        """``compare()`` result plus ``heard``; None when this clip cannot be checked."""
        if language not in CHECK_LANGUAGES:
            return None
        model = self._whisper()
        if model is None:
            return None
        segments, _ = model.transcribe(str(wav), language=language, beam_size=5,
                                       condition_on_previous_text=False)
        heard = " ".join(segment.text.strip() for segment in segments)
        return {**compare(text, heard), "heard": heard}
