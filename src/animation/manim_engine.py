"""Runs Manim for the generator: a fast extraction dry run, or a real render."""

from __future__ import annotations

import ast
import json
import re
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from src.animation.timing import (MODE_ENV, OUTPUT_ENV, PAUSE_ENV, SCENE_MARKER, TIMING_ENV,  # noqa: F401 (SCENE_MARKER re-exported)
                                  VALIDATION_ENV)
from src.config.video_config import PROJECT_ROOT
from src.utils.errors import LMSError

# Windows: Manim runs with its own hidden console (its output is captured anyway), so it still starts
# when the console of the process that launched it is gone (else: exit code 0xC0000142).
OWN_CONSOLE = getattr(subprocess, "CREATE_NO_WINDOW", 0)

NARRATED_BASES = {"LMSScene", "LMS3DScene", "LMSMovingCameraScene"}


def find_scene_class(animation_file: Path, requested: str | None = None) -> str:
    """Name of the narrated scene class in ``animation.py`` (subclass of LMSScene/LMS3DScene)."""
    # utf-8-sig: Windows editors (and PowerShell) may save a byte-order mark.
    tree = ast.parse(animation_file.read_text(encoding="utf-8-sig"))
    classes = {
        node.name: {getattr(b, "id", getattr(b, "attr", "")) for b in node.bases}
        for node in tree.body if isinstance(node, ast.ClassDef)
    }
    if requested:
        if requested not in classes:
            raise LMSError(f"Scene class '{requested}' not found in {animation_file}.", f"Classes found: {', '.join(classes) or 'none'}")
        return requested
    narrated = [name for name, bases in classes.items() if bases & NARRATED_BASES]
    if len(narrated) == 1:
        return narrated[0]
    if not narrated:
        raise LMSError(
            f"{animation_file} has no narrated scene.",
            "Narrated videos need a class that extends LMSScene (or LMS3DScene):\n\n"
            "    from src.animation import LMSScene\n\n    class MyLessonVideo(LMSScene):\n        ...",
        )
    raise LMSError(f"{animation_file} has several narrated scenes: {', '.join(narrated)}.", "Choose one with --scene <ClassName>.")


_EXCEPTION_LINE = re.compile(r"^(?:[\w.]+\.)?(\w*(?:Error|Exception|Exit|Interrupt))(?::\s*(.*))?$")


def manim_failure(output: str, animation_file: Path, step: str, log_file: Path) -> LMSError:
    """Readable error from Manim's output: the exception first (with the line
    of animation.py it happened on), a hint for common causes, then the log tail."""
    lines = [l.rstrip() for l in output.splitlines() if l.strip()]
    # Manim prints tracebacks through rich (boxed, "│ ... │"); strip the frame.
    plain = [l.strip().strip("│").strip() for l in lines]
    exception = next((l for l in reversed(plain) if _EXCEPTION_LINE.match(l)), None)
    line_no, code = None, None
    name = animation_file.name
    for index, text in enumerate(plain):
        match = re.search(rf'{re.escape(name)}"?,? line (\d+)', text) or re.search(rf"{re.escape(name)}:(\d+)", text)
        if match:
            line_no = int(match.group(1))
    if line_no:
        try:
            code = animation_file.read_text(encoding="utf-8-sig").splitlines()[line_no - 1].strip()
        except (OSError, IndexError):
            code = None

    message = f"Manim failed while {step}."
    if exception:
        message += f"\n\n{exception}"
    if line_no:
        message += f"\n\nanimation.py line {line_no}" + (f":  {code}" if code else "")

    hints = []
    text = exception or ""
    if "No module named" in text:
        missing = re.search(r"No module named '([^']+)'", text)
        module = missing.group(1) if missing else "?"
        if module.split(".")[0] in ("lms", "lms_video", "lms_video_generator", "video_generator", "core", "lms_scene", "animation"):
            hints.append(f"'{module}' is not this project's framework. Import it with:\n"
                         "    from src.animation import LMSScene")
        else:
            hints.append(f"The Python package '{module}' is not installed in this project's .venv. "
                         f"Remove the import, or install it:  .venv\\Scripts\\pip install {module.split('.')[0]}")
    elif "latex" in output.lower() and ("error" in text.lower() or "latex" in text.lower()):
        hints.append("A Tex/MathTex string could not be typeset by LaTeX. Check it for unsupported characters "
                     "(emoji, unusual symbols) or use Text(...) for plain text.")
    elif "camera" in text and "frame" in text:
        hints.append("self.camera.frame needs a camera-capable scene: extend LMSMovingCameraScene instead of LMSScene.")
    tail = "\n".join(lines[-25:])
    hints.append(f"Manim output (last lines):\n{tail}\n\nFull log: {log_file}")
    return LMSError(message, "\n\n".join(hints), line=line_no)


