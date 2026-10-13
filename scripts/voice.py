"""Manage the voice library in assets/voices/.

    python scripts/voice.py list
    python scripts/voice.py info teacher_a
    python scripts/voice.py validate [teacher_a]
    python scripts/voice.py add teacher_c --sample rec1.wav --sample rec2.wav --name "Teacher C"
    python scripts/voice.py speakers                       # XTTS built-in synthetic speakers
    python scripts/voice.py create-synthetic narrator --speaker "Viktor Eka" --samples 2

Only add recordings of people who have given permission to clone their voice.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

from src.audio.voice_manager import VoiceManager, sample_duration  # noqa: E402
from src.utils.errors import LMSError  # noqa: E402

# Reference sentences for synthetic test voices (~8-10 s each, varied intonation).
SYNTHETIC_TEXTS = [
    "Good morning, everyone. Today we are going to explore numbers, patterns, and the simple ideas behind counting.",
    "Take a moment and look closely. Can you see how each step builds on the one before it? That is how mathematics works.",
    "Wonderful work! Remember, it is perfectly fine to make mistakes, because every mistake teaches us something new.",
]


def cmd_list(vm: VoiceManager, _args) -> None:
    ids = vm.list_ids()
    if not ids:
        print("No voices yet. Add one with: python scripts/voice.py add <id> --sample <file.wav>")
        return
    print("Available voices:\n")
    for i, voice_id in enumerate(ids, 1):
        p = vm.get(voice_id)
        print(f"{i}. {voice_id:<12} {p.name:<18} {p.language:<4} {len(p.samples)} sample(s)  {p.description}")


def cmd_info(vm: VoiceManager, args) -> None:
    p = vm.get(args.voice)
    print(f"id:          {p.id}\nname:        {p.name}\nlanguage:    {p.language}\ndescription: {p.description}")
    for key, value in p.extra.items():
        print(f"{key + ':':<13}{value}")
    print(f"folder:      {p.folder}\nsamples:")
    for s in p.samples:
        length = f"{sample_duration(s):.1f}s" if s.exists() else "MISSING"
        print(f"  - {s.name} ({length})")


def cmd_validate(vm: VoiceManager, args) -> int:
    ids = [args.voice] if args.voice else vm.list_ids()
    failed = False
    for voice_id in ids:
        errors, warnings = vm.validate(voice_id)
        print(f"{voice_id}: {'✓ valid' if not errors else '✗ invalid'}")
        for e in errors:
            print(f"   error: {e}")
        for w in warnings:
            print(f"   warning: {w}")
        failed |= bool(errors)
    return 1 if failed else 0


def cmd_add(vm: VoiceManager, args) -> None:
    profile = vm.add(args.voice, [Path(s) for s in args.sample], name=args.name, language=args.language,
                     description=args.description or "")
    print(f"✓ {profile.id} now has {len(profile.samples)} sample(s): {', '.join(s.name for s in profile.samples)}")


def _engine():
    from src.audio.tts_engine import XTTSEngine
    from src.config.settings import load_settings, resolve_device

    return XTTSEngine(resolve_device(load_settings()["compute"]["device"]))


def cmd_speakers(_vm, _args) -> None:
    print("\n".join(_engine().builtin_speakers))


def cmd_create_synthetic(vm: VoiceManager, args) -> None:
    """Make a test voice from an XTTS built-in (synthetic, non-human) speaker."""
    from src.audio.audio_processor import normalize

    engine = _engine()
    if args.speaker not in engine.builtin_speakers:
        raise LMSError(f"Unknown built-in speaker '{args.speaker}'.", "List them with: python scripts/voice.py speakers")
    with tempfile.TemporaryDirectory() as tmp:
        samples = []
        for i, text in enumerate(SYNTHETIC_TEXTS[: args.samples], 1):
            raw, clean = Path(tmp) / f"raw_{i}.wav", Path(tmp) / f"sample_{i:02d}.wav"
            engine.synthesize_builtin(text, args.speaker, args.language, raw)
            normalize(raw, clean, sample_rate=24000)
            samples.append(clean)
            print(f"  sample {i}: {sample_duration(clean):.1f}s")
        profile = vm.add(args.voice, samples, name=args.name, language=args.language,
                         description=args.description or f"Synthetic test voice (XTTS speaker '{args.speaker}')",
                         extra={"synthetic": True, "source_speaker": args.speaker})
    print(f"✓ {profile.id}: {len(profile.samples)} sample(s) in {profile.folder}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Manage the voice library.")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list registered voices")
    info = sub.add_parser("info", help="show a voice's details")
    info.add_argument("voice")
    val = sub.add_parser("validate", help="check a voice (or all voices)")
    val.add_argument("voice", nargs="?")
    add = sub.add_parser("add", help="register a voice / add reference samples")
    add.add_argument("voice")
    add.add_argument("--sample", action="append", required=True, help="recording to copy in (repeatable)")
    add.add_argument("--name")
    add.add_argument("--language", default="en")
    add.add_argument("--description")
    sub.add_parser("speakers", help="list XTTS built-in synthetic speakers")
    syn = sub.add_parser("create-synthetic", help="create a test voice from an XTTS built-in speaker")
    syn.add_argument("voice")
    syn.add_argument("--speaker", required=True)
    syn.add_argument("--samples", type=int, default=1, choices=range(1, len(SYNTHETIC_TEXTS) + 1))
    syn.add_argument("--name")
    syn.add_argument("--language", default="en")
    syn.add_argument("--description")
    args = p.parse_args(argv)

    vm = VoiceManager()
    handlers = {"list": cmd_list, "info": cmd_info, "validate": cmd_validate, "add": cmd_add,
                "speakers": cmd_speakers, "create-synthetic": cmd_create_synthetic}
    try:
        return handlers[args.command](vm, args) or 0
    except LMSError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
