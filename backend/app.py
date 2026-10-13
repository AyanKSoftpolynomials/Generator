"""HTTP API for the frontend. Start with ``python -m backend`` (127.0.0.1:8765).

    GET  /api/health                      generator status
    GET  /api/voices                      voice library
    GET  /api/voices/{id}/preview         reference/preview sample (audio)
    POST /api/voices                      add a voice from an uploaded recording (multipart)
    DELETE /api/voices/{id}               remove an uploaded voice (only when no lesson uses it)
    POST /api/voices/{id}/test            speak a test sentence with the voice (background job)
    GET  /api/voice-tests/{job}/audio     the test sentence audio
    GET  /api/lessons                     lessons in lessons/
    GET  /api/lessons/{id}                a lesson's animation.py
    GET  /api/lessons/{id}/audio/{nid}    last generated clip of one narration block
    POST /api/analyze                     narration blocks detected in animation.py
    POST /api/generate                    start a generation job -> {"jobId"}
    GET  /api/generate/{job}/status       progress snapshot (poll)
    GET  /api/generate/{job}/events       the same, pushed as Server-Sent Events
    GET  /api/generate/{job}/result       final video info
    GET  /api/generate/{job}/video        the generator's MP4, byte for byte (?download=1)
    POST /api/generate/{job}/cancel
"""

from __future__ import annotations

import asyncio
import json
import tempfile
import threading
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from src.audio.voice_manager import VOICE_ID_PATTERN, VoiceManager
from src.config.settings import load_settings, resolve_device
from src.config.video_config import PROJECT_ROOT
from src.utils.errors import LMSError
from src.video.ffmpeg import ffmpeg_path

from backend import lessons
from backend.analysis import analyze
from backend.jobs import JOBS_DIR, TERMINAL, JobManager, _public
from backend.voice_upload import MAX_UPLOAD_BYTES, delete_voice, import_voice
from backend.voices import describe, list_voices, preview_file
from backend.preferences import PreferenceError
from backend.youtube import YouTubeError
from backend.youtube_api import make_router

