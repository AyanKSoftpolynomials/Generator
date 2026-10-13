"""One generation job, run in its own process by ``backend.jobs``:

    python -m backend.job_runner <job.json>

Runs the same ``VideoGenerator`` as ``python generate.py`` and reports
progress as JSON lines on stdout (prefixed with ``@@LMS ``). Any other
output (e.g. from the TTS library) is passed through as plain log lines.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

from backend import EVENT_PREFIX as PREFIX  # noqa: E402

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

from backend.speech_client import RemoteAligner, RemoteTTSEngine, speech_url  # noqa: E402
from src.config.settings import load_settings  # noqa: E402
from src.pipeline.generator import GenerateOptions, VideoGenerator, performance_summary  # noqa: E402
from src.utils.errors import LMSError  # noqa: E402


def emit(event: dict) -> None:
    sys.stdout.write(PREFIX + json.dumps(event, default=str) + "\n")
    sys.stdout.flush()


def voice_test(job: dict) -> int:
    """Speak a short sentence with one voice (XTTS clone), for "Test voice".

    Same engine, processing and audio cache as the generator, so a repeated
    test is instant and needs no model load."""
    from src.audio.audio_cache import AudioCache
    from src.audio.audio_processor import normalize
    from src.audio.tts_engine import create_engine, engine_fingerprint
    from src.audio.voice_manager import VoiceManager
    from src.config.settings import load_settings, resolve_device
    from src.config.video_config import PROJECT_ROOT

    try:
        settings = load_settings()
        audio = settings["audio"]
        processing = {k: audio[k] for k in ("sample_rate", "loudness_lufs", "trim_silence")}
        voice = VoiceManager().require(job["voiceId"])
        cache = AudioCache()
        engine_fp = engine_fingerprint(audio["engine"], settings, voice.id)
        key = cache.key(job["text"], voice.fingerprint(), job["language"], engine_fp, processing)
        cached = cache.has(key)
        emit({"kind": "stage_start", "stage": "TTS", "title": "Voice test"})
        if not cached:
            if speech_url():
                engine = RemoteTTSEngine(speech_url(), audio["engine"], job.get("jobId", ""))
            else:
                device = resolve_device(settings["compute"]["device"])
                emit({"kind": "progress", "stage": "TTS", "done": 0, "total": 1,
                      "message": f"Loading the {audio['engine']} model on {device.upper()}"})
                engine = create_engine(audio["engine"], device)
            emit({"kind": "progress", "stage": "TTS", "done": 0, "total": 1, "message": f"Speaking with {voice.name}"})
            raw = cache.staging_path(key, ".raw.wav")
            staged = cache.staging_path(key)
            engine.synthesize(job["text"], voice, job["language"], raw)
            normalize(raw, staged, **processing)
            cache.commit(staged, key)
            raw.unlink(missing_ok=True)
        emit({"kind": "stage_end", "stage": "TTS", "status": "Cached" if cached else "Generated"})
    except LMSError as err:
        emit({"kind": "error", "message": err.message, "hint": err.fix})
        return 1
    except Exception as err:
        emit({"kind": "error", "message": f"{type(err).__name__}: {err}", "hint": None,
              "traceback": traceback.format_exc()})
        return 1
    emit({"kind": "result", "voiceTest": True, "cached": cached,
          "audio": cache.path(key).relative_to(PROJECT_ROOT).as_posix()})
    return 0


def main(job_file: str) -> int:
    job = json.loads(Path(job_file).read_text(encoding="utf-8"))
    if job.get("kind") == "voice_test":
        return voice_test(job)
    options = GenerateOptions(
        quality=job.get("quality", "preview"),
        subtitles=job.get("subtitles"),
        voice_assignments=job.get("voiceAssignments") or None,
        force=bool(job.get("force")),
        # The job builds in its own workspace folder, not lessons/<id>/ (see backend/workspace.py).
        lesson_name=job.get("lessonId") or None,
        media_dir=Path(job["mediaDir"]) if job.get("mediaDir") else None,
    )
    # Speech runs in the API's shared speech service (one model for all jobs),
    # so this process never loads XTTS or WhisperX itself.
    url = speech_url()
    engine = RemoteTTSEngine(url, load_settings()["audio"]["engine"], job.get("jobId", "")) if url else None
    generator = VideoGenerator(
        Path(job["lessonDir"]), options,
        engine=engine,
        log=lambda message="": emit({"kind": "log", "message": str(message)}),
        progress=emit,
    )
    if url:
        aligners: dict = {}
        generator.aligner = lambda language: aligners.setdefault(language, RemoteAligner(url, language))
    try:
        report = generator.run()
    except LMSError as err:
        emit({"kind": "error", "message": err.message, "hint": err.fix, "line": err.line})
        return 1
    except Exception as err:  # unexpected: report with the traceback for developers
        emit({"kind": "error", "message": f"{type(err).__name__}: {err}", "hint": None,
              "traceback": traceback.format_exc()})
        return 1
    emit({
        "kind": "result",
        "title": report.title,
        "outputs": report.outputs,
        "status": report.status,
        "steps": report.steps,
        "generated": report.generated,
        "cached": report.cached,
        "warnings": report.warnings,
        "layout": report.layout,
        "totalSeconds": round(report.total_seconds, 1),
        "summary": performance_summary(report),
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
