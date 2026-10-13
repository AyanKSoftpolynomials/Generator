# LMS Video Generator: User Guide

Narrated, animated maths videos for the LMS / C-CAT courses.

> This is the full manual (it used to be the top-level README; messages in the
> program that say "see README > ..." refer to the sections below). Quick start:
> [../README.md](../README.md). Technical reference for developers and AI
> assistants: [../SUPPORT_FOR_CLAUDE.md](../SUPPORT_FOR_CLAUDE.md).

You write **one file per lesson**, `lessons/<name>/animation.py`, containing the
visuals (Manim) *and* the narration (`self.narrate(...)`). One command turns
it into a finished MP4 with cloned voices, audio-driven timing and subtitles:

```powershell
python scripts/generate_video.py lessons/whole_numbers
```

Prefer a browser? `npm run dev` opens a control panel on top of the same
engine: paste `animation.py`, analyze, pick voices, generate, watch the MP4
(see [Web control panel](#web-control-panel)).

Everything runs locally: **Manim** (animation), **XTTS v2** (voice cloning),
**WhisperX** (word timings), **FFmpeg** (audio/video). No API keys, and no
voice samples leave your machine.

If you know JavaScript/Node.js: `.venv/` is like `node_modules/`,
`requirements.txt` like `package.json`, `pytest` like Jest, and
`from src.components import x` like `import { x } from "./src/components"`.

---

## Contents

1. [How it works](#1-how-it-works)
2. [Installation](#2-installation)
3. [Writing a lesson (`animation.py`)](#3-writing-a-lesson-animationpy)
4. [Voices](#4-voices)
5. [Generating videos](#5-generating-videos)
6. [Subtitles](#6-subtitles)
7. [Configuration](#7-configuration)
8. [Project structure](#8-project-structure)
9. [Visual theme and components](#9-visual-theme-and-components)
10. [Tests](#10-tests)
11. [Troubleshooting](#11-troubleshooting)
12. [Licences, privacy and consent](#12-licences-privacy-and-consent)

---

## 1. How it works

```
animation.py  (visuals + narrate() calls; the only thing you author)
     │
     ├─ 1. dry run ───────────▶ generated/script.json   (every narration: id, text, voice, pause)
     │                          + layout validation     (text fits its box, in frame, no collisions)
     ├─ 2. voices resolved + validated   (assets/voices/<id>/)
     ├─ 3. XTTS v2 ───────────▶ audio/<id>.wav          (one clip per narration, cached, loudness-normalised)
     ├─ 4. WhisperX ──────────▶ alignment/alignment.json + generated/timing.json (durations, word times)
     ├─ 5. Manim render using timing.json ─▶ generated/timeline.json (when each clip starts in the video)
     ├─ 6. clips placed on the timeline ───▶ audio/narration_track.wav
     ├─ 7. subtitles (optional) ───────────▶ subtitles/<lesson>.srt / .vtt
     └─ 8. FFmpeg ────────────▶ output/<lesson>.mp4     (+ generated/metadata.json report)
```

**Audio is the timing authority.** The animation is rendered *after* the
audio exists, and every `narrate()` waits for the previous clip (plus its
pause) to finish. Change a voice, a sentence or the speaking speed and the
animation re-times itself; clips can never overlap.

`generated/script.json` is an intermediate file written by the generator.
Never edit it by hand: edit `animation.py` and re-run.

---

## 2. Installation

Requirements: **Windows 10/11**, **Python 3.12** (3.11-3.13 work; not 3.14),
~6 GB free disk (models), 8 GB+ RAM. An NVIDIA GPU is optional: it speeds up
speech generation roughly 10x, but everything works on CPU.

**Easiest:** from the project folder run
`powershell -ExecutionPolicy Bypass -File .\setup.ps1` (it does all of the steps
below plus the web UI, then runs `scripts/health_check.py`). Manual steps:

```powershell
# 1. Python 3.12 (per user, no admin), if you don't have it
py install 3.12

# 2. Virtual environment in the project folder
cd lms-video-generator
py -V:3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1          # prompt now starts with (.venv)

# 3. Everything else (packages, FFmpeg check/install, GPU detection)
python scripts/setup.py
python scripts/setup.py --full        # optional: also runs live TTS, WhisperX and Manim tests
```

If PowerShell refuses to run `Activate.ps1`, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

`setup.py` checks Python, the venv, Python packages (installing missing ones
from `requirements.txt`), FFmpeg (installing it with winget if missing),
LaTeX, Manim, XTTS, WhisperX and the GPU, and prints the exact fix for anything
that fails. If it finds an NVIDIA GPU it installs the CUDA build of PyTorch.

LaTeX (for `MathTex` equations) must be installed once by hand if missing:

```powershell
winget install --id MiKTeX.MiKTeX --scope user
initexmf --set-config-value="[MPM]AutoInstall=1"
```

**First run downloads models** (once, cached in your user profile): XTTS v2
(~1.9 GB) and the WhisperX English alignment model (~360 MB).

Manual alternative to `setup.py`: `pip install -r requirements.txt`.

---

## 3. Writing a lesson (`animation.py`)

A lesson scene extends `LMSScene` (or `LMS3DScene` for 3D, `LMSMovingCameraScene` for camera pan/zoom via `self.camera.frame`) instead of Manim's
`Scene`. Everything else is normal Manim.

```python
from manim import *
from src.animation import LMSScene


class WholeNumbersVideo(LMSScene):

    lesson_title = "Whole Numbers"
    default_voice = "teacher_a"          # lesson default voice

    def construct(self):

        self.scene_start("hook")         # a named section of the lesson

        title = Text("WHOLE NUMBERS")
        n = self.narrate("hook_01", "Hello again, my dear students!")
        self.play_with(n, Write(title))  # Write() lasts exactly as long as the sentence

        self.scene_start("dialogue", voice="teacher_b")   # section voice
        n = self.narrate("dialogue_01", "What comes after nine?")
        self.narrate("dialogue_02", "Ten!", voice="student_a", pause_after=0.5)

        n = self.narrate("dialogue_03", "Zero is a whole number too.")
        self.at_word(n, "zero")          # wait until "zero" is spoken...
        self.play(FadeIn(Text("0")))     # ...then show it
```

### The API

| Call | What it does |
|------|--------------|
| `self.narrate(id, text, voice=None, subtitle=True, pause_after=None)` | Speaks `text` starting now (after any narration still playing). Returns a `Narration` with `.duration`, `.start`, `.end`. `id` must be unique in the lesson (it names the WAV file). |
| `self.scene_start(id, voice=None, title=None)` | Starts a lesson section; `voice` becomes the default for its narration. |
| `self.play_with(n, *animations, fraction=1.0)` | Plays animations stretched over the rest of narration `n` (or `fraction` of it). |
| `self.at_word(n, "phrase", occurrence=1)` | Waits until that word/phrase is spoken (WhisperX timings), so the next `play()` lands on the word. |
| `self.wait_for_narration(n=None)` | Holds the picture until `n` (default: latest) has finished, including its pause. |
| `self.remaining(n=None)` / `self.duration_of(n)` | Seconds left in / total length of a narration. |
| class attributes | `lesson_title`, `default_voice`, `language` ("en"), `subtitles` (e.g. `{"enabled": False}` or `{"mode": "word"}`), `default_pause_after` |

Rules of thumb:

- Don't use `self.wait(3)` to time narrated content. Use `play_with`,
  `at_word` and `wait_for_narration`, which follow the real audio.
- `narrate()` doesn't block: animations after it play *while* it is spoken.
- Visual-only waits (e.g. a pause after the last sentence) are fine.
- Plain `manim` / `scripts/render.py` still work on an `LMSScene`. Without
  generated audio, durations are estimated from the text and the video is silent.

### Voice priority (most specific wins)

```
narrate(voice=...)  >  scene_start(voice=...)  >  class default_voice  >  settings.json voice.default
```

`generated/script.json` records which level each narration's voice came
from (`voice_source`). A voice chosen in the web UI (or with `--assign`)
sits above all of these.

Short voice names are mapped through `settings.json` → `voice.aliases`
(default: `"teacher"` → `teacher_a`, `"student"` → `student_a`), so
`narrate(voice="teacher")` works without editing the lesson.

### Lessons written for other tools

These work as-is:

- `from lms_video_generator.core import LMSScene`: an alias of
  `src.animation`; that `LMSScene` supports `self.camera.frame` zooms.
- `₹` and `−` inside `MathTex` / `Tex` (the LMS scenes add `tfrupee` and
  Unicode mappings to the LaTeX preamble).

When a lesson fails, the error shows the exception first, the
`animation.py` line it happened on (highlighted in the web editor) and a hint;
the raw Manim output is below it.

### Workflow with a teaching script

1. Give the AI the teaching script; it writes `animation.py` (visuals +
   `narrate()` calls + voices + timing hooks).
2. Save it as `lessons/<name>/animation.py` (optionally keep the original text
   as `lessons/<name>/source_script.txt` for reference).
3. `python scripts/generate_video.py lessons/<name>`

See [lessons/README.md](../lessons/README.md) for the lesson folder layout.

### 3D sections with Blender (optional)

Manim stays the engine for 2D maths and concepts. Where 3D has real teaching
value (solids, coordinate space, molecules, orbits, surfaces, physical set-ups,
camera moves around a structure) a section can be rendered by **Blender**
instead. Don't use it for what Manim does better (equations, graphs, number
lines, step-by-step algebra).

```python
from src.animation import BLENDER, LMSScene
from src.blender import BlenderScene

class PointInSpace(BlenderScene):            # built in Python, rendered headlessly
    def construct(self, b, t):               # b = toolkit, t = timing of this clip
        b.axes(length=4)
        p = b.sphere(radius=0.2, color="#FFD166", emission=0.8)
        b.move(p, to=(3, 0, 0), start=t.word("along x"), duration=1.2)
        b.orbit_camera(radius=14, height=6.5, start=0, end=t.duration)

class MyLesson(LMSScene):
    def construct(self):
        self.scene_start("space", title="The Third Direction", engine=BLENDER)
        n = self.narrate("space_01", "Go three steps along x, ...")
        self.blender(PointInSpace, narration=n)   # fills the narration's time exactly
```

- `self.blender(Scene, narration=n)` (or `duration=...`, plus any JSON
  `**params`, available as `t.params`) shows the 3D clip for exactly that time;
  `t.word("...")` gives the second a phrase is spoken (WhisperX timing), so 3D
  motion lands on words like `at_word` does in Manim.
- Toolkit (`src/blender/toolkit.py`): `sphere cube cylinder cone torus plane
  text line arrow polyline axes surface function_curve parametric_curve
  point_label material background camera look_at light default_lighting` and
  animations `keyframe move rotate grow_in shrink_out fade_in fade_out appear
  orbit orbit_camera` (times in seconds, colours "#RRGGBB", z is up).
- How it runs: Manim renders the lesson as usual (the Blender section holds the
  frames); then each clip is rendered by `blender -b` (no window) with
  `src/blender/runner.py`, encoded with FFmpeg and spliced over its exact frames.
  Narration, subtitles and the final FFmpeg step are unchanged. Clips are
  cached (`cache/blender/`) by their 3D code, timing, size and Blender settings:
  editing only the 2D part never re-renders them.
- Setup: Blender 4.2+ on PATH, or `settings.json` → `blender.path`, or the
  portable zip unpacked to `tools/blender/` (this PC: Blender 4.5 LTS there).
  `blender.engine`: `EEVEE` (default, GPU), `CYCLES` (CPU, slow) or `WORKBENCH`
  (fastest, flat). Lessons without `self.blender(...)` never need Blender.
- Example: `lessons/blender_demo/` (Manim → Blender → Manim, ~25 s;
  the 178-frame 3D clip renders in ~45 s at 480p on this PC).

### Layout validation

Every lesson's layout is checked **while the generator reads `animation.py`**
(step 1, the Manim dry run). That is before any audio is generated or any frame
is rendered, so mistakes show up in seconds, not in the finished video. The checks
use the real geometry of the mobjects (glyph and shape bounding boxes after
every `play()`/`wait()`), not guesses from character counts. Existing lessons
need no changes.

| Check | Severity | What it catches |
|---|---|---|
| `text_overflow` | ERROR | text whose centre is in a box (Rectangle, RoundedRectangle, Square, Circle, Ellipse) sticks out of it |
| `text_too_large` / `tight_fit` | WARNING / INFO | text fills more than 97 % of its box / nearly touches its edge |
| `frame_overflow` | ERROR (text) / WARNING | text cut off by the frame edge (WARNING when the camera has zoomed or moved); other objects partly outside |
| `safe_area` | WARNING | text within `safe_margin` of the frame edge |
| `off_screen` | INFO | text completely outside the frame (invisible, e.g. parked for a slide-in) |
| `overlap` | WARNING | texts of different top-level objects colliding (glyph level) |
| `box_overlap` | INFO | boxes of different top-level objects partly covering each other |
| `text_too_small` | WARNING / ERROR | effective font size (after `.scale()` and camera zoom) below `min_font_size` / `min_font_size_error` |

Objects in the same top-level group (`VGroup(box, label)`) are one design and
never collide with each other; copies stacked exactly on a text (glow, halo,
shadow layers) are not collisions; edges touching within `max_overflow` are fine.
Each problem is reported once, with the lesson section, the video time, the
`animation.py` line of the `play()` that showed it and the object's variable
name, for example:

```
Layout validation: 1 error(s), 1 warning(s), 0 info
  ERROR   [text_overflow] functions[1] (Text "MEMBER FUNCTIONS") overflows its box functions[0] (RoundedRectangle) by 0.58 left, 0.58 right.
          at scene 'why_it_matters', ~14.4s, animation.py line 305
          fix: Make the box bigger, shorten the text, or let the generator fit it:
              self.validator.check_fit(functions[1], functions[0], margin=0.2)
```

Where it shows: the console/log of every run, `generated/metadata.json`
(`layout_validation`: machine-readable issues with bounding boxes), the web
panel's Analyze warnings and the result's warnings. By default errors are
reported and generation continues; set `validation.fail_on_error: true` to stop
before TTS/rendering on any ERROR (per lesson: `layout_validation = {"fail_on_error": True}`).

**Explicit checks (optional).** `self.validator` is available in every `LMSScene`:

```python
card = RoundedRectangle(width=3.4, height=1.3)
label = Text("MEMBER FUNCTIONS", font_size=34).move_to(card)
self.validator.check_fit(label, card, margin=0.2)      # fits the text if it must
self.validator.check_in_frame(title)                   # inside the safe area
self.validator.check_spacing(a, b, min_gap=0.3, max_gap=1.0)
self.validator.check_size(group, max_width=config.frame_width - 1)
self.validator.check_no_overlap(a, b, c)
self.validator.ignore(title)                           # a deliberate effect: skip automatic checks
```

`check_fit` is the only check that changes anything, and only in the
deterministic case: text bigger than its box is scaled down and moved inside,
**never below `min_font_size`** (then it is an ERROR instead). It runs
identically in the dry run and the real render, so the video shows the fitted
text (`auto_fit` INFO in the report). The other checks only report (ERROR, as
you stated the intent), and the pair stays checked at every later `play()`.
Example: `lessons/layout_demo/`. Code: `src/validation/` (`layout.py`: checks,
`report.py`: console report); tests: `tests/test_validation.py`.

---

## 4. Voices

The voice library lives in `assets/voices/`, shared by all lessons:

```
assets/voices/
├── teacher_a/
│   ├── sample_01.wav     reference recordings (one or more)
│   ├── sample_02.wav
│   ├── sample_03.wav
│   └── voice.json
├── teacher_b/ ...
└── student_a/ ...
```

`voice.json`:

```json
{
  "id": "teacher_a",
  "name": "Teacher A",
  "language": "en",
  "samples": ["sample_01.wav", "sample_02.wav", "sample_03.wav"],
  "description": "Primary mathematics teacher voice"
}
```

XTTS uses **all** of a voice's samples together as the reference, so more
(clean) audio gives a more faithful clone.

### Managing voices

```powershell
python scripts/voice.py list
python scripts/voice.py info teacher_a
python scripts/voice.py validate              # all voices (or: validate teacher_a)
python scripts/voice.py add teacher_c --sample rec1.wav --sample rec2.wav --name "Teacher C" --description "..."
python scripts/voice.py add teacher_c --sample rec3.wav      # adds another sample to an existing voice
```

Good reference recordings: 6-30 s in total per voice, one speaker, no music or
echo, WAV/FLAC (MP3/OGG also accepted), 22 kHz or higher. Each sample must be
at least 2 s long.

**From the web UI** (Voice library → *Add voice*): upload a recording
(WAV, MP3, M4A, OGG, FLAC, WebM, AAC, Opus; up to 25 MB, 2 s to 5 min) and enter
the voice name, speaker, language and optional gender/role/description. You
must confirm you own the recording or have the speaker's permission. The file
is converted to a 24 kHz mono WAV and registered through the same
`VoiceManager.add` as the command above, so it becomes a normal
`assets/voices/<id>/` voice (the id comes from the name; an existing voice is
never overwritten). It appears in every narration dropdown at once.
*Preview* plays the recording; *Test voice* has XTTS speak a short sentence in
the cloned voice (queued like a generation, cached afterwards). *Delete* is only
offered for uploaded voices and is refused while a lesson or `settings.json`
still uses the voice; deleted voices are moved to `cache/deleted_voices/`.

### Test voices included

`teacher_a` (3 samples), `teacher_b`, `student_a` and `narrator` are
**synthetic test voices** generated from XTTS's built-in studio speakers (not
real people). Replace them with real, consented recordings: delete the folder
and `voice.py add` the new samples under the same id. The lessons need no
changes. To make more test voices:

```powershell
python scripts/voice.py speakers
python scripts/voice.py create-synthetic narrator_b --speaker "Gracie Wise" --samples 2
```

---

## 5. Generating videos

```powershell
python scripts/generate_video.py lessons/whole_numbers            # preview: 480p, real audio (default)
python scripts/generate_video.py lessons/whole_numbers --final    # Full HD 1080p60
python scripts/generate_audio.py lessons/whole_numbers            # narration only (same as --audio-only)
python scripts/generate_video.py lessons/whole_numbers --subtitles-only
python scripts/generate_video.py lessons/whole_numbers --no-subtitles
python scripts/generate_video.py lessons/whole_numbers --voice teacher_b   # one voice for everything
python scripts/generate_video.py lessons/whole_numbers --no-audio          # visuals only
```

| Output | Location |
|--------|----------|
| Final video | `lessons/<name>/output/<name>.mp4` (preview: `<name>_preview.mp4`) |
| Narration clips | `lessons/<name>/audio/<narration_id>.wav` |
| Combined narration track | `lessons/<name>/audio/narration_track.wav` |
| Subtitles | `lessons/<name>/subtitles/<name>.srt` and `.vtt` (SRT also embedded in the MP4 as a soft track) |
| Word/sentence timings | `lessons/<name>/alignment/alignment.json` |
| Generated metadata | `lessons/<name>/generated/` (`script.json`, `timing.json`, `timeline.json`, `metadata.json`, `logs/`) |

### Incremental builds (cache)

Every stage hashes exactly the inputs that affect it and is skipped when
nothing relevant changed. The log shows `[CACHE HIT]` / `[CACHE MISS]` per
item, and a timing summary is printed at the end.

| Stage | Re-runs only when... | Cache |
|-------|----------------------|-------|
| Script extraction | `animation.py` or framework code (`src/`, `manim.cfg`) changes | `generated/build_cache.json` |
| TTS (per narration) | its text, voice, voice samples, language, TTS model or audio settings change | `cache/audio/` (shared by all lessons) + `audio/<id>.meta.json` |
| WhisperX | any clip's audio or text changes; only changed clips are re-aligned | `alignment/alignment.meta.json` + `cache/alignment/` |
| Manim (per animation) | that animation's content changes: its objects, animation or run time (which follows its narration) | Manim's partial-movie cache in `output/media/<lesson>_narrated/`; per-scene report in `generated/manim/<quality>/` |
| Subtitles | alignment, timeline or subtitle settings change | `generated/build_cache.json` |
| Narration track + FFmpeg | the video, any clip, its position or the subtitles change | `generated/build_cache.json` |

So: changing only visuals never regenerates speech; changing one sentence
regenerates one clip and re-renders only the animations whose timing that
sentence changes (later scenes are reused even though they shift in time);
if nothing changed, no model is loaded at all.

```powershell
python generate.py lessons/integers/animation.py --dry-run         # what would be regenerated (nothing is written)
python generate.py lessons/integers/animation.py --force           # rebuild everything
python generate.py lessons/integers/animation.py --force-tts       # also: --force-alignment, --force-render, --force-compose
python generate.py lessons/integers/animation.py --workers 2       # parallel speech generation (see below)
```

`python generate.py <lesson or animation.py>` is a shortcut for
`python scripts/generate_video.py` and takes the same options. Delete
`cache/` or use `--force` to start from scratch.

### Speed (this PC: Ryzen 5 8500G, CPU only)

Measured on the Integers lesson (9 narration blocks, 1m 46s of speech), Full HD:

| Run | Time | What ran |
|-----|------|----------|
| Clean (`--force`) | 4m 54s | TTS 219 s, Manim 62 s, WhisperX 7 s |
| Same command again | 1 s | nothing (every stage cached) |
| One narration sentence changed | 1m 01s | 1 clip (43 s incl. model load), 1 clip aligned, 2 of 63 animations |
| One visual changed | 16 s | 2 of 63 animations + FFmpeg |

New narration is the slow part (XTTS ≈ 1.8x real time on this CPU).
`--workers N` (or `audio.workers` in settings.json) runs N speech-model
processes in parallel, each ~2 GB RAM. On this 6-core CPU two workers were
only ~8% faster (201 s vs 219 s) because PyTorch already uses every core, so
the default is 1. It pays off on a GPU or a CPU with many more cores.

### Web control panel

A browser UI (Next.js) around the **same** generator. It adds no second
pipeline: every button ends up in `VideoGenerator`, exactly like the CLI.

```powershell
npm run setup        # once: installs the frontend (frontend/node_modules)
npm run dev          # API on 127.0.0.1:8765 + UI on http://127.0.0.1:3000
npm run backend      # only the API          (= .venv\Scripts\python -m backend)
npm run frontend     # only the UI
```

Workflow: enter a lesson name → paste/upload `animation.py` (or *Open
existing*) → **Analyze Animation** → check the detected narration blocks and
choose a voice per block (or select a voice in the library and *Apply to
scene / all*) → **Generate Video** → watch progress → play or download the MP4.

How it maps onto the engine:

| UI | Engine |
|---|---|
| Analyze | the generator's own extraction (Manim dry run in a subprocess) + parser, in `cache/analyze/`; the lesson folder is untouched |
| Voice dropdowns | `GenerateOptions.voice_assignments` — the most specific level of the voice hierarchy (assignment > `narrate(voice=)` > scene > lesson > global). `animation.py` is never rewritten for a voice change. CLI equivalent: `--assign hook_main=teacher_b` |
| Generate | a new job (unique id) that runs `VideoGenerator` in its own background process (`backend/job_runner.py`) and its own workspace `cache/jobs/<jobId>/` (see below) |
| Progress / logs | structured events from the generator (stage start/end, per-clip TTS/WhisperX progress, per-scene Manim progress, cache hit/miss), streamed with Server-Sent Events |
| Video | the generator's MP4 served byte for byte (with seeking); nothing is re-encoded |

All caches apply as on the command line: an unchanged lesson regenerates in
about a second; changing one voice regenerates one clip and re-renders only
the affected animations.

**Several jobs at once.** Every tab can generate its own video; each tab
follows only its own job (the job id is kept per tab and shown next to the
progress bar). Each job builds in a private workspace:

```
cache/jobs/<jobId>/
    animation.py  generated/  audio/  alignment/  subtitles/  output/
    scenes/                 this job's Manim media folder
    job.json  output.log  state.json
```

The workspace starts as a copy of the lesson's last build (Manim's
content-hashed partial movies and LaTeX files are hard-linked, not copied), so
every cache still hits, and no job can touch another job's files. When a job
succeeds its build is published back to `lessons/<name>/` and the lesson's
Manim cache (briefly locked; the last job to finish wins), so the next job and
`python generate.py` start from it. The shared speech cache (`cache/audio`) is
content-addressed and written atomically.

**Parallel jobs.** Every job is its own OS process (`backend/job_runner.py`,
with its own Manim/FFmpeg children, log, exit status and PID); up to
`web.max_concurrent_jobs` run at the same time (5 in this project's
`settings.json`; env `MAX_CONCURRENT_JOBS` overrides), further jobs are
`queued` with a queue position (`queued` → `running` → `completed` / `failed` /
`cancelled`). Speech and word alignment run in **one shared speech process**
(`backend/speech_service.py`) that loads XTTS and WhisperX once for all jobs, so
a job process needs ~100 MB instead of ~2.5 GB — before this, five jobs meant
five XTTS models (~13 GB) and the machine swapped until most jobs crawled.
Speech requests from different jobs take turns on that model (on a CPU they
would share the same cores anyway), while each job's Manim render and FFmpeg run
fully in parallel. With RAM (or a GPU) to spare, `web.speech_workers` starts
more speech processes (each ~3 GB) and spreads jobs over them. Measured here
(Ryzen 5 8500G, 15 GB, CPU only): five lessons started within 15 s all ran at
once — five job processes, up to five Manim renders on the CPU simultaneously,
~2.4 GB RAM for all five jobs — and all finished within the same 7 minutes.
Cancelling a job kills only its own process tree; a failing job affects no
other job. The newest 30 finished jobs are kept on disk, so their videos stay
playable after an API restart.

Security: both servers listen on `127.0.0.1` only. Analyzing or generating
**runs the lesson's Python code** (as `python generate.py` does), so do not
expose the API to a network, and only load lessons you trust. The browser
never sees file paths, and there are no credentials to expose.

### Download and YouTube upload (optional)

After a job finishes, its result card has **Download Video** (with progress)
and, once YouTube is set up, **Upload to YouTube**. Neither is needed to
generate: with no YouTube setup everything works exactly as before.

**One-time Google setup** (free; uses only Google's official YouTube Data API v3 with OAuth 2.0):

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project and enable **YouTube Data API v3**.
2. *APIs & Services > OAuth consent screen*: set it up (External, testing is fine) and add your
   Google account as a **test user**.
3. *Credentials > Create credentials > OAuth client ID*, type **Web application**, with the
   authorized redirect URI exactly `http://127.0.0.1:3000/api/youtube/oauth/callback`
   (to use another address, change `settings.json` > `youtube.redirect_uri` to match).
4. Download the client JSON and add it in the web panel: *YouTube* panel > **Add client_secret.json**.

**Connect:** *YouTube* panel > **Connect YouTube**: Google's consent page opens in a
popup; allow uploading videos and viewing your YouTube account. The app asks the
API which channel you authorized and shows it. **Change account / Reconnect**
repeats this; **Disconnect** revokes the app's access at Google and forgets it
locally (your YouTube videos are not touched).

**Channel link:** type your channel link (`https://www.youtube.com/@handle` or
`…/channel/UC…`) and **Save**; edit and Save again to change it, or **Remove saved link**.
The link is only a reference, never used to sign in. An upload is refused with a
clear warning when the connected channel is not the saved link (you can then choose
to upload to the connected channel anyway, or reconnect the right account).
Legacy `/c/` and `/user/` links cannot be verified and ask for the same confirmation.

**Upload:** title (the video title by default), description and privacy
(Private / Unlisted / Public; the default is set in the YouTube panel). Progress is
shown in the result card, separate from generation. On success you see the YouTube
video ID and URL. Google keeps videos uploaded through **unverified API projects**
(created after 28 July 2020) **private** until the project passes Google's audit;
the app shows the privacy YouTube actually applied instead of hiding it.
Failures (expired authorization, quota, network, invalid details, missing video)
are shown with what to do; the local video is never deleted because of a failure.

**Deleting a job's generated files** (YouTube panel > *Generated files of a job*):
after a successful download and after a successful upload you can **Ask each time**
(default), **Keep the files**, or **Delete automatically** (needs an explicit
permission tick). "Successful" means the browser received every byte of the MP4
(checked against its size) or YouTube returned a video ID. Deletion covers only
that job's workspace, `cache/jobs/<job id>/` (final MP4, audio, alignment,
subtitles, renders), plus the lesson's published copy of the MP4 only if it is
byte-identical to that job's video. It never touches `lessons/<name>/animation.py`
or the lesson's reusable build, voices, caches, settings, preferences,
credentials or other jobs. A small record (`state.json`, `job.json`,
`youtube.json`) stays so the page can still show what happened; if deletion
fails, the download/upload is still reported as a success, with the cleanup
failure shown separately.

**Where things are stored** (`local/`, git-ignored): `youtube_client.bin` and
`youtube_token.bin` (the OAuth client and authorization, encrypted with Windows
DPAPI for your Windows user), `youtube_account.json` (the connected channel's
public id/title), `preferences.json` (channel link, privacy, cleanup choices).
Tokens and secrets never reach the browser or the logs. Code:
`backend/youtube.py`, `backend/youtube_api.py`, `backend/cleanup.py`,
`backend/preferences.py`, `backend/secure_store.py`; tests: `tests/test_youtube.py`
(fakes: no Google account needed).

---

## 6. Subtitles

Optional; on by default. Configure globally in `settings.json`:

```json
"subtitles": { "enabled": true, "mode": "sentence", "formats": ["srt", "vtt"], "max_chars": 84, "embed_in_mp4": true }
```

- `mode`: `"sentence"` (one cue per sentence; long sentences split at
  `max_chars`) or `"word"` (one cue per word, for karaoke-style players).
- Per lesson: `subtitles = {"enabled": False}` (class attribute). Per
  narration: `narrate(..., subtitle=False)`. Per run: `--subtitles` / `--no-subtitles`.
- Timings come from WhisperX word alignment placed on the rendered timeline.

---

## 7. Configuration

`settings.json` (project root) holds the global settings; missing keys use
the defaults in `src/config/settings.py`.

```json
{
  "voice":     { "default": "teacher_a" },
  "audio":     { "enabled": true, "engine": "xtts_v2", "sample_rate": 44100,
                 "loudness_lufs": -18, "trim_silence": true, "pause_after": 0.25 },
  "alignment": { "enabled": true },
  "subtitles": { "enabled": true, "mode": "sentence", "formats": ["srt", "vtt"] },
  "video":     { "preview_quality": "low", "final_quality": "high" },
  "compute":   { "device": "auto" }
}
```

- `compute.device`: `"auto"` (CUDA GPU if available, else CPU), `"cpu"` or `"cuda"`.
- `audio`: every clip is trimmed of edge silence and loudness-normalised
  (two-pass EBU R128, -1.5 dBTP peak limit), so different voices play at the
  same volume without clipping. `pause_after` is the default gap after each narration.
- `video` qualities: `low` (854x480 @15), `medium` (720p30), `high` (1080p60), `4k`.
- `audio.enabled: false` renders visuals only (timing estimated from the text).
- `audio.engine: "sarvam"` (or `--engine sarvam` for one run) speaks with Sarvam AI's
  hosted Bulbul voices instead of XTTS. Put `SARVAM_API_KEY=<key>` in `.env` (project
  root). Sarvam has stock speakers only (no cloning) and each new clip uses API credits:

  ```json
  "audio": { "sarvam": { "model": "bulbul:v3", "speaker": "shubh", "pace": 1.0,
                         "voices": { "teacher_a": "ritu", "student_a": "rahul" } } }
  ```

  `voices` maps a voice library id to a Sarvam speaker; other voices use `speaker`.
  Languages: bn, en, gu, hi, kn, ml, mr, od, pa, ta, te.
- `validation` (layout checks, see [Layout validation](#layout-validation)); scene units, the frame is 14.2 x 8:

  ```json
  "validation": { "enabled": true, "fail_on_error": false, "auto_fit": true,
                  "safe_margin": 0.25, "max_overflow": 0.05, "min_font_size": 14,
                  "min_font_size_error": 10, "overlap_tolerance": 0.1,
                  "max_fill": 0.97, "min_padding": 0.04 }
  ```

  A lesson can override any of them with `layout_validation = {...}` on its class.

---

## 8. Project structure

```
lms-video-generator/
├── assets/voices/<id>/        voice library (samples + voice.json)
├── assets/{images,icons,fonts,audio}/
├── cache/{audio,alignment}/   generated clips / alignments (safe to delete)
├── lessons/<name>/
│   ├── animation.py           ← you author this
│   ├── source_script.txt      (optional) original teaching script
│   ├── generated/             script.json, timing.json, timeline.json, metadata.json, logs/
│   ├── audio/  alignment/  subtitles/  output/
├── src/
│   ├── animation/             LMSScene API (lms_scene.py), timing.py, manim_engine.py
│   ├── audio/                 voice_manager, tts_engine, audio_processor, audio_cache, audio_timing, audio_composer
│   ├── subtitles/             whisper_alignment, subtitle_config (cues), srt_generator, vtt_generator
│   ├── script/                models, parser (voice resolution), validator
│   ├── video/                 ffmpeg, compositor
│   ├── pipeline/generator.py  the end-to-end pipeline
│   ├── blender/               optional 3D engine: scene.py (BlenderScene), toolkit.py, runner.py (in Blender), render.py
│   ├── validation/            layout checks: layout.py (LayoutValidator), report.py
│   ├── config/                settings.py (settings.json), video_config.py (quality presets)
│   ├── components/  themes/  utils/  scenes/    visual helpers (unchanged)
├── scripts/
│   ├── generate_video.py  generate_audio.py  voice.py  setup.py  health_check.py  make_package.py
│   ├── render.py  render_preview.py  clean.py     (plain Manim rendering, no audio)
├── backend/                   web API (FastAPI): app.py, analysis.py, jobs.py, job_runner.py, workspace.py,
│                              speech_service.py, speech_client.py, voices.py, voice_upload.py, lessons.py,
│                              youtube.py, youtube_api.py, cleanup.py, preferences.py, secure_store.py
├── frontend/                  web UI (Next.js + TypeScript + Tailwind + Monaco): app/, components/, lib/
├── docs/                      this guide, YouTube_Setup_Guide.pdf, tested-environment.txt
├── local/                     (created on use; never shared) YouTube login + web preferences
├── tests/
├── settings.json  requirements.txt  pyproject.toml  manim.cfg  setup.ps1
├── generate.py                CLI entry point      package.json   npm run dev / backend / frontend
```

`scripts/render.py` / `render_preview.py` still render any scene silently
with Manim (useful while designing visuals); `generate_video.py` is the full
narrated pipeline.

---

## 9. Visual theme and components

`src/themes/default_theme.py` holds all colours, font sizes, spacing and
timing constants; `src/components/` has small helpers (`create_title`,
`create_equation`, `create_number_line`, `create_highlight_box`,
`create_correct_indicator`, ...). Lessons may use them or their own styling
(the Whole Numbers lesson has its own black-background style).
If you change `BACKGROUND`, also change `background_color` in `manim.cfg`.

Assets: shared files in `assets/`, lesson-only files in `lessons/<name>/assets/`;
load them with `asset_path("images", "x.png")` / `lesson_asset(__file__, "x.png")`
from `src.utils`.

---

## 10. Tests

```powershell
python -m pytest -q
```

117 tests (~2 minutes) cover the voice manager (exists / missing / multiple samples / invalid
samples), script extraction and voice inheritance (valid, missing voice,
invalid voice, mixed voices), audio (generation, normalisation, caching,
durations, composition), subtitles (sentence + word timestamps, SRT, VTT),
the full pipeline (animation.py → audio → timing → Manim → MP4, cache reuse,
subtitles on/off, audio-only, visual-only), layout validation, Blender, the web
API and jobs, and the YouTube/download/cleanup feature (with fakes, no Google
account). They use a fast synthetic "tone" voice instead of XTTS;
`python scripts/health_check.py --full` exercises the real XTTS and WhisperX.

Is this PC ready? `python scripts/health_check.py` prints PASS / WARN / FAIL for
Python, packages, Manim, FFmpeg, LaTeX, models, voices, configuration, cache,
web UI and a real render test.

---

## 11. Troubleshooting

| Problem | Fix |
|---------|-----|
| `Voice 'x' does not exist` | `python scripts/voice.py list`, fix the id in `animation.py`, or `voice.py add x --sample file.wav` |
| `FFmpeg was not found` | `winget install --id Gyan.FFmpeg`, then open a **new** terminal |
| `Manim failed while reading the narration` | A Python error in `animation.py`; the message shows the last lines of `generated/logs/extract.log` |
| `'phrase' is not in narration` | `at_word()` must use words that are actually in that `narrate()` text |
| `Narration id 'x' is used twice` | Every `narrate()` needs a unique id |
| A narration sounds wrong | Change the text (or voice) and re-run: only that clip is regenerated. Different wording, e.g. spelling numbers as words, often helps |
| Voice doesn't sound like the reference | Use more/cleaner reference audio (6-30 s total, no music or noise) |
| Very slow speech generation | Normal on CPU (~1.8x real time). A CUDA GPU makes it ~10x faster; set `compute.device` to `"auto"` |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `Failed to build moderngl` on install | The venv uses Python 3.14; recreate it with `py -V:3.12 -m venv .venv` |
| `latex` not found / `LaTeX error` | Install MiKTeX (section 2), open a new terminal |
| Warnings about `torchcodec` / `pyannote` | Harmless: they come from WhisperX's speaker-diarisation part, which is not used |

Full Manim logs: `lessons/<name>/generated/logs/`.

---

## 12. Licences, privacy and consent

> **Only use voice samples that you own or have permission to clone and synthesize.**
> Get written consent from every person whose voice is in `assets/voices/`.

- **XTTS v2 model licence: Coqui Public Model License (CPML), non-commercial
  use only.** Coqui has shut down, so a commercial licence can't be bought. For
  commercial distribution, swap in a commercially licensed engine: engines
  plug in through `src/audio/tts_engine.py` (`TTSEngine`), and the rest of the
  pipeline is engine-independent.
- Everything runs locally; voice samples and scripts are never uploaded.
  Models are downloaded once from Hugging Face / PyTorch.
- `.gitignore` excludes all audio (including voice samples), video, caches and
  generated files, so recordings are not committed by accident.
- Manim (MIT), WhisperX (BSD-2), FFmpeg (LGPL/GPL build): see their licences.
