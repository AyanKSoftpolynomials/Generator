"""Generate a narrated lesson video from lessons/<name>/animation.py.

    python scripts/generate_video.py lessons/whole_numbers              # preview (480p), real audio
    python scripts/generate_video.py lessons/whole_numbers --final      # Full HD
    python scripts/generate_video.py lessons/whole_numbers --audio-only
    python scripts/generate_video.py lessons/whole_numbers --subtitles-only
    python scripts/generate_video.py lessons/whole_numbers --no-subtitles
    python scripts/generate_video.py lessons/whole_numbers --voice teacher_b   # one voice for everything
    python scripts/generate_video.py lessons/whole_numbers --engine sarvam     # Sarvam AI speech (needs .env)
    python scripts/generate_video.py lessons/whole_numbers --dry-run   # what would be regenerated
    python scripts/generate_video.py lessons/whole_numbers --force     # ignore every cache

Unchanged stages are reused automatically (see README > Incremental builds).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Windows consoles default to a legacy code page; make ✓ and → printable.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

from src.config.settings import load_settings  # noqa: E402
from src.pipeline.generator import GenerateOptions, VideoGenerator, performance_summary  # noqa: E402
from src.utils.errors import LMSError  # noqa: E402

BAR = "=" * 48


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate a narrated lesson video from animation.py.")
    p.add_argument("lesson", help="lesson folder, e.g. lessons/whole_numbers")
    quality = p.add_mutually_exclusive_group()
    quality.add_argument("--preview", action="store_true", help="fast low-quality render (default)")
    quality.add_argument("--final", action="store_true", help="final quality render (settings.json > video.final_quality)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--audio-only", action="store_true", help="generate narration clips + combined track, no video")
    mode.add_argument("--subtitles-only", action="store_true", help="rebuild subtitles from the last run's audio/timeline")
    subs = p.add_mutually_exclusive_group()
    subs.add_argument("--subtitles", dest="subtitles", action="store_true", default=None, help="force subtitles on")
    subs.add_argument("--no-subtitles", dest="subtitles", action="store_false", help="force subtitles off")
    p.add_argument("--no-audio", dest="audio", action="store_false", default=None, help="visual-only render")
    p.add_argument("--engine", choices=["xtts_v2", "sarvam"],
                   help="text-to-speech engine for this run (default: settings.json > audio.engine)")
    p.add_argument("--voice", help="use this voice for every narration block (overrides animation.py)")
    p.add_argument("--assign", action="append", default=[], metavar="ID=VOICE",
                   help="use VOICE for one narration block (repeatable), e.g. --assign hook_main=teacher_b")
    p.add_argument("--alias", action="append", default=[], metavar="NAME=VOICE",
                   help="speak every block that asks for voice NAME with VOICE instead (repeatable), "
                        "e.g. --alias vijay=narrator")
    p.add_argument("--speaker", action="append", default=[], metavar="VOICE=SPEAKER",
                   help="Sarvam engine: speak library voice VOICE with Sarvam speaker SPEAKER for this run "
                        "(repeatable), e.g. --speaker aditya=shubh")
    p.add_argument("--scene", help="scene class to use when animation.py has several")
    p.add_argument("--name", help="output file name (without .mp4)")
    cache = p.add_argument_group("incremental build (cache)")
    cache.add_argument("--force", action="store_true", help="rebuild every stage, ignoring all caches")
    cache.add_argument("--force-tts", action="store_true", help="regenerate all narration audio")
    cache.add_argument("--force-alignment", action="store_true", help="re-run WhisperX alignment (and subtitles)")
    cache.add_argument("--force-render", action="store_true", help="re-render every Manim animation")
    cache.add_argument("--force-compose", action="store_true", help="re-run the final FFmpeg composition")
    cache.add_argument("--dry-run", action="store_true", help="show what would be regenerated; generate nothing")
    cache.add_argument("--workers", type=int, help="parallel TTS workers (default 1; each loads its own model)")
    return p


def lesson_folder(target: str) -> Path:
    """Accept either lessons/<name> or lessons/<name>/animation.py."""
    path = Path(target)
    return path.parent if path.suffix == ".py" else path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    assignments = {}
    for item in args.assign:
        narration_id, sep, voice = item.partition("=")
        if not sep or not narration_id.strip() or not voice.strip():
            parser.error(f"--assign expects ID=VOICE, got '{item}'")
        assignments[narration_id.strip()] = voice.strip()
    options = GenerateOptions(
        quality="final" if args.final else "preview",
        audio_only=args.audio_only,
        subtitles_only=args.subtitles_only,
        subtitles=args.subtitles,
        audio=args.audio,
        voice_override=args.voice,
        voice_assignments=assignments or None,
        scene_class=args.scene,
        output_name=args.name,
        force=args.force,
        force_tts=args.force_tts,
        force_alignment=args.force_alignment,
        force_render=args.force_render,
        force_compose=args.force_compose,
        dry_run=args.dry_run,
        workers=args.workers,
    )
    lesson = lesson_folder(args.lesson)
    try:
        settings = load_settings()
        if args.engine:
            settings["audio"]["engine"] = args.engine
        for item in args.alias:
            name, sep, voice = item.partition("=")
            if not sep or not name.strip() or not voice.strip():
                parser.error(f"--alias expects NAME=VOICE, got '{item}'")
            settings["voice"]["aliases"][name.strip()] = voice.strip()
        for item in args.speaker:
            voice, sep, speaker = item.partition("=")
            if not sep or not voice.strip() or not speaker.strip():
                parser.error(f"--speaker expects VOICE=SPEAKER, got '{item}'")
            settings["audio"]["sarvam"]["voices"][voice.strip()] = speaker.strip()
        report = VideoGenerator(lesson, options, settings).run()
    except LMSError as err:
        print(f"\nERROR: {err}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130

    if args.dry_run:
        print(f"\nDry run finished in {report.total_seconds:.0f}s. No files were generated.")
        return 0
    if args.subtitles_only:
        print(f"\n{BAR}\nSUBTITLES GENERATED\n{BAR}\n" + "\n".join(report.outputs.get("subtitles", {}).values()))
        return 0

    for warning in report.warnings:
        print(f"warning: {warning}")
    print()
    print(performance_summary(report))
    outputs = report.outputs
    if "video" in outputs:
        print(f"\nOutput:\n{outputs['video']}")
    if "narration_track" in outputs:
        print(f"\nNarration track:\n{outputs['narration_track']}")
    if "subtitles" in outputs:
        print("\nSubtitles:\n" + "\n".join(outputs["subtitles"].values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
