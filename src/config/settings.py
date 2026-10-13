"""Project-wide generator settings, read from ``settings.json`` in the project root.

Every key has a default here, so ``settings.json`` only needs the values you
want to change. Lessons can override the subtitle settings (see
``LMSScene.subtitles``) and the CLI can override a few more.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from src.config.video_config import PROJECT_ROOT
from src.utils.errors import LMSError
from src.validation.layout import DEFAULT_CONFIG as VALIDATION_DEFAULTS

SETTINGS_FILE = PROJECT_ROOT / "settings.json"

DEFAULTS: dict = {
    # aliases: short names lessons may use in narrate(voice=...) -> voice library ids
    "voice": {"default": "teacher_a", "aliases": {}},
    "audio": {
        "enabled": True,
        "engine": "xtts_v2",
        "sample_rate": 44100,
        "loudness_lufs": -18,
        "trim_silence": True,
        "pause_after": 0.25,
        # engine "sarvam" (hosted, needs SARVAM_API_KEY in .env): stock speakers, no cloning.
        # voices: voice library id -> Sarvam speaker; other voices use "speaker".
        "sarvam": {"model": "bulbul:v3", "speaker": "shubh", "voices": {}, "pace": 1.0},
    },
    "alignment": {"enabled": True},
    "subtitles": {
        "enabled": True,
        "mode": "sentence",       # "sentence" or "word"
        "formats": ["srt", "vtt"],
        "max_chars": 84,          # longer sentences are split into several cues
        "embed_in_mp4": True,     # soft subtitle track players can toggle
    },
    "video": {"preview_quality": "low", "final_quality": "high"},
    "compute": {"device": "auto"},  # "auto", "cpu" or "cuda"
    # 3D sections (self.blender(...)): path "" = PATH / tools/blender / BLENDER_PATH env;
    # engine "EEVEE" (GPU, fast, good materials), "CYCLES" (CPU, slow, physically based) or "WORKBENCH".
    "blender": {"path": "", "engine": "EEVEE", "samples": 16},
    # web control panel: generation jobs (OS processes) that may run at once; the
    # rest queue. Speech models are shared, so a job needs ~0.3-1 GB RAM (mostly
    # Manim). Env MAX_CONCURRENT_JOBS overrides.
    # speech_workers: shared XTTS/WhisperX processes (each ~3 GB RAM) serving all jobs.
    "web": {"max_concurrent_jobs": 3, "speech_workers": 1},
    # Optional YouTube upload (web panel). The OAuth redirect must be registered exactly like this
    # in your Google Cloud OAuth client ("Authorized redirect URIs"); see README > YouTube.
    "youtube": {"redirect_uri": "http://127.0.0.1:3000/api/youtube/oauth/callback"},
    # layout checks while reading animation.py (text fits its box, stays in frame, no
    # collisions, readable size); thresholds in scene units / font points. See src/validation/.
    "validation": dict(VALIDATION_DEFAULTS),
}


def deep_merge(base: dict, override: dict) -> dict:
    """Return ``base`` with ``override`` merged in (nested dicts merged key by key)."""
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_settings(path: Path = SETTINGS_FILE) -> dict:
    """Defaults merged with ``settings.json`` (if it exists)."""
    if not path.exists():
        return copy.deepcopy(DEFAULTS)
    try:
        user = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LMSError(f"settings.json is not valid JSON: {exc}", f"Fix the syntax in {path}.") from exc
    return deep_merge(DEFAULTS, user)


def resolve_device(requested: str = "auto") -> str:
    """Turn "auto" into "cuda" when an NVIDIA GPU is usable, otherwise "cpu"."""
    if requested not in ("auto", "cpu", "cuda"):
        raise LMSError(f"Unknown compute device '{requested}'.", 'Use "auto", "cpu" or "cuda" in settings.json > compute.device.')
    if requested == "cpu":
        return "cpu"
    try:
        import torch

        has_cuda = torch.cuda.is_available()
    except ImportError:
        has_cuda = False
    if requested == "cuda" and not has_cuda:
        raise LMSError(
            "compute.device is \"cuda\" but no CUDA GPU is available to PyTorch.",
            'Set compute.device to "auto" or "cpu" in settings.json, or install a CUDA build of PyTorch (see README).',
        )
    return "cuda" if has_cuda else "cpu"
