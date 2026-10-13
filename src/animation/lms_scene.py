"""Authoring API for narrated lesson videos.

A lesson's ``animation.py`` subclasses ``LMSScene`` (or ``LMS3DScene``) and
writes narration and visuals side by side:

    class NaturalNumbersVideo(LMSScene):
        default_voice = "teacher_a"

        def construct(self):
            self.scene_start("hook")
            n = self.narrate("hook_01", "Hello again, my dear students!")
            self.play_with(n, Write(title))          # fills the narration
            n = self.narrate("hook_02", "How many apples are there?", voice="student_a")
            self.at_word(n, "apples")                # wait until "apples" is spoken
            self.play(FadeIn(apples))

Rules the API enforces for you:

* Audio is the timing authority. ``narrate()`` never starts before the
  previous narration (plus its ``pause_after``) has finished, so clips can
  never overlap, whatever voice or speed produced them.
* ``narration.duration`` and word times come from the real generated audio
  when the generator renders; in plain ``manim`` runs they are estimated.
* The generator reads every ``narrate()`` call automatically; nobody writes
  JSON by hand.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

import numpy as np
from manim import Mobject, MovingCameraScene, Scene, ThreeDScene, Wait, config

from src.animation.timing import (EXTRACT, PLAN, RENDER, SCENE_MARKER, STANDALONE, VALIDATION_ENV,
                                  NarrationTimingStore, Word, normalise_word)
from src.validation.layout import LayoutValidator

# Unicode that lesson text commonly contains but plain LaTeX rejects: lets
# MathTex(r"-₹2000") and MathTex("−3") work (tfrupee ships with MiKTeX/TeX Live).
LMS_TEX_PREAMBLE = r"""
\usepackage{tfrupee}
\DeclareUnicodeCharacter{20B9}{\ifmmode\text{\rupee}\else\rupee\fi}
\DeclareUnicodeCharacter{2212}{\ifmmode-\else\textminus\fi}
"""


# Animation engines a lesson section can use (``scene_start(engine=...)``).
MANIM = "MANIM"        # default: 2D maths / concepts, drawn by this scene
BLENDER = "BLENDER"    # 3D: rendered headlessly by Blender (see ``blender()`` and src/blender/)


def _use_lms_tex_template() -> None:
    template = config.tex_template
    if "tfrupee" not in template.preamble:
        template = template.copy()
        template.add_to_preamble(LMS_TEX_PREAMBLE)
        config.tex_template = template


@dataclass
class Narration:
    """A spoken block. Returned by ``narrate()``; times are scene seconds."""

    id: str
    text: str
    voice: str | None       # resolved up to lesson level; the generator applies the global default
    scene: str | None
    subtitle: bool
    pause_after: float
    start: float            # when the audio starts in the video
    duration: float         # length of the audio clip
    words: list[Word] = field(default_factory=list)
    estimated: bool = True  # True until real audio exists
    voice_source: str = ""  # "narration", "scene", "lesson" or "global" (settings.json default)

    @property
    def end(self) -> float:
        return self.start + self.duration

    def word_offset(self, phrase: str, occurrence: int = 1) -> float:
        """Seconds from the clip start until ``phrase`` (one or more words) is spoken."""
        target = [normalise_word(w) for w in phrase.split()]
        spoken = [normalise_word(w.text) for w in self.words]
        seen = 0
        for i in range(len(spoken) - len(target) + 1):
            if spoken[i:i + len(target)] == target:
                seen += 1
                if seen == occurrence:
                    return self.words[i].start
        raise ValueError(
            f"'{phrase}' (occurrence {occurrence}) is not in narration '{self.id}': \"{self.text}\""
        )


class NarrationMixin:
    """Adds narration, voices and audio-driven timing to a Manim scene class.

    Class attributes a lesson may set:

    * ``lesson_id``: defaults to the lesson folder name
    * ``lesson_title``: human-readable title
    * ``default_voice``: lesson default voice (overridden per scene/narration)
    * ``language``: narration language code, e.g. "en"
    * ``subtitles``: dict overriding settings.json > subtitles for this lesson,
      e.g. ``{"enabled": False}`` or ``{"mode": "word"}``
    * ``default_pause_after``: silence after each narration (seconds)
    * ``layout_validation``: dict overriding settings.json > validation for
      this lesson, e.g. ``{"min_font_size": 14}`` or ``{"enabled": False}``

    ``self.validator`` checks the layout (see src/validation/layout.py);
    lessons may add explicit checks such as ``self.validator.check_fit(text, box)``.
    """

    lesson_id: str | None = None
    lesson_title: str | None = None
    default_voice: str | None = None
    language: str = "en"
    subtitles: dict | None = None
    default_pause_after: float | None = None
    layout_validation: dict | None = None

    # -- lifecycle -----------------------------------------------------------

    def setup(self):
        super().setup()
        _use_lms_tex_template()
        self._timing = NarrationTimingStore.from_environment()
        self._narrations: list[Narration] = []
        self._sections: list[dict] = []
        self._scene_id: str | None = None
        self._scene_voice: str | None = None
        self._frames = 0                    # frames written so far = exact video position
        self._blender_segments: list[dict] = []
        self._last_play_cached = False
        self._watch_manim_cache()
        self.validator = self._make_validator()

    def tear_down(self):
        # Let the last narration finish before the video ends.
        self.wait_for_narration(include_pause=False)
        self.validator.checkpoint()
        if self._timing.mode == STANDALONE and self.validator.issues:
            from src.validation.report import format_report

            print(format_report(self.validator.results()), flush=True)
        if self._timing.output is not None:
            if self._timing.mode == EXTRACT:
                self._write_script()
            elif self._timing.mode == RENDER:
                self._write_timeline()
            elif self._timing.mode == PLAN:
                self._write_timeline()
                # Plan mode only asks "which animations are cached?": stop
                # before Manim tries to join partial movies that were never rendered.
                import os
                import sys

                sys.stdout.flush()
                os._exit(0)
        super().tear_down()

    def play(self, *args, **kwargs):
        """Manim's play(), plus exact frame counting and cache bookkeeping."""
        self._last_play_cached = False
        super().play(*args, **kwargs)
        # wait() plays a Wait whose empty placeholder Mobject Manim leaves on the scene. Those
        # invisible leftovers are part of every later animation's cache hash, so a scene with one
        # more or one fewer wait (e.g. after a narration change) would force every LATER scene to
        # re-render. Remove only those placeholders; nothing visible changes.
        for animation in args:
            placeholder = getattr(animation, "mobject", None) if isinstance(animation, Wait) else None
            if (type(placeholder) is Mobject and not placeholder.submobjects and len(placeholder.points) == 0
                    and placeholder in self.mobjects):
                self.remove(placeholder)
        self._frames += self._frames_in_last_play()
        section = self._sections[-1] if self._sections else None
        if section is not None:
            section["plays"] = section.get("plays", 0) + 1
            section["cached_plays"] = section.get("cached_plays", 0) + int(self._last_play_cached)
            hashes = getattr(self.renderer, "animations_hashes", None)
            if hashes and hashes[-1]:
                section.setdefault("animation_hashes", []).append(hashes[-1])
        self.validator.checkpoint()          # layout as it stays on screen after this animation

    # -- authoring API -------------------------------------------------------

    @property
    def now(self) -> float:
        """Current position in the video, in seconds (exact to the frame)."""
        return self._frames / config.frame_rate

    def scene_start(self, scene_id: str, voice: str | None = None, title: str | None = None,
                    engine: str = MANIM) -> None:
        """Begin a lesson section. ``voice`` becomes the default for its narration.

        ``engine=BLENDER`` marks a 3D section: show its picture with ``self.blender(...)``.
        """
        engine = (engine or MANIM).upper()
        if engine not in (MANIM, BLENDER):
            raise ValueError(f"Unknown engine '{engine}' for scene '{scene_id}' (use MANIM or BLENDER).")
        self._scene_id = scene_id
        self._scene_voice = voice
        section = {"id": scene_id, "title": title, "voice": voice, "start": round(self.now, 3)}
        if engine != MANIM:
            section["engine"] = engine
        self._sections.append(section)
        if self._timing.mode == RENDER:
            print(f"{SCENE_MARKER}{scene_id}", flush=True)   # progress for the web UI

    def scene_end(self, scene_id: str | None = None) -> None:
        """Mark the end of the current section (optional; recorded in timeline.json).

        The section's voice stops applying, so later narration falls back to
        the lesson default until the next ``scene_start()``.
        """
        section = next((s for s in reversed(self._sections) if scene_id in (None, s["id"])), None)
        if section is not None:
            section["end"] = round(self.now, 3)
        self._scene_voice = None

    def narrate(
        self,
        id: str,
        text: str,
        voice: str | None = None,
        subtitle: bool = True,
        pause_after: float | None = None,
    ) -> Narration:
        """Speak ``text``, starting now (after any narration still playing).

        Voice priority: ``voice`` argument > ``scene_start(voice=...)`` >
        class ``default_voice`` > settings.json global default.
        Returns a ``Narration`` whose ``duration`` you can use for timing.
        """
        if any(n.id == id for n in self._narrations):
            raise ValueError(f"Narration id '{id}' is used twice; every narrate() needs a unique id.")
        if not text or not text.strip():
            raise ValueError(f"Narration '{id}' has no text.")

        self.wait_for_narration()

        duration, words, estimated = self._timing.lookup(id, text)
        if voice:
            resolved, source = voice, "narration"
        elif self._scene_voice:
            resolved, source = self._scene_voice, "scene"
        elif self.default_voice:
            resolved, source = self.default_voice, "lesson"
        else:
            resolved, source = None, "global"
        narration = Narration(
            id=id,
            text=text.strip(),
            voice=resolved,
            voice_source=source,
            scene=self._scene_id,
            subtitle=subtitle,
            pause_after=self._pause_for(pause_after),
            start=self.now,
            duration=duration,
            words=words,
            estimated=estimated,
        )
        self._narrations.append(narration)
        return narration

    def duration_of(self, narration: Narration | str) -> float:
        """Audio length of a narration (object or id)."""
        return self._get(narration).duration

    def remaining(self, narration: Narration | str | None = None) -> float:
        """Seconds until ``narration`` (default: the latest one) finishes speaking."""
        n = self._get(narration) if narration is not None else self._last()
        # Rounded (far below one frame): the same scene must get the same run time, and so the same
        # Manim cache key, when only its start time shifted (float noise like 4.3838999 vs 4.3839001).
        return round(max(0.0, n.end - self.now), 6) if n else 0.0

    def play_with(self, narration: Narration | str, *animations, fraction: float = 1.0, min_run_time: float = 0.3, **kwargs):
        """Play ``animations`` stretched over the rest of ``narration``.

        ``fraction=0.5`` uses half the remaining narration time, leaving room
        for more animations before the narration ends.
        """
        run_time = round(max(min_run_time, self.remaining(narration) * fraction), 6)
        self.play(*animations, run_time=run_time, **kwargs)

    def at_word(self, narration: Narration | str, phrase: str, occurrence: int = 1, lead: float = 0.1) -> None:
        """Wait until ``phrase`` is spoken (``lead`` seconds early so visuals land on the word)."""
        n = self._get(narration)
        self._wait_until(n.start + n.word_offset(phrase, occurrence) - lead)

    def blender(self, scene, narration: Narration | str | None = None, duration: float | None = None,
                include_pause: bool = True, **params) -> None:
        """Show a Blender-rendered 3D clip here, from now until ``narration`` ends
        (default: the latest narration, plus its pause) or for ``duration`` seconds.

        ``scene`` is a ``src.blender.BlenderScene`` subclass defined in this
        animation.py; ``params`` (JSON values) are passed to it. The generator
        renders it headlessly with Blender, synced to the narration's word
        timings, and splices it into this exact time range of the video. Audio,
        subtitles and timing work exactly as for Manim sections.
        """
        name = scene if isinstance(scene, str) else getattr(scene, "__name__", str(scene))
        try:
            json.dumps(params)
        except TypeError as err:
            raise ValueError(f"blender({name}): parameters must be plain values (numbers, text, lists): {err}") from err
        self.clear()                                   # the 3D clip replaces the whole picture
        start_frame, start = self._frames, self.now
        if duration is not None:
            self._wait_until(start + float(duration))
        else:
            n = self._get(narration) if narration is not None else self._last()
            if n is None:
                raise ValueError(f"blender({name}) needs a narration (or duration=...) to know how long to show.")
            self._wait_until(n.end + (n.pause_after if include_pause else 0.0))
        frames = self._frames - start_frame
        if frames <= 0:
            raise ValueError(f"blender({name}) would last 0 frames: narrate first, or pass duration=...")
        end = self.now
        narrations = []
        for n in self._narrations:                     # speech inside this clip, times relative to its start
            if n.end > start and n.start < end:
                narrations.append({
                    "id": n.id, "start": round(n.start - start, 4), "end": round(n.end - start, 4),
                    "words": [{"text": w.text, "start": round(n.start + w.start - start, 4),
                               "end": round(n.start + w.end - start, 4)} for w in n.words],
                })
        self._blender_segments.append({
            "id": f"{self._scene_id or 'blender'}_{len(self._blender_segments) + 1}",
            "scene_class": name,
            "section": self._scene_id,
            "start_frame": start_frame,
            "frames": frames,
            "params": params,
            "narrations": narrations,
        })

    def wait_for_narration(self, narration: Narration | str | None = None, include_pause: bool = True) -> None:
        """Hold the picture until ``narration`` (default: the latest one) has finished."""
        n = self._get(narration) if narration is not None else self._last()
        if n is not None:
            self._wait_until(n.end + (n.pause_after if include_pause else 0.0))

    # -- internals -----------------------------------------------------------

    def _frames_in_last_play(self) -> int:
        """Frames the last play()/wait() adds to the video, computed exactly as Manim does.

        Manim advances ``renderer.time`` by the unrounded duration for cached
        animations but by whole frames for rendered ones. Counting frames
        ourselves keeps narration placement exact whether or not Manim
        reused its cache, which is what makes incremental rendering safe.
        """
        duration = self.duration
        if not self.animations or duration <= 0:
            return 0
        if self.is_current_animation_frozen_frame():
            return int(duration / (1 / self.camera.frame_rate))   # CairoRenderer.freeze_current_frame
        return len(np.arange(0, duration, 1 / config["frame_rate"]))  # Scene.get_time_progression

    def _watch_manim_cache(self) -> None:
        """Record whether Manim reused each animation from its partial-movie cache.

        In plan mode (``--dry-run``) every animation is reported as cached to
        Manim so nothing renders, while the real answer is recorded.
        """
        writer = getattr(self.renderer, "file_writer", None)
        if writer is None or self._timing.mode not in (RENDER, PLAN):
            return
        original = writer.is_already_cached
        plan = self._timing.mode == PLAN

        def is_already_cached(hash_invocation):
            hit = original(hash_invocation)
            self._last_play_cached = hit
            return True if plan else hit

        writer.is_already_cached = is_already_cached

    def _make_validator(self) -> LayoutValidator:
        """Layout checks run while the generator extracts (and in plain manim runs); while
        rendering only explicit check_fit() calls act, so the video gets the same fitted text."""
        import os

        raw = os.environ.get(VALIDATION_ENV)
        if raw:
            config = json.loads(raw)
        else:
            try:
                from src.config.settings import load_settings

                config = load_settings().get("validation", {})
            except Exception:           # standalone runs must never fail over settings
                config = {}
        config = {**config, **(self.layout_validation or {})}
        record = self._timing.mode in (EXTRACT, STANDALONE)
        return LayoutValidator(self, config, automatic=record, record=record)

    def _pause_for(self, pause_after: float | None) -> float:
        """narrate() argument > class default_pause_after > settings.json audio.pause_after."""
        if pause_after is not None:
            return float(pause_after)
        if self.default_pause_after is not None:
            return float(self.default_pause_after)
        return self._timing.default_pause

    def _last(self) -> Narration | None:
        return self._narrations[-1] if self._narrations else None

    def _get(self, narration: Narration | str) -> Narration:
        if isinstance(narration, Narration):
            return narration
        for n in self._narrations:
            if n.id == narration:
                return n
        raise ValueError(f"No narration with id '{narration}' has been narrated yet.")

    def _wait_until(self, target: float) -> None:
        remaining = target - self.now
        if remaining <= 1e-3:
            return
        # Round up to whole frames: Manim drops partial frames from waits,
        # which would let the next clip start before this one ends.
        fps = config.frame_rate
        frames = math.ceil(remaining * fps - 1e-6)
        self.wait((frames + 0.5) / fps)

    def _write_script(self) -> None:
        script = {
            "lesson": {
                "id": self.lesson_id,
                "title": self.lesson_title,
                "language": self.language,
                "default_voice": self.default_voice,
                "scene_class": type(self).__name__,
                "subtitles": self.subtitles,
            },
            "scenes": [{k: s[k] for k in ("id", "title", "voice", "engine") if k in s} for s in self._sections],
            "validation": self.validator.results(),
            "narration": [
                {
                    "id": n.id,
                    "text": n.text,
                    "voice": n.voice,
                    "voice_source": n.voice_source,
                    "scene": n.scene,
                    "subtitle": n.subtitle,
                    "pause_after": n.pause_after,
                    "estimated_duration": n.duration,
                }
                for n in self._narrations
            ],
        }
        self._timing.output.parent.mkdir(parents=True, exist_ok=True)
        self._timing.output.write_text(json.dumps(script, indent=2), encoding="utf-8")

    def _write_timeline(self) -> None:
        timeline = {
            "fps": config.frame_rate,
            "duration": round(self.now, 4),
            "sections": self._sections,
            "narrations": [
                {"id": n.id, "start": round(n.start, 4), "duration": n.duration, "end": round(n.end, 4)}
                for n in self._narrations
            ],
        }
        if self._blender_segments:
            timeline["blender"] = self._blender_segments
        self._timing.output.parent.mkdir(parents=True, exist_ok=True)
        self._timing.output.write_text(json.dumps(timeline, indent=2), encoding="utf-8")


class LMSScene(NarrationMixin, Scene):
    """2D narrated lesson scene."""


class LMS3DScene(NarrationMixin, ThreeDScene):
    """3D narrated lesson scene (same API as ``LMSScene``)."""


class LMSMovingCameraScene(NarrationMixin, MovingCameraScene):
    """2D narrated scene whose camera can pan/zoom via ``self.camera.frame.animate``."""


__all__ = ["LMSScene", "LMS3DScene", "LMSMovingCameraScene", "Narration", "NarrationMixin"]