app = FastAPI(title="LMS Video Generator API", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

jobs = JobManager()
voices = VoiceManager()
_environment: dict = {}


def _probe_environment() -> None:
    """Slow checks (PyTorch import for the device) run once, in the background."""
    settings = load_settings()
    info = {"engine": settings["audio"]["engine"]}
    try:
        ffmpeg_path()
        info["ffmpeg"] = True
    except LMSError:
        info["ffmpeg"] = False
    try:
        info["device"] = resolve_device(settings["compute"]["device"])
    except LMSError:
        info["device"] = "unavailable"
    _environment.update(info)


threading.Thread(target=_probe_environment, daemon=True).start()


# ------------------------------------------------------------------ errors

@app.exception_handler(lessons.InputError)
async def _input_error(_: Request, err: lessons.InputError):
    return JSONResponse(status_code=400, content={"error": err.message, "detail": err.detail, "line": err.line})


@app.exception_handler(LMSError)
async def _lms_error(_: Request, err: LMSError):
    return JSONResponse(status_code=422, content={"error": _public(err.message), "detail": _public(err.fix or "") or None,
                                                  "line": getattr(err, "line", None)})


@app.exception_handler(YouTubeError)
async def _youtube_error(_: Request, err: YouTubeError):
    status = 409 if err.code in ("not_connected", "channel_mismatch", "channel_unverified", "busy") else 422
    return JSONResponse(status_code=status, content={"error": err.message, "detail": err.hint, "code": err.code})


@app.exception_handler(PreferenceError)
async def _preference_error(_: Request, err: PreferenceError):
    return JSONResponse(status_code=400, content={"error": str(err)})


# Optional YouTube upload, download confirmation and job cleanup (backend/youtube_api.py).
app.include_router(make_router(jobs))


# ------------------------------------------------------------------ status

@app.get("/api/health")
def health():
    with jobs.lock:
        running = list(jobs.running)
    return {
        "status": "ready" if _environment.get("ffmpeg", True) else "degraded",
        "busy": bool(running),
        "running": running,
        "maxConcurrentJobs": jobs.workers,
        "speechServices": jobs.speech.status(),   # the shared XTTS/WhisperX process(es)
        "queued": jobs.queue.qsize(),
        "voices": len(voices.list_ids()),
        **_environment,
    }


# ------------------------------------------------------------------ voices

@app.get("/api/voices")
def get_voices():
    return {"voices": list_voices(voices)}


@app.get("/api/voices/{voice_id}/preview")
def voice_preview(voice_id: str):
    if not VOICE_ID_PATTERN.match(voice_id) or not voices.exists(voice_id):
        raise HTTPException(404, "Unknown voice")
    path = preview_file(voices, voice_id)
    if path is None:
        raise HTTPException(404, "This voice has no preview or reference sample")
    return FileResponse(path, media_type=_audio_type(path), headers={"Cache-Control": "no-cache"})


@app.post("/api/voices")
async def upload_voice(
    file: UploadFile = File(...),
    name: str = Form(...),
    speaker: str = Form(...),
    language: str = Form("en"),
    gender: str = Form(""),
    category: str = Form("teacher"),
    description: str = Form(""),
    consent: bool = Form(False),
):
    """Add a voice from an uploaded recording (see backend/voice_upload.py)."""
    with tempfile.TemporaryDirectory(prefix="lms_upload_") as tmp:
        target = Path(tmp) / f"upload{Path(file.filename or '').suffix.lower()[:8]}"
        size = 0
        with target.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise lessons.InputError(f"The file is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
                                             "Upload a shorter recording (6-30 seconds of speech is ideal).")
                out.write(chunk)
        meta = {"name": name, "speaker": speaker, "language": language, "gender": gender,
                "category": category, "description": description, "consent": consent}
        voice_id = await run_in_threadpool(import_voice, target, file.filename or "", meta, voices)
    return {"voice": describe(voices, voice_id)}


@app.delete("/api/voices/{voice_id}")
def remove_voice(voice_id: str):
    if not VOICE_ID_PATTERN.match(voice_id) or not voices.exists(voice_id):
        raise HTTPException(404, "Unknown voice")
    delete_voice(voice_id, voices)
    return {"deleted": voice_id}


TEST_SENTENCES = {
    "en": "Hello students! This is how I will sound in your lessons. Let's learn something new together today.",
    "hi": "नमस्ते विद्यार्थियों! आपके पाठों में मेरी आवाज़ ऐसी सुनाई देगी। चलिए आज कुछ नया सीखते हैं।",
    "es": "¡Hola, estudiantes! Así sonará mi voz en sus lecciones. Aprendamos algo nuevo hoy.",
    "fr": "Bonjour à tous ! Voici comment ma voix sonnera dans vos leçons. Apprenons quelque chose de nouveau aujourd'hui.",
    "de": "Hallo zusammen! So klingt meine Stimme in euren Lektionen. Lasst uns heute etwas Neues lernen.",
}


class VoiceTestRequest(BaseModel):
    text: str | None = None


@app.post("/api/voices/{voice_id}/test")
def test_voice(voice_id: str, body: VoiceTestRequest):
    """Queue a short XTTS sample in this voice ("Test voice"); poll /api/generate/{jobId}/status."""
    if not VOICE_ID_PATTERN.match(voice_id) or not voices.exists(voice_id):
        raise HTTPException(404, "Unknown voice")
    profile = voices.get(voice_id)
    language = profile.language if profile.language in TEST_SENTENCES or body.text else "en"
    text = (body.text or TEST_SENTENCES.get(language) or TEST_SENTENCES["en"]).strip()
    if not text or len(text) > 400:
        raise lessons.InputError("The test sentence must be 1-400 characters.")
    job = jobs.submit("", f"Voice test: {profile.name}", PROJECT_ROOT,
                      {"kind": "voice_test", "voiceId": voice_id, "text": text, "language": language})
    return {"jobId": job.id, "text": text}


@app.get("/api/voice-tests/{job_id}/audio")
def voice_test_audio(job_id: str):
    job = _job(job_id)
    relative = (job.result or {}).get("audio")
    if job.status != "completed" or not relative:
        raise HTTPException(404, "The voice test is not ready")
    path = (PROJECT_ROOT / relative).resolve()
    if (PROJECT_ROOT / "cache" / "audio").resolve() not in path.parents or not path.exists():
        raise HTTPException(404, "The test audio is missing")
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-cache"})


# ------------------------------------------------------------------ lessons

@app.get("/api/lessons")
def get_lessons():
    return {"lessons": lessons.list_lessons()}


@app.get("/api/lessons/{lesson_id}")
def get_lesson(lesson_id: str):
    try:
        return {"id": lesson_id, "animation": lessons.read_animation(lesson_id)}
    except FileNotFoundError:
        raise HTTPException(404, "Lesson not found") from None


@app.get("/api/lessons/{lesson_id}/audio/{narration_id}")
def narration_clip(lesson_id: str, narration_id: str):
    if not lessons.SLUG_PATTERN.match(narration_id.lower()):
        raise HTTPException(404, "Unknown narration")
    path = lessons.lesson_dir(lesson_id) / "audio" / f"{narration_id}.wav"
    if not path.exists():
        raise HTTPException(404, "No generated audio for this narration yet")
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-cache"})


# ------------------------------------------------------------------ analyze

class AnalyzeRequest(BaseModel):
    animation: str
    lessonName: str | None = None


@app.post("/api/analyze")
def post_analyze(body: AnalyzeRequest):
    slug = lessons.slugify(body.lessonName) if body.lessonName and body.lessonName.strip() else "untitled"
    return analyze(body.animation, slug, load_settings(), voices)


# ------------------------------------------------------------------ generate

class GenerateRequest(BaseModel):
    lessonName: str
    animation: str
    voiceAssignments: dict[str, str] = Field(default_factory=dict)
    quality: str = "preview"             # "preview" (480p) or "final" (settings.json > video.final_quality)
    subtitles: bool | None = None        # None = settings.json / lesson
    force: bool = False                  # ignore every cache (normally never needed)


@app.post("/api/generate")
def post_generate(body: GenerateRequest):
    slug = lessons.slugify(body.lessonName)
    if body.quality not in ("preview", "final"):
        raise lessons.InputError("quality must be 'preview' or 'final'.")
    lessons.check_source(lessons.normalise_source(body.animation))
    for narration_id, voice_id in body.voiceAssignments.items():
        if not VOICE_ID_PATTERN.match(voice_id or "") or not voices.exists(voice_id):
            raise lessons.InputError(f"Unknown voice '{voice_id}' selected for '{narration_id}'.")
        if not describe(voices, voice_id)["usable"]:
            raise lessons.InputError(f"Voice '{voice_id}' has problems and cannot be used.",
                                     "\n".join(describe(voices, voice_id)["problems"]))
    # lessons/<slug>/animation.py is only updated when the job succeeds (backend/workspace.py);
    # the job itself runs on its own copy, so concurrent jobs never touch each other's code.
    job = jobs.submit(slug, body.lessonName.strip(), lessons.lesson_dir(slug), {
        "animation": lessons.normalise_source(body.animation),
        "lessonName": body.lessonName.strip(),
        "voiceAssignments": body.voiceAssignments,
        "quality": body.quality,
        "subtitles": body.subtitles,
        "force": body.force,
    })
    return {"jobId": job.id, "lessonId": slug}


def _job(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "Unknown job (jobs are kept until the API restarts)")
    return job


@app.get("/api/generate/{job_id}/status")
def job_status(job_id: str, logsSince: int = 0):
    job = _job(job_id)
    with jobs.lock:
        return job.snapshot(logs_since=max(0, logsSince))


@app.get("/api/generate/{job_id}/events")
async def job_events(job_id: str, request: Request, logsSince: int = 0):
    job = _job(job_id)

    async def stream():
        version, sent, last_beat = -1, max(0, logsSince), time.time()
        yield "retry: 2000\n\n"
        while not await request.is_disconnected():
            # Send on every change, and at least once a second while running
            # (keeps elapsed time fresh and pushes through proxy buffering).
            if job.version != version or (job.status == "running" and time.time() - last_beat >= 1):
                with jobs.lock:
                    snap = job.snapshot(logs_since=sent)
                version, sent = snap["version"], snap["logCount"]
                yield f"event: status\ndata: {json.dumps(snap, default=str)}\n\n"
                if snap["status"] in TERMINAL:
                    return
                last_beat = time.time()
            elif time.time() - last_beat > 15:
                yield ": keep-alive\n\n"
                last_beat = time.time()
            await asyncio.sleep(0.25)

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"})


@app.get("/api/generate/{job_id}/result")
def job_result(job_id: str):
    job = _job(job_id)
    if job.status != "completed":
        return {"status": job.status, "lesson": job.lesson_name, "error": job.error}
    result = job.result or {}
    return {
        "status": "completed",
        "lesson": job.lesson_name,
        "lessonId": job.lesson_id,
        "title": result.get("title"),
        "videoUrl": f"/api/generate/{job.id}/video",
        "downloadUrl": f"/api/generate/{job.id}/video?download=1",
        "narrationUrl": f"/api/generate/{job.id}/narration" if _narration_track(job) else None,
        "fileName": Path(result.get("outputs", {}).get("video", "")).name,
        "stageStatus": result.get("status"),
        "steps": result.get("steps"),
        "totalSeconds": result.get("totalSeconds"),
        "generated": result.get("generated"),
        "cached": result.get("cached"),
        # Layout issues have their own field (and panel); the rest stay plain warnings.
        "warnings": [w for w in result.get("warnings") or [] if not w.startswith("Layout ")],
        "layout": result.get("layout") or None,
        "summary": result.get("summary"),
        "fileSize": _file_size(job),
        "downloaded": job.downloaded,
        "cleanup": job.cleanup,              # set once this job's generated files were deleted
    }


def _file_size(job) -> int | None:
    relative = (job.result or {}).get("outputs", {}).get("video")
    path = PROJECT_ROOT / relative if relative else None
    return path.stat().st_size if path and path.is_file() else None


@app.get("/api/generate/{job_id}/video")
def job_video(job_id: str, download: bool = False):
    job = _job(job_id)
    relative = (job.result or {}).get("outputs", {}).get("video")
    if job.cleanup:
        raise HTTPException(410, "This job's generated files were deleted after a successful "
                                 f"{job.cleanup.get('after', 'download')}.")
    if job.status != "completed" or not relative:
        raise HTTPException(404, "The video is not ready")
    path = (PROJECT_ROOT / relative).resolve()
    allowed = (lessons.LESSONS_DIR.resolve(), JOBS_DIR.resolve())
    if not any(root in path.parents for root in allowed) or not path.exists():
        raise HTTPException(404, "The video file is missing")
    # FileResponse streams the file as-is (with Range support for seeking): no re-encoding.
    return FileResponse(path, media_type="video/mp4", filename=path.name if download else None,
                        content_disposition_type="attachment" if download else "inline",
                        headers={"Cache-Control": "no-cache"})


@app.get("/api/generate/{job_id}/narration")
def job_narration(job_id: str):
    """The narration track the MP4's audio was encoded from (PCM WAV, plays in
    every browser). The player falls back to it when a browser cannot decode
    the MP4's AAC audio (e.g. some embedded/Electron browsers)."""
    job = _job(job_id)
    if job.status != "completed":
        raise HTTPException(404, "The video is not ready")
    path = _narration_track(job)
    if path is None:
        raise HTTPException(404, "No narration track for this lesson")
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-cache"})


@app.post("/api/generate/{job_id}/cancel")
def job_cancel(job_id: str):
    job = jobs.cancel(_job(job_id).id)
    return {"status": job.status}


def _narration_track(job) -> Path | None:
    """This job's own narration track (its workspace); older jobs built in the lesson folder."""
    for folder in (JOBS_DIR / job.id, lessons.lesson_dir(job.lesson_id)):
        path = folder / "audio" / "narration_track.wav"
        if path.exists():
            return path
    return None


def _audio_type(path: Path) -> str:
    return {".wav": "audio/wav", ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".flac": "audio/flac"}.get(
        path.suffix.lower(), "application/octet-stream")
