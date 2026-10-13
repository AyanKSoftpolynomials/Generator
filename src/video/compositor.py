"""Mux the rendered animation, the narration track and (optionally) subtitles."""

from __future__ import annotations

from pathlib import Path

from src.video.ffmpeg import run_ffmpeg


def compose(video: Path, audio: Path | None, out_path: Path, subtitles_srt: Path | None = None, language: str = "en") -> Path:
    """Write ``out_path``: video stream copied as-is, audio as AAC, SRT as a soft track."""
    args = ["-i", str(video)]
    maps = ["-map", "0:v:0"]
    codecs = ["-c:v", "copy"]
    if audio is not None:
        args += ["-i", str(audio)]
        maps += ["-map", "1:a:0"]
        codecs += ["-c:a", "aac", "-b:a", "192k"]
    if subtitles_srt is not None:
        index = 2 if audio is not None else 1
        args += ["-i", str(subtitles_srt)]
        maps += ["-map", f"{index}:s:0"]
        lang3 = {"en": "eng", "hi": "hin"}.get(language, "und")
        codecs += ["-c:s", "mov_text", f"-metadata:s:s:0", f"language={lang3}"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg([*args, *maps, *codecs, "-movflags", "+faststart", str(out_path)], "composing the final video")
    return out_path
