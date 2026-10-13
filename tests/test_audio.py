import subprocess
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from src.audio.audio_cache import AudioCache
from src.audio.audio_composer import concatenate, place_clips
from src.audio.audio_processor import audio_duration, normalize
from src.video.ffmpeg import ffmpeg_path
from tests.conftest import write_tone


def integrated_loudness(path: Path) -> float:
    result = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                            capture_output=True, text=True)
    summary = result.stderr.split("Summary:")[-1]
    return float(summary.split("I:")[1].split("LUFS")[0])


def test_audio_generation_with_engine(voices, tone_engine, tmp_path):
    out = tmp_path / "clip.wav"
    tone_engine.synthesize("Hello students!", voices.get("teacher_a"), "en", out)
    assert out.exists() and audio_duration(out) > 0.5
    assert tone_engine.calls == [("teacher_a", "Hello students!")]


def test_normalization_evens_out_volume_and_format(tmp_path):
    quiet = write_tone(tmp_path / "quiet.wav", 3.0, amplitude=0.02, rate=24000)
    loud = write_tone(tmp_path / "loud.wav", 3.0, amplitude=0.9, rate=22050)
    normalize(quiet, tmp_path / "q.wav", sample_rate=44100, loudness_lufs=-18)
    normalize(loud, tmp_path / "l.wav", sample_rate=44100, loudness_lufs=-18)
    for f in ("q.wav", "l.wav"):
        info = sf.info(str(tmp_path / f))
        assert (info.samplerate, info.channels) == (44100, 1)
        assert abs(integrated_loudness(tmp_path / f) - -18) < 1.5
    peak = np.abs(sf.read(str(tmp_path / "l.wav"))[0]).max()
    assert peak < 0.95  # true-peak limit: no clipping


def test_silence_is_trimmed(tmp_path):
    rate = 24000
    tone = sf.read(str(write_tone(tmp_path / "t.wav", 1.0, rate=rate)))[0]
    padded = np.concatenate([np.zeros(rate), tone, np.zeros(rate)])
    sf.write(str(tmp_path / "padded.wav"), padded, rate)
    normalize(tmp_path / "padded.wav", tmp_path / "trimmed.wav")
    assert audio_duration(tmp_path / "trimmed.wav") < 1.4


def test_cache_key_depends_on_text_voice_and_settings():
    base = dict(text="Hi", voice_fingerprint="v1", language="en", engine_fingerprint="xtts", processing={"sr": 44100})
    key = AudioCache.key(**base)
    assert key == AudioCache.key(**base)
    for change in ({"text": "Hello"}, {"voice_fingerprint": "v2"}, {"language": "hi"},
                   {"engine_fingerprint": "other"}, {"processing": {"sr": 48000}}):
        assert AudioCache.key(**{**base, **change}) != key


def test_duration_calculation(tmp_path):
    assert audio_duration(write_tone(tmp_path / "x.wav", 2.5)) == pytest.approx(2.5, abs=0.01)


def test_place_clips_on_timeline(tmp_path):
    a = write_tone(tmp_path / "a.wav", 1.0, rate=44100)
    b = write_tone(tmp_path / "b.wav", 0.5, rate=44100)
    warnings = place_clips([(a, 0.5), (b, 2.0)], 3.0, tmp_path / "track.wav")
    data, rate = sf.read(str(tmp_path / "track.wav"))
    assert warnings == []
    assert len(data) / rate == pytest.approx(3.0, abs=0.01)
    assert np.abs(data[: int(0.45 * rate)]).max() == 0         # silence before the first clip
    assert np.abs(data[int(1.6 * rate): int(1.95 * rate)]).max() == 0  # gap between clips
    assert np.abs(data[int(2.1 * rate): int(2.4 * rate)]).max() > 0.01


def test_place_clips_warns_on_overlap(tmp_path):
    a = write_tone(tmp_path / "a.wav", 1.0, rate=44100)
    warnings = place_clips([(a, 0.0), (a, 0.5)], 2.0, tmp_path / "track.wav")
    assert warnings and "before the previous clip ends" in warnings[0]


def test_concatenate_with_pauses(tmp_path):
    a = write_tone(tmp_path / "a.wav", 1.0, rate=44100)
    b = write_tone(tmp_path / "b.wav", 2.0, rate=44100)
    starts = concatenate([(a, 0.3), (b, 0.0)], tmp_path / "joined.wav")
    assert starts == [0.0, pytest.approx(1.3, abs=0.001)]
    assert audio_duration(tmp_path / "joined.wav") == pytest.approx(3.3, abs=0.01)
