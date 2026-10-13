"""Worker process for parallel speech generation (``--workers N``).

XTTS inference is not thread-safe, so each worker is a separate process that
loads its own model once (in ``init``) and then synthesises many clips.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

_engine = None


def init(engine_name: str, device: str, threads: int) -> None:
    """Runs once per worker process: pin CPU threads, create the engine (model loads lazily)."""
    global _engine
    import torch

    torch.set_num_threads(max(1, threads))
    from src.audio.tts_engine import create_engine

    _engine = create_engine(engine_name, device)


def synthesize(job: dict) -> tuple[str, float]:
    """Generate + normalise one clip. ``job`` holds only picklable values."""
    from src.audio.audio_processor import normalize
    from src.audio.voice_manager import VoiceManager

    started = time.time()
    voice = VoiceManager(Path(job["voices_dir"])).get(job["voice"])
    raw, out = Path(job["raw"]), Path(job["out"])
    _engine.synthesize(job["text"], voice, job["language"], raw)
    staged = Path(job["staged"])            # unique name, then an atomic rename (shared cache)
    normalize(raw, staged, sample_rate=job["sample_rate"], loudness_lufs=job["loudness_lufs"],
              trim_silence=job["trim_silence"])
    os.replace(staged, out)
    raw.unlink(missing_ok=True)
    return job["id"], time.time() - started
