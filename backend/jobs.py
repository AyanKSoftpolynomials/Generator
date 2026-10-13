"""Background generation jobs.

Every request gets its own job id and runs as a separate process
(``backend.job_runner``, i.e. the normal ``VideoGenerator``) in its own
workspace folder (``backend/workspace.py``), so jobs never share or
overwrite files and a crash or cancel never affects another job or the API.

Up to ``max_concurrent_jobs`` jobs run at the same time, each as its own OS
process (settings.json > web.max_concurrent_jobs, or the MAX_CONCURRENT_JOBS
environment variable). Further jobs wait in a queue (status "queued", with a
queue position); the browser never blocks.

Speech (XTTS) and word alignment (WhisperX) run in ONE shared speech process
(``backend/speech_service.py``) that loads each model once for all jobs. A job
process therefore needs no model of its own (~150 MB instead of ~2.5 GB), which
is what lets several jobs really run side by side on one machine.
"""

from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from src.config.settings import load_settings
from src.config.video_config import PROJECT_ROOT

from backend import EVENT_PREFIX as PREFIX
from backend import workspace
from backend.speech_client import SPEECH_URL_ENV

JOBS_DIR = PROJECT_ROOT / "cache" / "jobs"
STAGES = ["Script", "TTS", "WhisperX", "Manim", "Subtitles", "FFmpeg"]
# Share of the progress bar per stage (roughly where the time goes on a first build).
WEIGHTS = {"Script": 5, "TTS": 40, "WhisperX": 8, "Manim": 40, "Subtitles": 2, "FFmpeg": 5}
MAX_LOG_LINES = 4000
TERMINAL = {"completed", "failed", "cancelled"}
# Windows: children get their own hidden console instead of inheriting the API's. If the terminal
# that started the API is closed, inherited consoles vanish and every new child dies at start-up
# with 0xC0000142 (exit code 3221225794) before writing a single line.
OWN_CONSOLE = getattr(subprocess, "CREATE_NO_WINDOW", 0)
KEEP_WORKSPACES = 30                 # finished job folders kept on disk (their videos stay playable)


def max_concurrent_jobs() -> int:
    value = os.environ.get("MAX_CONCURRENT_JOBS") or load_settings().get("web", {}).get("max_concurrent_jobs", 2)
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 2


@dataclass
class Job:
    id: str
    lesson_id: str
    lesson_name: str
    request: dict
    status: str = "queued"               # queued / running / completed / failed / cancelled
    stage: str | None = None
    message: str = "Waiting to start"
    created: float = field(default_factory=time.time)
    started: float | None = None
    finished: float | None = None
    stages: dict = field(default_factory=lambda: {s: {"state": "pending"} for s in STAGES})
    logs: list = field(default_factory=list)
    result: dict | None = None
    error: dict | None = None
    version: int = 0
    process: subprocess.Popen | None = None
    queue_position: int | None = None      # 1 = next to start (only while queued)
    downloaded: dict | None = None         # last confirmed complete download of the video (bytes, time)
    cleanup: dict | None = None            # set once the job's generated files were deleted (backend/cleanup.py)
    segments: list | None = None           # per-scene status of an incremental render (generator "segments" events)

    @property
    def progress(self) -> int:
        if self.status == "completed":
            return 100
        total = 0.0
        for stage, weight in WEIGHTS.items():
            info = self.stages[stage]
            if info["state"] in ("done", "skipped"):
                total += weight
            elif info["state"] == "running" and info.get("total"):
                total += weight * min(1.0, info.get("done", 0) / info["total"])
        return int(total * 100 / sum(WEIGHTS.values()))

    def snapshot(self, logs_since: int = 0) -> dict:
        return {
            "jobId": self.id,
            "lessonId": self.lesson_id,
            "lessonName": self.lesson_name,
            "quality": self.request.get("quality"),
            "status": self.status,
            "stage": self.stage,
            "currentStage": self.stage,
            "queuePosition": self.queue_position,
            "pid": self.process.pid if self.process and self.process.poll() is None else None,
            "progress": self.progress,
            "message": self.message,
            "stages": self.stages,
            "created": self.created,
            "started": self.started,
            "finished": self.finished,
            "startedAt": _iso(self.started),
            "completedAt": _iso(self.finished),
            "elapsed": round((self.finished or time.time()) - (self.started or time.time()), 1) if self.started else 0,
            "logCount": len(self.logs),
            "logs": self.logs[logs_since:],
            "error": self.error,
            "result": self.result,
            "downloaded": self.downloaded,
            "cleanup": self.cleanup,
            "segments": self.segments,
            "segmentSummary": segment_summary(self.segments),
            "version": self.version,
        }


