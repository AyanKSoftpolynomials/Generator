"""Content-addressed cache of finished (normalised) narration clips.

The key covers everything that changes the sound: text, voice samples,
language, TTS engine/model and audio processing settings. Change any of them
and the clip is regenerated; change only the animation and it is reused.
"""

from __future__ import annotations

import hashlib
import os
import json
import shutil
import uuid
from pathlib import Path

from src.config.video_config import PROJECT_ROOT

CACHE_DIR = PROJECT_ROOT / "cache" / "audio"


class AudioCache:
    def __init__(self, folder: Path = CACHE_DIR):
        self.folder = Path(folder)

    @staticmethod
    def key(text: str, voice_fingerprint: str, language: str, engine_fingerprint: str, processing: dict) -> str:
        payload = json.dumps(
            {"text": text, "voice": voice_fingerprint, "language": language, "engine": engine_fingerprint,
             "processing": processing},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]

    def path(self, key: str) -> Path:
        return self.folder / f"{key}.wav"

    def has(self, key: str) -> bool:
        return self.path(key).exists()

    def store(self, key: str, wav: Path) -> Path:
        self.folder.mkdir(parents=True, exist_ok=True)
        tmp = self.staging_path(key)
        shutil.copy2(wav, tmp)
        return self.commit(tmp, key)

    # Several generation jobs can share this cache at the same time, so a clip
    # is written under a unique name and then renamed into place (atomic): a
    # reader never sees a half-written file, and two writers never collide.
    def staging_path(self, key: str, suffix: str = ".wav") -> Path:
        folder = self.folder / "tmp"
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{key}.{os.getpid()}.{uuid.uuid4().hex[:8]}{suffix}"

    def commit(self, staged: Path, key: str) -> Path:
        target = self.path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged, target)
        return target
