"""Sarvam engine: speaker mapping, request chunking and cache fingerprint (no network)."""

import base64
import io
from types import SimpleNamespace

import numpy as np
import soundfile as sf

from src.audio.tts_engine import SARVAM_SAMPLE_RATE, SarvamEngine, create_engine, engine_fingerprint, split_text
from src.audio.voice_manager import VoiceProfile
from src.config.settings import DEFAULTS, deep_merge

VOICE = VoiceProfile(id="teacher_a", name="Teacher A", language="en", samples=[])


class _TTS:
    def __init__(self):
        self.calls = []

    def convert(self, **request):
        self.calls.append(request)
        buffer = io.BytesIO()
        sf.write(buffer, np.zeros(SARVAM_SAMPLE_RATE // 10), SARVAM_SAMPLE_RATE, format="WAV")
        return SimpleNamespace(audios=[base64.b64encode(buffer.getvalue()).decode()])


def _engine(**config):
    engine = SarvamEngine({**DEFAULTS["audio"]["sarvam"], **config})
    engine._client = SimpleNamespace(text_to_speech=_TTS())
    return engine, engine._client.text_to_speech


def test_split_text_breaks_between_sentences():
    assert split_text("One. Two! Three?", 100) == ["One. Two! Three?"]
    assert split_text("One two. Three four. Five.", 12) == ["One two.", "Three four.", "Five."]
    assert all(len(c) <= 10 for c in split_text("a very long sentence without any stop", 10))


def test_synthesize_maps_voice_and_language(tmp_path):
    engine, tts = _engine(voices={"teacher_a": "ritu"})
    engine.synthesize("Hello students!", VOICE, "en", tmp_path / "clip.wav")
    assert tts.calls[0]["speaker"] == "ritu" and tts.calls[0]["language_code"] == "en-IN"
    assert sf.info(str(tmp_path / "clip.wav")).samplerate == SARVAM_SAMPLE_RATE
    assert engine.speaker("someone_else") == "shubh"            # unmapped voices: the default speaker


def test_long_text_is_sent_in_pieces_and_joined(tmp_path):
    engine, tts = _engine()
    engine.synthesize(" ".join(["This is one sentence."] * 200), VOICE, "hi", tmp_path / "clip.wav")
    assert len(tts.calls) > 1 and all(len(c["text"]) <= 2500 for c in tts.calls)
    assert abs(sf.info(str(tmp_path / "clip.wav")).duration - 0.1 * len(tts.calls)) < 0.01


def test_fingerprint_follows_the_sarvam_settings():
    settings = deep_merge(DEFAULTS, {"audio": {"engine": "sarvam"}})
    other = deep_merge(settings, {"audio": {"sarvam": {"speaker": "priya"}}})
    assert engine_fingerprint("sarvam", settings) == create_engine("sarvam", "cpu", settings).fingerprint()
    assert engine_fingerprint("sarvam", settings) != engine_fingerprint("sarvam", other)


def test_mapping_one_voice_keeps_the_other_voices_clips():
    plain = deep_merge(DEFAULTS, {"audio": {"engine": "sarvam"}})
    mapped = deep_merge(plain, {"audio": {"sarvam": {"voices": {"kavya": "kavya"}}}})
    assert engine_fingerprint("sarvam", mapped, "teacher_a") == engine_fingerprint("sarvam", plain, "teacher_a")
    assert engine_fingerprint("sarvam", mapped, "kavya") != engine_fingerprint("sarvam", plain, "kavya")
    assert engine_fingerprint("sarvam", plain, "teacher_a") == engine_fingerprint("sarvam", plain)   # earlier clips
