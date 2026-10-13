"""End-to-end: animation.py -> script.json -> audio -> timing -> Manim -> MP4.

Uses the fast tone engine instead of XTTS and estimated word timings instead
of WhisperX so it runs in well under a minute. The real engines are
exercised by the Natural Numbers acceptance run (see README).
"""

import json
import shutil
import subprocess
import textwrap
import uuid

import pytest

from src.audio.audio_cache import AudioCache
from src.config.settings import DEFAULTS, deep_merge
from src.config.video_config import MEDIA_DIR
from src.pipeline.generator import GenerateOptions, VideoGenerator
from src.video.ffmpeg import ffprobe_path, media_duration

LESSON = textwrap.dedent('''
    from manim import *
    from src.animation import LMSScene

    class PipelineTest(LMSScene):
        lesson_title = "Pipeline Test"
        default_voice = "teacher_a"

        def construct(self):
            self.scene_start("intro")
            square = Square()
            n = self.narrate("intro_01", "Hello students, look at this square.")
            self.play_with(n, Create(square))
            self.scene_start("dialogue", voice="teacher_b")
            n = self.narrate("dialogue_01", "What shape is it?", pause_after=0.5)
            self.narrate("dialogue_02", "It is a square!", voice="student_a")
            self.at_word("dialogue_02", "square")
            self.play(square.animate.set_color(YELLOW), run_time=0.3)
            self.narrate("dialogue_03", "Well done.", voice="teacher_a")
''')


def streams(path):
    out = subprocess.run([ffprobe_path(), "-v", "error", "-show_entries",
                          "stream=codec_type", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return sorted(set(out.split()))


@pytest.fixture
def lesson(tmp_path):
    # A unique lesson name gives each test its own Manim media/cache folder,
    # so cache hits come only from runs inside the same test.
    folder = tmp_path / f"pipeline_test_{uuid.uuid4().hex[:8]}"
    folder.mkdir()
    (folder / "animation.py").write_text(LESSON, encoding="utf-8")
    yield folder
    shutil.rmtree(MEDIA_DIR / f"{folder.name}_narrated", ignore_errors=True)


def make_generator(lesson, voices, engine, cache_dir, **options):
    settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}})
    return VideoGenerator(lesson, GenerateOptions(**options), settings=settings, voices=voices,
                          cache=AudioCache(cache_dir), engine=engine, log=lambda *_: None)


def test_full_pipeline_mixed_voices_subtitles_and_cache(lesson, voices, tone_engine, tmp_path):
    report = make_generator(lesson, voices, tone_engine, tmp_path / "cache").run()

    # script.json was generated from animation.py
    script = json.loads((lesson / "generated" / "script.json").read_text())
    assert [(n["id"], n["voice"]) for n in script["narration"]] == [
        ("intro_01", "teacher_a"), ("dialogue_01", "teacher_b"), ("dialogue_02", "student_a"), ("dialogue_03", "teacher_a")]

    # one clip per narration block, each with its own voice
    assert [c[0] for c in tone_engine.calls] == ["teacher_a", "teacher_b", "student_a", "teacher_a"]
    for nid in ("intro_01", "dialogue_01", "dialogue_02", "dialogue_03"):
        assert (lesson / "audio" / f"{nid}.wav").exists()

    # audio drives the timeline: in order, no overlaps, pauses respected
    timing = json.loads((lesson / "generated" / "timing.json").read_text())["narrations"]
    timeline = json.loads((lesson / "generated" / "timeline.json").read_text())
    placed = timeline["narrations"]
    for prev, cur in zip(placed, placed[1:]):
        assert cur["start"] >= prev["end"] - 1e-6
        assert prev["duration"] == timing[prev["id"]]["duration"]
    assert placed[2]["start"] - placed[1]["end"] >= 0.5 - 1 / timeline["fps"]
    assert timeline["duration"] >= placed[-1]["end"]

    # final MP4 has video + audio (+ soft subtitles) and the right length
    video = lesson / "output" / f"{lesson.name}_preview.mp4"
    assert report.outputs["video"].endswith(f"{lesson.name}_preview.mp4")
    assert streams(video) == ["audio", "subtitle", "video"]
    assert media_duration(video) == pytest.approx(timeline["duration"], abs=0.15)
    assert (lesson / "subtitles" / f"{lesson.name}.srt").read_text().startswith("1\n")
    assert (lesson / "subtitles" / f"{lesson.name}.vtt").read_text().startswith("WEBVTT")
    assert len(report.generated) == 4 and report.cached == []

    # second run: nothing regenerated
    tone_engine.calls.clear()
    again = make_generator(lesson, voices, tone_engine, tmp_path / "cache").run()
    assert tone_engine.calls == [] and len(again.cached) == 4


def logged(lines):
    return lambda *parts: lines.append(" ".join(str(p) for p in parts))


def test_unchanged_rerun_skips_every_stage(lesson, voices, tone_engine, tmp_path):
    make_generator(lesson, voices, tone_engine, tmp_path / "cache").run()
    lines = []
    settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}})
    report = VideoGenerator(lesson, GenerateOptions(), settings=settings, voices=voices,
                            cache=AudioCache(tmp_path / "cache"), engine=tone_engine, log=logged(lines)).run()
    text = "\n".join(lines)
    assert "[CACHE HIT] Script extraction" in text
    assert "[CACHE HIT] WhisperX alignment" in text
    assert "[CACHE HIT] Manim scene: intro" in text and "[CACHE HIT] Manim scene: dialogue" in text
    assert "[CACHE HIT] Subtitles" in text and "[CACHE HIT] Final composition" in text
    assert "[CACHE MISS]" not in text
    assert report.status["FFmpeg"] == "Cached"
    assert (lesson / "audio" / "intro_01.meta.json").exists()
    meta = json.loads((lesson / "audio" / "intro_01.meta.json").read_text())
    assert {"input_hash", "text", "voice", "voice_reference_hash", "tts_settings", "duration"} <= set(meta)


