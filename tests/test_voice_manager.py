import json

import pytest

from src.audio.voice_manager import VoiceManager, check_sample
from src.utils.errors import LMSError
from tests.conftest import write_tone


def test_voice_exists(voices):
    assert voices.exists("teacher_a")
    assert voices.list_ids() == ["student_a", "teacher_a", "teacher_b"]
    profile = voices.get("teacher_b")
    assert profile.name == "Teacher B" and profile.language == "en"


def test_voice_missing_lists_available_and_fix(voices):
    with pytest.raises(LMSError) as err:
        voices.get("teacher_x")
    text = str(err.value)
    assert "Voice 'teacher_x' does not exist" in text
    assert "- teacher_a" in text and "- student_a" in text
    assert "python scripts/voice.py add teacher_x --sample" in text


def test_multiple_samples(voices, tmp_path):
    profile = voices.get("teacher_a")
    assert [s.name for s in profile.samples] == ["sample_01.wav", "sample_02.wav", "sample_03.wav"]
    assert all(s.exists() for s in profile.samples)
    meta = json.loads((profile.folder / "voice.json").read_text())
    assert meta["samples"] == ["sample_01.wav", "sample_02.wav", "sample_03.wav"]
    # Adding another sample extends the voice instead of replacing it.
    voices.add("teacher_a", [write_tone(tmp_path / "extra.wav", 3.0)])
    assert len(voices.get("teacher_a").samples) == 4


def test_fingerprint_changes_when_samples_change(voices, tmp_path):
    before = voices.get("teacher_b").fingerprint()
    write_tone(voices.get("teacher_b").samples[0], 3.0, freq=500)
    assert voices.get("teacher_b").fingerprint() != before


def test_invalid_samples(tmp_path):
    assert "not found" in check_sample(tmp_path / "nope.wav")[0][0]
    txt = tmp_path / "notes.txt"
    txt.write_text("hello")
    assert "unsupported format" in check_sample(txt)[0][0]
    corrupt = tmp_path / "corrupt.wav"
    corrupt.write_bytes(b"RIFF0000WAVEjunk")
    assert "cannot read" in check_sample(corrupt)[0][0]
    short = write_tone(tmp_path / "short.wav", 0.5)
    assert "only 0.5s" in check_sample(short)[0][0]
    assert check_sample(write_tone(tmp_path / "ok.wav", 3.0)) == ([], [])


def test_validate_reports_missing_sample_file(voices):
    voices.get("student_a").samples[0].unlink()
    errors, _ = voices.validate("student_a")
    assert errors and "sample file not found" in errors[0]
    with pytest.raises(LMSError):
        voices.require("student_a")


def test_add_rejects_bad_id_and_bad_sample(tmp_path):
    vm = VoiceManager(tmp_path / "voices")
    with pytest.raises(LMSError, match="Invalid voice id"):
        vm.add("Teacher A", [write_tone(tmp_path / "x.wav", 3.0)])
    with pytest.raises(LMSError, match="Cannot add sample"):
        vm.add("teacher_c", [write_tone(tmp_path / "tiny.wav", 0.3)])
