"""Speech check: comparing what a clip says with its script (src/audio/speech_check.py).

Only the comparison is tested here (no Whisper model); the examples are real
XTTS / Whisper outputs from generated lessons.
"""

from pathlib import Path

import pytest

from src.audio.speech_check import SpeechChecker, compare
from src.audio.tts_engine import XTTSEngine
from src.audio.voice_manager import VoiceProfile


@pytest.mark.parametrize("text, heard", [
    ("No.", "No, I am not."),                                        # invented words after a short line
    ("Index one.", "Index 1, not us."),
    ("Twenty-one.", "Twinger ID-1"),                                 # garbled
    ("Five variables.", "Bye variables!"),
    ("Correct. And index zero?", "correct dot an index zero"),       # punctuation read aloud
    ("Blank two: (c), and. Two similar problems.", "Blank 2. C and R. E. New window soft. 2. Similar problems."),
    ("Suppose we want to store the marks of five students.", ""),    # silence
])
def test_wrong_speech_is_rejected(text, heard):
    assert not compare(text, heard)["ok"]


@pytest.mark.parametrize("text, heard", [
    ("No.", "No."),
    ("Twenty-five.", "25."),
    ("Zero, one, two, three, four.", "0, 1, 2, 3, 4."),
    ("Two: four, eight, twelve, sixteen and twenty: five twentieths, one quarter.",
     "2, 4, 8, 12, 16 and 20, 520th, 1 quarter."),
    ("Not prime: forty minus twelve is twenty-eight. The odds in favour are twelve to twenty-eight, three to "
     "seven, so the odds against you are seven to three.",
     "Not Prime! 40-12 is 28. The odds in favor are 12-28, 3-7, so the odds against you are 7-3."),
    ("Two hundred and twenty-five times eighteen, divided by five times eighty-one: ten seconds.",
     "225 × 18 ÷ 5 × 81 10 seconds"),
    ("With u ten and v two: ninety-six divided by ten is nine point six kilometres per hour.",
     "With U10 and V2, 96 divided by 10 is 9.6 kilometers per hour."),
    ("This video closes Module three. It combines everything from Videos one to seven into one method: S-G-C-V-R.",
     "This video closes module 3. It combines everything from videos 1 to 7 into one method, SGCVR."),
    ("The rule: odds compare favourable with unfavourable; probability compares favourable with the total.",
     "The rule, odds compare favorable with unfavorable, probability compares favorable with the total."),
])
def test_same_speech_written_differently_is_accepted(text, heard):
    assert compare(text, heard)["ok"]


def test_other_languages_are_not_checked(tmp_path):
    assert SpeechChecker().check(tmp_path / "clip.wav", "नमस्ते", "hi") is None


class _Model:
    """Stands in for the XTTS model: writes one more file per attempt."""

    def __init__(self):
        self.calls = 0

    def tts_to_file(self, text, speaker_wav, language, file_path):
        self.calls += 1
        Path(file_path).write_text(f"attempt {self.calls}", encoding="utf-8")


class _Checker:
    def __init__(self, heard):
        self.heard = list(heard)

    def check(self, wav, text, language):
        heard = self.heard.pop(0)
        return None if heard is None else {**compare(text, heard), "heard": heard}


def _engine(heard):
    engine = XTTSEngine()
    model = _Model()
    engine._model = lambda: model
    engine._checker = _Checker(heard)
    return engine, model


VOICE = VoiceProfile(id="v", name="v", language="en", samples=[])


def test_clip_is_regenerated_until_it_matches(tmp_path):
    engine, model = _engine(["No, I am not.", "No."])
    engine.synthesize("No.", VOICE, "en", tmp_path / "clip.wav")
    assert model.calls == 2
    assert engine.last_check["ok"] and engine.last_check["attempts"] == 2
    assert (tmp_path / "clip.wav").read_text(encoding="utf-8") == "attempt 2"
    assert list(tmp_path.iterdir()) == [tmp_path / "clip.wav"]


def test_closest_attempt_is_kept_when_none_matches(tmp_path):
    engine, model = _engine(["No, I am not here.", "No, sir.", "No, I am not.", "Know this one."])
    engine.synthesize("No.", VOICE, "en", tmp_path / "clip.wav")
    assert model.calls == 4
    assert not engine.last_check["ok"] and engine.last_check["heard"] == "No, sir."
    assert (tmp_path / "clip.wav").read_text(encoding="utf-8") == "attempt 2"
    assert list(tmp_path.iterdir()) == [tmp_path / "clip.wav"]


def test_unchecked_clip_is_generated_once(tmp_path):
    engine, model = _engine([None])
    engine.synthesize("No.", VOICE, "en", tmp_path / "clip.wav")
    assert model.calls == 1 and engine.last_check is None