def test_changed_narration_regenerates_only_that_clip_and_stays_frame_exact(lesson, voices, tone_engine, tmp_path):
    make_generator(lesson, voices, tone_engine, tmp_path / "cache").run()
    animation = lesson / "animation.py"
    animation.write_text(animation.read_text().replace("What shape is it?", "Which shape do you see here?"))
    tone_engine.calls.clear()
    lines = []
    settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}})
    report = VideoGenerator(lesson, GenerateOptions(), settings=settings, voices=voices,
                            cache=AudioCache(tmp_path / "cache"), engine=tone_engine, log=logged(lines)).run()
    text = "\n".join(lines)
    assert tone_engine.calls == [("teacher_b", "Which shape do you see here?")]
    assert report.generated == ["dialogue_01"] and len(report.cached) == 3
    assert "[CACHE HIT] Manim scene: intro" in text          # earlier scene untouched
    assert "[CACHE MISS] Manim scene: dialogue" in text      # its timing changed
    # Cached + freshly rendered animations still line up with the audio exactly.
    timeline = json.loads((lesson / "generated" / "timeline.json").read_text())
    placed = timeline["narrations"]
    assert all(b["start"] >= a["end"] - 1e-6 for a, b in zip(placed, placed[1:]))
    video = lesson / "output" / f"{lesson.name}_preview.mp4"
    assert media_duration(video) == pytest.approx(timeline["duration"], abs=1.5 / timeline["fps"])


def test_changed_visuals_do_not_regenerate_audio(lesson, voices, tone_engine, tmp_path):
    make_generator(lesson, voices, tone_engine, tmp_path / "cache").run()
    animation = lesson / "animation.py"
    unique = "#%06X" % (abs(hash(str(tmp_path))) % 0xFFFFFF)   # never seen by Manim's cache before
    animation.write_text(animation.read_text().replace("set_color(YELLOW)", f"set_color('{unique}')"))
    tone_engine.calls.clear()
    lines = []
    settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}})
    report = VideoGenerator(lesson, GenerateOptions(), settings=settings, voices=voices,
                            cache=AudioCache(tmp_path / "cache"), engine=tone_engine, log=logged(lines)).run()
    text = "\n".join(lines)
    assert tone_engine.calls == [] and report.generated == []
    assert "[CACHE HIT] WhisperX alignment" in text
    assert "[CACHE HIT] Manim scene: intro" in text and "[CACHE MISS] Manim scene: dialogue" in text
    assert report.status["FFmpeg"] == "Generated"


def test_dry_run_generates_nothing(lesson, voices, tone_engine, tmp_path):
    lines = []
    settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}})
    VideoGenerator(lesson, GenerateOptions(dry_run=True), settings=settings, voices=voices,
                   cache=AudioCache(tmp_path / "cache"), engine=tone_engine, log=logged(lines)).run()
    text = "\n".join(lines)
    assert "[CACHE MISS] TTS: intro_01" in text and "[CACHE MISS] Final composition" in text
    assert tone_engine.calls == []
    assert sorted(p.name for p in lesson.iterdir()) == ["animation.py"]


def test_force_render_refills_the_animation_cache(lesson, voices, tone_engine, tmp_path):
    """--force-render re-renders everything but must leave a usable cache behind."""
    make_generator(lesson, voices, tone_engine, tmp_path / "cache", force_render=True).run()
    animation = lesson / "animation.py"
    animation.write_text(animation.read_text().replace("Well done.", "Well done, everyone, that was great."))
    lines = []
    settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}})
    VideoGenerator(lesson, GenerateOptions(), settings=settings, voices=voices,
                   cache=AudioCache(tmp_path / "cache"), engine=tone_engine, log=logged(lines)).run()
    assert "[CACHE HIT] Manim scene: intro" in "\n".join(lines)


def test_force_tts_regenerates(lesson, voices, tone_engine, tmp_path):
    make_generator(lesson, voices, tone_engine, tmp_path / "cache").run()
    tone_engine.calls.clear()
    report = make_generator(lesson, voices, tone_engine, tmp_path / "cache", force_tts=True).run()
    assert len(tone_engine.calls) == 4 and len(report.generated) == 4


def test_subtitles_disabled_and_voice_override(lesson, voices, tone_engine, tmp_path):
    report = make_generator(lesson, voices, tone_engine, tmp_path / "cache",
                            subtitles=False, voice_override="teacher_b", output_name="no_subs").run()
    assert {c[0] for c in tone_engine.calls} == {"teacher_b"}
    assert not (lesson / "subtitles").exists()
    video = lesson / "output" / "no_subs.mp4"
    assert streams(video) == ["audio", "video"] and "subtitles" not in report.outputs


def test_audio_only_mode(lesson, voices, tone_engine, tmp_path):
    make_generator(lesson, voices, tone_engine, tmp_path / "cache", audio_only=True).run()
    assert (lesson / "audio" / "narration_track.wav").exists()
    assert not (lesson / "output").exists()


def test_visual_only_when_audio_disabled(lesson, voices, tone_engine, tmp_path):
    make_generator(lesson, voices, tone_engine, tmp_path / "cache", audio=False).run()
    assert tone_engine.calls == []
    assert streams(lesson / "output" / f"{lesson.name}_preview.mp4") == ["video"]
