"""The video generator: animation.py in, narrated MP4 (+ subtitles) out.

    animation.py --(dry run)--> generated/script.json
        --> voices resolved + validated
        --> XTTS clip per narration --> normalised      (audio/<id>.wav + .meta.json)
        --> WhisperX word timings  --> generated/timing.json
        --> Manim render driven by timing.json --> generated/timeline.json
        --> narration track placed on the timeline
        --> SRT/VTT subtitles (optional)
        --> final MP4 (+ metadata.json report)

Incremental build: every stage hashes exactly the inputs that affect its
output and is skipped when the hash matches the last successful build
(see ``build_cache.py``). Models are loaded only when a stage actually has
work to do, and at most once per run.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from src.audio.audio_cache import AudioCache
from src.audio.audio_composer import concatenate, place_clips
from src.audio.audio_processor import audio_duration, normalize
from src.audio.audio_timing import format_duration, read_timing, write_timing
from src.audio.tts_engine import TTSEngine, create_engine, engine_fingerprint
from src.audio.voice_manager import VoiceManager
from src.animation.manim_engine import SCENE_MARKER, find_scene_class, run_manim
from src.animation.timing import estimate_duration
from src.config.settings import deep_merge, load_settings, resolve_device
from src.config.video_config import MEDIA_DIR, QUALITY_PRESETS
from src.pipeline.build_cache import BuildManifest, framework_hash, hash_file, hash_files, hash_value, lesson_asset_files
from src.script.models import LessonScript
from src.script.parser import parse_extracted
from src.script.validator import validate_script
from src.subtitles.srt_generator import write_srt
from src.subtitles.subtitle_config import SubtitleSettings, build_cues
from src.subtitles.vtt_generator import write_vtt
from src.subtitles.whisper_alignment import ALIGN_VERSION, Aligner, estimated_alignment
from src.utils.errors import LMSError
from src.validation.report import errors as layout_errors, format_issue, format_report, one_line
from src.video.compositor import compose
from src.video.ffmpeg import ffmpeg_path

HIT, MISS = "[CACHE HIT]", "[CACHE MISS]"


@dataclass
class GenerateOptions:
    quality: str = "preview"             # "preview" or "final"
    audio_only: bool = False
    subtitles_only: bool = False
    subtitles: bool | None = None        # None = use settings / lesson
    audio: bool | None = None            # None = use settings
    voice_override: str | None = None    # force one voice for every narration
    voice_assignments: dict[str, str] | None = None   # narration id -> voice (per-block override)
    scene_class: str | None = None
    output_name: str | None = None       # custom MP4 file name (without extension)
    # incremental build controls
    force: bool = False                  # rebuild every stage
    force_tts: bool = False
    force_alignment: bool = False
    force_render: bool = False
    force_compose: bool = False
    dry_run: bool = False                # report hits/misses, generate nothing
    workers: int | None = None           # parallel TTS workers (None = settings, default 1)
    # Set by the web backend, which builds each job in its own workspace folder:
    lesson_name: str | None = None       # lesson id when the folder name is not it (default: folder name)
    media_dir: Path | None = None        # Manim media folder (default: output/media/<lesson>_narrated)

    def __post_init__(self):
        if self.force:
            self.force_tts = self.force_alignment = self.force_render = self.force_compose = True


@dataclass
class LessonPaths:
    root: Path

    def __post_init__(self):
        self.animation = self.root / "animation.py"
        self.generated = self.root / "generated"
        self.audio = self.root / "audio"
        self.alignment = self.root / "alignment"
        self.subtitles = self.root / "subtitles"
        self.output = self.root / "output"
        self.logs = self.generated / "logs"
        self.extracted = self.generated / "extracted.json"
        self.script = self.generated / "script.json"
        self.timing = self.generated / "timing.json"
        self.timeline = self.generated / "timeline.json"
        self.metadata = self.generated / "metadata.json"
        self.manifest = self.generated / "build_cache.json"
        self.manim_meta = self.generated / "manim"
        self.alignment_file = self.alignment / "alignment.json"
        self.alignment_meta = self.alignment / "alignment.meta.json"
        self.track = self.audio / "narration_track.wav"


@dataclass
class Report:
    steps: dict = field(default_factory=dict)          # stage -> seconds
    generated: list = field(default_factory=list)      # narration ids synthesised this run
    cached: list = field(default_factory=list)         # narration ids reused
    warnings: list = field(default_factory=list)
    outputs: dict = field(default_factory=dict)
    status: dict = field(default_factory=dict)         # stage -> "cached" / "generated" / ...
    manim_sections: dict = field(default_factory=dict) # section -> (rendered plays, total plays)
    layout: dict = field(default_factory=dict)         # layout validation results (src/validation)
    title: str = ""
    total_seconds: float = 0.0


class VideoGenerator:
    def __init__(
        self,
        lesson_dir: Path,
        options: GenerateOptions | None = None,
        settings: dict | None = None,
        voices: VoiceManager | None = None,
        cache: AudioCache | None = None,
        engine: TTSEngine | None = None,
        log=print,
        progress=None,
    ):
        self.paths = LessonPaths(Path(lesson_dir).resolve())
        self.options = options or GenerateOptions()
        self.lesson_name = self.options.lesson_name or self.paths.root.name
        self.settings = settings or load_settings()
        self.voices = voices or VoiceManager()
        self.cache = cache or AudioCache()
        self._engine = engine
        self._engine_injected = engine is not None
        self.log = log
        # Optional structured progress callback (used by the web backend):
        # receives dicts like {"kind": "stage_start", "stage": "TTS"}.
        self.progress = progress
        self.report = Report()
        self.manifest = BuildManifest(self.paths.manifest)
        self._aligner: Aligner | None = None
        self._voice_fp: dict[str, str] = {}

    # ------------------------------------------------------------------ run

    def run(self) -> Report:
        started = time.time()
        if self.options.subtitles_only:
            report = self._subtitles_only()
            report.total_seconds = time.time() - started
            return report
        if self.options.dry_run:
            report = self.plan()
            report.total_seconds = time.time() - started
            return report

        self._check_environment()
        script = self._step("Script", "Loading lesson", self.extract_script)
        self.report.title = script.title or script.lesson_id
        audio_on = self._audio_enabled()

        if audio_on:
            self.load_voices(script)
            clips = self._step("TTS", "Generating narration", lambda: self.generate_audio(script))
            timing = self._step("WhisperX", "Alignment", lambda: self.align(script, clips))
        else:
            self.log("Audio disabled: rendering visuals only (timing estimated from the text).")
            timing = {}
            self.paths.timing.unlink(missing_ok=True)

        if self.options.audio_only:
            self._step("FFmpeg", "Building narration track", lambda: self.audio_only_track(script, timing))
            return self._finish(script, started)

        video = self._step("Manim", "Manim animation", lambda: self.render(script, audio_on))
        timeline = json.loads(self.paths.timeline.read_text(encoding="utf-8"))
        subtitle_files = self._step("Subtitles", "Subtitles", lambda: self.write_subtitles(script, timing, timeline))
        self._step("FFmpeg", "Final composition", lambda: self.compose_video(script, video, timing, timeline, subtitle_files, audio_on))
        return self._finish(script, started)

    # ---------------------------------------------------------- extraction

    def _extract_key(self) -> str:
        return hash_value({
            "animation": hash_file(self.paths.animation),
            "framework": framework_hash(),
            "scene": self.options.scene_class,
            "pause": self.settings["audio"]["pause_after"],
            "validation": self.settings.get("validation"),
        })

    def extract_script(self, target: Path | None = None) -> LessonScript:
        if not self.paths.animation.exists():
            raise LMSError(f"No animation.py in {self.paths.root}.", "Each lesson folder needs an animation.py (see lessons/README.md).")
        scene_class = find_scene_class(self.paths.animation, self.options.scene_class)
        key = self._extract_key()
        extracted = target or self.paths.extracted
        if target is None and self.manifest.matches("extract", key, extracted):
            self.log(f"  {HIT} Script extraction (animation.py unchanged)")
        else:
            self.log(f"  {MISS} Script extraction: reading narrate() calls from animation.py...")
            # Own media folder (not the shared output/media): LaTeX scratch files of
            # concurrent runs must not meet (Manim deletes non-SVG files after each formula).
            run_manim(self.paths.animation, scene_class, "extract", extracted, self.paths.logs / "extract.log",
                      media_dir=self._media_dir(), default_pause=float(self.settings["audio"]["pause_after"]),
                      validation=self.settings.get("validation"))
            if target is None:
                self.manifest.record("extract", key)
        raw = json.loads(extracted.read_text(encoding="utf-8"))
        script = parse_extracted(raw, self.lesson_name, self.settings["voice"].get("default"),
                                 self.settings["voice"].get("aliases"))
        self._apply_voice_choices(script)
        self.report.warnings += validate_script(script, self.voices, check_voices=self._audio_enabled())
        self.check_layout(raw.get("validation"))
        if target is None:
            script.save(self.paths.script)
        self.log(f"  ✓ {script.title or script.lesson_id}: {len(script.narration)} narration blocks, "
                 f"{len(script.scenes)} sections ({scene_class})")
        self._emit("script", title=script.title or script.lesson_id, narrations=len(script.narration),
                   scenes=len(script.scenes), voices={b.id: b.voice for b in script.narration})
        return script

    def check_layout(self, results: dict | None, fail: bool = True) -> None:
        """Report the layout checks made during extraction (src/validation). ERRORs stop
        the run here, before any audio or video is made, unless fail_on_error is off."""
        if not results:
            return
        self.report.layout = results
        issues = results.get("issues", [])
        self._emit("validation", summary=results.get("summary", {}), issues=issues)
        if not issues:
            self.log("  ✓ Layout validation: no problems found")
            return
        self.log("  " + format_report(results).replace("\n", "\n  "))
        found = layout_errors(results)
        if found and fail and results.get("config", {}).get("fail_on_error", False):
            raise LMSError(
                f"Layout validation found {len(found)} error(s) in animation.py:\n\n"
                + "\n\n".join(format_issue(i) for i in found),
                "Fix the layout and generate again. To render anyway (problems listed as warnings), set\n"
                "settings.json > validation.fail_on_error to false, or in the lesson class:\n"
                "    layout_validation = {\"fail_on_error\": False}",
                line=found[0].get("line"),
            )
        self.report.warnings += [one_line(i) for i in issues if i["severity"] != "INFO"]

    def _apply_voice_choices(self, script: LessonScript) -> None:
        """--voice (one voice for everything), then per-block assignments.

        Assignments are the most specific level of the voice hierarchy
        (assignment > narrate(voice=) > scene > lesson > global). They never
        touch animation.py; they only change which voice synthesises a block.
        """
        if self.options.voice_override:
            for block in script.narration:
                block.voice, block.voice_source = self.options.voice_override, "override"
        assignments = self.options.voice_assignments or {}
        ids = {b.id for b in script.narration}
        for narration_id in sorted(set(assignments) - ids):
            self.report.warnings.append(f"Voice assignment for unknown narration '{narration_id}' ignored.")
        for block in script.narration:
            chosen = assignments.get(block.id)
            if chosen and chosen != block.voice:
                block.voice, block.voice_source = chosen, "assigned"

    def load_voices(self, script: LessonScript) -> None:
        for voice_id in script.voices_used:
            self.voices.require(voice_id)

    # ----------------------------------------------------------------- TTS

    def _processing(self) -> dict:
        audio_cfg = self.settings["audio"]
        return {k: audio_cfg[k] for k in ("sample_rate", "loudness_lufs", "trim_silence")}

    def _voice_fingerprint(self, voice_id: str) -> str:
        if voice_id not in self._voice_fp:
            self._voice_fp[voice_id] = self.voices.get(voice_id).fingerprint()
        return self._voice_fp[voice_id]

    def _engine_fingerprint(self, voice_id: str) -> str:
        if self._engine is not None:
            return self._engine.voice_fingerprint(voice_id)
        return engine_fingerprint(self.settings["audio"]["engine"], self.settings, voice_id)   # no model load

    def audio_key(self, block, language: str) -> str:
        return self.cache.key(block.text, self._voice_fingerprint(block.voice), language,
                              self._engine_fingerprint(block.voice), self._processing())

    def generate_audio(self, script: LessonScript) -> dict[str, dict]:
        self.paths.audio.mkdir(parents=True, exist_ok=True)
        processing = self._processing()
        plan = []
        for block in script.narration:
            key = self.audio_key(block, script.language)
            cached = self.cache.has(key) and not self.options.force_tts
            plan.append((block, key, cached))

        misses = [(b, k) for b, k, c in plan if not c]
        self._tts_done, self._tts_total = 0, len(plan)
        for block, key, cached in plan:
            if cached:
                self.log(f"  {HIT} TTS: {block.id} → {block.voice}")
                self._tts_progress(block.id, cached=True)
        if misses:
            self._synthesize_all(misses, script.language, processing)

        clips = {}
        for block, key, cached in plan:
            target = self.paths.audio / f"{block.id}.wav"
            meta_path = self.paths.audio / f"{block.id}.meta.json"
            meta = _read_json(meta_path)
            if not (target.exists() and meta.get("input_hash") == key):
                shutil.copy2(self.cache.path(key), target)
            duration = meta.get("duration") if meta.get("input_hash") == key else None
            if duration is None:
                duration = audio_duration(target)
            profile = self.voices.get(block.voice)
            meta = {
                "input_hash": key,
                "text": block.text,
                "voice": block.voice,
                "voice_reference_hash": self._voice_fingerprint(block.voice),
                "voice_samples": [s.name for s in profile.samples],
                "language": script.language,
                "tts_settings": {"engine_fingerprint": self._engine_fingerprint(block.voice), **processing},
                "duration": round(duration, 4),
            }
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            clips[block.id] = {"audio": target, "duration": duration, "voice": block.voice, "cache_key": key}
            (self.report.cached if cached else self.report.generated).append(block.id)

        speech = sum(c["duration"] for c in clips.values())
        self._emit("cache", stage="TTS", generated=len(self.report.generated), cached=len(self.report.cached))
        self.report.status["TTS"] = f"Generated: {len(self.report.generated)}\n  Cached: {len(self.report.cached)}"
        self.log(f"  Total speech: {format_duration(speech)}  "
                 f"(generated {len(self.report.generated)}, reused {len(self.report.cached)} from cache)")
        return clips

    def _workers(self) -> int:
        workers = self.options.workers or int(self.settings["audio"].get("workers", 1))
        return max(1, workers)

    def _synthesize_all(self, misses, language: str, processing: dict) -> None:
        """Generate the missing clips.

        One worker: this process, model loaded once and reused for every clip.
        N workers: N processes, each loading its own model once (XTTS inference
        is not thread-safe, so threads are not an option).
        """
        for block, _ in misses:
            self.log(f"  {MISS} TTS: {block.id} → {block.voice}")
        workers = min(self._workers(), len(misses))
        if workers > 1 and not self._engine_injected:
            self._synthesize_parallel(misses, language, processing, workers)
            return

        engine = self.engine()
        for index, (block, key) in enumerate(misses):
            self._emit("progress", stage="TTS", done=self._tts_done, total=self._tts_total,
                       message=f"Generating {block.id} with {block.voice} ({self._tts_done + 1}/{self._tts_total})")
            started = time.time()
            tmp = self.cache.staging_path(key, ".raw.wav")     # unique: other jobs may share the cache
            staged = self.cache.staging_path(key)
            engine.synthesize(block.text, self.voices.get(block.voice), language, tmp)
            normalize(tmp, staged, sample_rate=processing["sample_rate"],
                      loudness_lufs=processing["loudness_lufs"], trim_silence=processing["trim_silence"])
            self.cache.commit(staged, key)
            tmp.unlink(missing_ok=True)
            check = getattr(engine, "last_check", None)     # speech compared with the text (XTTS only)
            if check and not check["ok"]:
                self.report.warnings.append(
                    f"Speech check: '{block.id}' ({block.voice}) may not match its text after "
                    f"{check['attempts']} attempts. Heard: \"{check['heard']}\". Listen to audio/{block.id}.wav.")
                self.log(f"      ! {block.id}: speech may not match the text (heard: {check['heard']})")
            elif check and check["attempts"] > 1:
                self.log(f"      {block.id}: speech matched the text on attempt {check['attempts']}")
            self.log(f"      ✓ {block.id} generated in {time.time() - started:.1f}s")
            self._tts_progress(block.id, cached=False)

    def _tts_progress(self, narration_id: str, cached: bool) -> None:
        self._tts_done += 1
        self._emit("progress", stage="TTS", done=self._tts_done, total=self._tts_total,
                   message=f"{'Reused' if cached else 'Generated'} {narration_id} ({self._tts_done}/{self._tts_total})")

    def _synthesize_parallel(self, misses, language: str, processing: dict, workers: int) -> None:
        from src.audio import tts_worker

        device = resolve_device(self.settings["compute"]["device"])
        threads = max(1, (os.cpu_count() or 2) // workers) if device == "cpu" else 1
        self._emit("progress", stage="TTS", done=self._tts_done, total=self._tts_total,
                   message=f"Generating {len(misses)} clips with {workers} workers")
        self.log(f"  Generating {len(misses)} clips with {workers} worker processes "
                 f"({threads} CPU threads each; each loads the model once)...")
        jobs = [{
            "id": block.id, "text": block.text, "voice": block.voice, "language": language,
            "voices_dir": str(self.voices.voices_dir),
            "raw": str(self.cache.staging_path(key, ".raw.wav")), "staged": str(self.cache.staging_path(key)),
            "out": str(self.cache.path(key)), **processing,
        } for block, key in misses]
        with ProcessPoolExecutor(max_workers=workers, initializer=tts_worker.init,
                                 initargs=(self.settings["audio"]["engine"], device, threads)) as pool:
            for narration_id, seconds in pool.map(tts_worker.synthesize, jobs):
                self.log(f"      ✓ {narration_id} generated in {seconds:.1f}s")
                self._tts_progress(narration_id, cached=False)

    # ----------------------------------------------------------- alignment

    def _alignment_key(self, script: LessonScript, clips: dict[str, dict]) -> str:
        return hash_value({
            "clips": [(b.id, hash_file(clips[b.id]["audio"]), b.text) for b in script.narration],
            "language": script.language,
            "version": ALIGN_VERSION,
            "whisperx": bool(self.settings["alignment"].get("enabled", True)),
        })

    def align(self, script: LessonScript, clips: dict[str, dict]) -> dict[str, dict]:
        key = self._alignment_key(script, clips)
        stored = _read_json(self.paths.alignment_meta)
        if (not self.options.force_alignment and stored.get("input_hash") == key
                and self.paths.alignment_file.exists() and self.paths.timing.exists()):
            self.log(f"  {HIT} WhisperX alignment (all {len(clips)} clips unchanged). Skipping alignment.")
            self.report.status["WhisperX"] = "Cached"
            self._emit("cache", stage="WhisperX", generated=0, cached=len(clips))
            return read_timing(self.paths.timing)

        self.log(f"  {MISS} WhisperX alignment. Running alignment...")
        use_whisperx = self.settings["alignment"].get("enabled", True)
        entries, aligned, reused = {}, 0, 0
        for block in script.narration:
            clip = clips[block.id]
            if use_whisperx:
                aligner = self.aligner(script.language)
                alignment, from_cache = aligner.align(clip["audio"], block.text, clip["duration"],
                                                      force=self.options.force_alignment)
                if alignment is None:
                    use_whisperx = False
                    self.report.warnings.append("WhisperX is not available; word timings are estimated.")
                    alignment, from_cache = estimated_alignment(block.text, clip["duration"]), False
                reused += from_cache
                aligned += not from_cache
            else:
                alignment = estimated_alignment(block.text, clip["duration"])
            self._emit("progress", stage="WhisperX", done=len(entries) + 1, total=len(script.narration),
                       message=f"Aligned {block.id} ({len(entries) + 1}/{len(script.narration)})")
            entries[block.id] = {
                "duration": round(clip["duration"], 4),
                "audio": f"audio/{Path(clip['audio']).name}",   # lesson-relative: same in a job workspace
                "voice": clip["voice"],
                "words": alignment["words"],
                "sentences": alignment["sentences"],
                "alignment": alignment["method"],
            }
        write_timing(self.paths.timing, entries)
        self.paths.alignment.mkdir(parents=True, exist_ok=True)
        self.paths.alignment_file.write_text(json.dumps(
            {nid: {"words": e["words"], "sentences": e["sentences"], "method": e["alignment"]} for nid, e in entries.items()},
            indent=1), encoding="utf-8")
        self.paths.alignment_meta.write_text(json.dumps({
            "input_hash": key,
            "language": script.language,
            "version": ALIGN_VERSION,
            "clips": {nid: hash_file(c["audio"]) for nid, c in clips.items()},
        }, indent=2), encoding="utf-8")
        self.log(f"  ✓ aligned {aligned} clip(s), reused {reused} clip alignment(s) from cache")
        self.report.status["WhisperX"] = f"Aligned: {aligned}\n  Cached: {reused}" if use_whisperx else "Estimated"
        self._emit("cache", stage="WhisperX", generated=aligned, cached=reused, estimated=not use_whisperx)
        return entries

    # --------------------------------------------------------- audio only

    def audio_only_track(self, script: LessonScript, timing: dict) -> None:
        clips = [(self.paths.audio / f"{b.id}.wav", b.pause_after) for b in script.narration]
        concatenate(clips, self.paths.track, int(self.settings["audio"]["sample_rate"]))
        self.report.outputs["narration_track"] = self._rel(self.paths.track)
        self.log(f"  ✓ {self._rel(self.paths.track)} ({format_duration(audio_duration(self.paths.track))})")

    # --------------------------------------------------------------- Manim

    def _preset(self) -> str:
        return self.settings["video"]["final_quality" if self.options.quality == "final" else "preview_quality"]

    def _media_dir(self) -> Path:
        return self.options.media_dir or MEDIA_DIR / f"{self.lesson_name}_narrated"

    def _render_key(self, script: LessonScript, timing_file: Path | None) -> str:
        from importlib.metadata import version

        return hash_value({
            "animation": hash_file(self.paths.animation),
            "framework": framework_hash(),
            "assets": hash_files(lesson_asset_files(self.paths.root)),
            "timing": hash_file(timing_file) if timing_file and timing_file.exists() else None,
            "quality": QUALITY_PRESETS[self._preset()][0],
            "scene": script.scene_class,
            "pause": self.settings["audio"]["pause_after"],
            "manim": version("manim"),
            **self._blender_key(),
            **self._validation_key(),
        })

    def _blender_key(self) -> dict:
        """Blender version/settings, only for lessons with 3D sections (Manim-only keys are unchanged)."""
        from src.blender.render import fingerprint, uses_blender

        return {"blender": fingerprint(self.settings)} if uses_blender(self.paths.animation) else {}

    def _validation_key(self) -> dict:
        """Validation settings, only for lessons whose check_fit() calls may resize text."""
        if "check_fit(" not in self.paths.animation.read_text(encoding="utf-8-sig"):
            return {}
        return {"validation": self.settings.get("validation")}

    def render(self, script: LessonScript, audio_on: bool) -> Path:
        preset = self._preset()
        flag, description = QUALITY_PRESETS[preset]
        meta_dir = self.paths.manim_meta / preset
        render_meta = meta_dir / "render.meta.json"
        timing_file = self.paths.timing if audio_on else None
        key = self._render_key(script, timing_file)
        stored = _read_json(render_meta)
        video = Path(stored["video"]) if stored.get("video") else None

        if not self.options.force_render and stored.get("input_hash") == key and video and video.exists():
            timeline = stored["timeline"]
            self.paths.timeline.write_text(json.dumps(timeline, indent=2), encoding="utf-8")
            for section in timeline.get("sections", []):
                self.log(f"  {HIT} Manim scene: {section['id']}")
                self.report.manim_sections[section["id"]] = (0, section.get("plays", 0))
            self.log(f"  Skipping render ({preset}: {description}).")
            self.report.status["Manim"] = f"Rendered: 0\n  Cached: {len(timeline.get('sections', []))}"
            self._emit("cache", stage="Manim", generated=0, cached=len(timeline.get("sections", [])))
            self._emit_segments(self._segments(script, timeline.get("sections", []), final=True))
            return video

        # Web jobs: which scenes will re-render and which are reused (a Manim "plan" pass, nothing is
        # rendered), then live status per scene while rendering. The CLI output is unchanged.
        segments = self._plan_segments(script, timing_file, flag) if self.progress else None
        self.log(f"  Rendering changed animations ({preset}: {description})...")
        try:
            video = run_manim(
                self.paths.animation, script.scene_class, "render", self.paths.timeline, self.paths.logs / "render.log",
                quality_flag=flag, media_dir=self._media_dir(), timing_file=timing_file,
                default_pause=float(self.settings["audio"]["pause_after"]), flush_cache=self.options.force_render,
                on_line=self._manim_line_watcher(script, segments) if self.progress else None,
                validation=self.settings.get("validation"),
            )
        except Exception:
            if segments:
                for s in segments:
                    if s["status"] == "regenerating":
                        s["status"] = "failed"
                self._emit_segments(segments)
            raise
        timeline = json.loads(self.paths.timeline.read_text(encoding="utf-8"))
        if self.progress:
            self._emit_segments(self._segments(script, timeline["sections"], final=True))
        if timeline.get("blender"):
            # 3D sections (self.blender(...)): Blender renders them headlessly and they
            # are spliced over their exact frame range; everything after this is unchanged.
            from src.blender.render import apply_segments

            video = apply_segments(
                self.paths.animation, timeline, video, self._media_dir(), preset, self.settings, log=self.log,
                progress=lambda message: self._emit("progress", stage="Manim", message=message, done=0, total=0),
            )
        rendered_sections = self._report_sections(timeline["sections"])
        meta_dir.mkdir(parents=True, exist_ok=True)
        for section in timeline["sections"]:
            (meta_dir / f"{section['id']}.meta.json").write_text(json.dumps(section, indent=2), encoding="utf-8")
        render_meta.write_text(json.dumps({"input_hash": key, "video": str(video), "timeline": timeline}, indent=2),
                               encoding="utf-8")
        cached_sections = len(timeline["sections"]) - rendered_sections
        self.report.status["Manim"] = f"Rendered: {rendered_sections}\n  Cached: {cached_sections}"
        self._emit("cache", stage="Manim", generated=rendered_sections, cached=cached_sections)
        self.log(f"  ✓ Animation: {format_duration(timeline['duration'])}, {len(timeline['narrations'])} narration points")
        return video

    def _manim_line_watcher(self, script: LessonScript, segments: list[dict] | None = None):
        """Turn the scene markers LMSScene prints while rendering into progress events
        (and, with ``segments``, per-scene status: changed -> regenerating -> completed)."""
        titles = {s["id"]: s.get("title") or s["id"] for s in script.scenes}
        total = max(1, len(script.scenes))
        seen: list[str] = []
        by_id = {s["segment_id"]: s for s in segments or []}

        def finish_running() -> None:
            for s in segments or []:
                if s["status"] == "regenerating":
                    s["status"] = "completed"

        def on_line(line: str) -> None:
            if line.startswith(SCENE_MARKER):
                scene_id = line[len(SCENE_MARKER):].strip()
                seen.append(scene_id)
                index = min(len(seen), total)
                segment = by_id.get(scene_id)
                if segments is not None:
                    finish_running()
                    if segment and segment["status"] == "changed":
                        segment["status"] = "regenerating"
                    self._emit_segments(segments)
                reused = segment is not None and segment["status"] == "cached"
                verb = "Reusing cached scene" if reused else "Regenerating" if segment else "Rendering scene"
                self._emit("progress", stage="Manim", done=index - 1, total=total, scene=scene_id,
                           message=f"{verb} {index} of {total}: {titles.get(scene_id, scene_id)}")
            elif "Combining to Movie file" in line:
                if segments is not None:
                    finish_running()
                    self._emit_segments(segments)
                self._emit("progress", stage="Manim", done=total, total=total,
                           message="Segments complete: assembling the scenes" if segments else "Joining animation clips")
        return on_line

    # ------------------------------------------------ per-scene (segment) status

    def _segments(self, script: LessonScript, sections: list[dict], final: bool = False) -> list[dict]:
        """One segment per scene_start() section, in animation.py order. ``final``: from a real render
        (all plays cached -> "cached", else "completed"); otherwise from a plan (-> "cached"/"changed")."""
        titles = {s["id"]: s.get("title") for s in script.scenes}
        out = []
        for order, section in enumerate(sections, 1):
            reused = section.get("plays", 0) == section.get("cached_plays", 0)
            out.append({"segment_id": section["id"], "segment_order": order,
                        "segment_name": titles.get(section["id"]) or section["id"],
                        "status": "cached" if reused else ("completed" if final else "changed")})
        return out

    def _plan_segments(self, script: LessonScript, timing_file: Path | None, flag: str) -> list[dict] | None:
        """Which scenes this render will regenerate (Manim plan pass: nothing is rendered)."""
        if self.options.force_render:
            return [{"segment_id": s["id"], "segment_order": i, "segment_name": s.get("title") or s["id"],
                     "status": "changed"} for i, s in enumerate(script.scenes, 1)]
        self._emit("progress", stage="Manim", done=0, total=0, message="Checking which scenes changed")
        tmp = Path(tempfile.mkdtemp(prefix="lms_plan_"))
        try:
            run_manim(self.paths.animation, script.scene_class, "plan", tmp / "timeline.json", tmp / "plan.log",
                      quality_flag=flag, media_dir=self._media_dir(), timing_file=timing_file,
                      default_pause=float(self.settings["audio"]["pause_after"]),
                      validation=self.settings.get("validation"))
            sections = json.loads((tmp / "timeline.json").read_text(encoding="utf-8"))["sections"]
        except Exception as err:            # status display only: never let it stop the real render
            self.log(f"  (could not pre-check changed scenes: {err})")
            return None
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        segments = self._segments(script, sections)
        self._emit_segments(segments)
        return segments

    def _emit_segments(self, segments: list[dict] | None) -> None:
        if segments is not None:
            self._emit("segments", stage="Manim", segments=[dict(s) for s in segments])

    def _report_sections(self, sections: list[dict], predicted: bool = False) -> int:
        """Print per-scene cache status; return how many scenes (re)render."""
        rendered = 0
        verb = "would render" if predicted else "rendered"
        for section in sections:
            plays, cached = section.get("plays", 0), section.get("cached_plays", 0)
            new = plays - cached
            self.report.manim_sections[section["id"]] = (new, plays)
            if new == 0:
                self.log(f"  {HIT} Manim scene: {section['id']} ({plays} animations reused)")
            else:
                rendered += 1
                self.log(f"  {MISS} Manim scene: {section['id']} ({verb} {new} of {plays} animations)")
        return rendered

    # ----------------------------------------------------------- subtitles

    def subtitle_settings(self, script: LessonScript) -> SubtitleSettings:
        merged = deep_merge(self.settings["subtitles"], script.subtitles or {})
        if self.options.subtitles is not None:
            merged["enabled"] = self.options.subtitles
        return SubtitleSettings.from_dict(merged)

    def _subtitle_key(self, script, timing, timeline, settings) -> str:
        return hash_value({
            "placement": [(n["id"], n["start"]) for n in timeline["narrations"]],
            "timing": {nid: (e.get("words"), e.get("sentences")) for nid, e in timing.items()},
            "flags": {b.id: b.subtitle for b in script.narration},
            "settings": settings.__dict__,
        })

    def write_subtitles(self, script: LessonScript, timing: dict, timeline: dict) -> dict[str, Path]:
        settings = self.subtitle_settings(script)
        if not settings.enabled or not timing:
            reason = "disabled" if not settings.enabled else "no narration audio"
            self.log(f"  - Subtitles skipped ({reason})")
            self.report.status["Subtitles"] = "Disabled" if not settings.enabled else "None"
            self._emit("cache", stage="Subtitles", skipped=reason)
            return {}
        files = {fmt: self.paths.subtitles / f"{script.lesson_id}.{fmt}" for fmt in settings.formats}
        key = self._subtitle_key(script, timing, timeline, settings)
        if not self.options.force_alignment and self.manifest.matches("subtitles", key, *files.values()):
            self.log(f"  {HIT} Subtitles ({', '.join(f.upper() for f in files)})")
            self.report.status["Subtitles"] = "Cached"
            self._emit("cache", stage="Subtitles", generated=0, cached=1)
        else:
            self.log(f"  {MISS} Subtitles")
            cues = build_cues(timeline["narrations"], timing, {b.id: {"subtitle": b.subtitle} for b in script.narration}, settings)
            writers = {"srt": write_srt, "vtt": write_vtt}
            for fmt, path in files.items():
                writers[fmt](cues, path)
                self.log(f"  ✓ {fmt.upper()} ({settings.mode} mode, {len(cues)} cues): {self._rel(path)}")
            self.manifest.record("subtitles", key)
            self.report.status["Subtitles"] = "Generated"
            self._emit("cache", stage="Subtitles", generated=1, cached=0)
        self.report.outputs["subtitles"] = {fmt: self._rel(p) for fmt, p in files.items()}
        return files

    # ---------------------------------------------------------- composition

    def compose_video(self, script, video: Path, timing: dict, timeline: dict, subtitle_files: dict, audio_on: bool) -> Path:
        track = None
        if audio_on and timing:
            clips = [(self.paths.audio / f"{n['id']}.wav", n["start"]) for n in timeline["narrations"]]
            sample_rate = int(self.settings["audio"]["sample_rate"])
            track_key = hash_value({"clips": [(hash_file(p), s) for p, s in clips],
                                    "duration": timeline["duration"], "rate": sample_rate})
            if not self.options.force_compose and self.manifest.matches("track", track_key, self.paths.track):
                self.log(f"  {HIT} Narration track")
            else:
                self.log(f"  {MISS} Narration track: placing {len(clips)} clips on the timeline")
                self.report.warnings += place_clips(clips, timeline["duration"], self.paths.track, sample_rate)
                self.manifest.record("track", track_key)
            track = self.paths.track

        name = self.options.output_name or (script.lesson_id if self.options.quality == "final" else f"{script.lesson_id}_preview")
        out = self.paths.output / f"{name}.mp4"
        embed = subtitle_files.get("srt") if self.subtitle_settings(script).embed_in_mp4 else None
        compose_key = hash_value({
            "video": hash_file(video),
            "track": hash_file(track) if track else None,
            "srt": hash_file(embed) if embed else None,
            "language": script.language,
        })
        stage = f"compose:{name}"
        if not self.options.force_compose and self.manifest.matches(stage, compose_key, out):
            self.log(f"  {HIT} Final composition. Skipping FFmpeg.")
            self.report.status["FFmpeg"] = "Cached"
            self._emit("cache", stage="FFmpeg", generated=0, cached=1)
        else:
            self.log(f"  {MISS} Final composition. Running FFmpeg...")
            compose(video, track, out, embed, script.language)
            self.manifest.record(stage, compose_key)
            self.report.status["FFmpeg"] = "Generated"
            self._emit("cache", stage="FFmpeg", generated=1, cached=0)
        self.report.outputs["video"] = self._rel(out)
        self.log(f"  ✓ {self._rel(out)}")
        return out

    # -------------------------------------------------------------- dry run

    def plan(self) -> Report:
        """--dry-run: report what a real run would do. Only temporary files are written."""
        self.log("DRY RUN: nothing will be generated.\n")
        tmp = Path(tempfile.mkdtemp(prefix="lms_plan_"))
        try:
            key = self._extract_key()
            if self.manifest.matches("extract", key, self.paths.extracted):
                self.log(f"{HIT} Script extraction")
                script = self._load_script(self.paths.extracted)
            else:
                self.log(f"{MISS} Script extraction (animation.py changed)")
                script = self._extract_to(tmp / "extracted.json")
            audio_on = self._audio_enabled()
            if not audio_on:
                self.log("\nAudio disabled.")
                return self.report

            self.log("")
            planned_timing, tts_misses = {}, 0
            existing = read_timing(self.paths.timing)
            for block in script.narration:
                key = self.audio_key(block, script.language)
                hit = self.cache.has(key) and not self.options.force_tts
                meta = _read_json(self.paths.audio / f"{block.id}.meta.json")
                self.log(f"{HIT if hit else MISS} TTS: {block.id} → {block.voice}")
                if hit and meta.get("input_hash") == key and block.id in existing:
                    planned_timing[block.id] = existing[block.id]
                else:
                    tts_misses += not hit
                    duration = estimate_duration(block.text)
                    planned_timing[block.id] = {"duration": duration}
                    if hit:  # clip exists in the shared cache but not yet in this lesson
                        planned_timing[block.id] = {"duration": audio_duration(self.cache.path(key))}
            self.report.status["TTS"] = f"Would generate: {tts_misses}\n  Cached: {len(script.narration) - tts_misses}"

            timing_unchanged = (not tts_misses and not self.options.force_alignment
                                and all(block.id in existing for block in script.narration)
                                and self.paths.alignment_meta.exists())
            self.log(f"\n{HIT if timing_unchanged else MISS} WhisperX alignment")

            timing_file = tmp / "timing.json"
            write_timing(timing_file, planned_timing)
            preset = self._preset()
            stored = _read_json(self.paths.manim_meta / preset / "render.meta.json")
            real_timing = self.paths.timing if timing_unchanged else None
            render_hit = (real_timing is not None and not self.options.force_render
                          and stored.get("input_hash") == self._render_key(script, real_timing)
                          and stored.get("video") and Path(stored["video"]).exists())
            self.log("")
            if render_hit:
                for section in stored["timeline"].get("sections", []):
                    self.log(f"{HIT} Manim scene: {section['id']}")
                rendered = 0
            elif self.options.force_render:
                self.log(f"{MISS} Manim: every scene (--force-render)")
                rendered = len(script.scenes)
            else:
                flag, _ = QUALITY_PRESETS[preset]
                run_manim(self.paths.animation, script.scene_class, "plan", tmp / "timeline.json",
                          tmp / "plan.log", quality_flag=flag, media_dir=self._media_dir(), timing_file=timing_file,
                          default_pause=float(self.settings["audio"]["pause_after"]),
                          validation=self.settings.get("validation"))
                sections = json.loads((tmp / "timeline.json").read_text(encoding="utf-8"))["sections"]
                rendered = self._report_sections(sections, predicted=True)
            downstream_changed = bool(tts_misses) or not timing_unchanged or rendered > 0
            self.log(f"\n{MISS if downstream_changed or self.options.force_alignment else HIT} Subtitles")
            self.log(f"{MISS if downstream_changed or self.options.force_compose else HIT} Final composition")
            return self.report
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _extract_to(self, target: Path) -> LessonScript:
        scene_class = find_scene_class(self.paths.animation, self.options.scene_class)
        run_manim(self.paths.animation, scene_class, "extract", target, target.parent / "extract.log",
                  media_dir=self._media_dir(), default_pause=float(self.settings["audio"]["pause_after"]),
                  validation=self.settings.get("validation"))
        return self._load_script(target)

    def _load_script(self, path: Path) -> LessonScript:
        raw = json.loads(path.read_text(encoding="utf-8"))
        script = parse_extracted(raw, self.lesson_name, self.settings["voice"].get("default"),
                                 self.settings["voice"].get("aliases"))
        self._apply_voice_choices(script)
        validate_script(script, self.voices, check_voices=self._audio_enabled())
        self.check_layout(raw.get("validation"), fail=False)       # dry run: report only
        return script

    # ------------------------------------------------------- other modes

    def _subtitles_only(self) -> Report:
        for needed in (self.paths.script, self.paths.timing, self.paths.timeline):
            if not needed.exists():
                raise LMSError(f"{self._rel(needed)} is missing.", "Run the full generator once first:\n\n"
                               f"    python scripts/generate_video.py {self._rel(self.paths.root)}")
        raw = json.loads(self.paths.script.read_text(encoding="utf-8"))
        script = parse_extracted({"lesson": raw["lesson"], "scenes": raw["scenes"], "narration": raw["narration"]},
                                 self.lesson_name, self.settings["voice"].get("default"),
                                 self.settings["voice"].get("aliases"))
        timing = read_timing(self.paths.timing)
        timeline = json.loads(self.paths.timeline.read_text(encoding="utf-8"))
        if self.options.subtitles is None:
            self.options.subtitles = True
        self._step("Subtitles", "Subtitles", lambda: self.write_subtitles(script, timing, timeline))
        return self.report

    # ------------------------------------------------------------ helpers

    def engine(self) -> TTSEngine:
        """The TTS model: loaded on the first cache miss, then reused for the whole run."""
        if self._engine is None:
            device = resolve_device(self.settings["compute"]["device"])
            self.log(f"  Loading {self.settings['audio']['engine']} on {device.upper()} (once per run)...")
            self._emit("progress", stage="TTS", done=getattr(self, "_tts_done", 0), total=getattr(self, "_tts_total", 0),
                       message=f"Loading the {self.settings['audio']['engine']} model on {device.upper()}")
            self._engine = create_engine(self.settings["audio"]["engine"], device, self.settings)
        return self._engine

    def aligner(self, language: str) -> Aligner:
        """WhisperX aligner: created on first need; its model loads only on a per-clip cache miss."""
        if self._aligner is None:
            self._aligner = Aligner(language, resolve_device(self.settings["compute"]["device"]))
        return self._aligner

    def _audio_enabled(self) -> bool:
        return self.options.audio if self.options.audio is not None else bool(self.settings["audio"].get("enabled", True))

    def _check_environment(self) -> None:
        ffmpeg_path()

    def _step(self, stage: str, title: str, fn):
        self.log(f"\n{title}...")
        self._emit("stage_start", stage=stage, title=title)
        started = time.time()
        try:
            result = fn()
        except BaseException:
            self.report.steps[stage] = round(self.report.steps.get(stage, 0) + time.time() - started, 1)
            self._emit("stage_failed", stage=stage)
            raise
        self.report.steps[stage] = round(self.report.steps.get(stage, 0) + time.time() - started, 1)
        self._emit("stage_end", stage=stage, seconds=self.report.steps[stage], status=self.report.status.get(stage))
        return result

    def _emit(self, kind: str, **data) -> None:
        if self.progress is not None:
            self.progress({"kind": kind, **data})

    def _rel(self, path: Path) -> str:
        from src.config.video_config import PROJECT_ROOT

        try:
            return Path(path).resolve().relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            return str(path)

    def _finish(self, script: LessonScript, started: float) -> Report:
        self.report.total_seconds = time.time() - started
        metadata = {
            "lesson": script.lesson_id,
            "title": script.title,
            "quality": self.options.quality,
            "voices": {v: [b.id for b in script.narration if b.voice == v] for v in script.voices_used},
            "voice_sources": {b.id: b.voice_source for b in script.narration},
            "audio_generated": self.report.generated,
            "audio_from_cache": self.report.cached,
            "stage_status": self.report.status,
            "manim_sections": {k: {"rendered": r, "animations": t} for k, (r, t) in self.report.manim_sections.items()},
            "step_seconds": self.report.steps,
            "total_seconds": round(self.report.total_seconds, 1),
            "outputs": self.report.outputs,
            "warnings": self.report.warnings,
            "layout_validation": self.report.layout,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.paths.metadata.parent.mkdir(parents=True, exist_ok=True)
        self.paths.metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return self.report


def _read_json(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def performance_summary(report: Report) -> str:
    """The end-of-run block: per-stage cache status and timings."""
    bar = "=" * 40
    lines = [bar, "VIDEO GENERATION COMPLETE", bar, "", f"Lesson: {report.title}", ""]
    for stage in ("TTS", "WhisperX", "Manim", "Subtitles", "FFmpeg"):
        if stage in report.status:
            lines += [f"{stage}:", f"  {report.status[stage]}", ""]
    lines.append(f"Total time: {format_duration(report.total_seconds)}")
    lines += ["", bar, ""]
    width = 12
    for stage in ("Script", "TTS", "WhisperX", "Manim", "Subtitles", "FFmpeg"):
        if stage in report.steps:
            lines.append(f"{stage + ':':<{width}}{report.steps[stage]:>7.1f}s")
    lines += ["-" * 32, f"{'TOTAL:':<{width}}{report.total_seconds:>7.1f}s"]
    return "\n".join(lines)
