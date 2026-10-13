"""Build the team distribution ZIP of this project (source + docs, no private data).

    python scripts/make_package.py                 # -> dist/LMS_Video_Generator_Team_Package_v<version>.zip
    python scripts/make_package.py --list          # only print what would be packed
    python scripts/make_package.py --include-voice prasad   # also ship a real (non-synthetic) voice you may share

What is left out, and why:
    .venv/ frontend/node_modules/ frontend/.next/    recreated by setup.ps1
    frontend/public/monaco/                          copied from node_modules by npm install
    cache/ output/ lessons/*/{generated,audio,alignment,subtitles,output}/   generated; rebuilt from animation.py
    local/                                           YouTube OAuth client + token (encrypted, per Windows user), preferences
    tools/                                           portable Blender (optional, ~1 GB; install separately)
    assets/voices/<id>/ unless voice.json has "synthetic": true   real people's recordings are personal data
    __pycache__ .pytest_cache *.pyc *.log .env dist/

Before writing the ZIP every text file is scanned for secrets (OAuth client
secrets, access/refresh tokens, API keys, private keys). A hit stops the build.
Nothing in the project is changed; only dist/ is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE_FOLDER = "LMS_Video_Generator"

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SKIP_TOP = {".venv", "cache", "output", "local", "tools", "dist", "media", ".git", ".pytest_cache", ".playwright-mcp"}
SKIP_ANYWHERE = {"__pycache__", ".pytest_cache", "node_modules", ".next"}
SKIP_PATHS = {"frontend/public/monaco", "frontend/tsconfig.tsbuildinfo"}
LESSON_GENERATED = {"generated", "audio", "alignment", "subtitles", "output"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".log", ".mp4", ".mov", ".webm", ".tmp"}
SKIP_NAMES = {".env", "Thumbs.db", ".DS_Store", "animation.previous.py"}
AUDIO = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
TEXT = {".py", ".md", ".txt", ".json", ".toml", ".cfg", ".ts", ".tsx", ".mjs", ".js", ".css", ".ps1", ".yml",
        ".yaml", ".ini", ".html", ".gitignore"}

SECRET_PATTERNS = {
    "Google OAuth client secret": re.compile(r"GOCSPX-[A-Za-z0-9_\-]{10,}"),
    "Google access token": re.compile(r"ya29\.[A-Za-z0-9_\-]{20,}"),
    "Google refresh token": re.compile(r"\b1//0[A-Za-z0-9_\-]{20,}"),
    "Google API key": re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "client_secret value": re.compile(r"\"client_secret\"\s*:\s*\"[^\"]{12,}\""),
    "token value": re.compile(r"\"(?:access_token|refresh_token)\"\s*:\s*\"[^\"]{12,}\""),
    "DPAPI secret blob": re.compile(r"LMSDPAPI1\n"),
}
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
ALLOWED_EMAILS = {"noreply@anthropic.com"}


def version() -> str:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def shareable_voices(extra: set[str]) -> set[str]:
    voices = set()
    for meta in (ROOT / "assets" / "voices").glob("*/voice.json"):
        try:
            synthetic = json.loads(meta.read_text(encoding="utf-8")).get("synthetic") is True
        except ValueError:
            synthetic = False
        if synthetic or meta.parent.name in extra:
            voices.add(meta.parent.name)
    return voices


def included(rel: Path, voices: set[str]) -> bool:
    parts = rel.parts
    posix = rel.as_posix()
    if parts[0] in SKIP_TOP or set(parts) & SKIP_ANYWHERE:
        return False
    if any(posix == p or posix.startswith(p + "/") for p in SKIP_PATHS):
        return False
    if rel.name in SKIP_NAMES or rel.suffix.lower() in SKIP_SUFFIXES:
        return False
    if parts[0] == "lessons" and len(parts) > 2 and parts[2] in LESSON_GENERATED:
        return False
    if parts[:2] == ("assets", "voices") and len(parts) > 3:
        return parts[2] in voices
    if rel.suffix.lower() in AUDIO:
        return False                     # no audio outside the shared (synthetic) voice library
    return True


def collect(voices: set[str]) -> list[Path]:
    files = []
    for folder, dirs, names in os.walk(ROOT):
        here = Path(folder).relative_to(ROOT)
        # prune skipped folders instead of walking .venv / node_modules
        dirs[:] = [d for d in dirs if d not in SKIP_ANYWHERE and not (here == Path(".") and d in SKIP_TOP)]
        for name in names:
            rel = here / name
            if included(rel, voices):
                files.append(rel)
    return sorted(files, key=lambda p: p.as_posix())


def scan(files: list[Path]) -> tuple[list[str], list[str]]:
    secrets, notes = [], []
    for rel in files:
        if rel.suffix.lower() not in TEXT and rel.name not in {".gitignore"}:
            continue
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for label, pattern in SECRET_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                secrets.append(f"{rel.as_posix()}:{line}: {label}")
        for email in sorted(set(EMAIL.findall(text)) - ALLOWED_EMAILS):
            if not email.endswith((".png", ".svg", ".js", ".json")):
                notes.append(f"{rel.as_posix()}: e-mail address {email}")
    return secrets, notes


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the team distribution ZIP.")
    parser.add_argument("--list", action="store_true", help="print the files that would be packed and stop")
    parser.add_argument("--include-voice", action="append", default=[], metavar="ID",
                        help="also pack this non-synthetic voice (only with the speaker's consent to share it)")
    args = parser.parse_args()

    voices = shareable_voices(set(args.include_voice))
    files = collect(voices)
    if args.list:
        print("\n".join(f.as_posix() for f in files))
        print(f"\n{len(files)} files; voices: {', '.join(sorted(voices))}")
        return 0

    secrets, notes = scan(files)
    for note in notes:
        print(f"note: {note}")
    if secrets:
        print("SECRETS FOUND - package not written:")
        for hit in secrets:
            print(f"  {hit}")
        return 1

    name = f"LMS_Video_Generator_Team_Package_v{version()}"
    DIST.mkdir(exist_ok=True)
    target = DIST / f"{name}.zip"
    listing = [f"{name}  (built {time.strftime('%Y-%m-%d %H:%M')})", "sha256  bytes  path"]
    total = 0
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in files:
            path = ROOT / rel
            size = path.stat().st_size
            total += size
            listing.append(f"{sha256(path)}  {size}  {rel.as_posix()}")
            zf.write(path, f"{PACKAGE_FOLDER}/{rel.as_posix()}")
        zf.writestr(f"{PACKAGE_FOLDER}/PACKAGE_FILES.txt", "\n".join(listing) + "\n")
    print(f"voices packed: {', '.join(sorted(voices))}")
    print(f"secret scan: no secrets in {len(files)} files")
    print(f"{target}  ({target.stat().st_size / 1e6:.1f} MB zipped, {total / 1e6:.1f} MB unpacked, {len(files) + 1} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
