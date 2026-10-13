"""Blender engine: 3D sections of a lesson rendered headlessly and spliced into the video."""

import json
import shutil
import subprocess
import textwrap
import uuid

import pytest

from src.blender import Timing
from src.blender.render import blender_source, find_blender, uses_blender
from src.config.settings import DEFAULTS, deep_merge
from src.config.video_config import MEDIA_DIR
from src.utils.errors import LMSError
from src.video.ffmpeg import ffprobe_path
from tests.test_pipeline import make_generator


def _has_blender() -> bool:
    try:
        find_blender(DEFAULTS)
        return True
    except LMSError:
        return False


needs_blender = pytest.mark.skipif(not _has_blender(), reason="Blender is not installed")

LESSON_3D = textwrap.dedent('''
    from manim import *
    from src.animation import BLENDER, LMSScene
    from src.blender import BlenderScene

    SIZE = 1.2

    class Spin(BlenderScene):
        def construct(self, b, t):
            cube = b.cube(size=SIZE, color="#FFD166")
            b.rotate(cube, by=(0, 0, 90), start=0, duration=t.duration)
            b.camera(location=(4, -4, 3))

    class Mixed(LMSScene):
        default_voice = "teacher_a"

        def construct(self):
            self.scene_start("flat")
            n = self.narrate("flat_01", "First a flat square.")
            self.play_with(n, Create(Square()))
            self.scene_start("solid", engine=BLENDER)
            n = self.narrate("solid_01", "Now a solid cube.")
            self.blender(Spin, narration=n)
            self.scene_start("end")
            n = self.narrate("end_01", "Done.")
            self.play_with(n, FadeIn(Circle()))
''')


@pytest.fixture
def lesson3d(tmp_path):
    folder = tmp_path / f"blender_test_{uuid.uuid4().hex[:8]}"
    folder.mkdir()
    (folder / "animation.py").write_text(LESSON_3D, encoding="utf-8")
    yield folder
    shutil.rmtree(MEDIA_DIR / f"{folder.name}_narrated", ignore_errors=True)


def test_timing_words_and_frames():
    t = Timing(duration=4, fps=15, frames=60, params={},
               narrations=[{"id": "a", "words": [{"text": "Go", "start": 0.5, "end": 0.7},
                                                 {"text": "along", "start": 1.0, "end": 1.2},
                                                 {"text": "X,", "start": 1.3, "end": 1.5}]}])
    assert t.word("along x") == 1.0
    assert t.word("nowhere", default=2.0) == 2.0
    with pytest.raises(ValueError):
        t.word("nowhere")
    assert t.frame(0) == 1 and t.frame(1.0) == 16


def test_blender_code_hash_ignores_the_manim_lesson_class(tmp_path):
    a = tmp_path / "a.py"
    a.write_text(LESSON_3D, encoding="utf-8")
    b = tmp_path / "b.py"
    b.write_text(LESSON_3D.replace("First a flat square.", "Changed 2D narration."), encoding="utf-8")
    c = tmp_path / "c.py"
    c.write_text(LESSON_3D.replace("SIZE = 1.2", "SIZE = 1.5"), encoding="utf-8")
    assert uses_blender(a)
    assert blender_source(a) == blender_source(b)          # 2D edit: 3D clip stays cached
    assert blender_source(a) != blender_source(c)          # 3D code/constant edit: re-render


@needs_blender
def test_mixed_lesson_renders_blender_section_in_place(lesson3d, voices, tone_engine, tmp_path):
    settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}, "blender": {"engine": "WORKBENCH", "samples": 1}})
    gen = make_generator(lesson3d, voices, tone_engine, tmp_path / "cache")
    gen.settings = settings
    report = gen.run()

    timeline = json.loads((lesson3d / "generated" / "timeline.json").read_text())
    [segment] = timeline["blender"]
    assert segment["scene_class"] == "Spin" and segment["section"] == "solid"
    assert [s.get("engine", "MANIM") for s in timeline["sections"]] == ["MANIM", "BLENDER", "MANIM"]
    solid = next(n for n in timeline["narrations"] if n["id"] == "solid_01")
    assert abs(segment["start_frame"] / timeline["fps"] - solid["start"]) < 0.1     # starts with its narration

    video = lesson3d / "output" / f"{lesson3d.name}_preview.mp4"
    frames = subprocess.run([ffprobe_path(), "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                             "stream=nb_read_frames", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    assert int(frames) == round(timeline["duration"] * timeline["fps"])            # frame-exact splice
    assert report.outputs["video"]

    again = make_generator(lesson3d, voices, tone_engine, tmp_path / "cache")
    again.settings = settings
    report = again.run()
    assert report.status["Manim"].startswith("Rendered: 0")                        # everything cached


@needs_blender
def test_missing_blender_scene_class_is_reported(lesson3d, voices, tone_engine, tmp_path):
    (lesson3d / "animation.py").write_text(LESSON_3D.replace("self.blender(Spin", "self.blender('Nope'"),
                                           encoding="utf-8")
    gen = make_generator(lesson3d, voices, tone_engine, tmp_path / "cache")
    gen.settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}, "blender": {"engine": "WORKBENCH", "samples": 1}})
    with pytest.raises(LMSError, match="Nope"):
        gen.run()


def test_manim_only_lessons_are_unchanged(tmp_path, voices, tone_engine):
    from tests.test_pipeline import LESSON

    folder = tmp_path / f"manim_only_{uuid.uuid4().hex[:8]}"
    folder.mkdir()
    (folder / "animation.py").write_text(LESSON, encoding="utf-8")
    try:
        gen = make_generator(folder, voices, tone_engine, tmp_path / "cache")
        assert gen._blender_key() == {}                                             # render cache key as before
        gen.run()
        timeline = json.loads((folder / "generated" / "timeline.json").read_text())
        assert "blender" not in timeline and all("engine" not in s for s in timeline["sections"])
    finally:
        shutil.rmtree(MEDIA_DIR / f"{folder.name}_narrated", ignore_errors=True)
