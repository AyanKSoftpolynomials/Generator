"""POST /api/analyze: read the narration out of a pasted animation.py.

Uses the generator's own extraction (the Manim dry run in a subprocess that
records every ``narrate()`` / ``scene_start()`` call) and its own parser and
voice resolution, so the browser sees exactly what a generation would use.
The code runs in a scratch folder; the lesson folder is not touched.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
import time

from src.animation.manim_engine import run_manim
from src.audio.voice_manager import VoiceManager
from src.config.video_config import PROJECT_ROOT
from src.pipeline.build_cache import framework_hash
from src.script.parser import parse_extracted
from src.script.validator import validate_script

from backend.lessons import check_source, last_clip_info, lesson_dir, normalise_source, read_animation

ANALYZE_DIR = PROJECT_ROOT / "cache" / "analyze"
TEX_POOL = ANALYZE_DIR / "_tex"      # compiled formulas (SVG) shared by all analyses
KEEP_ANALYSES = 30


def analysis_digest(source: str, slug: str, settings: dict) -> str:
    """Cache identity of one analysis: SHA-256 of the animation.py CONTENT (+ framework, lesson, validation)."""
    validation = settings.get("validation")
    return hashlib.sha256(f"{framework_hash()}\n{slug}\n{json.dumps(validation, sort_keys=True)}\n{normalise_source(source)}"
                          .encode("utf-8")).hexdigest()[:20]


def forget_analysis(source: str, slug: str, settings: dict) -> bool:
    """Delete the cached analysis of exactly this script (the shared compiled-LaTeX pool is kept)."""
    folder = ANALYZE_DIR / analysis_digest(source, slug, settings)
    if not folder.is_dir():
        return False
    shutil.rmtree(folder, ignore_errors=True)
    return True


def analyze(source: str, slug: str, settings: dict, voices: VoiceManager) -> dict:
    started = time.time()
    source = normalise_source(source)
    scene_class = check_source(source)
    validation = settings.get("validation")
    digest = analysis_digest(source, slug, settings)
    work = ANALYZE_DIR / digest / slug
    extracted = work / "extracted.json"
    if not extracted.exists():
        work.mkdir(parents=True, exist_ok=True)
        (work / "animation.py").write_bytes(source.encode("utf-8"))
        # Private media folder: several analyses (tabs) may run at once, and Manim
        # deletes the non-SVG LaTeX files in its Tex folder after every formula.
        media = work / "media"
        _share_svgs(TEX_POOL, media / "Tex")
        run_manim(work / "animation.py", scene_class, "extract", extracted, work / "extract.log",
                  media_dir=media, default_pause=float(settings["audio"]["pause_after"]), validation=validation)
        _share_svgs(media / "Tex", TEX_POOL)
        _prune()

    raw = json.loads(extracted.read_text(encoding="utf-8"))
    script = parse_extracted(raw, slug, settings["voice"].get("default"), settings["voice"].get("aliases"))
    warnings = validate_script(script, voices, check_voices=False)   # ids / text; voices checked below
    layout = raw.get("validation") or None     # layout checks (text in boxes, frame, ...): own panel in the UI
    known = set(voices.list_ids())
    titles = {s["id"]: s.get("title") for s in script.scenes}

    narrations = []
    for block in script.narration:
        last = last_clip_info(slug, block.id)
        same_text = last.get("text") == block.text
        narrations.append({
            "id": block.id,
            "scene": block.scene,
            "sceneTitle": titles.get(block.scene),
            "text": block.text,
            "voice": block.voice,
            "voiceSource": block.voice_source,
            "voiceMissing": bool(block.voice) and block.voice not in known,
            "subtitle": block.subtitle,
            "pauseAfter": block.pause_after,
            "estimatedDuration": round(block.estimated_duration, 1),
            # Real duration of the last generated clip, when the text is unchanged.
            "lastDuration": round(last["duration"], 2) if same_text and last.get("duration") else None,
            "lastVoice": last.get("voice") if same_text else None,
        })
    missing = sorted({n["voice"] for n in narrations if n["voiceMissing"]})
    if missing:
        warnings.append(f"Voice(s) not in the library: {', '.join(missing)}. Choose a voice for those blocks.")

    try:
        saved = read_animation(slug)
    except (FileNotFoundError, ValueError):
        saved = None
    return {
        "lessonId": slug,
        "lesson": {
            "id": script.lesson_id,
            "title": script.title,
            "className": script.scene_class or scene_class,
            "language": script.language,
            "defaultVoice": script.default_voice,
            "subtitles": script.subtitles,
        },
        "scenes": [{
            "id": s["id"], "title": s.get("title"), "voice": s.get("voice"), "engine": s.get("engine", "MANIM"),
            "narrations": sum(1 for n in narrations if n["scene"] == s["id"]),
        } for s in script.scenes],
        "narrations": narrations,
        "warnings": warnings,
        "layout": layout,
        "lessonExists": lesson_dir(slug).joinpath("animation.py").exists(),
        "matchesSavedLesson": saved == source,
        "seconds": round(time.time() - started, 1),
    }


def _share_svgs(source: Path, target: Path) -> None:
    """Hard-link compiled formulas (content-hashed .svg files, never rewritten) from source to target."""
    if not source.is_dir():
        return
    target.mkdir(parents=True, exist_ok=True)
    for svg in source.glob("*.svg"):
        destination = target / svg.name
        if destination.exists():
            continue
        try:
            os.link(svg, destination)
        except FileExistsError:
            pass
        except OSError:
            shutil.copy2(svg, destination)


def _prune() -> None:
    folders = sorted((p for p in ANALYZE_DIR.iterdir() if p.is_dir() and not p.name.startswith("_")),
                     key=lambda p: p.stat().st_mtime, reverse=True)
    for old in folders[KEEP_ANALYSES:]:
        shutil.rmtree(old, ignore_errors=True)
