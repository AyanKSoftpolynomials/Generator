"""One shared speech process for all generation jobs.

    python -m backend.speech_service --port 8766      (started by the API)

Loads the XTTS model and the WhisperX alignment model ONCE and serves every
job, instead of each job process loading its own copy (~2.5 GB of RAM each,
kept until the job ends). Requests from different jobs are served one at a
time per model (XTTS is not thread-safe; on a CPU the models would share
the same cores anyway). Speech and alignment have separate locks, so an
alignment never waits behind a synthesis.

The engine and aligner used here are exactly the generator's own
(``create_engine`` / ``Aligner``); jobs reach them through
``backend.speech_client``.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

from src.audio.tts_engine import create_engine  # noqa: E402
from src.audio.voice_manager import VoiceProfile  # noqa: E402
from src.config.settings import load_settings, resolve_device  # noqa: E402
from src.subtitles.whisper_alignment import Aligner  # noqa: E402
from src.utils.errors import LMSError  # noqa: E402


class SpeechModels:
    def __init__(self):
        settings = load_settings()
        self.engine_name = settings["audio"]["engine"]
        self.device = resolve_device(settings["compute"]["device"])
        self.tts_lock = threading.Lock()
        self.align_lock = threading.Lock()
        self._engine = None
        self._aligners: dict[str, Aligner] = {}
        self.waiting = {"tts": 0, "align": 0}
        self.served = {"tts": 0, "align": 0}
        self._count = threading.Lock()

    def _enter(self, kind: str, delta: int) -> None:
        with self._count:
            self.waiting[kind] += delta

    def synthesize(self, req: dict) -> dict:
        voice = VoiceProfile(id=req["voice"]["id"], name=req["voice"]["name"], language=req["voice"]["language"],
                             samples=[Path(s) for s in req["voice"]["samples"]])
        self._enter("tts", 1)
        with self.tts_lock:
            self._enter("tts", -1)
            started = time.time()
            if self._engine is None:
                log(f"loading {self.engine_name} on {self.device.upper()} (once for all jobs)")
                self._engine = create_engine(self.engine_name, self.device)
            self._engine.synthesize(req["text"], voice, req["language"], Path(req["out"]))
            check = getattr(self._engine, "last_check", None)    # speech checked against the text
            self.served["tts"] += 1
            log(f"tts job {req.get('job', '?')}: {len(req['text'])} chars in {time.time() - started:.1f}s"
                + (f" ({check['attempts']} attempts, {'ok' if check['ok'] else 'NOT MATCHING'})"
                   if check and (check["attempts"] > 1 or not check["ok"]) else ""))
        return {"ok": True, "check": check}

    def align(self, req: dict) -> dict:
        self._enter("align", 1)
        with self.align_lock:
            self._enter("align", -1)
            language = req["language"]
            if language not in self._aligners:
                self._aligners[language] = Aligner(language, self.device)
            result, from_cache = self._aligners[language].align(Path(req["wav"]), req["text"], float(req["duration"]),
                                                                force=bool(req.get("force")))
            self.served["align"] += 1
        return {"alignment": result, "fromCache": from_cache}


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def make_handler(models: SpeechModels):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):   # quiet: one line per request is logged by the models
            pass

        def _reply(self, status: int, body: dict) -> None:
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self._reply(200, {"ok": True, "modelLoaded": models._engine is not None, "device": models.device,
                                  "waiting": models.waiting, "served": models.served})
            else:
                self._reply(404, {"error": "not found"})

        def do_POST(self):
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                if self.path == "/synthesize":
                    self._reply(200, models.synthesize(req))
                elif self.path == "/align":
                    self._reply(200, models.align(req))
                else:
                    self._reply(404, {"error": "not found"})
            except LMSError as err:
                self._reply(422, {"error": err.message, "hint": err.fix})
            except Exception as err:
                log(f"error: {err}")
                self._reply(500, {"error": f"{type(err).__name__}: {err}", "traceback": traceback.format_exc()})

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Shared XTTS/WhisperX process for generation jobs")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(SpeechModels()))
    server.daemon_threads = True
    log(f"speech service on 127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