def run_manim(
    animation_file: Path,
    scene_class: str,
    mode: str,
    output_file: Path,
    log_file: Path,
    quality_flag: str = "-ql",
    media_dir: Path | None = None,
    timing_file: Path | None = None,
    default_pause: float = 0.25,
    flush_cache: bool = False,
    on_line=None,
    validation: dict | None = None,
) -> Path | None:
    """Run ``manim render``.

    ``mode``:
      * "extract": dry run that records narrate() calls
      * "render":  real render; Manim reuses every animation whose content
        (mobjects, animation, run time) is unchanged from its partial-movie cache
      * "plan":    like render, but only reports which animations are cached

    ``on_line`` (optional) is called with every line Manim prints, as it
    prints it; the full output always goes to ``log_file``.

    ``validation``: settings.json > validation for the scene's layout checks
    (None: the scene reads settings.json itself).

    Returns the rendered MP4 (render mode) or None.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(PROJECT_ROOT), env.get("PYTHONPATH")]))
    env[MODE_ENV] = mode
    env[OUTPUT_ENV] = str(output_file)
    env[PAUSE_ENV] = str(default_pause)
    env["PYTHONDONTWRITEBYTECODE"] = "1"   # no __pycache__ folders inside lesson directories
    # Fixed hash seed: some animations (e.g. TransformMatchingShapes) key on
    # Python's per-process randomised hash(), which would give them a new
    # cache key on every run and force a pointless re-render.
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONUNBUFFERED"] = "1"          # lines reach on_line as they are printed
    env["PYTHONIOENCODING"] = "utf-8"
    env.pop(TIMING_ENV, None)
    env.pop(VALIDATION_ENV, None)
    if validation is not None:
        env[VALIDATION_ENV] = json.dumps(validation)
    if timing_file is not None:
        env[TIMING_ENV] = str(timing_file)

    cmd = [sys.executable, "-m", "manim", "render", str(animation_file), scene_class, quality_flag]
    if media_dir is not None:
        cmd += ["--media_dir", str(media_dir)]
    if mode == "extract":
        cmd.append("--dry_run")
    elif flush_cache and media_dir is not None:
        # --force-render: drop this scene's cached animation clips BEFORE the
        # render, so it re-renders everything and refills the cache. (Manim's
        # own --flush_cache deletes the cache AFTER rendering, leaving none.)
        for folder in (media_dir / "videos").glob(f"*/*/partial_movie_files/{scene_class}"):
            shutil.rmtree(folder, ignore_errors=True)
    # Render/plan keep Manim's partial-movie cache ON: LMSScene counts frames
    # itself, so narration placement stays exact for cached animations too.

    started = time.time()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("w", encoding="utf-8", errors="replace") as log:
        if on_line is None:
            returncode = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                        creationflags=OWN_CONSOLE).returncode
        else:
            proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding="utf-8", errors="replace", creationflags=OWN_CONSOLE)
            for line in proc.stdout:
                log.write(line)
                on_line(line.rstrip("\r\n"))
            returncode = proc.wait()
    if returncode != 0:
        step = "reading the narration from animation.py" if mode == "extract" else "rendering the animation"
        raise manim_failure(log_file.read_text(encoding="utf-8", errors="replace"), animation_file, step, log_file)
    if not output_file.exists():
        raise LMSError(f"Manim finished but did not write {output_file.name}.", "Does the scene class extend LMSScene?")
    if mode in ("extract", "plan"):
        return None

    videos =[p for p in (media_dir / "videos").rglob(f"{scene_class}.mp4")
              if "partial_movie_files" not in p.parts and p.stat().st_mtime >= started - 1]
    if not videos:
        raise LMSError("Manim finished but produced no video (does the scene play any animations?).", f"Log: {log_file}")
    return videos[0]
