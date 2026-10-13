"""Check and set up everything the video generator needs.

    python scripts/setup.py              # check + install missing Python packages
    python scripts/setup.py --full       # ...and run real TTS / WhisperX / Manim tests
    python scripts/setup.py --check      # check only, install nothing

Run it from the project root with .venv activated. It is safe to re-run.
"""

from __future__ import annotations

import argparse
import importlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

PACKAGES = {  # import name -> pip name (for messages)
    "manim": "manim", "numpy": "numpy", "scipy": "scipy", "PIL": "pillow", "torch": "torch",
    "torchaudio": "torchaudio", "TTS": "coqui-tts", "whisperx": "whisperx", "soundfile": "soundfile", "pytest": "pytest",
}
CUDA_INDEX = "https://download.pytorch.org/whl/cu128"

results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "", fix: str = "") -> bool:
    results.append((name, ok, detail if ok else f"{detail}\n      FIX: {fix}" if fix else detail))
    print(f"  {'✓' if ok else '✗'} {name:<20} {detail}")
    if not ok and fix:
        print(f"      FIX: {fix}")
    return ok


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kwargs)


def check_python() -> bool:
    v = sys.version_info
    ok = (3, 11) <= (v.major, v.minor) <= (3, 13)
    return record("Python", ok, platform.python_version(),
                  "Use Python 3.12:  py install 3.12  then  py -V:3.12 -m venv .venv")


def check_venv() -> bool:
    inside = Path(sys.prefix).resolve() == (ROOT / ".venv").resolve()
    return record("Virtual environment", inside, sys.prefix,
                  "Activate it first:  .\\.venv\\Scripts\\Activate.ps1")


def has_nvidia_gpu() -> str | None:
    smi = shutil.which("nvidia-smi")
    if not smi:
        return None
    out = run([smi, "--query-gpu=name", "--format=csv,noheader"])
    return out.stdout.strip().splitlines()[0] if out.returncode == 0 and out.stdout.strip() else None


def install_packages(check_only: bool, gpu: str | None) -> None:
    missing = []
    for module, pip_name in PACKAGES.items():
        try:
            importlib.import_module(module)
        except Exception:
            missing.append(pip_name)
    if missing and not check_only:
        print(f"\n  Installing: {', '.join(missing)} (this can take several minutes)...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
        if result.returncode != 0:
            record("Python packages", False, "pip install failed", "Read the pip error above; then re-run this script.")
            return
    still_missing = []
    for module, pip_name in PACKAGES.items():
        try:
            importlib.import_module(module)
        except Exception:
            still_missing.append(pip_name)
    record("Python packages", not still_missing, "all installed" if not still_missing else f"missing: {', '.join(still_missing)}",
           "python scripts/setup.py   (without --check)")

    if gpu and not still_missing:
        import torch

        if not torch.cuda.is_available():
            if check_only:
                record("CUDA PyTorch", False, f"{gpu} found but PyTorch is the CPU build",
                       "python scripts/setup.py   (installs the CUDA build)")
            else:
                print(f"\n  NVIDIA GPU found ({gpu}); installing CUDA PyTorch...")
                subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "torch==2.8.0",
                                "torchaudio==2.8.0", "--index-url", CUDA_INDEX])


def check_ffmpeg(check_only: bool) -> bool:
    path = shutil.which("ffmpeg")
    if not path and not check_only and platform.system() == "Windows" and shutil.which("winget"):
        print("\n  FFmpeg missing; installing with winget...")
        subprocess.run(["winget", "install", "--id", "Gyan.FFmpeg", "--accept-package-agreements",
                        "--accept-source-agreements", "--disable-interactivity"])
        path = shutil.which("ffmpeg")
    if not path:
        fixes = {"Windows": "winget install --id Gyan.FFmpeg   (then open a new terminal)",
                 "Darwin": "brew install ffmpeg", "Linux": "sudo apt install ffmpeg"}
        return record("FFmpeg", False, "not found", fixes.get(platform.system(), "Install FFmpeg and add it to PATH"))
    version = run([path, "-version"]).stdout.split("\n")[0].replace("ffmpeg version ", "").split(" ")[0]
    return record("FFmpeg", True, version)


