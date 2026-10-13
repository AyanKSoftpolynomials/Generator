"""Reusable voice library in ``assets/voices/<voice_id>/``.

Each voice folder holds one or more reference recordings plus ``voice.json``:

    assets/voices/teacher_a/
        sample_01.wav
        sample_02.wav
        voice.json   {"id": "teacher_a", "name": "Teacher A", "language": "en",
                      "samples": ["sample_01.wav", "sample_02.wav"], "description": "..."}

Only use recordings you own or have permission to clone.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from src.config.video_config import PROJECT_ROOT
from src.utils.errors import LMSError

VOICES_DIR = PROJECT_ROOT / "assets" / "voices"
SUPPORTED_FORMATS = {".wav", ".flac", ".ogg", ".mp3"}
MIN_SAMPLE_SECONDS = 2.0
RECOMMENDED_SAMPLE_SECONDS = 6.0
VOICE_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")


@dataclass
class VoiceProfile:
    id: str
    name: str
    language: str
    samples: list[Path]
    description: str = ""
    folder: Path | None = None
    extra: dict = field(default_factory=dict)

    def fingerprint(self) -> str:
        """Hash of the reference audio; changes when any sample file changes."""
        digest = hashlib.sha256(self.id.encode())
        for sample in sorted(self.samples):
            digest.update(sample.name.encode())
            digest.update(hashlib.sha256(sample.read_bytes()).digest())
        return digest.hexdigest()[:16]


class VoiceManager:
    """Register, load, list and validate voices."""

    def __init__(self, voices_dir: Path = VOICES_DIR):
        self.voices_dir = Path(voices_dir)

    # -- lookup --------------------------------------------------------------

    def list_ids(self) -> list[str]:
        if not self.voices_dir.exists():
            return []
        return sorted(p.parent.name for p in self.voices_dir.glob("*/voice.json"))

    def exists(self, voice_id: str) -> bool:
        return (self.voices_dir / voice_id / "voice.json").exists()

    def get(self, voice_id: str) -> VoiceProfile:
        """Load a voice or raise a readable error listing the available ones."""
        if not self.exists(voice_id):
            raise self.not_found_error(voice_id)
        folder = self.voices_dir / voice_id
        try:
            meta = json.loads((folder / "voice.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise LMSError(f"{folder / 'voice.json'} is not valid JSON: {exc}") from exc
        samples = [folder / s for s in meta.get("samples", [])]
        known = {"id", "name", "language", "samples", "description"}
        return VoiceProfile(
            id=meta.get("id", voice_id),
            name=meta.get("name", voice_id),
            language=meta.get("language", "en"),
            samples=samples,
            description=meta.get("description", ""),
            folder=folder,
            extra={k: v for k, v in meta.items() if k not in known},
        )

    def not_found_error(self, voice_id: str) -> LMSError:
        available = self.list_ids()
        listing = "\n".join(f"- {v}" for v in available) or "(none registered yet)"
        return LMSError(
            f"Voice '{voice_id}' does not exist.\n\nAvailable voices:\n{listing}",
            f"Add the voice using:\n\n    python scripts/voice.py add {voice_id} --sample <path-to-recording.wav>",
        )

    # -- validation ----------------------------------------------------------

    def validate(self, voice_id: str) -> tuple[list[str], list[str]]:
        """Return ``(errors, warnings)`` for a voice. No errors means it is usable."""
        if not self.exists(voice_id):
            return [str(self.not_found_error(voice_id))], []
        profile = self.get(voice_id)
        errors, warnings = [], []
        if not profile.samples:
            errors.append(f"{voice_id}: voice.json lists no samples.")
        if not profile.language:
            errors.append(f"{voice_id}: no language configured in voice.json.")
        for sample in profile.samples:
            errors_for, warnings_for = check_sample(sample)
            errors += [f"{voice_id}: {e}" for e in errors_for]
            warnings += [f"{voice_id}: {w}" for w in warnings_for]
        total = sum(sample_duration(s) for s in profile.samples if s.exists() and not check_sample(s)[0])
        if profile.samples and not errors and total < RECOMMENDED_SAMPLE_SECONDS:
            warnings.append(f"{voice_id}: only {total:.1f}s of reference audio; 6-30s gives better cloning.")
        return errors, warnings

    def require(self, voice_id: str) -> VoiceProfile:
        """``get()`` plus validation; raises on the first problem."""
        errors, _ = self.validate(voice_id)
        if errors:
            raise LMSError("\n".join(errors), f"Check the files in {self.voices_dir / voice_id}.")
        return self.get(voice_id)

    # -- registration --------------------------------------------------------

    def add(
        self,
        voice_id: str,
        samples: list[Path],
        name: str | None = None,
        language: str = "en",
        description: str = "",
        extra: dict | None = None,
    ) -> VoiceProfile:
        """Create or extend a voice by copying reference recordings into its folder."""
        if not VOICE_ID_PATTERN.match(voice_id):
            raise LMSError(f"Invalid voice id '{voice_id}'.", "Use lower-case letters, digits and underscores, e.g. teacher_a.")
        for sample in samples:
            errors, _ = check_sample(Path(sample))
            if errors:
                raise LMSError(f"Cannot add sample: {errors[0]}")

        folder = self.voices_dir / voice_id
        folder.mkdir(parents=True, exist_ok=True)
        meta = {"id": voice_id, "name": name or voice_id.replace("_", " ").title(), "language": language,
                "samples": [], "description": description}
        if (folder / "voice.json").exists():
            meta.update(json.loads((folder / "voice.json").read_text(encoding="utf-8")))
            if name:
                meta["name"] = name
            if description:
                meta["description"] = description
        meta.update(extra or {})

        for sample in samples:
            sample = Path(sample)
            if sample.resolve().parent == folder.resolve():
                target = sample.resolve()
            else:
                index = len(meta["samples"]) + 1
                target = folder / f"sample_{index:02d}{sample.suffix.lower()}"
                while target.exists():
                    index += 1
                    target = folder / f"sample_{index:02d}{sample.suffix.lower()}"
                shutil.copy2(sample, target)
            if target.name not in meta["samples"]:
                meta["samples"].append(target.name)

        (folder / "voice.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return self.get(voice_id)


def sample_duration(path: Path) -> float:
    import soundfile as sf

    return sf.info(str(path)).duration


def check_sample(path: Path) -> tuple[list[str], list[str]]:
    """Check one reference recording: exists, supported, readable, long enough."""
    path = Path(path)
    if not path.exists():
        return [f"sample file not found: {path}"], []
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        return [f"unsupported format '{path.suffix}' for {path.name} (use {', '.join(sorted(SUPPORTED_FORMATS))})"], []
    try:
        import soundfile as sf

        info = sf.info(str(path))
    except Exception as exc:  # soundfile raises several types for corrupt files
        return [f"cannot read {path.name}: {exc}"], []
    warnings = []
    if info.duration < MIN_SAMPLE_SECONDS:
        return [f"{path.name} is only {info.duration:.1f}s long (minimum {MIN_SAMPLE_SECONDS:.0f}s)"], []
    if info.samplerate < 16000:
        warnings.append(f"{path.name} has a low sample rate ({info.samplerate} Hz); 22050 Hz or more is better")
    return [], warnings
