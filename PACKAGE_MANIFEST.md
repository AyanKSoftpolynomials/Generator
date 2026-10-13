# Package manifest

| | |
|---|---|
| Package | `LMS_Video_Generator_Team_Package_v0.2.0.zip` |
| Version | 0.2.0 (from `pyproject.toml`; application behaviour unchanged by packaging) |
| Created | 2026-09-28 |
| Built with | `python scripts/make_package.py` (file list + SHA-256 of every file: `PACKAGE_FILES.txt`) |
| Tested on | Windows 11 Pro, AMD Ryzen 5 8500G (6C/12T), 15 GB RAM, no NVIDIA GPU (CPU speech) |

## Included

- Generator source (`src/`, `generate.py`, `lms_video_generator/`), web API (`backend/`), web UI source (`frontend/`, with `package-lock.json`)
- CLI tools (`scripts/`), including the new `health_check.py` and `make_package.py`; `setup.ps1`
- Configuration: `settings.json`, `manim.cfg`, `requirements.txt`, `pyproject.toml`, `package.json`, `.vscode/settings.json`, `.gitignore`
- 29 lesson sources (`lessons/<name>/animation.py`, plus READMEs and a source script), including `lessons/team_test` (smoke test)
- Synthetic test voices `teacher_a`, `teacher_b`, `student_a`, `narrator` (made from XTTS's built-in speakers, not real people)
- Tests (`tests/`, 117 tests)
- Docs: `SUPPORT_FOR_CLAUDE.md`, `README.md`, `docs/USER_GUIDE.md`, `docs/YouTube_Setup_Guide.pdf`, `docs/tested-environment.txt`, `lessons/README.md`

## Not included (on purpose)

| Left out | Why / how to get it |
|---|---|
| `.venv/`, `frontend/node_modules/`, `frontend/public/monaco/` | created by `setup.ps1` |
| XTTS v2 model (~1.9 GB), WhisperX alignment model (~360 MB) | downloaded automatically on first use (or `health_check.py --full`) |
| `cache/`, `output/`, generated lesson folders, videos, logs | rebuilt from `animation.py` |
| `local/` (YouTube OAuth client + token, preferences) | personal secrets; each user adds their own Google OAuth client |
| Real people's voice recordings (6 uploaded voices) | personal data; add consented recordings with `scripts/voice.py add` or the web UI |
| `tools/blender/` (portable Blender, ~1 GB) | optional; install Blender 4.2+ only for 3D lessons (`lessons/blender_demo`) |

## Expected environment

- Python 3.12 (3.11–3.13 work; 3.14 is not supported), FFmpeg 9.x on PATH, Node.js 20.9+ (tested 24.18.0), MiKTeX for `MathTex`
- Direct Python dependencies are pinned in `requirements.txt`: manim 0.21.0, torch/torchaudio 2.8.0 (CPU), coqui-tts 0.27.5,
  whisperx 3.8.6, fastapi 0.141.1, uvicorn 0.53.0, google-api-python-client 2.200.0, pytest 9.1.1, and others.
  The full tested set is in `docs/tested-environment.txt`.
- Frontend: next 16.3.6, react 19.2.8, monaco-editor 0.57.0, typescript 5.9.3, tailwindcss 4.3.3

## Verification (2026-09-28, before packaging)

| Check | Result |
|---|---|
| Python test suite | 117 passed |
| Frontend `npm run lint` / `npx tsc --noEmit` | clean / clean |
| Syntax: new scripts, all 29 lessons (`py_compile -W error`), `setup.ps1` (PowerShell parser) | OK |
| `scripts/health_check.py` on the development PC | READY (all PASS, incl. render test) |
| End-to-end: `generate.py lessons/team_test` (real XTTS + WhisperX + Manim + FFmpeg) | OK, 58 s; H.264 854x480 + AAC + subtitle track; layout check 0 issues |
| Secret scan of every packed text file | no secrets found |
| Fresh install from the extracted ZIP into a new folder with a space in its path (`setup.ps1 -Full`, new `.venv` + `node_modules`) | exit 0, health check **READY (1 warning: Blender not installed, optional)**; real XTTS test PASS (19 s incl. model load), WhisperX test PASS, render test PASS |

Note: the fresh install ran on the development PC, so pip/npm caches and the speech models (stored per Windows user)
were already present. On a brand-new PC the first run also downloads about 2 GB of packages and about 2.3 GB of models.

## Known limitations

See `SUPPORT_FOR_CLAUDE.md` §29. In short:
- XTTS v2 is licensed for non-commercial use only.
- Speech on a CPU is slow.
- Parallel jobs share one speech model, the CPU and the RAM.
- YouTube needs your own Google Cloud project; unverified projects can only upload private videos.
- LaTeX and Blender are installed manually.
