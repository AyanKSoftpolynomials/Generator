"""Generator side of the Blender engine: render clips headlessly, splice them in.

After Manim has rendered a lesson (with the narration-driven, frame-exact
timeline), every ``self.blender(...)`` segment in timeline.json is:

  1. rendered by Blender in background mode (``blender -b ... --python
     runner.py``) to PNG frames, in the job's/lesson's own media folder;
  2. encoded to H.264 with the project's FFmpeg (exactly ``frames`` frames);
  3. cached in cache/blender/<key>.mp4 (key: the lesson's Blender code, the
     src/blender toolkit, the clip's frames/size/fps, its word timings, its
     params and the Blender version/settings), written atomically;
  4. spliced into the Manim video over exactly its frame range.

The result is an ordinary video file, so subtitles, the narration track and
the final FFmpeg composition run unchanged.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import time
import uuid
from functools import lru_cache
from pathlib import Path

from src.config.video_config import PROJECT_ROOT
from src.utils.errors import LMSError
from src.video.ffmpeg import ffmpeg_path, ffprobe_path

BLENDER_CACHE = PROJECT_ROOT / "cache" / "blender"
RUNNER = Path(__file__).with_name("runner.py")
PORTABLE = [PROJECT_ROOT / "tools" / "blender" / "blender.exe", PROJECT_ROOT / "tools" / "blender" / "blender"]
NARRATED_BASES = {"LMSScene", "LMS3DScene", "LMSMovingCameraScene"}


def find_blender(settings: dict) -> Path:
    configured = (settings.get("blender") or {}).get("path") or os.environ.get("BLENDER_PATH")
    candidates = [Path(configured)] if configured else []
    candidates += PORTABLE
    found = shutil.which("blender")
    if found:
        candidates.append(Path(found))
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    raise LMSError(
        "This lesson has 3D (Blender) sections, but Blender was not found.",
        "Install Blender 4.2+ (https://www.blender.org/download/) and either put it on PATH, set\n"
        'settings.json > blender.path, or unpack the portable zip to tools/blender/ (see README).',
    )


@lru_cache(maxsize=4)
def blender_version(executable: str) -> str:
    out = subprocess.run([executable, "--version"], capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=120).stdout
    return (out.splitlines() or ["unknown"])[0].strip()


def fingerprint(settings: dict) -> dict:
    """What decides how Blender clips look (part of the render cache key of lessons that use Blender)."""
    cfg = settings.get("blender") or {}
    try:
        version = blender_version(str(find_blender(settings)))
    except LMSError:
        version = "missing"
    return {"engine": cfg.get("engine", "EEVEE"), "samples": cfg.get("samples", 16), "version": version,
            "toolkit": _toolkit_hash()}


def uses_blender(animation_file: Path) -> bool:
    return "self.blender(" in animation_file.read_text(encoding="utf-8-sig")


def _toolkit_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def blender_source(animation_file: Path) -> str:
    """animation.py without its Manim lesson class(es): editing the 2D part never
    invalidates the 3D clips, editing the 3D code (or shared constants) does."""
    source = animation_file.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    parts = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = {getattr(b, "id", getattr(b, "attr", "")) for b in node.bases}
            if bases & NARRATED_BASES:
                continue
        parts.append(ast.get_source_segment(source, node) or "")
    return "\n".join(parts)


def apply_segments(animation_file: Path, timeline: dict, video: Path, media_dir: Path, preset: str,
                   settings: dict, log=print, progress=None) -> Path:
    """Render every Blender segment and splice them into ``video``. Returns the new video."""
    segments = timeline.get("blender") or []
    if not segments:
        return video
    executable = find_blender(settings)
    width, height = _video_size(video)
    fps = float(timeline["fps"])
    cfg = settings.get("blender") or {}
    code = blender_source(animation_file)
    base = {"code": hashlib.sha256(code.encode("utf-8")).hexdigest(), **fingerprint(settings),
            "width": width, "height": height, "fps": fps}

    clips = []
    for index, seg in enumerate(segments, 1):
        key = hashlib.sha256(json.dumps({**base, "segment": {k: seg[k] for k in (
            "scene_class", "frames", "params", "narrations")}}, sort_keys=True).encode()).hexdigest()[:24]
        clip = BLENDER_CACHE / f"{key}.mp4"
        label = f"{seg['id']} ({seg['scene_class']}, {seg['frames']} frames)"
        if clip.exists():
            log(f"  [CACHE HIT] Blender clip: {label}")
        else:
            log(f"  [CACHE MISS] Blender clip: {label}: rendering headlessly...")
            if progress:
                progress(f"Rendering 3D clip {index} of {len(segments)} with Blender: {seg['scene_class']}")
            started = time.time()
            _render(executable, animation_file, seg, fps, width, height, cfg, media_dir, clip)
            log(f"      ✓ {seg['id']} rendered in {time.time() - started:.1f}s")
        clips.append((seg, clip))

    out = media_dir / "videos" / "lms_blender" / preset / f"{video.stem}.mp4"
    _splice(video, clips, out, fps)
    log(f"  ✓ {len(clips)} Blender clip(s) spliced into the video")
    return out


def _render(executable: Path, animation_file: Path, seg: dict, fps: float, width: int, height: int,
            cfg: dict, media_dir: Path, clip: Path) -> None:
    import manim  # the names the runner stands in for while loading animation.py

    work = media_dir / "blender" / f"{seg['id']}_{uuid.uuid4().hex[:8]}"   # this job's own folder
    frames_dir = work / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    job = {
        "project_root": str(PROJECT_ROOT),
        "animation": str(Path(animation_file).resolve()),
        "scene_class": seg["scene_class"],
        "params": seg["params"],
        "narrations": seg["narrations"],
        "fps": fps, "frames": seg["frames"], "width": width, "height": height,
        "engine": cfg.get("engine", "EEVEE"), "samples": int(cfg.get("samples", 16)),
        "frames_dir": str(frames_dir),
        "manim_names": [n for n in dir(manim) if not n.startswith("_")],
    }
    (work / "job.json").write_text(json.dumps(job), encoding="utf-8")
    log_file = work / "blender.log"
    with log_file.open("w", encoding="utf-8", errors="replace") as out:
        # -b: background (no window, no UI); --factory-startup: ignore any user prefs/add-ons.
        code = subprocess.run(
            [str(executable), "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(RUNNER),
             "--", str(work / "job.json")],
            stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=PROJECT_ROOT,
        ).returncode
    text = log_file.read_text(encoding="utf-8", errors="replace")
    rendered = sorted(frames_dir.glob("frame_*.png"))
    if code != 0 or "LMS-BLENDER-ERROR" in text or len(rendered) != seg["frames"]:
        detail = text.split("LMS-BLENDER-ERROR", 1)[-1].strip(": \n") if "LMS-BLENDER-ERROR" in text else \
            "\n".join(text.splitlines()[-20:])
        raise LMSError(f"Blender failed to render the 3D clip '{seg['id']}' ({seg['scene_class']}).\n\n{detail[-3000:]}",
                       f"Full Blender log (kept for debugging): {log_file}")
    BLENDER_CACHE.mkdir(parents=True, exist_ok=True)
    staged = BLENDER_CACHE / f".{clip.stem}.{uuid.uuid4().hex[:8]}.mp4"
    _ffmpeg(["-framerate", f"{fps}", "-start_number", "1", "-i", str(frames_dir / "frame_%04d.png"),
             "-frames:v", str(seg["frames"]), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(staged)],
            "encoding a Blender clip")
    os.replace(staged, clip)                                       # atomic: concurrent jobs may share the cache
    shutil.rmtree(work, ignore_errors=True)


def _splice(video: Path, clips: list[tuple[dict, Path]], out: Path, fps: float) -> None:
    """Replace each segment's frame range of ``video`` by its Blender clip (frame-exact)."""
    width, height = _video_size(video)
    inputs, filters, labels, cursor = ["-i", str(video)], [], [], 0
    fmt = f"scale={width}:{height},setsar=1,format=yuv420p,fps={fps}"
    for n, (seg, clip) in enumerate(sorted(clips, key=lambda c: c[0]["start_frame"]), 1):
        start, end = seg["start_frame"], seg["start_frame"] + seg["frames"]
        if start > cursor:
            filters.append(f"[0:v]trim=start_frame={cursor}:end_frame={start},setpts=PTS-STARTPTS,{fmt}[m{n}]")
            labels.append(f"[m{n}]")
        inputs += ["-i", str(clip)]
        filters.append(f"[{n}:v]trim=end_frame={seg['frames']},setpts=PTS-STARTPTS,{fmt}[b{n}]")
        labels.append(f"[b{n}]")
        cursor = end
    filters.append(f"[0:v]trim=start_frame={cursor},setpts=PTS-STARTPTS,{fmt}[tail]")
    labels.append("[tail]")
    graph = ";".join(filters) + f";{''.join(labels)}concat=n={len(labels)}:v=1:a=0[out]"
    out.parent.mkdir(parents=True, exist_ok=True)
    staged = out.with_name(f".{out.stem}.{uuid.uuid4().hex[:8]}.mp4")
    _ffmpeg([*inputs, "-filter_complex", graph, "-map", "[out]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-crf", "16", "-r", f"{fps}", str(staged)], "splicing the 3D clips into the video")
    os.replace(staged, out)


def _video_size(video: Path) -> tuple[int, int]:
    out = subprocess.run([ffprobe_path(), "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    w, h = out.strip().split(",")[:2]
    return int(w), int(h)


def _ffmpeg(args: list[str], step: str) -> None:
    result = subprocess.run([ffmpeg_path(), "-v", "error", "-y", *args], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise LMSError(f"FFmpeg failed while {step}.\n\n{result.stderr[-2000:]}")
