"""Make every narration clip sound consistent: same format, loudness and edges.

Two-pass EBU R128 loudness normalisation (FFmpeg ``loudnorm``) brings
different voices to the same perceived volume without squashing them, and a
true-peak limit prevents clipping. Leading/trailing silence is trimmed so the
pauses between clips are controlled by the lesson, not by the TTS engine.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import soundfile as sf

from src.video.ffmpeg import run_ffmpeg

TRUE_PEAK_DB = -1.5
LOUDNESS_RANGE = 11
SILENCE_THRESHOLD_DB = -45

_TRIM = (
    f"silenceremove=start_periods=1:start_threshold={SILENCE_THRESHOLD_DB}dB:start_silence=0.05,"
    "areverse,"
    f"silenceremove=start_periods=1:start_threshold={SILENCE_THRESHOLD_DB}dB:start_silence=0.08,"
    "areverse"
)


def normalize(src: Path, dst: Path, sample_rate: int = 44100, loudness_lufs: float = -18, trim_silence: bool = True) -> None:
    """Write a mono, ``sample_rate`` Hz, 16-bit, loudness-normalised copy of ``src``."""
    pre = f"{_TRIM}," if trim_silence else ""
    target = f"I={loudness_lufs}:TP={TRUE_PEAK_DB}:LRA={LOUDNESS_RANGE}"

    # Pass 1: measure.
    measured = run_ffmpeg(
        ["-i", str(src), "-af", f"{pre}loudnorm={target}:print_format=json", "-f", "null", "-"],
        f"measuring loudness of {src.name}",
    )
    stats = _parse_loudnorm(measured.stderr)

    # Pass 2: apply the measured correction linearly (keeps the voice's natural dynamics).
    second = (
        f"{pre}loudnorm={target}"
        f":measured_I={stats['input_i']}:measured_TP={stats['input_tp']}"
        f":measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}"
        f":offset={stats['target_offset']}:linear=true,aresample={sample_rate}"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        ["-i", str(src), "-af", second, "-ac", "1", "-ar", str(sample_rate), "-c:a", "pcm_s16le", str(dst)],
        f"normalising {src.name}",
    )


def _parse_loudnorm(stderr: str) -> dict:
    blocks = re.findall(r"\{[^{}]*\}", stderr, flags=re.S)
    if not blocks:
        raise ValueError("FFmpeg loudnorm did not report measurements")
    stats = json.loads(blocks[-1])
    # Silent clips report -inf; fall back to neutral values so pass 2 still runs.
    for key, fallback in (("input_i", "-70"), ("input_tp", "-70"), ("input_lra", "0"), ("input_thresh", "-80"), ("target_offset", "0")):
        if "inf" in str(stats.get(key, "")):
            stats[key] = fallback
    return stats


def audio_duration(path: Path) -> float:
    """Length of a WAV/FLAC/OGG file in seconds."""
    return float(sf.info(str(path)).duration)
