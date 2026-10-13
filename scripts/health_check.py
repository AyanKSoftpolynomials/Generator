"""Health check for the LMS video generator: is this PC ready to generate videos?

    python scripts/health_check.py            # environment + a small Manim render test (~20 s)
    python scripts/health_check.py --quick    # skip the render test
    python scripts/health_check.py --full     # also run real XTTS speech + WhisperX alignment
                                              # (loads the models; the first run downloads ~2.3 GB)

Run it from the project root with .venv activated (setup.ps1 runs it for you).
It only reads and tests: it installs nothing and changes no project file
(the render test writes to a temporary folder that is deleted afterwards).

Every line is PASS, WARN (works, but something optional is missing or
differs) or FAIL (generation will not work until it is fixed). The exit code
is 1 if anything FAILed, else 0.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
COLORS = {PASS: "\x1b[32m", WARN: "\x1b[33m", FAIL: "\x1b[31m"}
TEST_ONLY = {"pytest", "httpx"}                   # needed only to run the test suite
XTTS_FOLDER = "tts_models--multilingual--multi-dataset--xtts_v2"
ALIGN_CHECKPOINT = "wav2vec2_fairseq_base_ls960_asr_ls960.pth"   # WhisperX English alignment (torchaudio)

results: list[tuple[str, str, str, str]] = []


def report(name: str, status: str, detail: str = "", fix: str = "") -> str:
    results.append((name, status, detail, fix))
    color = COLORS[status] if sys.stdout.isatty() else ""
    reset = "\x1b[0m" if color else ""
    print(f"{name:<22} {color}{status}{reset}  {detail}")
    if fix and status != PASS:
        print(f"{'':<22}       fix: {fix}")
    return status


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kwargs)


# ------------------------------------------------------------------ environment

def check_python() -> bool:
    v = sys.version_info
    if (3, 11) <= (v.major, v.minor) <= (3, 13):
        note = "" if (v.major, v.minor) == (3, 12) else " (3.12 recommended)"
        report("Python", PASS, f"{v.major}.{v.minor}.{v.micro}{note}")
        return True
    report("Python", FAIL, f"{v.major}.{v.minor}.{v.micro}: needs 3.11-3.13 (Manim's OpenGL wheels)",
           "py install 3.12; then recreate .venv with: py -V:3.12 -m venv .venv")
    return False


def check_venv() -> bool:
    inside = Path(sys.prefix).resolve() == (ROOT / ".venv").resolve()
    if inside:
        report("Virtual environment", PASS, ".venv")
    else:
        report("Virtual environment", FAIL, f"running on {sys.prefix}",
               r"Run with .\.venv\Scripts\python.exe scripts\health_check.py (or run setup.ps1 first)")
    return inside


def pinned_requirements() -> dict[str, str]:
    pins = {}
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*([A-Za-z0-9_.\-]+)==([^\s#;]+)", line)
        if match:
            pins[match.group(1).lower()] = match.group(2)
    return pins


def check_packages() -> bool:
    missing, missing_tests, different = [], [], []
    for name, wanted in pinned_requirements().items():
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            (missing_tests if name in TEST_ONLY else missing).append(name)
            continue
        if installed.split("+")[0] != wanted:          # torch 2.8.0+cpu == 2.8.0
            different.append(f"{name} {installed} (pinned {wanted})")
    if missing:
        report("Python packages", FAIL, "missing: " + ", ".join(missing), r".\setup.ps1   (or: python scripts/setup.py)")
        return False
    if missing_tests or different:
        report("Python packages", WARN, "; ".join(filter(None, [
            "test tools missing: " + ", ".join(missing_tests) if missing_tests else "",
            "versions differ from requirements.txt: " + ", ".join(different) if different else ""])),
            "pip install -r requirements.txt")
    else:
        report("Python packages", PASS, f"{len(pinned_requirements())} pinned packages match requirements.txt")
    return True


def check_import(label: str, module: str, dist: str, fix: str) -> bool:
    started = time.time()
    try:
        __import__(module)
    except Exception as exc:
        report(label, FAIL, f"import {module} failed: {str(exc).splitlines()[0][:120]}", fix)
        return False
    report(label, PASS, f"{dist} {metadata.version(dist)} (import {time.time() - started:.1f}s)")
    return True


def check_web_packages() -> None:
    # Imported by name only: importing backend.app would start the job manager.
    modules = {"fastapi": "fastapi", "uvicorn": "uvicorn", "multipart": "python-multipart",
               "googleapiclient": "google-api-python-client", "google_auth_oauthlib": "google-auth-oauthlib"}
    failed = []
    for module in modules:
        try:
            __import__(module)
        except Exception:
            failed.append(modules[module])
    if failed:
        report("Web API packages", FAIL, "import failed: " + ", ".join(failed), "pip install -r requirements.txt")
    else:
        report("Web API packages", PASS, f"fastapi {metadata.version('fastapi')}, uvicorn, YouTube client libraries")


def check_ffmpeg() -> bool:
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        report("FFmpeg", FAIL, "ffmpeg/ffprobe not on PATH",
               "winget install --id Gyan.FFmpeg   then open a NEW terminal")
        return False
    version = run([ffmpeg, "-version"]).stdout.split("\n")[0].replace("ffmpeg version ", "").split(" ")[0]
    report("FFmpeg", PASS, f"{version} (ffprobe too)")
    return True


def check_latex() -> None:
    if shutil.which("latex") and shutil.which("dvisvgm"):
        report("LaTeX (MathTex)", PASS, "latex + dvisvgm found")
    else:
        report("LaTeX (MathTex)", WARN, "not found: lessons using MathTex/Tex will fail (Text() works)",
               'winget install --id MiKTeX.MiKTeX --scope user; then: initexmf --set-config-value="[MPM]AutoInstall=1"')


def check_device() -> None:
    from src.config.settings import load_settings, resolve_device

    try:
        device = resolve_device(load_settings()["compute"]["device"])
    except Exception as exc:
        report("Compute device", FAIL, str(exc).splitlines()[0], 'settings.json > compute.device: "auto"')
        return
    if device == "cuda":
        import torch

        report("Compute device", PASS, f"CUDA GPU ({torch.cuda.get_device_name(0)})")
    else:
        report("Compute device", PASS, "CPU (works; speech ~1.8x real time on a 6-core CPU)")


def tts_model_dir() -> Path:
    try:
        from trainer.io import get_user_data_dir     # what coqui-tts itself uses (TTS_HOME, XDG_DATA_HOME, ...)

        return Path(get_user_data_dir("tts")) / XTTS_FOLDER
    except Exception:
        base = os.environ.get("TTS_HOME") or os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
        return Path(base) / "tts" / XTTS_FOLDER


def check_models() -> None:
    folder = tts_model_dir()
    if (folder / "model.pth").exists():
        size = sum(p.stat().st_size for p in folder.rglob("*") if p.is_file()) / 1e9
        report("XTTS v2 model", PASS, f"{size:.1f} GB in {folder}")
    else:
        report("XTTS v2 model", WARN, "not downloaded yet: the first generation downloads it (~1.9 GB)",
               "python scripts/health_check.py --full   (downloads and tests it now)")
    try:
        import torch

        checkpoint = Path(torch.hub.get_dir()) / "checkpoints" / ALIGN_CHECKPOINT
    except Exception as exc:
        report("WhisperX model", FAIL, f"torch unavailable: {exc}")
        return
    if checkpoint.exists():
        report("WhisperX model", PASS, f"English alignment model ({checkpoint.stat().st_size / 1e6:.0f} MB)")
    else:
        report("WhisperX model", WARN, "not downloaded yet: the first alignment downloads it (~360 MB)",
               "python scripts/health_check.py --full")


# ------------------------------------------------------------------ project

def check_directories() -> None:
    required = ["src", "backend", "scripts", "lessons", "assets/voices", "tests"]
    absent = [d for d in required if not (ROOT / d).is_dir()]
    if absent:
        report("Project folders", FAIL, "missing: " + ", ".join(absent), "Re-extract the package; files are missing")
        return
    created = [d for d in ("cache", "output") if not (ROOT / d).is_dir()]
    try:
        probe_dir = ROOT / "cache" if (ROOT / "cache").is_dir() else ROOT
        with tempfile.NamedTemporaryFile(dir=probe_dir, prefix=".health_", delete=True):
            pass
    except OSError as exc:
        report("Project folders", FAIL, f"project folder is not writable: {exc}",
               "Extract the project somewhere you can write (e.g. Documents), not Program Files")
        return
    detail = "source, lessons and voice folders present; writable"
    if created:
        detail += f" ({', '.join(created)}/ will be created on the first run)"
    report("Project folders", PASS, detail)


def check_settings() -> dict | None:
    from src.config.settings import load_settings

    try:
        settings = load_settings()
    except Exception as exc:
        report("Configuration", FAIL, str(exc).splitlines()[0], "Fix the JSON syntax in settings.json")
        return None
    problems = []
    if settings["audio"]["engine"] != "xtts_v2":
        problems.append(f"audio.engine is '{settings['audio']['engine']}' (only xtts_v2 exists)")
    if settings["compute"]["device"] not in ("auto", "cpu", "cuda"):
        problems.append("compute.device must be auto/cpu/cuda")
    if problems:
        report("Configuration", FAIL, "; ".join(problems), "Edit settings.json")
        return settings
    web = settings.get("web", {})
    source = "settings.json" if (ROOT / "settings.json").exists() else "built-in defaults (no settings.json)"
    report("Configuration", PASS, f"{source}; default voice {settings['voice']['default']}, "
           f"{web.get('max_concurrent_jobs')} parallel jobs, {web.get('speech_workers')} speech worker(s)")
    return settings


def check_voices(settings: dict | None) -> None:
    from src.audio.voice_manager import VoiceManager

    manager = VoiceManager()
    ids = manager.list_ids()
    if not ids:
        report("Voice library", FAIL, "assets/voices/ has no voices", "python scripts/voice.py add <id> --sample file.wav")
        return
    broken = []
    for voice_id in ids:
        errors, _warnings = manager.validate(voice_id)
        if errors:
            broken.append(voice_id)
    default = (settings or {}).get("voice", {}).get("default")
    if default and (default not in ids or default in broken):
        report("Voice library", FAIL, f"default voice '{default}' missing or broken ({len(ids)} voices)",
               "settings.json > voice.default: use an id from: python scripts/voice.py list")
    elif broken:
        report("Voice library", WARN, f"{len(ids)} voices; problems in: {', '.join(broken)}",
               "python scripts/voice.py validate")
    else:
        report("Voice library", PASS, f"{len(ids)} voices ({', '.join(ids)})")


def folder_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.is_dir() else 0


def check_cache() -> None:
    cache = ROOT / "cache"
    if not cache.is_dir():
        report("Cache", PASS, "empty (fresh install; the first build of each narration is slower)")
        return
    parts = {name: folder_size(cache / name) for name in ("audio", "alignment", "jobs", "analyze", "blender")}
    total = sum(parts.values()) / 1e6
    detail = ", ".join(f"{k} {v / 1e6:.0f} MB" for k, v in parts.items() if v)
    report("Cache", PASS if total < 20_000 else WARN, f"{total:.0f} MB ({detail or 'empty'})",
           "python scripts/clean.py --cache   frees cached audio (it is rebuilt when needed)")


def check_blender(settings: dict | None) -> None:
    from src.blender.render import find_blender

    users = sorted(p.parent.name for p in (ROOT / "lessons").glob("*/animation.py")
                   if "self.blender(" in p.read_text(encoding="utf-8", errors="replace"))
    try:
        found = find_blender(settings or {})
        report("Blender (optional)", PASS, str(found))
    except Exception:
        if users:
            report("Blender (optional)", WARN, f"not installed; only needed by lessons using self.blender(...): {', '.join(users)}",
                   "Install Blender 4.2+ and put it on PATH, or unpack it to tools/blender/")
        else:
            report("Blender (optional)", PASS, "not installed (no lesson needs it)")


def check_youtube() -> None:
    client = (ROOT / "local" / "youtube_client.bin").exists()
    token = (ROOT / "local" / "youtube_token.bin").exists()
    if token:
        report("YouTube (optional)", PASS, "connected (encrypted token in local/)")
    elif client:
        report("YouTube (optional)", PASS, "OAuth client added; not connected (click Connect YouTube in the web UI)")
    else:
        report("YouTube (optional)", PASS, "not set up (optional; see docs/YouTube_Setup_Guide.pdf)")


def check_frontend() -> None:
    node, npm = shutil.which("node"), shutil.which("npm")
    if not node or not npm:
        report("Node.js (web UI)", WARN, "node/npm not found: the web UI cannot run (the CLI works)",
               "winget install --id OpenJS.NodeJS.LTS   then open a new terminal")
        return
    version = run([node, "--version"]).stdout.strip()
    major = int(re.sub(r"\D", "", version.split(".")[0]) or 0)
    if major < 20:
        report("Node.js (web UI)", WARN, f"{version}: Next.js 16 needs Node 20.9+", "winget install --id OpenJS.NodeJS.LTS")
    elif not (ROOT / "frontend" / "node_modules").is_dir():
        report("Node.js (web UI)", WARN, f"{version}; frontend packages not installed", "npm run setup")
    else:
        report("Node.js (web UI)", PASS, f"{version}; frontend packages installed")


def http_ok(url: str) -> dict | bool:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            body = response.read()
            try:
                return json.loads(body)
            except ValueError:
                return response.status == 200
    except Exception:
        return False


def check_servers() -> None:
    api = http_ok("http://127.0.0.1:8765/api/health")
    web = http_ok("http://127.0.0.1:3000/")
    if api and web:
        busy = isinstance(api, dict) and api.get("busy")
        report("Web app", PASS, f"API :8765 and UI :3000 running{' (a job is running)' if busy else ''}")
    elif api or web:
        report("Web app", WARN, f"only the {'API (:8765)' if api else 'UI (:3000)'} is running", "npm run dev")
    else:
        report("Web app", PASS, "not running (start it with: npm run dev)")


# ------------------------------------------------------------------ live tests

def render_test() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="lms_health_"))
    started = time.time()
    try:
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        result = run([sys.executable, "-m", "manim", "render", "tests/test_scene.py", "HelloStudents", "-ql",
                      "--media_dir", str(tmp / "media"), "--disable_caching"], cwd=ROOT, env=env)
        videos = list((tmp / "media").rglob("HelloStudents.mp4"))
        if result.returncode == 0 and videos:
            report("Render test", PASS, f"Manim + FFmpeg rendered a test scene ({time.time() - started:.0f}s)")
        else:
            tail = (result.stdout + result.stderr).strip().splitlines()[-3:]
            report("Render test", FAIL, "Manim render failed: " + " | ".join(tail)[:300],
                   "python scripts/render_preview.py tests/test_scene.py   shows the full error")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def speech_test() -> None:
    from src.audio.tts_engine import XTTSEngine
    from src.audio.voice_manager import VoiceManager
    from src.config.settings import load_settings, resolve_device
    from src.subtitles.whisper_alignment import Aligner

    tmp = Path(tempfile.mkdtemp(prefix="lms_health_"))
    text = "Hello students, this is a short test."
    try:
        settings = load_settings()
        device = resolve_device(settings["compute"]["device"])
        voice = VoiceManager().get(settings["voice"]["default"])
        wav = tmp / "tts_test.wav"
        started = time.time()
        try:
            XTTSEngine(device).synthesize(text, voice, "en", wav)
            import soundfile as sf

            duration = sf.info(str(wav)).duration
            report("TTS test", PASS, f"XTTS spoke {duration:.1f}s with '{voice.id}' ({time.time() - started:.0f}s incl. model load)")
        except Exception as exc:
            report("TTS test", FAIL, str(exc).splitlines()[0][:200], "See SUPPORT_FOR_CLAUDE.md > Common errors")
            return
        started = time.time()
        try:
            data, _ = Aligner("en", device, tmp).align(wav, text, duration)
            if data is None:
                raise RuntimeError("whisperx is not installed")
            report("WhisperX test", PASS, f"aligned {len(data['words'])} words ({time.time() - started:.0f}s)")
        except Exception as exc:
            report("WhisperX test", FAIL, str(exc).splitlines()[0][:200], "See SUPPORT_FOR_CLAUDE.md > Common errors")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ main

def main() -> int:
    parser = argparse.ArgumentParser(description="Check that this PC can generate LMS videos.")
    parser.add_argument("--quick", action="store_true", help="skip the Manim render test")
    parser.add_argument("--full", action="store_true", help="also run real XTTS speech and WhisperX alignment")
    args = parser.parse_args()

    print("LMS VIDEO GENERATOR HEALTH CHECK\n")
    python_ok = check_python()
    venv_ok = check_venv()
    packages_ok = check_packages() if python_ok else False
    if packages_ok:
        check_import("Manim", "manim", "manim", "pip install -r requirements.txt")
        check_import("TTS (XTTS v2)", "TTS", "coqui-tts", "pip install -r requirements.txt")
        check_import("WhisperX", "whisperx", "whisperx", "pip install -r requirements.txt")
        check_web_packages()
    ffmpeg_ok = check_ffmpeg()
    check_latex()
    if packages_ok:
        check_device()
        check_models()
    check_directories()
    settings = check_settings() if packages_ok else None
    if packages_ok:
        check_voices(settings)
        check_blender(settings)
    check_cache()
    check_youtube()
    check_frontend()
    check_servers()
    if packages_ok and ffmpeg_ok and not args.quick:
        render_test()
    if packages_ok and args.full:
        print("\nRunning real speech tests (the first run downloads the models)...")
        speech_test()

    failed = [r for r in results if r[1] == FAIL]
    warned = [r for r in results if r[1] == WARN]
    print()
    if failed:
        print(f"NOT READY: {len(failed)} FAIL, {len(warned)} WARN (see the fix lines above)")
    elif warned:
        print(f"READY ({len(warned)} warning(s): optional parts or first-run downloads)")
    else:
        print("READY")
    if not venv_ok:
        print("(checked outside .venv: results describe that other Python, not the project)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
