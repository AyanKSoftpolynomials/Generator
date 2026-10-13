"""The voice library as the browser sees it (no file paths, no copies).

Built on ``VoiceManager`` — the same ``assets/voices/<id>/voice.json``
library the generator uses. Optional ``voice.json`` fields used here:

    "category": "teacher"          (otherwise taken from the id: teacher_a -> teacher)
    "preview":  "preview.wav"      (otherwise the first reference sample is played)
"""

from __future__ import annotations

from pathlib import Path

from src.audio.voice_manager import VoiceManager, sample_duration

LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese",
    "pl": "Polish", "tr": "Turkish", "ru": "Russian", "nl": "Dutch", "cs": "Czech", "ar": "Arabic",
    "zh-cn": "Chinese", "ja": "Japanese", "hu": "Hungarian", "ko": "Korean", "hi": "Hindi",
}


def preview_file(manager: VoiceManager, voice_id: str) -> Path | None:
    profile = manager.get(voice_id)
    preview = profile.extra.get("preview")
    candidates = ([profile.folder / preview] if preview else []) + list(profile.samples)
    return next((p for p in candidates if p.exists() and p.resolve().parent == profile.folder.resolve()), None)


def describe(manager: VoiceManager, voice_id: str) -> dict:
    profile = manager.get(voice_id)
    errors, warnings = manager.validate(voice_id)
    seconds = 0.0
    for sample in profile.samples:
        try:
            seconds += sample_duration(sample)
        except Exception:  # unreadable sample: reported by validate()
            pass
    category = profile.extra.get("category") or voice_id.split("_")[0]
    return {
        "id": profile.id,
        "name": profile.name,
        "category": category,
        "language": LANGUAGE_NAMES.get(profile.language, profile.language),
        "languageCode": profile.language,
        "description": profile.description,
        "referenceAudioFiles": [s.name for s in profile.samples],
        "referenceSeconds": round(seconds, 1),
        "synthetic": bool(profile.extra.get("synthetic")),
        "speaker": profile.extra.get("speaker") or profile.extra.get("source_speaker"),
        "gender": profile.extra.get("gender"),
        "uploaded": profile.extra.get("source") == "upload",
        "created": profile.extra.get("created"),
        "preview": f"/api/voices/{voice_id}/preview" if preview_file(manager, voice_id) else None,
        "usable": not errors,
        "problems": errors + warnings,
    }


def list_voices(manager: VoiceManager) -> list[dict]:
    return [describe(manager, voice_id) for voice_id in manager.list_ids()]
