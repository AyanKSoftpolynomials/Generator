"""Script extraction from animation.py, voice inheritance and validation."""

import json
import textwrap

import pytest

from src.animation.manim_engine import find_scene_class, run_manim
from src.script.parser import parse_extracted
from src.script.validator import validate_script
from src.utils.errors import LMSError

MIXED_LESSON = textwrap.dedent('''
    from manim import *
    from src.animation import LMSScene

    class MixedVoices(LMSScene):
        lesson_title = "Mixed"
        default_voice = "teacher_a"

        def construct(self):
            self.scene_start("hook")
            n = self.narrate("hook_01", "Hello students!")
            self.play_with(n, FadeIn(Square()))
            self.scene_start("how", voice="teacher_b")
            self.narrate("how_01", "Numbers start at one.")
            self.narrate("how_02", "I think so too.", voice="student_a", pause_after=0.5, subtitle=False)
''')


def raw_script(narration, scenes=None, default_voice="teacher_a"):
    return {"lesson": {"id": None, "title": "T", "language": "en", "default_voice": default_voice,
                       "scene_class": "X", "subtitles": None},
            "scenes": scenes or [], "narration": narration}


def test_extract_script_json_from_animation_py(tmp_path):
    """script.json is generated from narrate() calls - nobody writes JSON."""
    lesson = tmp_path / "mixed_lesson"
    lesson.mkdir()
    (lesson / "animation.py").write_text(MIXED_LESSON, encoding="utf-8")
    scene = find_scene_class(lesson / "animation.py")
    assert scene == "MixedVoices"
    out = lesson / "generated" / "extracted.json"
    run_manim(lesson / "animation.py", scene, "extract", out, lesson / "extract.log")

    raw = json.loads(out.read_text())
    assert [n["id"] for n in raw["narration"]] == ["hook_01", "how_01", "how_02"]
    script = parse_extracted(raw, "mixed_lesson", "narrator")
    by_id = script.by_id()
    assert (by_id["hook_01"].voice, by_id["hook_01"].voice_source) == ("teacher_a", "lesson")
    assert (by_id["how_01"].voice, by_id["how_01"].voice_source) == ("teacher_b", "scene")
    assert (by_id["how_02"].voice, by_id["how_02"].voice_source) == ("student_a", "narration")
    assert by_id["how_02"].pause_after == 0.5 and by_id["how_02"].subtitle is False
    assert script.lesson_id == "mixed_lesson" and script.title == "Mixed"
    assert script.voices_used == ["student_a", "teacher_a", "teacher_b"]


def test_global_default_voice_used_last():
    raw = raw_script([{"id": "a", "text": "Hi.", "voice": None, "voice_source": "global", "scene": None}],
                     default_voice=None)
    script = parse_extracted(raw, "lesson", "narrator")
    assert script.narration[0].voice == "narrator"
    assert script.narration[0].voice_source == "global"


def test_valid_script_passes(voices):
    raw = raw_script([
        {"id": "a", "text": "Hi.", "voice": "teacher_a", "voice_source": "lesson", "scene": "s"},
        {"id": "b", "text": "Yo.", "voice": "student_a", "voice_source": "narration", "scene": "s"},
    ])
    warnings = validate_script(parse_extracted(raw, "l", None), voices)
    # Valid, but the 3 s test recordings are flagged as short for cloning.
    assert all("reference audio" in w for w in warnings)


def test_missing_voice_is_an_error(voices):
    raw = raw_script([{"id": "a", "text": "Hi.", "voice": None, "voice_source": "global", "scene": None}],
                     default_voice=None)
    with pytest.raises(LMSError, match="has no voice"):
        validate_script(parse_extracted(raw, "l", None), voices)


def test_invalid_voice_is_an_error(voices):
    raw = raw_script([{"id": "a", "text": "Hi.", "voice": "teacher_x", "voice_source": "narration", "scene": None}])
    with pytest.raises(LMSError) as err:
        validate_script(parse_extracted(raw, "l", None), voices)
    assert "teacher_x" in str(err.value) and "Used by: a" in str(err.value)


def test_duplicate_ids_are_an_error(voices):
    raw = raw_script([
        {"id": "a", "text": "Hi.", "voice": "teacher_a", "scene": None},
        {"id": "a", "text": "Again.", "voice": "teacher_a", "scene": None},
    ])
    with pytest.raises(LMSError, match="used more than once"):
        validate_script(parse_extracted(raw, "l", None), voices)


def test_scene_class_detection(tmp_path):
    f = tmp_path / "animation.py"
    f.write_text("from manim import *\nclass Plain(Scene):\n    pass\n")
    with pytest.raises(LMSError, match="no narrated scene"):
        find_scene_class(f)
