# LMS Video Generator

Turns one Python file per lesson (`lessons/<name>/animation.py`: Manim visuals + `self.narrate(...)`)
into a narrated MP4 with cloned voices, audio-synced animation and subtitles. Runs fully locally
(Manim, XTTS v2, WhisperX, FFmpeg); optional web UI, download and YouTube upload.

## Quick start (Windows)

1. **Extract the ZIP** to a folder you can write to, e.g. `C:\Work\LMS_Video_Generator`.
2. **Open that folder in VS Code** (File → Open Folder).
3. **Read [SUPPORT_FOR_CLAUDE.md](SUPPORT_FOR_CLAUDE.md)**, or tell your AI assistant:
   *"Read SUPPORT_FOR_CLAUDE.md and set up / run this project."*
4. **Run setup** (VS Code terminal, PowerShell; ~10-20 min the first time):
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\setup.ps1
   ```
5. **Health check** (setup already ran it; re-run any time):
   ```powershell
   .\.venv\Scripts\python.exe scripts\health_check.py
   ```
   Expect `READY`. Fix any `FAIL` line with the `fix:` shown under it.
6. **Start the application**:
   ```powershell
   npm run dev          # then open http://127.0.0.1:3000
   ```
7. **Generate a test video** (~1 min on a CPU; the first run also downloads the ~2 GB speech models):
   ```powershell
   .\.venv\Scripts\python.exe generate.py lessons\team_test
   ```
   Result: `lessons\team_test\output\team_test_preview.mp4`. In the web UI: *Open existing* → `team_test`
   → **Analyze Animation** → **Generate Video**.

Needs Windows 10/11, 8 GB+ RAM (16 GB recommended), ~6 GB disk. `setup.ps1` installs Python 3.12,
FFmpeg and Node.js with winget if missing. For lessons with formulas (`MathTex`) install MiKTeX once:
`winget install --id MiKTeX.MiKTeX --scope user`, then `initexmf --set-config-value="[MPM]AutoInstall=1"`.

## Documentation

| File | For |
|---|---|
| [SUPPORT_FOR_CLAUDE.md](SUPPORT_FOR_CLAUDE.md) | technical reference: architecture, workflow, dependencies, errors, rules for AI assistants |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | full user manual (writing lessons, voices, generating, web UI, YouTube, troubleshooting). Messages saying "see README > …" refer to its sections |
| [lessons/README.md](lessons/README.md) | lesson folder layout |
| [docs/YouTube_Setup_Guide.pdf](docs/YouTube_Setup_Guide.pdf) | optional YouTube upload setup |
| [PACKAGE_MANIFEST.md](PACKAGE_MANIFEST.md) | package version, tested versions, test results |

**Licence note:** the XTTS v2 voice model is licensed for **non-commercial use only** (Coqui Public Model License).
Only use voice recordings you own or have the speaker's permission to clone.