class SpeechService:
    """Starts (and restarts, if it died) one shared speech process; hands out its URL."""

    def __init__(self, python: str, threads: int | None = None):
        self.python = python
        self.threads = threads                  # torch CPU threads (None: torch's default, all cores)
        self.process: subprocess.Popen | None = None
        self.url: str | None = None
        self.lock = threading.Lock()

    def ensure(self) -> str | None:
        with self.lock:
            if self.process is not None and self.process.poll() is None and self._healthy():
                return self.url
            port = _free_port()
            env = os.environ.copy()
            env.update({"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"})
            env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(PROJECT_ROOT), env.get("PYTHONPATH")]))
            if self.threads:
                env["OMP_NUM_THREADS"] = env["MKL_NUM_THREADS"] = str(self.threads)
            JOBS_DIR.mkdir(parents=True, exist_ok=True)
            log = (JOBS_DIR.parent / "speech_service.log").open("a", encoding="utf-8")
            self.process = subprocess.Popen([self.python, "-m", "backend.speech_service", "--port", str(port)],
                                            cwd=PROJECT_ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                            stdin=subprocess.DEVNULL, creationflags=OWN_CONSOLE)
            self.url = f"http://127.0.0.1:{port}"
            for _ in range(240):                      # imports torch etc.: a few seconds
                if self.process.poll() is not None:
                    return None
                if self._healthy():
                    return self.url
                time.sleep(0.25)
            return None

    def _healthy(self) -> bool:
        import urllib.request

        try:
            with urllib.request.urlopen(f"{self.url}/health", timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def status(self) -> dict | None:
        import urllib.request

        if not self.url or self.process is None or self.process.poll() is not None:
            return None
        try:
            with urllib.request.urlopen(f"{self.url}/health", timeout=2) as response:
                return {**json.loads(response.read()), "pid": self.process.pid}
        except Exception:
            return None


class SpeechPool:
    """``web.speech_workers`` shared speech processes (default 1); jobs are spread over
    them. Each one holds its own XTTS model (~2.5-3 GB RAM), so more than one only
    pays off with spare RAM (or a GPU) — on one CPU they share the same cores."""

    def __init__(self, python: str, size: int):
        self.size = max(1, size)
        threads = max(1, (os.cpu_count() or 2) // self.size) if self.size > 1 else None
        self.services = [SpeechService(python, threads) for _ in range(self.size)]
        self._next = 0
        self._lock = threading.Lock()

    def ensure(self) -> str | None:
        with self._lock:
            service = self.services[self._next % self.size]
            self._next += 1
        return service.ensure()

    def status(self) -> list[dict]:
        return [s for s in (service.status() for service in self.services) if s]


def speech_workers() -> int:
    value = os.environ.get("SPEECH_WORKERS") or load_settings().get("web", {}).get("speech_workers", 1)
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1


def _free_port() -> int:
    import socket

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class JobManager:
    def __init__(self, python: str = sys.executable, workers: int | None = None):
        self.python = python
        self.workers = workers or max_concurrent_jobs()
        self.jobs: dict[str, Job] = {}
        self.running: dict[str, Job] = {}      # by job id (never one global "current job")
        self.lock = threading.Lock()
        self.queue: queue.Queue[Job] = queue.Queue()
        self.speech = SpeechPool(python, speech_workers())
        self._load_history()
        for n in range(self.workers):
            threading.Thread(target=self._worker, name=f"generation-worker-{n + 1}", daemon=True).start()

    def _load_history(self, keep: int = 50) -> None:
        """Finished jobs survive an API restart (their state.json), so a reloaded
        page can still show the last video instead of 'unknown job'."""
        states = sorted(JOBS_DIR.glob("*/state.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:keep]
        for path in states:
            try:
                snap = json.loads(path.read_text(encoding="utf-8"))
                request = json.loads((path.parent / "job.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if snap.get("status") not in TERMINAL:
                continue
            self.jobs[snap["jobId"]] = Job(
                id=snap["jobId"], lesson_id=snap["lessonId"], lesson_name=snap["lessonName"], request=request,
                status=snap["status"], stage=snap.get("stage"), message=snap.get("message", ""),
                created=snap.get("created") or path.stat().st_mtime, started=snap.get("started"),
                finished=snap.get("finished"), stages=snap.get("stages") or {s: {"state": "pending"} for s in STAGES},
                logs=snap.get("logs") or [], result=snap.get("result"), error=snap.get("error"),
                downloaded=snap.get("downloaded"), cleanup=snap.get("cleanup"), segments=snap.get("segments"),
            )

    # -- public ------------------------------------------------------------

    def submit(self, lesson_id: str, lesson_name: str, lesson_dir: Path, request: dict) -> Job:
        job = Job(id=uuid.uuid4().hex[:12], lesson_id=lesson_id, lesson_name=lesson_name,
                  request={**request, "lessonDir": str(lesson_dir)})
        with self.lock:
            self.jobs[job.id] = job
            waiting = self.queue.qsize() + len(self.running) - self.workers + 1
            self._log(job, f"Job {job.id} queued: {waiting} job(s) ahead ({self.workers} run at a time)"
                      if waiting > 0 else f"Job {job.id} accepted", milestone=True)
            self._update_queue_positions()
        self.queue.put(job)
        return job

    def _update_queue_positions(self) -> None:
        """Call with self.lock held."""
        waiting = sorted((j for j in self.jobs.values() if j.status == "queued"), key=lambda j: j.created)
        for position, job in enumerate(waiting, 1):
            if job.queue_position != position:
                job.queue_position = position
                job.message = f"Queued: position {position} ({self.workers} jobs run at a time)"
                job.version += 1

    def get(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def cancel(self, job_id: str) -> Job | None:
        job = self.jobs.get(job_id)
        if job is None or job.status in TERMINAL:
            return job
        with self.lock:
            if job.status == "queued":
                job.queue_position = None
                self._finish(job, "cancelled", "Cancelled before it started")
                self._update_queue_positions()
                return job
            job.status = "cancelling"
            job.version += 1
        if job.process and job.process.poll() is None:
            _kill_tree(job.process)
        return job

    @property
    def busy(self) -> bool:
        return bool(self.running)

    # -- worker ------------------------------------------------------------

    def _worker(self) -> None:
        while True:
            job = self.queue.get()
            with self.lock:
                if job.status in TERMINAL:
                    continue
                self.running[job.id] = job
                job.queue_position = None
                job.status, job.started, job.message = "running", time.time(), "Preparing the job workspace"
                job.version += 1
                self._update_queue_positions()
            try:
                self._run(job)
            except Exception as err:  # never let the worker thread die
                with self.lock:
                    job.error = {"stage": job.stage, "message": f"Job runner crashed: {err}", "hint": None}
                    self._finish(job, "failed", "Generation failed")
            finally:
                with self.lock:
                    self.running.pop(job.id, None)

    def _run(self, job: Job) -> None:
        folder = JOBS_DIR / job.id
        folder.mkdir(parents=True, exist_ok=True)
        generation = job.request.get("kind") != "voice_test"
        job.request["jobId"] = job.id
        if generation:
            # Private copy of the lesson's last build: this job reads and writes only here.
            settings = load_settings()
            preset = settings["video"]["final_quality" if job.request.get("quality") == "final" else "preview_quality"]
            scenes = workspace.seed(folder, job.lesson_id, job.request["animation"], preset)
            job.request.update(lessonDir=str(folder), mediaDir=str(scenes), lessonId=job.lesson_id)
        self._prune()
        with self.lock:
            if job.status == "cancelling":            # cancelled while the workspace was prepared
                self._finish(job, "cancelled", "Generation cancelled")
                return
        job_file = folder / "job.json"
        job_file.write_text(json.dumps(job.request, indent=2), encoding="utf-8")
        env = os.environ.copy()
        env.update({"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"})
        # Concurrent jobs share the CPU: split its threads instead of oversubscribing it.
        threads = str(max(1, (os.cpu_count() or 2) // self.workers))
        env.setdefault("OMP_NUM_THREADS", threads)
        env.setdefault("MKL_NUM_THREADS", threads)
        with self.lock:
            job.message = "Connecting to the shared speech service"
            job.version += 1
        url = self.speech.ensure()
        if url:
            env[SPEECH_URL_ENV] = url
        else:
            with self.lock:
                self._log(job, "warning: shared speech service unavailable; this job loads its own model",
                          milestone=True)
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(PROJECT_ROOT), env.get("PYTHONPATH")]))
        with self.lock:
            job.message = "Starting generator"
            self._log(job, f"Generator started (job {job.id}; {len(self.running)} of {self.workers} slots in use)",
                      milestone=True)
        flags = (subprocess.CREATE_NEW_PROCESS_GROUP | OWN_CONSOLE) if os.name == "nt" else 0
        job.process = subprocess.Popen(
            [self.python, "-m", "backend.job_runner", str(job_file)], cwd=PROJECT_ROOT, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            creationflags=flags, stdin=subprocess.DEVNULL,   # own pipes; never the API's console
        )
        with (folder / "output.log").open("w", encoding="utf-8") as raw_log:
            for line in job.process.stdout:
                raw_log.write(line)
                line = line.rstrip("\r\n")
                with self.lock:
                    if line.startswith(PREFIX):
                        try:
                            self._on_event(job, json.loads(line[len(PREFIX):]))
                        except json.JSONDecodeError:
                            self._log(job, line)
                    elif line.strip():
                        self._log(job, line)
        code = job.process.wait()
        if generation and job.status != "cancelling" and job.result is not None and code == 0:
            try:   # the finished build becomes the lesson's current one (for the next job and the CLI)
                workspace.publish(folder, job.lesson_id, job.request["animation"])
            except Exception as err:
                with self.lock:
                    self._log(job, f"warning: could not update lessons/{job.lesson_id} ({err}); "
                              "the video in this job is fine", milestone=True)
        with self.lock:
            if job.status == "cancelling":
                self._finish(job, "cancelled", "Generation cancelled")
            elif job.result is not None and code == 0:
                self._finish(job, "completed", "Video ready")
            else:
                if job.error is None:
                    job.error = {"stage": job.stage, "message": f"The generator stopped unexpectedly (exit code {code}).",
                                 "hint": "See the generation log for details."}
                self._finish(job, "failed", "Generation failed")
        (folder / "state.json").write_text(json.dumps(job.snapshot(), indent=2, default=str), encoding="utf-8")

    def save_state(self, job: Job) -> None:
        """Rewrite a finished job's state.json (after a download, upload or cleanup was recorded)."""
        folder = JOBS_DIR / job.id
        if folder.is_dir():
            with self.lock:
                snapshot = job.snapshot()
            (folder / "state.json").write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    def _prune(self) -> None:
        """Keep the newest KEEP_WORKSPACES finished job folders; never touch active jobs."""
        with self.lock:
            active = {j.id for j in self.jobs.values() if j.status not in TERMINAL}
        folders = sorted((p for p in JOBS_DIR.iterdir() if p.is_dir() and p.name not in active),
                         key=lambda p: p.stat().st_mtime, reverse=True)
        for old in folders[KEEP_WORKSPACES:]:
            shutil.rmtree(old, ignore_errors=True)
            with self.lock:
                self.jobs.pop(old.name, None)

    # -- events from the generator -------------------------------------------

    def _on_event(self, job: Job, event: dict) -> None:
        kind = event.get("kind")
        stage = event.get("stage")
        info = job.stages.get(stage) if stage else None
        if kind == "log":
            self._log(job, event.get("message", ""))
        elif kind == "stage_start" and info is not None:
            info.update(state="running", started=time.time())
            job.stage, job.message = stage, _STAGE_TEXT.get(stage, stage)
            self._log(job, f"{_STAGE_NAMES.get(stage, stage)} started", milestone=True)
        elif kind == "stage_end" and info is not None:
            info.update(state="done", seconds=event.get("seconds"), status=event.get("status"))
            info.pop("started", None)
            self._log(job, f"{_STAGE_NAMES.get(stage, stage)} completed ({event.get('seconds', 0):.1f}s)", milestone=True)
        elif kind == "stage_failed" and info is not None:
            info["state"] = "failed"
        elif kind == "progress" and info is not None:
            info.update(done=event.get("done", 0), total=event.get("total", 0))
            job.message = event.get("message") or job.message
            if stage == "Manim" and event.get("scene"):
                self._log(job, job.message, milestone=True)
        elif kind == "cache" and info is not None:
            info["cache"] = {k: v for k, v in event.items() if k not in ("kind", "stage")}
        elif kind == "segments":
            job.segments = event.get("segments") or []
            summary = segment_summary(job.segments)
            running = [s["segment_name"] for s in job.segments if s["status"] == "regenerating"]
            if running:
                self._log(job, f"Regenerating: {', '.join(running)} ({summary['cached_segments']} of "
                          f"{summary['total_segments']} scenes reused)", milestone=True)
        elif kind == "script":
            self._log(job, "Animation validated", milestone=True)
            self._log(job, f"Found {event.get('narrations', 0)} narration blocks in {event.get('scenes', 0)} scenes",
                      milestone=True)
            assigned = job.request.get("voiceAssignments") or {}
            if assigned:
                self._log(job, f"Voice assignments loaded ({len(assigned)} blocks)", milestone=True)
        elif kind == "validation":
            counts = event.get("summary") or {}
            if counts.get("ERROR") or counts.get("WARNING"):
                self._log(job, f"Layout check: {counts.get('ERROR', 0)} error(s), {counts.get('WARNING', 0)} warning(s)",
                          milestone=True)
            else:
                self._log(job, "Layout check passed", milestone=True)
        elif kind == "error":
            job.error = {"stage": job.stage, "message": event.get("message"), "hint": event.get("hint"),
                         "traceback": event.get("traceback")}
            self._log(job, f"ERROR: {event.get('message')}", milestone=True)
        elif kind == "result":
            job.result = event
            for name in STAGES:
                if job.stages[name]["state"] == "pending":
                    job.stages[name]["state"] = "skipped"
        job.version += 1

    # -- helpers -------------------------------------------------------------

    def _log(self, job: Job, message: str, milestone: bool = False) -> None:
        for line in str(message).splitlines() or [""]:
            job.logs.append({"t": time.time(), "message": _public(line), "milestone": milestone})
        del job.logs[:-MAX_LOG_LINES]
        job.version += 1

    def _finish(self, job: Job, status: str, message: str) -> None:
        job.status, job.message, job.finished = status, message, time.time()
        if status == "completed":
            self._log(job, "Video ready", milestone=True)
        elif status == "cancelled":
            self._log(job, message, milestone=True)
        job.version += 1


_STAGE_NAMES = {"Script": "Validation", "TTS": "TTS", "WhisperX": "WhisperX", "Manim": "Manim",
                "Subtitles": "Subtitles", "FFmpeg": "FFmpeg composition"}
_STAGE_TEXT = {"Script": "Validating animation.py", "TTS": "Generating narration audio",
               "WhisperX": "Aligning words with WhisperX", "Manim": "Rendering animation",
               "Subtitles": "Writing subtitles", "FFmpeg": "Composing the final video"}


SEGMENT_STATUSES = ("cached", "changed", "queued", "regenerating", "completed", "failed")


def segment_summary(segments: list | None) -> dict | None:
    """Counts per segment status, e.g. {"total_segments": 10, "cached_segments": 9, "changed_segments": 1, ...}."""
    if segments is None:
        return None
    counts = {f"{status}_segments": 0 for status in SEGMENT_STATUSES}
    for segment in segments:
        key = f"{segment.get('status')}_segments"
        if key in counts:
            counts[key] += 1
    return {"total_segments": len(segments), **counts}


def _iso(t: float | None) -> str | None:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t)) if t else None


def _public(text: str) -> str:
    """Hide the machine's folder layout: show paths relative to the project."""
    root = str(PROJECT_ROOT)
    return text.replace(root + os.sep, "").replace(root.replace("\\", "/") + "/", "").replace(root, ".")


def _kill_tree(process: subprocess.Popen) -> None:
    """Stop the job and its children (Manim, FFmpeg, TTS workers)."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(process.pid)], capture_output=True)
    else:
        process.kill()
