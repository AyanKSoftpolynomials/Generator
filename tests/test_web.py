"""Web control panel: per-block voice assignments, progress events and the API layer."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import lessons
from scripts.generate_video import main as cli_main
from tests.test_pipeline import LESSON, lesson, make_generator  # noqa: F401  (fixture re-export)


def test_voice_assignments_override_only_the_chosen_blocks(lesson, voices, tone_engine, tmp_path):  # noqa: F811
    gen = make_generator(lesson, voices, tone_engine, tmp_path / "cache",
                         voice_assignments={"intro_01": "student_a", "dialogue_03": "teacher_a", "nope": "teacher_b"})
    report = gen.run()
    script = json.loads((lesson / "generated" / "script.json").read_text())
    voices_used = {n["id"]: (n["voice"], n["voice_source"]) for n in script["narration"]}
    assert voices_used["intro_01"] == ("student_a", "assigned")          # overridden
    assert voices_used["dialogue_03"] == ("teacher_a", "narration")      # same as animation.py: untouched
    assert voices_used["dialogue_01"] == ("teacher_b", "scene")          # not assigned: hierarchy as before
    assert tone_engine.calls[0][0] == "student_a"
    assert any("unknown narration 'nope'" in w for w in report.warnings)
    # animation.py itself is never rewritten
    assert (lesson / "animation.py").read_text(encoding="utf-8") == LESSON


def test_changing_one_assignment_regenerates_only_that_clip(lesson, voices, tone_engine, tmp_path):  # noqa: F811
    make_generator(lesson, voices, tone_engine, tmp_path / "cache").run()
    tone_engine.calls.clear()
    report = make_generator(lesson, voices, tone_engine, tmp_path / "cache",
                            voice_assignments={"dialogue_01": "student_a"}).run()
    assert report.generated == ["dialogue_01"]
    assert sorted(report.cached) == ["dialogue_02", "dialogue_03", "intro_01"]
    assert tone_engine.calls == [("student_a", "What shape is it?")]


def test_progress_events_cover_every_stage(lesson, voices, tone_engine, tmp_path):  # noqa: F811
    events = []
    gen = make_generator(lesson, voices, tone_engine, tmp_path / "cache")
    gen.progress = events.append
    gen.run()
    starts = [e["stage"] for e in events if e["kind"] == "stage_start"]
    ends = [e["stage"] for e in events if e["kind"] == "stage_end"]
    assert starts == ends == ["Script", "TTS", "WhisperX", "Manim", "Subtitles", "FFmpeg"]
    tts = [e for e in events if e["kind"] == "progress" and e["stage"] == "TTS"]
    assert (tts[-1]["done"], tts[-1]["total"]) == (4, 4)
    # scene markers printed by LMSScene while Manim renders
    scenes = [e["scene"] for e in events if e["kind"] == "progress" and e["stage"] == "Manim" and "scene" in e]
    assert scenes == ["intro", "dialogue"]
    caches = {e["stage"]: e for e in events if e["kind"] == "cache"}
    assert caches["TTS"]["generated"] == 4 and caches["FFmpeg"]["generated"] == 1


def test_cli_assign_flag_validates_format(capsys):
    with pytest.raises(SystemExit):
        cli_main(["lessons/whatever", "--assign", "missing_equals_sign"])
    assert "ID=VOICE" in capsys.readouterr().err


# ---------------------------------------------------------------- API layer

@pytest.fixture
def client():
    from backend.app import app

    return TestClient(app)


def test_slugify():
    assert lessons.slugify("  Integers ") == "integers"
    assert lessons.slugify("Whole Numbers: Part 2!") == "whole_numbers_part_2"
    with pytest.raises(lessons.InputError):
        lessons.slugify("!!!")


def test_write_animation_keeps_unchanged_files_and_backs_up_changes(tmp_path, monkeypatch):
    monkeypatch.setattr(lessons, "LESSONS_DIR", tmp_path)
    path = lessons.write_animation("demo", "print('a')\r\n")
    assert path.read_bytes() == b"print('a')\n"
    mtime = path.stat().st_mtime_ns
    lessons.write_animation("demo", "﻿print('a')\n")          # same content: not rewritten
    assert path.stat().st_mtime_ns == mtime
    lessons.write_animation("demo", "print('b')\n")
    assert path.read_text() == "print('b')\n"
    assert (tmp_path / "demo" / "generated" / "animation.previous.py").read_text() == "print('a')\n"


def test_analyze_rejects_bad_source_before_running_it(client):
    r = client.post("/api/analyze", json={"animation": "class X(:\n  pass", "lessonName": "t"})
    assert r.status_code == 400 and r.json()["line"] == 1 and "syntax" in r.json()["error"].lower()
    r = client.post("/api/analyze", json={"animation": "x = 1\n", "lessonName": "t"})
    assert r.status_code == 400 and "No narrated scene" in r.json()["error"]
    r = client.post("/api/analyze", json={"animation": "   ", "lessonName": "t"})
    assert r.status_code == 400


def test_analyze_detects_narration(client):
    r = client.post("/api/analyze", json={"animation": LESSON, "lessonName": "Web Test Lesson"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["lessonId"] == "web_test_lesson"
    assert [n["id"] for n in body["narrations"]] == ["intro_01", "dialogue_01", "dialogue_02", "dialogue_03"]
    assert [n["voice"] for n in body["narrations"]] == ["teacher_a", "teacher_b", "student_a", "teacher_a"]
    assert [s["id"] for s in body["scenes"]] == ["intro", "dialogue"]
    assert not (lessons.LESSONS_DIR / "web_test_lesson").exists()     # analysis never touches lessons/


def test_generate_validates_voices_and_lesson(client):
    r = client.post("/api/generate", json={"lessonName": "t", "animation": LESSON, "voiceAssignments": {"intro_01": "ghost"}})
    assert r.status_code == 400 and "ghost" in r.json()["error"]
    r = client.post("/api/generate", json={"lessonName": "", "animation": LESSON})
    assert r.status_code == 400


def test_voices_and_unknown_job(client):
    voices = client.get("/api/voices").json()["voices"]
    assert voices and {"id", "name", "category", "language", "preview", "referenceAudioFiles"} <= set(voices[0])
    first = voices[0]
    audio = client.get(first["preview"])
    assert audio.status_code == 200 and audio.headers["content-type"].startswith("audio/")
    assert client.get("/api/voices/../settings/preview").status_code == 404
    assert client.get("/api/generate/doesnotexist/status").status_code == 404


# ------------------------------------------------ pasted-lesson compatibility

def test_voice_aliases_map_short_names_to_library_voices():
    from src.script.parser import parse_extracted

    raw = {"lesson": {"default_voice": "student"},
           "narration": [{"id": "a", "text": "Hi.", "voice": "teacher"}, {"id": "b", "text": "Yo.", "voice": None}]}
    script = parse_extracted(raw, "demo", "teacher_a", {"teacher": "teacher_a", "student": "student_a"})
    assert [n.voice for n in script.narration] == ["teacher_a", "teacher_a"]   # b: no lesson voice recorded -> global
    assert script.default_voice == "student_a"


def test_lms_video_generator_core_import_alias():
    from lms_video_generator.core import LMSScene
    from src.animation import LMSMovingCameraScene

    assert LMSScene is LMSMovingCameraScene


def test_manim_failure_puts_the_exception_and_line_first(tmp_path):
    from src.animation.manim_engine import manim_failure

    anim = tmp_path / "animation.py"
    anim.write_text("from manim import *\nfrom lms_video_generator.corez import LMSScene\n", encoding="utf-8")
    output = ('Traceback (most recent call last):\n  File "x.py", line 5, in main\n'
              f'  File "{anim}", line 2, in <module>\n    from lms_video_generator.corez import LMSScene\n'
              "ModuleNotFoundError: No module named 'lms_video_generator.corez'\n")
    err = manim_failure(output, anim, "reading the narration from animation.py", tmp_path / "log.txt")
    assert "ModuleNotFoundError: No module named 'lms_video_generator.corez'" in err.message
    assert "animation.py line 2:  from lms_video_generator.corez import LMSScene" in err.message
    assert err.line == 2 and "Manim output (last lines):" in err.fix


# ------------------------------------------------------------ voice uploads

@pytest.fixture
def upload_client(tmp_path, monkeypatch, voices):
    import backend.app as app_module
    import backend.voice_upload as upload_module

    monkeypatch.setattr(app_module, "voices", voices)                 # temporary library, never assets/voices
    monkeypatch.setattr(upload_module, "DELETED_DIR", tmp_path / "deleted")
    return TestClient(app_module.app), voices


def _upload(client, path, name="Priya Maths", consent=True, **extra):
    fields = {"name": name, "speaker": "Priya Sharma", "language": "en", "gender": "female",
              "category": "teacher", "description": "calm", "consent": str(consent).lower(), **extra}
    with open(path, "rb") as f:
        return client.post("/api/voices", data=fields, files={"file": (path.name, f, "application/octet-stream")})


def test_upload_voice_registers_it_like_any_other_voice(upload_client, tmp_path):
    import soundfile as sf
    from tests.conftest import write_tone

    client, vm = upload_client
    r = _upload(client, write_tone(tmp_path / "priya.wav", 7.0, rate=44100))
    assert r.status_code == 200, r.text
    voice = r.json()["voice"]
    assert voice["id"] == "priya_maths" and voice["speaker"] == "Priya Sharma" and voice["uploaded"]
    profile = vm.get("priya_maths")
    info = sf.info(str(profile.samples[0]))
    assert (info.channels, info.samplerate) == (1, 24000)            # converted for XTTS
    assert profile.extra["consent_confirmed"] and profile.extra["source"] == "upload"
    assert vm.validate("priya_maths")[0] == []                      # usable by the generator
    # same name again: a new id, the first voice is untouched
    r2 = _upload(client, write_tone(tmp_path / "again.wav", 7.0))
    assert r2.json()["voice"]["id"] == "priya_maths_2"
    assert client.get("/api/voices").json()["voices"]


@pytest.mark.parametrize("case, expected", [
    ("bad_ext", "Unsupported file type"),
    ("short", "only 1.0s long"),
    ("silent", "silent"),
    ("no_consent", "permission"),
    ("not_audio", "could not be read as audio"),
])
def test_upload_voice_rejects_bad_input(upload_client, tmp_path, case, expected):
    import numpy as np
    import soundfile as sf
    from tests.conftest import write_tone

    client, vm = upload_client
    kwargs = {}
    if case == "bad_ext":
        path = tmp_path / "notes.txt"
        path.write_text("hello")
    elif case == "short":
        path = write_tone(tmp_path / "short.wav", 1.0)
    elif case == "silent":
        path = tmp_path / "silent.wav"
        sf.write(str(path), np.zeros(24000 * 5, dtype="float32"), 24000)
    elif case == "no_consent":
        path, kwargs = write_tone(tmp_path / "ok.wav", 5.0), {"consent": False}
    else:
        path = tmp_path / "fake.mp3"
        path.write_bytes(b"this is not audio" * 100)
    r = _upload(client, path, **kwargs)
    assert r.status_code == 400 and expected in r.json()["error"], r.text
    assert not any(vm.get(v).extra.get("source") == "upload" for v in vm.list_ids())


def test_delete_voice_rules(upload_client, tmp_path, monkeypatch):
    import backend.voice_upload as upload_module
    from tests.conftest import write_tone

    client, vm = upload_client
    voice_id = _upload(client, write_tone(tmp_path / "v.wav", 6.0)).json()["voice"]["id"]
    assert client.delete("/api/voices/teacher_a").status_code == 400          # built-in: protected
    monkeypatch.setattr(upload_module, "voice_usage", lambda v: ["lesson 'integers' (hook_main)"])
    r = client.delete(f"/api/voices/{voice_id}")
    assert r.status_code == 400 and "integers" in r.json()["detail"]         # in use: kept
    monkeypatch.setattr(upload_module, "voice_usage", lambda v: [])
    assert client.delete(f"/api/voices/{voice_id}").status_code == 200
    assert not vm.exists(voice_id) and any((tmp_path / "deleted").iterdir())  # moved, recoverable


# ------------------------------------------------------ concurrent job workspaces

def test_concurrent_jobs_are_isolated_and_publish_cleanly(tmp_path, monkeypatch, voices, tone_engine):
    import hashlib
    import threading

    from backend import lessons as lessons_module
    from backend import workspace
    from src.audio.audio_cache import AudioCache
    from src.config.settings import DEFAULTS, deep_merge
    from src.pipeline.generator import GenerateOptions, VideoGenerator

    monkeypatch.setattr(lessons_module, "LESSONS_DIR", tmp_path / "lessons")
    monkeypatch.setattr(workspace, "MEDIA_DIR", tmp_path / "media")
    settings = deep_merge(DEFAULTS, {"alignment": {"enabled": False}})
    cache = AudioCache(tmp_path / "audio_cache")

    def generate(folder, media, **options):
        return VideoGenerator(folder, GenerateOptions(lesson_name="demo", media_dir=media, **options), settings=settings,
                              voices=voices, cache=cache, engine=tone_engine, log=lambda *_: None).run()

    # the lesson's first build, the ordinary way (as python generate.py does)
    lesson = lessons_module.lesson_dir("demo")
    lesson.mkdir(parents=True)
    (lesson / "animation.py").write_text(LESSON, encoding="utf-8")
    generate(lesson, workspace.lesson_media_dir("demo"))
    shared = {p: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in workspace.lesson_media_dir("demo").rglob("*") if p.is_file()}

    # two jobs on the SAME lesson, at the same time, with different voices
    jobs = {"a": {"intro_01": "student_a"}, "b": {"intro_01": "teacher_b"}}
    folders = {name: tmp_path / "jobs" / name for name in jobs}
    media = {name: workspace.seed(folders[name], "demo", LESSON, "low") for name in jobs}
    reports, errors = {}, []

    def run(name):
        try:
            reports[name] = generate(folders[name], media[name], voice_assignments=jobs[name])
        except Exception as err:  # pragma: no cover - reported below
            errors.append(err)

    threads = [threading.Thread(target=run, args=(n,)) for n in jobs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors

    for name, voice in (("a", "student_a"), ("b", "teacher_b")):
        out = folders[name] / "output" / "demo_preview.mp4"                  # lesson id, not the job folder name
        assert out.exists() and Path(reports[name].outputs["video"]) == out
        script = json.loads((folders[name] / "generated" / "script.json").read_text())
        assert script["narration"][0]["voice"] == voice                       # each job kept its own choice
        assert reports[name].generated == ["intro_01"]                        # the rest came from the cache
    # the lesson's shared Manim files were read, never modified
    for path, digest in shared.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path

    workspace.publish(folders["a"], "demo", LESSON)
    workspace.publish(folders["b"], "demo", LESSON)                           # last finished wins
    script = json.loads((lesson / "generated" / "script.json").read_text())
    assert script["narration"][0]["voice"] == "teacher_b"
    meta = json.loads((lesson / "generated" / "manim" / "low" / "render.meta.json").read_text())
    assert Path(meta["video"]).is_relative_to(workspace.lesson_media_dir("demo")) and Path(meta["video"]).exists()

    # a third job with the same input as the published one is fully cached
    folder_c = tmp_path / "jobs" / "c"
    report = generate(folder_c, workspace.seed(folder_c, "demo", LESSON, "low"), voice_assignments=jobs["b"])
    assert report.generated == [] and report.status["Manim"].startswith("Rendered: 0")
    assert report.status["FFmpeg"] == "Cached"


def test_manim_runs_never_share_the_global_latex_folder(tmp_path, monkeypatch, lesson, voices, tone_engine):  # noqa: F811
    """Concurrent analyses/jobs broke when they shared output/media/Tex: Manim deletes the
    non-SVG LaTeX files there after every formula, i.e. the files of the other runs."""
    import backend.analysis as analysis
    from src.config.settings import DEFAULTS, deep_merge
    from src.config.video_config import MEDIA_DIR

    calls = []
    real = analysis.run_manim

    def spy(*args, **kwargs):
        calls.append(kwargs.get("media_dir"))
        return real(*args, **kwargs)

    monkeypatch.setattr(analysis, "ANALYZE_DIR", tmp_path / "analyze")
    monkeypatch.setattr(analysis, "TEX_POOL", tmp_path / "analyze" / "_tex")
    monkeypatch.setattr(analysis, "run_manim", spy)
    analysis.analyze(LESSON, "demo", deep_merge(DEFAULTS, {}), voices)
    assert calls and calls[0] is not None and (tmp_path / "analyze") in Path(calls[0]).parents

    import src.pipeline.generator as generator_module
    monkeypatch.setattr(generator_module, "run_manim", spy)
    calls.clear()
    make_generator(lesson, voices, tone_engine, tmp_path / "cache").run()
    assert calls and all(m is not None and Path(m) != MEDIA_DIR for m in calls)


# ------------------------------------------------------- shared speech service

def test_jobs_share_one_speech_service(tmp_path, voices, tone_engine):
    """Two generator runs at once, both using the shared speech service over HTTP
    (the real handler; a tone engine stands in for the XTTS model)."""
    import threading
    from http.server import ThreadingHTTPServer

    from backend import speech_service
    from backend.speech_client import RemoteAligner, RemoteTTSEngine
    from src.audio.audio_cache import AudioCache
    from src.audio.tts_engine import XTTSEngine
    from src.config.settings import DEFAULTS, deep_merge
    from src.pipeline.generator import GenerateOptions, VideoGenerator
    from src.subtitles.whisper_alignment import estimated_alignment

    class FakeModels(speech_service.SpeechModels):
        def __init__(self):
            super().__init__()
            self._engine = tone_engine          # "loaded once"
            self.aligned = 0

        def align(self, req):
            with self.align_lock:
                self.aligned += 1
                return {"alignment": estimated_alignment(req["text"], float(req["duration"])), "fromCache": False}

    models = FakeModels()
    server = ThreadingHTTPServer(("127.0.0.1", 0), speech_service.make_handler(models))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        remote = RemoteTTSEngine(url, "xtts_v2", "job")
        assert remote.fingerprint() == XTTSEngine().fingerprint()     # cache keys unchanged

        settings = deep_merge(DEFAULTS, {"alignment": {"enabled": True}})
        results, errors = {}, []

        def run(name, voice):
            folder = tmp_path / name
            folder.mkdir()
            (folder / "animation.py").write_text(LESSON, encoding="utf-8")
            gen = VideoGenerator(folder, GenerateOptions(voice_assignments={"intro_01": voice}, lesson_name="shared_demo",
                                                         media_dir=tmp_path / f"media_{name}"),
                                 settings=settings, voices=voices, cache=AudioCache(tmp_path / "cache"),
                                 engine=RemoteTTSEngine(url, "xtts_v2", name), log=lambda *_: None)
            gen.aligner = lambda language: RemoteAligner(url, language)
            try:
                results[name] = gen.run()
            except Exception as err:
                errors.append(err)

        threads = [threading.Thread(target=run, args=a) for a in (("a", "student_a"), ("b", "teacher_b"))]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, errors
        assert all((tmp_path / n / "output" / "shared_demo_preview.mp4").exists() for n in ("a", "b"))
        assert models.served["tts"] == len(tone_engine.calls) >= 5          # every clip went through the service
        assert models.aligned >= 8
    finally:
        server.shutdown()


def test_segment_status_contract():
    from backend.jobs import segment_summary

    segments = [{"segment_id": s, "segment_order": i, "segment_name": s.title(), "status": st}
                for i, (s, st) in enumerate([("hook", "cached"), ("example", "regenerating"), ("summary", "changed"),
                                             ("done", "completed")], 1)]
    summary = segment_summary(segments)
    assert summary["total_segments"] == 4 and summary["cached_segments"] == 1
    assert summary["regenerating_segments"] == 1 and summary["changed_segments"] == 1
    assert summary["completed_segments"] == 1 and summary["failed_segments"] == 0 and summary["queued_segments"] == 0
    assert segment_summary(None) is None
