"""Shared test fixtures: temporary voice library, fast deterministic TTS engine."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from src.audio.tts_engine import TTSEngine
from src.audio.voice_manager import VoiceManager


def write_tone(path: Path, seconds: float, freq: float = 220.0, amplitude: float = 0.3, rate: int = 24000) -> Path:
    t = np.arange(int(seconds * rate)) / rate
    # A little amplitude wobble so loudness measurement behaves like speech.
    signal = amplitude * np.sin(2 * np.pi * freq * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t))
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), signal.astype(np.float32), rate)
    return path


class ToneEngine(TTSEngine):
    """Stands in for XTTS in tests: a tone whose length follows the text.

    Pitch and volume differ per voice so tests can tell voices apart and
    check that normalisation evens out the volume.
    """

    name = "tone-test"

    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def synthesize(self, text, voice, language, out_path):
        self.calls.append((voice.id, text))
        seed = int(hashlib.md5(voice.id.encode()).hexdigest()[:4], 16)
        write_tone(Path(out_path), 0.4 + 0.045 * len(text), freq=150 + seed % 300, amplitude=0.05 + (seed % 7) / 10)

    def fingerprint(self):
        return self.name


@pytest.fixture
def voices(tmp_path) -> VoiceManager:
    """Library with teacher_a (3 samples), teacher_b and student_a (1 sample each)."""
    vm = VoiceManager(tmp_path / "voices")
    src = tmp_path / "recordings"
    vm.add("teacher_a", [write_tone(src / f"a{i}.wav", 3.0, 200 + i) for i in range(3)], name="Teacher A")
    vm.add("teacher_b", [write_tone(src / "b.wav", 3.0, 120)], name="Teacher B")
    vm.add("student_a", [write_tone(src / "s.wav", 3.0, 330)], name="Student A")
    return vm


@pytest.fixture
def tone_engine() -> ToneEngine:
    return ToneEngine()
