"""Job-side stand-ins for the TTS engine and the WhisperX aligner.

A job process gives these to the (unchanged) ``VideoGenerator``: the
generator calls ``synthesize()`` / ``align()`` exactly as before, and the work
is done by the shared speech service (``backend.speech_service``), so the job
process itself never loads a model. Cache keys are unchanged: the fingerprint
is the real engine's.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from src.audio.tts_engine import TTSEngine, engine_fingerprint
from src.audio.voice_manager import VoiceProfile
from src.utils.errors import LMSError

SPEECH_URL_ENV = "LMS_SPEECH_URL"


def _post(url: str, path: str, body: dict) -> dict:
    request = urllib.request.Request(url + path, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=None) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as err:
        try:
            body = json.loads(err.read())
        except ValueError:
            body = {}
        raise LMSError(body.get("error") or f"Speech service error ({err.code})", body.get("hint")) from err
    except urllib.error.URLError as err:
        raise LMSError("The shared speech service is not reachable.",
                       "It is started by the API (npm run backend); restart the API and generate again.") from err


class RemoteTTSEngine(TTSEngine):
    def __init__(self, url: str, engine_name: str, job_id: str = ""):
        self.url = url
        self.name = engine_name
        self.job_id = job_id

    def synthesize(self, text: str, voice: VoiceProfile, language: str, out_path: Path) -> None:
        reply = _post(self.url, "/synthesize", {
            "job": self.job_id, "text": text, "language": language, "out": str(Path(out_path).resolve()),
            "voice": {"id": voice.id, "name": voice.name, "language": voice.language,
                      "samples": [str(Path(s).resolve()) for s in voice.samples]},
        })
        self.last_check = reply.get("check")     # same meaning as XTTSEngine.last_check

    def fingerprint(self) -> str:
        # Same as the generator uses for its own engine, so every cached clip still matches.
        return engine_fingerprint(self.name)

    def voice_fingerprint(self, voice_id: str) -> str:
        return engine_fingerprint(self.name, voice_id=voice_id)


class RemoteAligner:
    """Same ``align()`` as ``src.subtitles.whisper_alignment.Aligner``."""

    def __init__(self, url: str, language: str):
        self.url = url
        self.language = language

    def align(self, wav: Path, text: str, duration: float, force: bool = False) -> tuple[dict | None, bool]:
        reply = _post(self.url, "/align", {"wav": str(Path(wav).resolve()), "text": text, "duration": duration,
                                           "force": force, "language": self.language})
        return reply["alignment"], bool(reply["fromCache"])


def speech_url() -> str | None:
    return os.environ.get(SPEECH_URL_ENV) or None
