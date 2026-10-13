# SUPPORT_FOR_CLAUDE.md — LMS Video Generator

Technical handoff document for an AI coding assistant (Claude or similar) or a
developer who takes over this project without the original developer.
Everything here was checked against the code of package v0.2.0 (2026-09-28).
When this file and the code disagree, **the code wins**; then fix this file.

**If you were told "read the support file and set up / run this project":**
do [§8 Installation](#8-installation), then [§32 Health check](#32-health-check-instructions),
then [§12 Generate a video](#12-how-to-generate-a-video). Read
[Rules for Claude](#rules-for-claude-working-on-this-project) before changing any code.

Other documents: `README.md` (short onboarding), `docs/USER_GUIDE.md` (full user
manual; program messages saying "see README > X" mean the section X there),
`lessons/README.md` (lesson folder layout), `docs/YouTube_Setup_Guide.pdf`,
`PACKAGE_MANIFEST.md` (versions, test results), `docs/tested-environment.txt`
(full `pip freeze` of the tested environment).

---

## Contents

1. [Project purpose](#1-project-purpose) · 2. [Structure](#2-project-structure) · 3. [Architecture map](#3-architecture-map) ·
4. [Component responsibilities](#4-component-responsibilities) · 5. [Complete workflow](#5-complete-workflow) ·
6. [Dependencies](#6-dependencies) · 7. [System requirements](#7-system-requirements) · 8. [Installation](#8-installation) ·
9. [Configuration](#9-configuration) · 10. [Environment variables](#10-environment-variables) · 11. [Start](#11-how-to-start-the-project) ·
12. [Generate a video](#12-how-to-generate-a-video) · 13. [animation.py API](#13-animationpy-formatapi) · 14. [LMSScene requirements](#14-lmsscene-requirements) ·
15. [Validation](#15-validation-workflow) · 16. [TTS](#16-tts-workflow) · 17. [WhisperX](#17-whisperx-workflow) · 18. [Manim](#18-manim-workflow) ·
19. [FFmpeg](#19-ffmpeg-workflow) · 20. [Job isolation](#20-jobworkspace-isolation) · 21. [Parallel jobs](#21-parallel-job-behavior) ·
22. [Cache](#22-cache-behavior) · 23. [Frontend/backend](#23-frontendbackend-communication) · 24. [Download](#24-download-workflow) ·
25. [YouTube](#25-youtube-upload-workflow) · 26. [Cleanup](#26-cleanup-behavior) · 27. [Important files](#27-important-directoriesfiles) ·
28. [Common errors](#28-common-errors-and-fixes) · 29. [Limitations](#29-known-limitations) · 30. [Safe modification](#30-safe-modification-rules) ·
31. [Testing](#31-testing-instructions) · 32. [Health check](#32-health-check-instructions) · 33. [Windows notes](#33-windows-specific-instructions) ·
[Rules for Claude](#rules-for-claude-working-on-this-project)

---

## 1. Project purpose

Turns ONE Python file per lesson, `lessons/<name>/animation.py`, into a finished
narrated teaching video (MP4 with voice-cloned narration, audio-synchronised
animation and subtitles) for the LMS / C-CAT maths and programming courses.

- The lesson author writes Manim visuals **and** narration (`self.narrate(...)`) in `animation.py`.
  It is the **only authoring source**: `generated/script.json` is extracted automatically.
  Never introduce a hand-written JSON/script workflow.
- Everything runs **locally**: Manim (animation), Coqui **XTTS v2** (voice cloning TTS),
  **WhisperX** (word timestamps), **FFmpeg** (audio/video). No cloud AI, no API keys, no paid services.
  (The only network use: first-run model downloads, pip/npm installs, and the optional YouTube upload.)
- Two front doors onto the **same engine** (`src/pipeline/generator.py::VideoGenerator`):
  the CLI (`python generate.py ...`) and a local web control panel (FastAPI + Next.js, `npm run dev`).
- Optional: Blender 3D sections, download with confirmation, YouTube upload (official API), job cleanup.

**Licence constraint:** the XTTS v2 model is under the Coqui Public Model License
(**non-commercial only**). The project owner accepted it for non-commercial use.
Commercial use requires swapping the TTS engine (see §16).

## 2. Project structure

```
lms-video-generator/                 project root (all commands run from here)
├── generate.py                      CLI entry: python generate.py lessons/<name>[/animation.py] [options]
├── setup.ps1                        one-time Windows setup (venv, packages, FFmpeg, Node, health check)
├── settings.json                    project configuration (merged over defaults in src/config/settings.py)
├── requirements.txt                 pinned Python dependencies (direct)
├── pyproject.toml                   version 0.2.0, Python >=3.11,<3.14, pytest config
├── manim.cfg                        Manim defaults (480p15, background #0E1726, media_dir, cache size)
├── package.json                     npm scripts: setup / dev / backend / frontend / build / lint
├── SUPPORT_FOR_CLAUDE.md  README.md  PACKAGE_MANIFEST.md
├── src/                             the generator (pure Python; no web code)
│   ├── animation/                   LMSScene authoring API (lms_scene.py), timing.py, manim_engine.py
│   ├── audio/                       voice_manager, tts_engine (XTTS), tts_worker, audio_processor,
│   │                                audio_cache, audio_timing, audio_composer
│   ├── subtitles/                   whisper_alignment (WhisperX), subtitle_config (cues), srt/vtt generators
│   ├── script/                      models (LessonScript), parser (voice resolution), validator
│   ├── pipeline/                    generator.py (VideoGenerator: the whole pipeline), build_cache.py
│   ├── validation/                  layout.py (LayoutValidator), report.py
│   ├── video/                       ffmpeg.py (wrapper), compositor.py (mux video+audio+subs)
│   ├── blender/                     optional 3D: scene.py, toolkit.py, runner.py (runs inside Blender), render.py
│   ├── config/                      settings.py (settings.json + defaults), video_config.py (paths, quality presets)
│   ├── components/ themes/ utils/   visual helpers, colour theme, errors (LMSError), asset helpers
│   └── scenes/                      empty placeholders (lesson code lives in lessons/)
├── lms_video_generator/core.py      compatibility alias: `from lms_video_generator.core import LMSScene`
├── backend/                         web API (FastAPI) + job system; wraps VideoGenerator, never re-implements it
├── frontend/                        web UI (Next.js 16, React 19, TypeScript, Tailwind 4, Monaco editor)
├── scripts/                         CLI tools: generate_video, generate_audio, voice, setup, health_check,
│                                    render, render_preview, clean, make_package, run_web.mjs
├── lessons/<name>/animation.py      lesson sources (+ generated/ audio/ alignment/ subtitles/ output/ after a build)
├── assets/voices/<id>/              voice library: sample_XX.wav + voice.json
├── assets/{images,icons,fonts,audio}/   shared lesson assets
├── tests/                           pytest suite (141 tests)
├── docs/                            USER_GUIDE.md, YouTube_Setup_Guide.pdf, tested-environment.txt
│
│   created at runtime (not in the package, never commit):
├── .venv/                           Python virtual environment
├── frontend/node_modules/  frontend/public/monaco/   npm packages; Monaco copied for offline use
├── cache/                           audio/ alignment/ jobs/ analyze/ blender/ deleted_voices/ speech_service.log
├── output/media/                    Manim working files per lesson (<lesson>_narrated/)
├── local/                           YouTube OAuth client+token (DPAPI-encrypted), preferences.json
└── tools/blender/                   optional portable Blender
```

## 3. Architecture map

```
                         ┌──────────────────────────── Browser (http://127.0.0.1:3000) ─┐
                         │ frontend/  Next.js UI: editor, narration table, voices,      │
                         │ progress (SSE), result card (play/download/YouTube)          │
                         └──────────────┬───────────────────────────────────────────────┘
                                        │ fetch /api/*  (Next.js rewrites → 127.0.0.1:8765)
┌───────────────────────────────────────▼──────────────────────────────────────────────┐
│ backend/app.py (FastAPI, 127.0.0.1:8765)  + backend/youtube_api.py router            │
│   analyze ─► backend/analysis.py ─► src/animation/manim_engine.run_manim("extract")  │
│   generate ─► backend/jobs.py JobManager (queue, N worker threads)                   │
└───────┬──────────────────────────────────────────────┬───────────────────────────────┘
        │ per job: workspace.seed() + subprocess        │ once: subprocess
        ▼                                               ▼
┌──────────────────────────────────┐   HTTP    ┌─────────────────────────────────────┐
│ python -m backend.job_runner     │ ────────► │ python -m backend.speech_service    │
│   (one OS process per job)       │ synthesize│   XTTS v2 + WhisperX loaded ONCE,   │
│   VideoGenerator.run() with      │ / align   │   shared by all jobs (locks: one    │
│   RemoteTTSEngine/RemoteAligner  │           │   TTS + one alignment at a time)    │
│   (backend/speech_client.py)     │           └─────────────────────────────────────┘
│   → Manim subprocess, FFmpeg     │
│   cwd = cache/jobs/<id>/         │
└──────────────┬───────────────────┘
               │ on success: workspace.publish() → lessons/<name>/ + output/media/<name>_narrated/
               ▼
          final MP4 in cache/jobs/<id>/output/  → download / YouTube upload / optional cleanup

CLI path (no web):  generate.py → scripts/generate_video.py → VideoGenerator (in-process XTTS + WhisperX,
                    builds directly in lessons/<name>/)
```

## 4. Component responsibilities

### Generator (`src/`)

| File | Key classes / functions | Responsibility |
|---|---|---|
| `src/pipeline/generator.py` | `VideoGenerator.run()`, `GenerateOptions`, `LessonPaths`, `Report`, `extract_script`, `check_layout`, `load_voices`, `generate_audio`, `align`, `render`, `write_subtitles`, `compose_video`, `plan` (dry run) | The whole pipeline, stage by stage, with per-stage caching and progress events |
| `src/pipeline/build_cache.py` | `hash_file`, `framework_hash`, `BuildManifest` | Input hashes per stage; `generated/build_cache.json` |
| `src/animation/lms_scene.py` | `NarrationMixin`, `LMSScene`, `LMS3DScene`, `LMSMovingCameraScene`, `Narration` | Authoring API: `narrate`, `scene_start/end`, `play_with`, `at_word`, `wait_for_narration`, `blender`; records narration (extract mode), writes timeline (render mode) |
| `src/animation/timing.py` | `NarrationTimingStore`, env `LMS_MODE` etc. | Modes: standalone / extract / render / plan; real durations from `generated/timing.json` |
| `src/animation/manim_engine.py` | `find_scene_class`, `run_manim`, `manim_failure` | Runs Manim as a subprocess; turns failures into readable `LMSError` with the animation.py line |
| `src/script/parser.py` / `models.py` / `validator.py` | `parse_extracted`, `LessonScript`, `NarrationBlock`, `validate_script` | Extracted data → script.json; voice aliases; id/text checks |
| `src/audio/voice_manager.py` | `VoiceManager`, `VoiceProfile`, `check_sample` | Voice library in `assets/voices/<id>/` |
| `src/audio/tts_engine.py` | `TTSEngine` (ABC), `XTTSEngine`, `create_engine` | XTTS v2 synthesis (model `tts_models/multilingual/multi-dataset/xtts_v2`) |
| `src/audio/tts_worker.py` | `init`, `synthesize` | CLI `--workers N`: parallel TTS processes |
| `src/audio/audio_processor.py` | `normalize` | Trim silence + two-pass EBU R128 loudness (FFmpeg loudnorm) |
| `src/audio/audio_cache.py` | `AudioCache` | Content-addressed clip cache `cache/audio/` |
| `src/audio/audio_composer.py` | `place_clips` | Narration track from clips at timeline positions |
| `src/subtitles/whisper_alignment.py` | `Aligner` | WhisperX forced alignment (wav2vec2), cache `cache/alignment/` |
| `src/subtitles/*` | `build_cues`, `write_srt`, `write_vtt` | Subtitle cues (sentence/word mode) |
| `src/video/ffmpeg.py`, `compositor.py` | `ffmpeg_path`, `run_ffmpeg`, `compose` | FFmpeg wrapper; final mux (H.264 + AAC + mov_text subtitles) |
| `src/validation/layout.py`, `report.py` | `LayoutValidator` (`check_fit`, `check_in_frame`, ...), `format_report` | Layout checks during the extract dry run |
| `src/blender/*` | `BlenderScene`, `Toolkit`, `apply_segments`, `find_blender` | Optional 3D sections rendered headlessly by Blender and spliced in |
| `src/config/settings.py` | `DEFAULTS`, `load_settings`, `resolve_device` | Settings merge; device auto/cpu/cuda |
| `src/config/video_config.py` | `PROJECT_ROOT`, `MEDIA_DIR`, `QUALITY_PRESETS` | Paths and quality presets (low/medium/high/4k) |
| `src/utils/errors.py` | `LMSError(message, fix, line)` | User-facing errors (message + fix), no tracebacks |

### Web backend (`backend/`)

| File | Responsibility |
|---|---|
| `app.py` | FastAPI app, all `/api/*` routes (health, voices, lessons, analyze, generate/status/events/result/video/cancel), error handlers, environment probe |
| `__main__.py` | `python -m backend [--port 8765] [--host 127.0.0.1]` (uvicorn) |
| `jobs.py` | `JobManager` (queue, `max_concurrent_jobs` worker threads, job state/logs, history reload, prune to 30 workspaces), `Job`, `SpeechService`/`SpeechPool` (starts the shared speech process) |
| `job_runner.py` | Child process for ONE job: builds `GenerateOptions`, runs `VideoGenerator` with remote TTS/aligner, emits JSON events on stdout (prefix `backend.EVENT_PREFIX`); also voice-test jobs |
| `workspace.py` | `seed()` job workspace from the lesson's last build (copies + hard links of write-once Manim files), `publish()` result back; per-lesson lock |
| `speech_service.py` | Shared HTTP speech server: `SpeechModels.synthesize/align` with separate locks |
| `speech_client.py` | `RemoteTTSEngine`, `RemoteAligner` (drop-in replacements used by job processes); env `LMS_SPEECH_URL` |
| `analysis.py` | `/api/analyze`: static check + extraction dry run in `cache/analyze/<hash>/`; returns narration blocks, voices, layout |
| `lessons.py` | Slugs, `check_source` (static AST checks), `write_animation`, `list_lessons` |
| `voices.py`, `voice_upload.py` | Voice library for the browser; upload → FFmpeg → 24 kHz mono WAV → `VoiceManager.add`; delete → `cache/deleted_voices/` |
| `youtube.py`, `youtube_api.py` | Optional YouTube: OAuth 2.0 + `videos.insert`, channel check, upload progress; download confirmation; cleanup endpoints |
| `cleanup.py` | `cleanup_job()`: deletes one job's generated files only |
| `preferences.py` | `local/preferences.json` (channel link, privacy, cleanup choices) |
| `secure_store.py` | DPAPI-encrypted secret files (Windows); chmod 600 elsewhere |

### Frontend (`frontend/`)

| File | Responsibility |
|---|---|
| `app/page.tsx`, `app/layout.tsx` | Single page → `VideoGeneratorApp` |
| `components/VideoGeneratorApp.tsx` | Page state: lesson, analysis, voice assignments, job, YouTube/prefs |
| `components/LessonPanel.tsx`, `CodeEditor.tsx` | Lesson name, Monaco editor (error line markers), open existing lesson |
| `components/NarrationPanel.tsx`, `LayoutReport.tsx` | Detected narration blocks + per-block voice dropdowns; layout issues |
| `components/VoiceLibrary.tsx`, `AddVoiceDialog.tsx` | Voices, preview, test, upload, delete |
| `components/GenerationPanel.tsx` | Progress per stage, logs, cancel |
| `components/VideoResult.tsx`, `VideoActions.tsx`, `NarratedVideo.tsx` | Player, Download (with confirmation), YouTube upload, cleanup prompt |
| `components/YouTubeSettings.tsx` | Channel link, OAuth client, connect/disconnect, privacy + cleanup preferences |
| `lib/api.ts`, `lib/types.ts` | API client + types; `lib/useJob.ts` job progress (SSE with polling fallback); `lib/youtubeConnect.ts` OAuth popup |
| `next.config.ts` | Rewrites `/api/*` → `LMS_API_URL` (default `http://127.0.0.1:8765`) |
| `scripts/copy-monaco.mjs` | Copies Monaco into `public/monaco` (offline editor) on install/dev/build |
| `AGENTS.md` / `CLAUDE.md` | Next.js 16 note: APIs differ from older Next.js; read `node_modules/next/dist/docs/` before editing |

## 5. Complete workflow

Actual order implemented in `VideoGenerator.run()` (stage names as shown in the UI):

```
animation.py (lesson source)
   │  [web only] POST /api/analyze: static checks (lessons.check_source) + extraction dry run
   │             in cache/analyze/ → narration table + voice dropdowns + layout report (lesson folder untouched)
   │  [web only] POST /api/generate → job id (12 hex) → queued → worker slot →
   │             workspace.seed(cache/jobs/<id>/) → subprocess backend.job_runner
   ▼
1 "Script"    Manim DRY RUN (LMS_MODE=extract): executes construct(), records every narrate()/scene_start(),
              runs LAYOUT VALIDATION → generated/script.json (+ layout results)   [cache: animation.py + framework hash]
   ▼          voices resolved (assignment > narrate(voice=) > scene_start(voice=) > class default_voice >
              settings voice.default; aliases applied) and validated (assets/voices/<id>/)
2 "TTS"       XTTS v2 per narration block → normalise (trim + loudness) → audio/<id>.wav   [cache: cache/audio/]
   ▼          (web: via the shared speech service; CLI: in-process, or --workers N processes)
3 "WhisperX"  forced alignment per clip → alignment/alignment.json + generated/timing.json   [cache: cache/alignment/]
   ▼
4 "Manim"     REAL RENDER (LMS_MODE=render) using real durations/word times → scene video
              + generated/timeline.json (when each narration starts)   [cache: Manim partial movies]
              + optional Blender segments rendered and spliced (src/blender/render.py)
   ▼
5 "Subtitles" cues from alignment + timeline → subtitles/<lesson>.srt/.vtt   (if enabled)
   ▼
6 "FFmpeg"    clips placed on the timeline → audio/narration_track.wav; mux video + audio + soft subtitles
              → output/<lesson>_preview.mp4 (preview) or output/<lesson>.mp4 (final) + generated/metadata.json
   ▼
   [web] job completed → workspace.publish() to lessons/<name>/ (last successful job wins)
   ▼
   Download (browser fetch with progress, byte count confirmed by server)  and/or  YouTube upload
   ▼
   optional cleanup of that job's workspace (only after a confirmed success; §26)
```

Audio is the timing authority: the animation is rendered after the audio exists, so it re-times itself
when narration changes; clips can never overlap.

## 6. Dependencies

### Python packages (`requirements.txt`, pinned; installed by `setup.ps1`)

| Package | Version | Purpose |
|---|---|---|
| manim | 0.21.0 | animation engine (Community Edition) |
| numpy / scipy / pillow | 2.5.3 / 1.18.1 / 12.3.0 | numerics, images |
| torch / torchaudio | 2.8.0 (CPU wheels via `--extra-index-url https://download.pytorch.org/whl/cpu`; CUDA 12.8 wheels installed by `scripts/setup.py` if an NVIDIA GPU is found) | XTTS / WhisperX runtime |
| coqui-tts | 0.27.5 | XTTS v2 (maintained Coqui fork; import name `TTS`) |
| whisperx | 3.8.6 | forced alignment |
| soundfile | 0.14.0 | WAV I/O |
| fastapi / uvicorn / python-multipart | 0.141.1 / 0.53.0 / 0.0.32 | web API, uploads |
| google-api-python-client / google-auth-oauthlib / google-auth-httplib2 | 2.200.0 / 1.4.1 / 0.4.2 | optional YouTube upload (imported lazily) |
| pytest / httpx | 9.1.1 / 0.28.1 | tests only |

The full tested environment (181 packages incl. transitive, e.g. transformers 4.57.6, pyannote-audio 4.0.7,
moderngl 5.12.0, av 18.1.0) is frozen in `docs/tested-environment.txt`.

### System dependencies / external tools

| Tool | Tested version | Required? | Install (Windows) |
|---|---|---|---|
| Python | 3.12.10 (3.11–3.13 OK; **3.14 NOT**: no moderngl/glcontext wheels) | yes | `winget install Python.Python.3.12` or `py install 3.12` |
| FFmpeg + ffprobe | 9.0.1 (gyan.dev full build) | yes (on PATH) | `winget install --id Gyan.FFmpeg` (setup does it) |
| LaTeX: MiKTeX (`latex`, `dvisvgm`) | MiKTeX 25.12, dvisvgm 3.4.3 | only for `MathTex`/`Tex` (most math lessons use it) | `winget install --id MiKTeX.MiKTeX --scope user` then `initexmf --set-config-value="[MPM]AutoInstall=1"` |
| Node.js + npm | 24.18.0 / 11.16.0 (Next.js 16 needs ≥ 20.9) | only for the web UI | `winget install --id OpenJS.NodeJS.LTS` (setup does it) |
| Blender | 4.5 LTS | optional (only lessons calling `self.blender(...)`, e.g. `lessons/blender_demo`) | PATH, `settings.json > blender.path`, env `BLENDER_PATH`, or portable in `tools/blender/` |

### Frontend packages (`frontend/package.json`, locked by `frontend/package-lock.json`)

next 16.3.6, react / react-dom 19.2.8, monaco-editor 0.57.0, @monaco-editor/react 4.7.0,
typescript 5.9.3, tailwindcss 4.3.3, eslint 9.39.5 (+ eslint-config-next 16.3.6).

### Model files (downloaded automatically on first use; not in the package)

| Model | Size | Location | Downloaded when |
|---|---|---|---|
| XTTS v2 (`tts_models/multilingual/multi-dataset/xtts_v2`) | ~1.9 GB | `%LOCALAPPDATA%\tts\tts_models--multilingual--multi-dataset--xtts_v2\` (override: env `TTS_HOME`) | first TTS (or `health_check.py --full`) |
| WhisperX English alignment (torchaudio `WAV2VEC2_ASR_BASE_960H`) | ~360 MB | `%USERPROFILE%\.cache\torch\hub\checkpoints\wav2vec2_fairseq_base_ls960_asr_ls960.pth` | first alignment |
| Other languages' alignment models | varies | Hugging Face cache `%USERPROFILE%\.cache\huggingface\` | first alignment in that language |
| Whisper `small` (faster-whisper, speech check §16) | ~460 MB | Hugging Face cache `%USERPROFILE%\.cache\huggingface\hub\models--Systran--faster-whisper-small` | first new clip (without it clips are generated unchecked) |

`XTTSEngine` sets `COQUI_TOS_AGREED=1` (CPML accepted by the project owner) so no interactive prompt appears.

### Optional

Blender (3D), MiKTeX (formulas), Node.js (web UI), Google Cloud OAuth client (YouTube), NVIDIA GPU + CUDA PyTorch (~10x faster speech).

## 7. System requirements

- Windows 10/11 (primary, tested on Windows 11 Pro). macOS/Linux mostly work for the CLI; DPAPI secret storage is Windows-only (elsewhere: file mode 600).
- CPU: any modern x64. Tested: AMD Ryzen 5 8500G (6 cores / 12 threads), **no GPU**: XTTS ≈ 1.8x real time.
- RAM: 8 GB minimum, 16 GB recommended. Shared speech process ≈ 2.5–3 GB; each job process ≈ 0.3–1 GB (mostly Manim).
- Disk: ~6 GB for packages + models, plus caches (grow with use; `scripts/clean.py`).
- Network: first install and first model download only (and YouTube upload if used).

## 8. Installation

Fresh Windows PC, from the extracted project folder (e.g. `C:\Work\LMS_Video_Generator`), in PowerShell:

```powershell
cd C:\Work\LMS_Video_Generator
powershell -ExecutionPolicy Bypass -File .\setup.ps1          # ~10-20 min on first run (downloads ~2 GB of packages)
# optional flags: -Full (also download + test XTTS/WhisperX models), -SkipFrontend (CLI only), -NoInstallTools (no winget)
```

`setup.ps1` (safe to re-run; never deletes `.venv`, settings, lessons, voices or `local/`):
1. finds Python 3.12/3.13/3.11 via `py` or `python` (installs 3.12 with winget if none),
2. creates `.venv` if missing (refuses a `.venv` with the wrong Python instead of deleting it),
3. `pip install -r requirements.txt`,
4. runs `scripts/setup.py` (FFmpeg via winget if missing; CUDA PyTorch if `nvidia-smi` finds a GPU; LaTeX check),
5. Node.js check/install + `npm --prefix frontend install` (postinstall copies Monaco),
6. creates `cache/ output/ local/`,
7. runs `scripts/health_check.py` (with `--full` if `-Full`).

**Manual steps that cannot be automated:**
- MiKTeX (LaTeX) if missing and lessons use `MathTex`: `winget install --id MiKTeX.MiKTeX --scope user`, then
  `initexmf --set-config-value="[MPM]AutoInstall=1"`, open a **new** terminal.
- After winget installs anything, a **new terminal** may be needed for PATH (setup refreshes PATH in its own session).
- YouTube upload needs the user's own Google Cloud OAuth client (§25).
- Real people's voices are not shipped (§16); add consented recordings with `scripts/voice.py add` or the web UI.

Manual alternative to setup.ps1:
```powershell
py -V:3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1                 # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install -r requirements.txt
python scripts/setup.py                      # FFmpeg / GPU / LaTeX checks
npm run setup                                # web UI packages
python scripts/health_check.py
```

## 9. Configuration

| File | Edited by | Content |
|---|---|---|
| `settings.json` | hand | project settings; any missing key falls back to `src/config/settings.py::DEFAULTS` (deep merge) |
| `manim.cfg` | hand (rarely) | Manim defaults; `background_color` must equal `src/themes/default_theme.py::BACKGROUND` (a test checks) |
| `local/preferences.json` | web UI | YouTube channel link, default privacy, cleanup choices + permission timestamp |
| `local/youtube_client.bin`, `youtube_token.bin` | web UI | encrypted OAuth client / token (never edit, never share) |
| `assets/voices/<id>/voice.json` | `scripts/voice.py` / web UI | voice metadata |

`settings.json` keys (values shipped in the package):

```jsonc
{
  "voice":     { "default": "teacher_a", "aliases": { "teacher": "teacher_a", "student": "student_a" } },
  "audio":     { "enabled": true, "engine": "xtts_v2", "sample_rate": 44100, "loudness_lufs": -18,
                 "trim_silence": true, "pause_after": 0.25, "workers": 1 },   // workers: CLI TTS processes
  "alignment": { "enabled": true },
  "subtitles": { "enabled": true, "mode": "sentence", "formats": ["srt","vtt"], "max_chars": 84, "embed_in_mp4": true },
  "video":     { "preview_quality": "low", "final_quality": "high" },          // low 480p15, medium 720p30, high 1080p60, 4k
  "compute":   { "device": "auto" },                                            // auto | cpu | cuda
  "web":       { "max_concurrent_jobs": 5, "speech_workers": 1 }
  // defaults also exist for: "blender" {path, engine EEVEE|CYCLES|WORKBENCH, samples},
  // "youtube" {redirect_uri: "http://127.0.0.1:3000/api/youtube/oauth/callback"},
  // "validation" {enabled, fail_on_error:false, auto_fit, safe_margin, max_overflow, min_font_size, ...}
}
```

On a PC with less than 16 GB RAM consider `"max_concurrent_jobs": 2` or `3` (default in code is 3).

There is **no `.env` file**: the project does not read one. Environment variables (§10) are optional overrides.

## 10. Environment variables

| Variable | Read by | Effect |
|---|---|---|
| `MAX_CONCURRENT_JOBS` | `backend/jobs.py` | overrides `settings.json > web.max_concurrent_jobs` |
| `SPEECH_WORKERS` | `backend/jobs.py` | overrides `web.speech_workers` (each shared speech process ≈ 3 GB RAM) |
| `LMS_API_URL` | `frontend/next.config.ts` | where the UI proxies `/api/*` (default `http://127.0.0.1:8765`) |
| `BLENDER_PATH` | `src/blender/render.py` | Blender executable if not in settings/PATH/tools |
| `TTS_HOME` | coqui-tts | where the XTTS model is stored/downloaded |
| `COQUI_TOS_AGREED` | coqui-tts | set to 1 automatically by `XTTSEngine` |
| `OMP_NUM_THREADS`, `MKL_NUM_THREADS` | torch | set per job by `JobManager` (cpu_count // max_concurrent_jobs) unless already set |
| **Internal — never set by hand:** `LMS_MODE`, `LMS_TIMING_FILE`, `LMS_OUTPUT_FILE`, `LMS_DEFAULT_PAUSE`, `LMS_VALIDATION` (generator → Manim subprocess, `src/animation/timing.py`), `LMS_SPEECH_URL` (API → job process) | | |

## 11. How to start the project

```powershell
npm run dev          # API (python -m backend, 127.0.0.1:8765, docs at /api/docs) + UI (http://127.0.0.1:3000)
npm run backend      # API only   (= .\.venv\Scripts\python.exe -m backend)
npm run frontend     # UI only    (needs the API for anything useful)
```

`scripts/run_web.mjs` starts both, prefixes their output `[api]` / `[web]`, and stops both when one exits.
It requires `.venv` and `frontend/node_modules` (it prints what to run if missing). Both servers bind to
**127.0.0.1 only** — analyzing/generating executes the lesson's Python code, so never expose them to a network.
The API starts the shared speech process lazily on the first job (log: `cache/speech_service.log`).

## 12. How to generate a video

**CLI** (builds in `lessons/<name>/`):

```powershell
.\.venv\Scripts\python.exe generate.py lessons\team_test               # preview 480p (default); ~1 min on CPU first time
.\.venv\Scripts\python.exe generate.py lessons\team_test --final       # 1080p60
.\.venv\Scripts\python.exe generate.py lessons\integers --dry-run      # what would be regenerated
# more: --audio-only --subtitles-only --no-subtitles --no-audio --voice ID --assign NARRATION_ID=VOICE
#       --scene CLASS --name FILE --force --force-tts --force-alignment --force-render --force-compose --workers N
```
Output: `lessons/<name>/output/<name>_preview.mp4` (or `<name>.mp4` for `--final`), subtitles in
`lessons/<name>/subtitles/`, report in `lessons/<name>/generated/metadata.json`, logs in `generated/logs/`.
`scripts/generate_video.py` is the same program; `scripts/generate_audio.py` = narration only.

**Web UI:** `npm run dev` → http://127.0.0.1:3000 → lesson name → paste/upload `animation.py` (or *Open existing*)
→ **Analyze Animation** → check narration blocks / choose voices → **Generate Video** (preview or final) →
progress → play → **Download Video** / **Upload to YouTube**.

`lessons/team_test/` is a ~9 s two-voice smoke-test lesson (Text only, no LaTeX; verified end to end: 58 s on a CPU-only PC).

## 13. animation.py format/API

```python
from manim import *
from src.animation import LMSScene          # also: LMS3DScene, LMSMovingCameraScene, Narration, MANIM, BLENDER
# (legacy alias also works: from lms_video_generator.core import LMSScene  -> camera-capable scene)


class WholeNumbersVideo(LMSScene):          # exactly ONE class whose base is literally LMSScene / LMS3DScene / LMSMovingCameraScene

    lesson_title = "Whole Numbers"          # optional; shown as the video title (fallback: lesson id = folder name)
    default_voice = "teacher_a"             # optional lesson default voice
    # optional: language = "en"; subtitles = {"enabled": False} or {"mode": "word"};
    #           default_pause_after = 0.4; lesson_id = "..."; layout_validation = {"min_font_size": 14}

    def construct(self):
        self.scene_start("hook", title="Hook")                       # named section; optional voice=, engine=MANIM|BLENDER
        title = Text("WHOLE NUMBERS")
        n = self.narrate("hook_01", "Hello again, my dear students!") # returns Narration (.duration .start .end)
        self.play_with(n, Write(title))                              # animation lasts the rest of the narration
        self.wait_for_narration(n)                                   # hold until it (plus pause) has finished
        self.scene_end()                                             # optional: section voice stops applying

        self.scene_start("dialogue", voice="teacher_b")              # section default voice
        n = self.narrate("dialogue_01", "Zero is a whole number too.")
        self.at_word(n, "zero")                                      # wait until the word is spoken (WhisperX)
        self.play(FadeIn(Text("0")))
        self.narrate("dialogue_02", "Ten!", voice="student_a", pause_after=0.5, subtitle=True)
```

| Call | Meaning |
|---|---|
| `narrate(id, text, voice=None, subtitle=True, pause_after=None)` | Queue speech starting now (after any narration still playing). Does not block. `id` unique in the lesson (names `audio/<id>.wav`; duplicate → error). Empty text → error. |
| `scene_start(id, voice=None, title=None, engine=MANIM)` | Begin a section; `voice` = default for its narration; `engine=BLENDER` for 3D sections. |
| `scene_end(id=None)` | End the section (recorded in timeline.json; clears the section voice). |
| `play_with(n, *anims, fraction=1.0)` | Play animations over the remaining time of narration `n` (or a fraction). |
| `at_word(n, "phrase", occurrence=1, lead=0.1)` | Wait until the phrase is spoken. The phrase must occur in that narration's text. |
| `wait_for_narration(n=None, include_pause=True)` | Hold the picture until `n` (default: latest) finishes. |
| `remaining(n=None)`, `duration_of(n)` | Seconds left / total audio length. |
| `blender(SceneClass, narration=n, duration=None, **params)` | 3D clip rendered by Blender for exactly that time (`src/blender/`). |
| `self.validator.check_fit / check_in_frame / check_spacing / check_size / check_no_overlap / ignore` | Explicit layout checks (§15). |

**Voice selection** (most specific wins): web/CLI assignment (`--assign id=voice`, UI dropdown) > `narrate(voice=)` >
`scene_start(voice=)` > class `default_voice` > `settings.json voice.default`. Aliases from `settings.json voice.aliases`
(`"teacher"`→`teacher_a`, `"student"`→`student_a`). A voice change in the UI never rewrites `animation.py`.

**Subtitles:** on by default; per lesson `subtitles = {...}` class attribute; per narration `subtitle=False`;
per run `--subtitles/--no-subtitles` (or the UI toggle).

**Title / class name:** the video title is `lesson_title` or else the lesson id (folder name / slug of the UI lesson name).
The class name only identifies the scene (`--scene` picks one if several plain classes exist).

## 14. LMSScene requirements

- **Static detection (AST, before any code runs):** the file must parse, and must contain exactly ONE top-level
  class whose base is written literally as `LMSScene`, `LMS3DScene` or `LMSMovingCameraScene` (`X(LMSScene)` or
  `X(module.LMSScene)`). Web: `backend/lessons.py::check_source` ("No narrated scene found" / "Several narrated scenes").
  CLI: `src/animation/manim_engine.py::find_scene_class`. A subclass of a subclass (`class A(MyBase)`) is NOT detected.
- **`narrate()` is detected by EXECUTION, not by parsing:** the extract dry run runs `construct()` and records each
  `narrate()` call actually executed. Therefore narration must be **deterministic**: the same ids/texts, in the same
  order, in the extract run and the render run (no randomness, time, or file-dependent branching around `narrate`).
  Narration inside loops/helper functions is fine if deterministic. Ids must be unique.
- Don't time narrated content with `self.wait(3)`; use `play_with` / `at_word` / `wait_for_narration`.
- Everything else is ordinary Manim (Community Edition 0.21). `MathTex`/`Tex` need LaTeX; `₹` and `−` work in MathTex (preamble added by LMSScene).
- Plain `manim` / `scripts/render.py` still render an LMSScene silently with estimated durations.
- Assets: `asset_path("images","x.png")`, `lesson_asset(__file__, "x.png")` from `src.utils`.
- Size limit via the web: 1 MB source.

## 15. Validation workflow

1. **Static** (`check_source`): syntax, narrated class (above).
2. **Script validation** (`src/script/validator.py`): ids, text, voices exist (web analyze: voices reported as warnings).
3. **Layout validation** (`src/validation/layout.py`), inside the extract dry run using real mobject geometry after every
   `play()`/`wait()`: `text_overflow` (ERROR), `frame_overflow`, `safe_area`, `off_screen`, `overlap`, `box_overlap`,
   `text_too_large`/`tight_fit`, `text_too_small`. Reported in the console/log, `generated/metadata.json > layout_validation`,
   the UI's Analyze panel and the job result. **`fail_on_error` defaults to false**: 8 of the 21 lessons that existed when validation was added have real
   layout errors and must keep generating. Only `check_fit` changes geometry (scales text into its box, never below
   `min_font_size`); all other checks only report. Config: `settings.json > validation`, per lesson `layout_validation = {...}`.
   Tests: `tests/test_validation.py`.

## 16. TTS workflow

- Engine: `XTTSEngine` (`src/audio/tts_engine.py`), Coqui XTTS v2 via `coqui-tts` 0.27.5, languages
  en es fr de it pt pl tr ru nl cs ar zh-cn ja hu ko hi. Only engine implemented (`settings.json audio.engine = "xtts_v2"`).
- Voice cloning uses **all** `sample_*.wav` of the voice as `speaker_wav` references.
- **Voice library** `assets/voices/<id>/voice.json` + samples. Shipped in the package: `teacher_a` (3 samples), `teacher_b`,
  `student_a`, `narrator` — **synthetic** voices generated from XTTS built-in speakers (`"synthetic": true`, not real people).
  Real people's uploaded voices are personal data and are **not** in the package; add your own with consent:
  `python scripts/voice.py add <id> --sample rec.wav --name "..."` or the web *Add voice* dialog
  (WAV/MP3/M4A/OGG/FLAC/WebM/AAC/Opus, ≤25 MB, 2 s–5 min, consent checkbox → 24 kHz mono WAV).
  `scripts/voice.py list|info|validate|speakers|create-synthetic`.
- Per clip: XTTS → `audio_processor.normalize` (trim edge silence, two-pass EBU R128 to −18 LUFS, −1.5 dBTP, 44.1 kHz)
  → `cache/audio/<key>.wav` → `audio/<id>.wav` + `<id>.meta.json`. Key = text + voice sample hashes + language + engine
  fingerprint + processing settings.
- **Speech check** (`src/audio/speech_check.py`, called by `XTTSEngine.synthesize`): XTTS sometimes speaks words that are
  not in the text, mostly on one-to-three-word lines ("No." → "No, I am not.") and around unusual punctuation. Every
  new English clip is transcribed with a local Whisper model (faster-whisper `small`) and compared with its text; a clip
  that does not match is generated again, up to `MAX_ATTEMPTS` (4), and the closest attempt is kept. A clip that never
  matched is reported as a `Speech check: '<id>' ...` warning in the job result / `metadata.json` with what was heard.
  Numbers are compared loosely (Whisper writes "40-12" for "forty minus twelve"), so a wrong number is NOT detected;
  other languages are not checked; `--workers N` retries but does not report the warning. The engine fingerprint ends
  in `checked-v1`, so clips cached before the check existed are regenerated, not reused.
- **Device:** `compute.device` auto → CUDA if `torch.cuda.is_available()` else CPU. `setup.py` installs CUDA torch when `nvidia-smi` exists.
- **Model loading:** lazily on the first cache miss (a fully cached run never imports TTS). CLI: in-process
  (or `--workers N` separate processes, each ~2 GB). Web: ONE shared process `backend/speech_service.py` loads it once;
  jobs call it over HTTP through `RemoteTTSEngine`; a TTS lock serves one synthesis at a time. If the service can't start,
  a job falls back to loading its own model (logged warning).
- Swapping engines (e.g. for commercial use): implement `TTSEngine` (`synthesize`, `fingerprint`, `settings`) and register
  it in `create_engine`; the rest of the pipeline is engine-independent.

## 17. WhisperX workflow

- `Aligner` (`src/subtitles/whisper_alignment.py`): **forced alignment** of the known text (wav2vec2 via
  `whisperx.load_align_model` + `whisperx.align`), not speech recognition. Output: word + sentence times.
- Cache: `cache/alignment/<audio hash>-<text hash>-<lang>-wav2vec2-forced-v1.json` (atomic writes, shared by jobs).
  Only changed clips are re-aligned. Missing word times are interpolated; if WhisperX is unavailable, times are estimated.
- Results: `alignment/alignment.json`, `generated/timing.json` (durations + word times read by the Manim render).
- Web: runs in the shared speech service (separate lock from TTS). Harmless warnings about torchcodec/pyannote come from WhisperX's unused diarisation part.

## 18. Manim workflow

- Manim Community 0.21.0 is run as a **subprocess** by `run_manim()` in three modes (env `LMS_MODE`):
  `extract` (dry run: record narration + layout, `generated/script.json`), `render` (real, with `generated/timing.json`,
  writes `generated/timeline.json`), `plan` (for `--dry-run`: which animations are cached).
- Quality presets: preview → `video.preview_quality` (low = 854x480 @15), final → `video.final_quality` (high = 1920x1080 @60).
- Media folder: CLI `output/media/<lesson>_narrated/`; web job `cache/jobs/<id>/scenes/`. `max_files_cached = 5000`
  (manim.cfg) so partial-movie caching works for long lessons: only changed animations re-render.
- Failures are converted to `LMSError` with the exception, the `animation.py` line and a hint; raw log in `generated/logs/`.
- Blender sections: after Manim, `src/blender/render.py` renders each `self.blender(...)` segment with
  `blender -b --factory-startup --python src/blender/runner.py` and splices it over its exact frames (cache `cache/blender/`).

## 19. FFmpeg workflow

`src/video/ffmpeg.py` finds `ffmpeg`/`ffprobe` on PATH (clear error + winget fix otherwise). Used for: loudness
normalisation of every clip, voice upload conversion, narration track assembly (`audio_composer.place_clips` →
`audio/narration_track.wav`), durations (ffprobe), Blender clip encoding, and the final mux
(`compositor.compose`): H.264 video + AAC audio + optional `mov_text` soft subtitle track → MP4. Verified output of
`lessons/team_test`: h264 854x480 + aac + mov_text.

## 20. Job/workspace isolation

- Each web generation = job with id `uuid4().hex[:12]` (validated by regex `^[0-9a-f]{12}$` where used as a path).
- Own **workspace** `cache/jobs/<id>/`: `animation.py` (the submitted code), `generated/ audio/ alignment/ subtitles/
  output/`, `scenes/` (own Manim media), `job.json` (request), `output.log` (raw log), `state.json` (final snapshot),
  `youtube.json` (after an upload).
- `workspace.seed()` copies the lesson's last successful build in (small files copied; Manim's write-once content-hashed
  files hard-linked), so caches still hit. Files a job may rewrite are real copies → a job cannot modify another job's
  or the lesson's files.
- Own **process** (`python -m backend.job_runner job.json`), own stdout pipe → own **logs** (max 4000 lines in memory)
  and **status** (`queued → running → completed | failed | cancelled`, with per-stage state, progress %, queue position,
  PID). Cancel kills only that process tree (`taskkill /T /F`). A crash affects no other job.
- `lessons/<name>/animation.py` is only (re)written when a job **succeeds** (`workspace.publish`, under a per-lesson lock).
- Finished jobs survive an API restart (reloaded from `state.json`); the newest 30 workspaces are kept (`KEEP_WORKSPACES`).

## 21. Parallel job behavior

Facts (not marketing): jobs are separate processes with separate workspaces/status/logs, **but they are NOT fully
independent**:

- `web.max_concurrent_jobs` (5 in the shipped `settings.json`, code default 3, env `MAX_CONCURRENT_JOBS`) jobs run at
  once; more wait in a FIFO queue with a position.
- **Shared speech process:** with `speech_workers: 1`, all jobs share ONE XTTS model and ONE WhisperX model. TTS requests
  from different jobs are served **one at a time** (lock); alignment likewise (separate lock). So 5 jobs' speech stages
  queue behind each other; Manim/FFmpeg run truly in parallel. If the speech process dies, it is restarted on the next
  job's `ensure()`; running jobs' speech calls fail meanwhile. `speech_workers: N` starts N speech processes (≈3 GB each)
  and round-robins jobs over them.
- **Shared CPU/RAM:** each job gets `OMP/MKL_NUM_THREADS = cpu_count // max_concurrent_jobs`. Five renders on a 6-core
  CPU all slow down. Measured on the dev PC (Ryzen 5 8500G, 15 GB, CPU only): five lessons started within 15 s all ran,
  ~2.4 GB RAM for the five job processes, all finished within ~7 minutes.
- **Shared caches:** `cache/audio`, `cache/alignment`, `cache/analyze/_tex`, Manim write-once files (hard links). All are
  content-addressed and written atomically (temp file + `os.replace`), so sharing is safe and only speeds things up.
- **Same lesson in two jobs:** each builds in its own workspace; on success each publishes to `lessons/<name>/` under a
  lock — **the last job to finish wins** as the lesson's saved version. Both jobs' videos stay intact in their workspaces.
- Voice-test jobs use the same queue/slots.
- The 5-at-once configuration was measured once on the dev PC; it has no automated test.

## 22. Cache behavior

| Stage | Re-runs only when… | Where |
|---|---|---|
| Script extraction | `animation.py`, framework code (`src/`, `manim.cfg`), pause or validation settings change | `generated/build_cache.json` |
| TTS (per clip) | its text, voice samples, language, engine/model, audio settings change | `cache/audio/` (shared by all lessons/jobs) + `audio/<id>.meta.json` |
| WhisperX (per clip) | the clip's audio or text changes | `cache/alignment/` + `alignment/alignment.meta.json` |
| Manim (per animation) | that animation's content/run time changes | Manim partial movies in the media folder; `generated/manim/<quality>/` |
| Subtitles / FFmpeg | inputs change | `generated/build_cache.json` |

Unchanged lesson → ~1 s rebuild, no model loaded. `--force*` flags bypass caches; `--dry-run` shows the plan.
Other caches: `cache/analyze/` (last 30 analyses + shared compiled LaTeX `_tex`), `cache/jobs/` (last 30 jobs),
`cache/blender/`, `cache/deleted_voices/` (voices removed in the UI, restorable). Voice tests run as ordinary jobs
in `cache/jobs/`. **Everything in `cache/` and `output/` may be deleted**
when the app is stopped (it is rebuilt; first builds are slower). `python scripts/clean.py [--all] [--cache]` cleans
Manim files / videos / audio cache.

## 23. Frontend/backend communication

- Browser → Next.js (127.0.0.1:3000) → rewrite `/api/*` → FastAPI (127.0.0.1:8765). The browser never talks to 8765 directly
  and never sees absolute paths (logs are made project-relative by `jobs._public`).
- Main endpoints (`backend/app.py`, `backend/youtube_api.py`; interactive docs at http://127.0.0.1:8765/api/docs):
  `GET /api/health` · `GET/POST/DELETE /api/voices…` · `POST /api/voices/{id}/test` · `GET /api/lessons[/{id}]` ·
  `POST /api/analyze` · `POST /api/generate` → `{jobId}` · `GET /api/generate/{job}/status|events|result|video[?download=1]|narration` ·
  `POST /api/generate/{job}/cancel` · `POST /api/generate/{job}/downloaded|cleanup|youtube` · `GET /api/generate/{job}/youtube` ·
  `GET/PUT /api/preferences` · `GET /api/youtube`, `PUT/DELETE /api/youtube/link`, `POST /api/youtube/client|connect|refresh|disconnect`,
  `GET /api/youtube/oauth/callback`.
- Progress: `lib/useJob.ts` uses Server-Sent Events (`/events`), falling back to polling `/status`. Job id is kept per browser tab.
- Errors: JSON `{error, detail(hint), line?, code?}`: `InputError` → 400, `LMSError` → 422 (both with the animation.py
  `line` for the editor marker), `YouTubeError` → 409 (not_connected, channel_mismatch/unverified, busy) or 422, with `code`.

## 24. Download workflow

Result card → **Download Video**: `lib/api.ts::downloadWithProgress` fetches `GET /api/generate/{job}/video?download=1`
(the generator's MP4 from `cache/jobs/<id>/output/`, byte for byte, never re-encoded) into a Blob with a progress bar,
saves it via the browser, then `POST /api/generate/{job}/downloaded {bytes}`; the server confirms only if `bytes` equals the
file size (else `incomplete_download`, nothing deleted). The confirmation (`downloaded: {bytes, at}`) is stored in the job's
`state.json` and may trigger the cleanup preference (§26). Download works without any YouTube setup.
CLI users just take `lessons/<name>/output/*.mp4`.

## 25. YouTube upload workflow

Optional; nothing changes for users who never set it up. Official **YouTube Data API v3** only (`videos.insert`,
`channels.list(mine=True)`), OAuth 2.0 authorization-code flow with PKCE (`google_auth_oauthlib.Flow`), scopes
`youtube.upload` + `youtube.readonly`. No scraping, browser automation or passwords.

1. **Google setup (user, once, free)** — step-by-step with clickable links in `docs/YouTube_Setup_Guide.pdf`:
   Cloud project → enable YouTube Data API v3 → OAuth consent screen (External, Testing, add the channel owner as test user)
   → OAuth client **Web application** with redirect URI exactly `http://127.0.0.1:3000/api/youtube/oauth/callback`
   (`settings.json > youtube.redirect_uri` if different) → download the client JSON.
2. Web UI → YouTube panel → **Add client_secret.json** (≤64 KB) → stored DPAPI-encrypted in `local/youtube_client.bin`.
3. **Connect YouTube** → popup to Google → callback page `postMessage`s the result → token stored encrypted in
   `local/youtube_token.bin`; the API asks YouTube which channel was authorized → `local/youtube_account.json` (public id/title).
4. **Channel link** (optional, a reference only, never used for auth): saved in `local/preferences.json`; before an upload the
   authorized channel is compared with it → `channel_mismatch` / `channel_unverified` (409) unless the user confirms.
5. **Upload:** title (1–100 chars), description (≤5000 bytes, no `<`/`>`), privacy private/unlisted/public, category 27
   (Education). Background thread, resumable 8 MB chunks with retries; progress polled every 1 s (separate from generation).
   Result: video id + URL + the privacy YouTube actually applied (`youtube.json` in the job folder).
6. **Failures** are mapped to codes (quota, upload_limit, expired → reconnect, forbidden, invalid_metadata, network,
   missing_video) and never delete anything.
7. **Constraints:** Google forces uploads from **unverified** API projects (created after 28 Jul 2020) to **private** until an
   audit — the app shows this, never bypasses it. Testing-mode tokens expire after **7 days** (Reconnect). Default quota
   ≈ 6 uploads/day. Disconnect revokes the token at Google and deletes it locally.
8. Secrets never reach the browser, logs, job metadata or the package. `local/` is per-user and per-PC (DPAPI): copying it to
   another PC does not work — each teammate adds their own client JSON.
Code: `backend/youtube.py`, `backend/youtube_api.py`, `frontend/components/YouTubeSettings.tsx`, `VideoActions.tsx`,
`lib/youtubeConnect.ts`. Tests: `tests/test_youtube.py` (fakes, no network).

## 26. Cleanup behavior

- Preferences (YouTube panel): after download / after upload → **Ask each time** (default) | **Keep** | **Delete automatically**
  (requires an explicit permission tick; stored with a timestamp; cleared when no longer used).
- Runs **only after a confirmed success** (complete byte count, or a YouTube video id). A failed download/upload is never
  permission. Manual cleanup `POST /api/generate/{job}/cleanup {after}` is refused without that success.
- Scope (`backend/cleanup.py`): strictly `cache/jobs/<job id>/` of that job (id validated, path must resolve inside
  `cache/jobs`), keeping `state.json`, `job.json`, `youtube.json` so the UI can still show what happened; plus the lesson's
  published MP4 copy **only if byte-identical** (SHA-256) to that job's video. Never touches `lessons/<name>/animation.py`,
  the lesson's reusable build, voices, caches, settings, preferences, credentials or other jobs.
- Refused while the job or its upload is running. A cleanup failure is reported separately and never turns the download/upload
  success into a failure. After cleanup the video endpoint returns 410.
- Separate from cleanup: the API keeps only the newest 30 job workspaces (`jobs._prune`, never active jobs).

## 27. Important directories/files

| Path | Notes |
|---|---|
| `src/pipeline/generator.py` | the pipeline — read first when debugging generation |
| `src/animation/lms_scene.py` | authoring API contract — changes affect every lesson |
| `backend/jobs.py`, `workspace.py`, `job_runner.py`, `speech_service.py` | job system and isolation |
| `settings.json`, `src/config/settings.py` | configuration + defaults |
| `lessons/<name>/animation.py` | lesson sources (28 lessons + `team_test`); generated sub-folders are rebuilt |
| `lessons/<name>/generated/metadata.json`, `generated/logs/` | per-build report and Manim logs |
| `cache/jobs/<id>/output.log`, `state.json` | per-job raw log and final state |
| `cache/speech_service.log` | shared speech process log |
| `assets/voices/` | voice library (only synthetic voices in the package) |
| `local/` | per-user secrets + preferences — never commit, never package |
| `tests/conftest.py` | test fixtures: temporary voice library + deterministic "tone" TTS engine |

## 28. Common errors and fixes

| Symptom | Cause / fix |
|---|---|
| `Failed to build moderngl` during pip install | venv on Python 3.14 → delete/rename `.venv`, `py -V:3.12 -m venv .venv`, re-run setup |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (or run setup with `-ExecutionPolicy Bypass`) |
| `python -` hangs in Git Bash | Windows Store python alias waiting on stdin — call `.venv/Scripts/python.exe` explicitly |
| `FFmpeg was not found` | `winget install --id Gyan.FFmpeg`, open a **new** terminal |
| `latex` not found / LaTeX error / MathTex fails | install MiKTeX + AutoInstall (§8), new terminal; `tests/test_environment.py` also fails without it |
| `No narrated scene found` | the class must extend `LMSScene`/`LMS3DScene`/`LMSMovingCameraScene` directly (a plain `Scene` has no narration) |
| `Several narrated scenes found` | keep one narrated class per animation.py (CLI: `--scene`) |
| `Narration id 'x' is used twice` | every `narrate()` needs a unique id |
| `'phrase' is not in narration` | `at_word()` phrase must be in that narration's text |
| `Voice 'x' does not exist` | `python scripts/voice.py list`; fix the id, pick another voice in the UI, or `voice.py add x --sample f.wav`. Lessons built on another PC may reference uploaded voices that are not shipped |
| `Manim failed while reading the narration` | Python error in animation.py; see the highlighted line and `generated/logs/extract.log` |
| `No .venv found` / `Frontend dependencies missing` from `npm run dev` | run `setup.ps1` (or `npm run setup`) |
| Port 3000/8765 in use | another instance is running: find it with `Get-NetTCPConnection -LocalPort 8765` (or 3000) and stop it. The ports are fixed in `scripts/run_web.mjs` / `frontend/package.json` / `LMS_API_URL`, and 3000 is part of the YouTube redirect URI |
| Very slow speech | normal on CPU (~1.8x real time); first run also downloads ~1.9 GB model |
| A clip says words that are not in the script | XTTS inventing speech (short lines, odd punctuation); the speech check (§16) regenerates such clips. `Speech check: '<id>' ...` warning = it never matched: listen to `audio/<id>.wav`, reword the line (avoid one-word lines and "(c), and."-style punctuation) or rebuild with `--force-tts` |
| Warnings about torchcodec / pyannote / audioop | harmless |
| YouTube `redirect_uri_mismatch` | redirect URI in Google must exactly equal the one shown in the YouTube panel |
| YouTube "expired" after a week | testing-mode token expiry → Reconnect |
| Upload applied "private" although public was chosen | unverified Google API project; change visibility in YouTube Studio |
| `compute.device is "cuda" but no CUDA GPU` | set `"auto"` or `"cpu"`, or install CUDA torch (`python scripts/setup.py` on a GPU PC) |

## 29. Known limitations

- XTTS v2 licence: **non-commercial only** (CPML). Speech on CPU is slow (~1.8x real time).
- Parallel jobs share one speech model (serialised TTS/alignment), CPU and RAM (§21); last successful job of a lesson wins.
- Narration is extracted by execution → must be deterministic; narrated class detected only by its literal base name.
- `fail_on_error` is off by default; 8 of the 21 older lessons contain real layout errors (they still generate).
- LaTeX (MiKTeX) is a manual install; lessons with `MathTex` fail without it.
- Blender lessons need Blender installed separately (not shipped; ~1 GB).
- YouTube: own Google Cloud project required; unverified projects upload private; 7-day token expiry in testing mode; ~6 uploads/day quota.
  DPAPI secrets are bound to one Windows user on one PC.
- Web UI/API are local-only (127.0.0.1), single-user, no authentication — do not expose them to a network.
- Real people's voice recordings are not included; lessons generated before with those voices need another voice or the recordings (with consent).
- Tested on Windows 11 only.

## 30. Safe modification rules

- The web backend must keep wrapping the **same** `VideoGenerator` as the CLI — never add a second pipeline.
- Voice choices from the UI are `voice_assignments`; never rewrite `animation.py` to change a voice.
- Keep `animation.py` backwards compatible: existing lessons must keep generating (don't turn layout errors into failures by default).
- Keep job isolation: jobs write only in their workspace; lessons/ updated only via `workspace.publish` under the lock;
  shared caches content-addressed + atomic writes.
- Keep ONE shared speech process per `speech_workers`; don't reintroduce per-job model loading (it swapped a 15 GB PC to a crawl).
- Only `check_fit` may mutate geometry in validation.
- Cleanup must stay limited to one validated job workspace and only after a confirmed success, with explicit permission.
- Never log/print/send OAuth tokens or client secrets; they stay in `local/` (encrypted), never in the frontend, logs,
  job metadata, `animation.py` or the package.
- Don't restart the web app while a job is running (`GET /api/health` → `busy`).
- Don't edit lesson files with PowerShell `Get-Content/Set-Content` (it mangled `—`, `₹`, `−` once); use an editor/UTF-8-safe tool.
- Next.js 16 differs from older versions — read `frontend/node_modules/next/dist/docs/` before changing frontend code.
- No LLM / paid AI / cloud service may be added to the pipeline.

## 31. Testing instructions

```powershell
.\.venv\Scripts\python.exe -m pytest -q                 # 141 tests, ~2 min, no network, no real models
.\.venv\Scripts\python.exe -m pytest tests/test_web.py -q   # one file
npm run lint                                             # frontend ESLint
cd frontend; npx tsc --noEmit; cd ..                     # frontend type check
```

Tests use a deterministic "tone" TTS engine and temporary voice libraries (`tests/conftest.py`), fakes for Google
(`tests/test_youtube.py`), and real Manim + FFmpeg renders. `tests/test_environment.py` requires running inside `.venv`
and `ffmpeg`, `latex`, `dvisvgm` on PATH. Real XTTS + WhisperX: `python scripts/health_check.py --full`.
Real end-to-end: `python generate.py lessons\team_test` (~1 min on CPU; add `--force` to ignore caches).

**Building a new team package:** `python scripts/make_package.py` → `dist/LMS_Video_Generator_Team_Package_v<version>.zip`
(version from `pyproject.toml`). It packs source, docs, lesson `animation.py` files and only the synthetic voices;
excludes `.venv`, `node_modules`, `cache/`, `output/`, `local/`, `tools/`, generated lesson folders, videos and logs;
scans every text file for secrets and refuses to write the ZIP on a hit; adds `PACKAGE_FILES.txt` (SHA-256 of every file).
`--list` previews; `--include-voice ID` adds a real voice only with the speaker's consent to share it.

## 32. Health-check instructions

```powershell
.\.venv\Scripts\python.exe scripts\health_check.py          # ~20-30 s incl. a real Manim render test
.\.venv\Scripts\python.exe scripts\health_check.py --quick  # skip the render test
.\.venv\Scripts\python.exe scripts\health_check.py --full   # + real XTTS speech and WhisperX alignment (downloads models on first run)
```

Checks (each PASS / WARN / FAIL with a fix line): Python version, `.venv`, pinned package versions vs `requirements.txt`,
Manim / TTS / WhisperX / web packages import, FFmpeg + ffprobe, LaTeX, compute device, XTTS + WhisperX models present,
project folders writable, `settings.json`, voice library (default voice usable), cache size, Blender (only WARN if a lesson
needs it), YouTube (optional), Node.js + frontend packages, whether the web app is running, render test.
Ends with `READY`, `READY (n warnings)` or `NOT READY` (exit code 1). It installs nothing and changes no project files.
The running API also reports `GET http://127.0.0.1:8765/api/health` (busy, running jobs, speech service, ffmpeg, device).
The older `python scripts/setup.py --check` still exists (setup-oriented checks).

## 33. Windows-specific instructions

- Use PowerShell from the project root. Call the venv's Python explicitly (`.\.venv\Scripts\python.exe`) or activate it.
- Execution policy: `powershell -ExecutionPolicy Bypass -File .\setup.ps1`, or once `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- After any `winget install`, open a new terminal so PATH changes apply.
- Extract the project to a user-writable folder (e.g. `C:\Work\...` or Documents), not `Program Files`; paths with spaces work.
- Job cancel uses `taskkill /T /F` on the job's process tree; jobs start with `CREATE_NEW_PROCESS_GROUP`.
- Hard links are used between caches and workspaces (same NTFS volume; falls back to copies otherwise).
- File locks: Windows keeps open files locked; e.g. the YouTube upload closes its MP4 handle before cleanup (WinError 32 fix).
- Secrets use Windows DPAPI (per Windows user). Python 3.14 is not supported; the Windows Store `python` alias can hang in Git Bash.

---

## Rules for Claude Working on This Project

1. **Read this file before modifying code**, then read the actual implementation of what you change — do not assume APIs
   from memory (Manim 0.21, Next.js 16 and coqui-tts differ from older versions you may know).
2. **Do not replace working architecture unnecessarily.** Prefer minimal, targeted changes in the existing files.
3. **Do not remove dependencies or features** (CLI, web UI, Blender, validation, voices, download, YouTube, cleanup) without explicit instruction.
4. **Preserve `animation.py` compatibility**: every existing lesson must still generate; `animation.py` stays the only authoring source.
5. **Preserve job isolation** (§20) and the shared speech service (§21); keep the web path wrapping the same `VideoGenerator`.
6. **Preserve the TTS → WhisperX → Manim → Subtitles → FFmpeg workflow** and its caches (§5, §22).
7. **After setup, run the health check** (`scripts/health_check.py`); report FAIL/WARN lines honestly.
8. **After modifications, run the relevant tests** (`python -m pytest -q`, plus `npm run lint` / `npx tsc --noEmit` for frontend
   changes); for pipeline changes also generate `lessons/team_test`.
9. **Never expose or commit secrets** (`local/`, client JSON, tokens); never log them; never put them in the frontend or package.
10. **Never delete user data** (lessons, voices, `local/`, job outputs) unless the user explicitly asks; confirm destructive steps.
11. **Don't restart the web app while a job is running** (check `/api/health` → `busy`).
12. **Only use voice samples the user owns or has permission to clone**; keep the XTTS non-commercial licence in mind.
13. **No LLMs, paid AI or cloud services** in the pipeline; everything stays local.
14. **Update this file (and `docs/USER_GUIDE.md`) when architecture or commands change.** Describe facts, not assumptions.
