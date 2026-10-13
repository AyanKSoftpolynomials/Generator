"""Timing helpers for pacing animations against (future) narration."""

from src.themes import default_theme as theme

# Comfortable narration speed for students, in words per minute.
DEFAULT_WORDS_PER_MINUTE = 140


def reading_time(text: str, words_per_minute: int = DEFAULT_WORDS_PER_MINUTE, minimum: float = theme.PAUSE) -> float:
    """Seconds a student needs to read (or hear) ``text``.

    Use it for waits after showing text: ``self.wait(reading_time(sentence))``.
    """
    words = len(text.split())
    return max(minimum, words / words_per_minute * 60)


def total_duration(*durations: float) -> float:
    """Add up animation/wait durations, e.g. to check a scene fits a narration clip."""
    return float(sum(durations))
