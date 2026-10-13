"""Add / remove voices from the browser, on top of the existing voice library.

An uploaded recording is converted to a mono WAV with the project's FFmpeg,
checked with the same rules as ``scripts/voice.py add`` (``check_sample``),
and registered with ``VoiceManager.add`` — so it lands in
``assets/voices/<id>/`` with a normal ``voice.json`` and XTTS uses it like
any other voice. Existing voices are never modified: a new upload always
gets a new id.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from src.audio.voice_manager import MIN_SAMPLE_SECONDS, RECOMMENDED_SAMPLE_SECONDS, VoiceManager, check_sample, sample_duration
from src.config.settings import load_settings
from src.config.video_config import PROJECT_ROOT
from src.video.ffmpeg import ffmpeg_path

from backend.lessons import LESSONS_DIR, InputError
from backend.voices import LANGUAGE_NAMES

UPLOAD_FORMATS = {".wav", ".mp3", ".m4a", ".ogg", ".oga", ".flac", ".webm", ".aac", ".opus"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_SECONDS = 5 * 60
SAMPLE_RATE = 24000                 # XTTS resamples references to 22.05 kHz; 24 kHz keeps full detail
DELETED_DIR = PROJECT_ROOT / "cache" / "deleted_voices"
GENDERS = {"", "female", "male", "other"}
CATEGORIES = {"teacher", "student", "narrator", "other"}


def new_voice_id(name: str, manager: VoiceManager) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")[:40].strip("_") or "voice"
    if not base[0].isalpha():
        base = f"voice_{base}"
    voice_id, n = base, 2
    while manager.exists(voice_id) or (manager.voices_dir / voice_id).exists():
        voice_id, n = f"{base}_{n}", n + 1
    return voice_id


def import_voice(upload: Path, filename: str, meta: dict, manager: VoiceManager) -> str:
    """Validate + convert + register one uploaded recording. Returns the new voice id."""
    name = (meta.get("name") or "").strip()
    speaker = (meta.get("speaker") or "").strip()
    language = (meta.get("language") or "").strip()
    gender = (meta.get("gender") or "").strip().lower()
    category = (meta.get("category") or "teacher").strip().lower()
    if not name:
        raise InputError("Enter a voice name.")
    if len(name) > 60 or len(speaker) > 80 or len(meta.get("description") or "") > 300:
        raise InputError("Name (60), speaker (80) or description (300 characters) is too long.")
    if not speaker:
        raise InputError("Enter the speaker's name (the person whose voice this is).")
    if language not in LANGUAGE_NAMES:
        raise InputError(f"Choose a supported language ({', '.join(LANGUAGE_NAMES.values())}).")
    if gender not in GENDERS or category not in CATEGORIES:
        raise InputError("Invalid gender or category.")
    if not meta.get("consent"):
        raise InputError("Confirm that you own this recording or have the speaker's permission to clone their voice.")

    suffix = Path(filename or "").suffix.lower()
    if suffix not in UPLOAD_FORMATS:
        raise InputError(f"Unsupported file type '{suffix or '?'}'.",
                         f"Upload one of: {', '.join(sorted(UPLOAD_FORMATS))}.")
    if upload.stat().st_size == 0:
        raise InputError("The uploaded file is empty.")

    with tempfile.TemporaryDirectory(prefix="lms_voice_") as tmp:
        wav = Path(tmp) / "reference.wav"
        result = subprocess.run(
            [ffmpeg_path(), "-v", "error", "-y", "-i", str(upload), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
             "-c:a", "pcm_s16le", str(wav)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode != 0 or not wav.exists():
            raise InputError("This file could not be read as audio.",
                             "Is it a real, undamaged recording? " + (result.stderr.strip().splitlines() or [""])[-1])
        errors, _ = check_sample(wav)
        if errors:
            raise InputError(errors[0].replace("reference.wav", "The recording"),
                             f"Use a clear recording of at least {RECOMMENDED_SAMPLE_SECONDS:.0f} seconds "
                             f"(minimum {MIN_SAMPLE_SECONDS:.0f} s).")
        seconds = sample_duration(wav)
        if seconds > MAX_SECONDS:
            raise InputError(f"The recording is {seconds / 60:.1f} minutes long (maximum {MAX_SECONDS // 60}).",
                             "6-30 seconds of clear speech is ideal; trim the recording.")
        if _peak_db(wav) < -45:
            raise InputError("The recording is silent (or almost).", "Check the microphone and record again.")

        voice_id = new_voice_id(name, manager)
        manager.add(voice_id, [wav], name=name, language=language, description=(meta.get("description") or "").strip(),
                    extra={
                        "speaker": speaker,
                        "gender": gender or None,
                        "category": category,
                        "source": "upload",
                        "original_file": Path(filename).name[:120],
                        "consent_confirmed": True,
                        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                    })
    return voice_id


def _peak_db(wav: Path) -> float:
    import numpy as np
    import soundfile as sf

    data, _ = sf.read(str(wav), dtype="float32")
    peak = float(np.max(np.abs(data))) if data.size else 0.0
    return 20 * np.log10(peak) if peak > 0 else -120.0


def voice_usage(voice_id: str) -> list[str]:
    """Where a voice is in use: lesson narrations (last generated script) and settings.json."""
    used = []
    settings = load_settings()
    if settings["voice"].get("default") == voice_id:
        used.append("settings.json (default voice)")
    for alias, target in (settings["voice"].get("aliases") or {}).items():
        if target == voice_id:
            used.append(f"settings.json (alias '{alias}')")
    for script in sorted(LESSONS_DIR.glob("*/generated/script.json")):
        try:
            narration = json.loads(script.read_text(encoding="utf-8")).get("narration", [])
        except (OSError, ValueError):
            continue
        ids = [n["id"] for n in narration if n.get("voice") == voice_id]
        if ids:
            used.append(f"lesson '{script.parent.parent.name}' ({', '.join(ids[:4])}{'…' if len(ids) > 4 else ''})")
    return used


def delete_voice(voice_id: str, manager: VoiceManager) -> None:
    """Remove an uploaded voice (moved to cache/deleted_voices, so it can be restored)."""
    profile = manager.get(voice_id)
    if profile.extra.get("source") != "upload":
        raise InputError(f"'{profile.name}' is a built-in voice and cannot be deleted here.",
                         "Only voices uploaded from the Voice Library can be deleted.")
    used = voice_usage(voice_id)
    if used:
        raise InputError(f"'{profile.name}' is still in use, so it was not deleted.",
                         "Used by:\n" + "\n".join(f"- {u}" for u in used)
                         + "\n\nChoose another voice for those narrations and generate again first.")
    DELETED_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(profile.folder), str(DELETED_DIR / f"{voice_id}_{time.strftime('%Y%m%d_%H%M%S')}"))
