"""Checks a lesson script before any audio is generated."""

from __future__ import annotations

from src.audio.voice_manager import VoiceManager
from src.script.models import LessonScript
from src.utils.errors import LMSError


def validate_script(script: LessonScript, voices: VoiceManager, check_voices: bool = True) -> list[str]:
    """Return warnings; raise ``LMSError`` for problems that stop generation."""
    errors, warnings = [], []
    if not script.narration:
        warnings.append("The lesson has no narrate() calls; the video will be silent.")

    seen = set()
    for block in script.narration:
        if block.id in seen:
            errors.append(f"Narration id '{block.id}' is used more than once.")
        seen.add(block.id)
        if not block.text.strip():
            errors.append(f"Narration '{block.id}' has no text.")
        if check_voices and not block.voice:
            errors.append(
                f"Narration '{block.id}' has no voice: set voice=..., a scene voice, the lesson's "
                "default_voice, or voice.default in settings.json."
            )

    if errors:
        raise LMSError("The lesson script has problems:\n" + "\n".join(f"- {e}" for e in errors))

    if check_voices:
        for voice_id in script.voices_used:
            if not voices.exists(voice_id):
                users = [b.id for b in script.narration if b.voice == voice_id]
                err = voices.not_found_error(voice_id)
                raise LMSError(f"{err.message}\n\nUsed by: {', '.join(users)}", err.fix)
            voice_errors, voice_warnings = voices.validate(voice_id)
            if voice_errors:
                raise LMSError("\n".join(voice_errors), f"Fix or re-add the samples: python scripts/voice.py validate {voice_id}")
            warnings += voice_warnings
    return warnings
