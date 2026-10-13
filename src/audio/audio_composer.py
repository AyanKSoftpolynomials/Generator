"""Build one narration track out of many per-block clips (any mix of voices)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


def _read_mono(path: Path, sample_rate: int) -> np.ndarray:
    data, rate = sf.read(str(path), dtype="float32", always_2d=True)
    if rate != sample_rate:
        raise ValueError(f"{path.name} is {rate} Hz, expected {sample_rate} Hz (normalise it first)")
    return data.mean(axis=1)


def place_clips(clips: list[tuple[Path, float]], total_duration: float, out_path: Path, sample_rate: int = 44100) -> list[str]:
    """Write a track of ``total_duration`` seconds with each clip starting at its time.

    ``clips`` is ``[(wav_path, start_seconds), ...]``. Returns warnings for
    clips that overlap or run past the end (they are still written, mixed).
    """
    warnings = []
    track = np.zeros(int(round(total_duration * sample_rate)) + 1, dtype=np.float32)
    previous_end = 0.0
    for path, start in sorted(clips, key=lambda c: c[1]):
        audio = _read_mono(path, sample_rate)
        begin = int(round(start * sample_rate))
        end = begin + len(audio)
        if start < previous_end - 0.02:
            warnings.append(f"{path.stem} starts {previous_end - start:.2f}s before the previous clip ends")
        if end > len(track):
            warnings.append(f"{path.stem} runs {(end - len(track)) / sample_rate:.2f}s past the end of the video")
            track = np.concatenate([track, np.zeros(end - len(track), dtype=np.float32)])
        track[begin:end] += audio
        previous_end = start + len(audio) / sample_rate
    np.clip(track, -1.0, 1.0, out=track)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_path), track, sample_rate, subtype="PCM_16")
    return warnings


def concatenate(clips: list[tuple[Path, float]], out_path: Path, sample_rate: int = 44100) -> list[float]:
    """Join clips back to back; ``clips`` is ``[(wav_path, pause_after), ...]``.

    Used for audio-only previews. Returns the start time of every clip.
    """
    parts, starts, cursor = [], [], 0.0
    for path, pause in clips:
        audio = _read_mono(path, sample_rate)
        starts.append(round(cursor, 4))
        parts += [audio, np.zeros(int(round(pause * sample_rate)), dtype=np.float32)]
        cursor += len(audio) / sample_rate + pause
    track = np.concatenate(parts) if parts else np.zeros(1, dtype=np.float32)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_path), track, sample_rate, subtype="PCM_16")
    return starts
