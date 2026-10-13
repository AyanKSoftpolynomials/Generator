"""Turn the raw data recorded by ``narrate()`` into a ``LessonScript``.

Voice resolution (most specific wins):

    narrate(voice=...)  >  scene_start(voice=...)  >  class default_voice  >  settings.json voice.default

Short names from settings.json ``voice.aliases`` (e.g. "teacher" -> "teacher_a")
are then mapped to voice library ids.
"""

from __future__ import annotations

from src.script.models import LessonScript, NarrationBlock


def parse_extracted(raw: dict, lesson_folder_name: str, global_default_voice: str | None,
                    aliases: dict[str, str] | None = None) -> LessonScript:
    lesson = raw.get("lesson", {})
    scenes = raw.get("scenes", [])
    aliases = aliases or {}
    lesson_voice = aliases.get(lesson.get("default_voice"), lesson.get("default_voice"))

    blocks = []
    for item in raw.get("narration", []):
        recorded = item.get("voice")  # narration > scene > lesson, already resolved by narrate()
        source = item.get("voice_source") or ("global" if not recorded else "narration")
        blocks.append(NarrationBlock(
            id=item["id"],
            text=item["text"],
            voice=aliases.get(recorded, recorded) or global_default_voice,
            scene=item.get("scene"),
            subtitle=item.get("subtitle", True),
            pause_after=float(item.get("pause_after", 0.25)),
            estimated_duration=float(item.get("estimated_duration", 0.0)),
            voice_source=source,
        ))

    return LessonScript(
        lesson_id=lesson.get("id") or lesson_folder_name,
        title=lesson.get("title"),
        language=lesson.get("language") or "en",
        default_voice=lesson_voice or global_default_voice,
        scene_class=lesson.get("scene_class", ""),
        subtitles=lesson.get("subtitles"),
        scenes=scenes,
        narration=blocks,
    )