def check_latex() -> bool:
    ok = bool(shutil.which("latex") and shutil.which("dvisvgm"))
    return record("LaTeX (MathTex)", ok, "latex + dvisvgm found" if ok else "not found",
                  "winget install --id MiKTeX.MiKTeX --scope user   then   initexmf --set-config-value=\"[MPM]AutoInstall=1\"")


def check_versions() -> None:
    for module, label in (("manim", "Manim"), ("TTS", "XTTS (coqui-tts)"), ("whisperx", "WhisperX")):
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, "__version__", None)
            if version is None:
                from importlib.metadata import version as dist_version

                version = dist_version({"whisperx": "whisperx"}.get(module, module))
            record(label, True, str(version))
        except Exception as exc:
            record(label, False, f"import failed: {exc}", "python scripts/setup.py")


def check_device() -> None:
    from src.config.settings import load_settings, resolve_device

    try:
        device = resolve_device(load_settings()["compute"]["device"])
    except Exception as exc:
        record("Compute device", False, str(exc))
        return
    gpu = has_nvidia_gpu()
    detail = f"NVIDIA CUDA ({gpu})" if device == "cuda" else "CPU" + (f" (GPU {gpu} not used by PyTorch)" if gpu else " (no NVIDIA GPU; slower but works)")
    record("GPU / CPU", True, detail)


def full_tests() -> None:
    from src.audio.voice_manager import VoiceManager

    tmp = Path(tempfile.mkdtemp())
    vm = VoiceManager()
    voices = vm.list_ids()
    wav = tmp / "tts_test.wav"
    try:
        from src.audio.tts_engine import XTTSEngine
        from src.config.settings import load_settings, resolve_device

        engine = XTTSEngine(resolve_device(load_settings()["compute"]["device"]))
        text = "Hello students, this is a short test."
        if voices:
            engine.synthesize(text, vm.get(voices[0]), "en", wav)
        else:
            engine.synthesize_builtin(text, engine.builtin_speakers[0], "en", wav)
        import soundfile as sf

        record("TTS test", True, f"{sf.info(str(wav)).duration:.1f}s of speech generated")
    except Exception as exc:
        record("TTS test", False, str(exc)[:200], "See README > Troubleshooting")
        return
    try:
        from src.subtitles.whisper_alignment import Aligner

        data, _ = Aligner("en", "cpu", tmp).align(wav, text, 3.0)
        record("WhisperX test", True, f"aligned {len(data['words'])} words")
    except Exception as exc:
        record("WhisperX test", False, str(exc)[:200], "See README > Troubleshooting")
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    result = run([sys.executable, "-m", "manim", "render", "tests/test_scene.py", "HelloStudents", "-ql",
                  "--media_dir", str(tmp / "media")], cwd=ROOT, env=env)
    record("Manim test", result.returncode == 0, "rendered tests/test_scene.py" if result.returncode == 0 else "render failed",
           "python scripts/render_preview.py tests/test_scene.py   to see the error")


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up / check the LMS video generator environment.")
    parser.add_argument("--check", action="store_true", help="only check, install nothing")
    parser.add_argument("--full", action="store_true", help="also run real TTS, WhisperX and Manim tests")
    args = parser.parse_args()

    print("=" * 48 + "\n LMS VIDEO GENERATOR SETUP\n" + "=" * 48 + "\n")
    if not check_python():
        return 1
    if not check_venv():
        return 1
    gpu = has_nvidia_gpu()
    install_packages(args.check, gpu)
    check_ffmpeg(args.check)
    check_latex()
    check_versions()
    check_device()
    if args.full:
        print("\n  Running live tests (first run downloads models, ~2 GB)...")
        full_tests()

    failed = [r for r in results if not r[1]]
    print("\n" + ("Environment ready." if not failed else f"{len(failed)} problem(s) to fix (see FIX lines above)."))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
