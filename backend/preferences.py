"""Persistent user preferences set in the web panel (local/preferences.json).

Kept apart from settings.json (the project configuration you edit by hand):

    youtube.channel_url      the saved YouTube destination (a reference only, never authentication)
    youtube.default_privacy  "private" / "unlisted" / "public" (the upload form's starting value)
    cleanup.after_download   "ask" / "keep" / "delete"  what to do with a job's files after a
    cleanup.after_upload     "ask" / "keep" / "delete"  successful download / YouTube upload
    cleanup.permission       when the user explicitly allowed automatic deletion (needed for "delete")
"""

from __future__ import annotations

import copy
import json
import os
import threading
import time
from pathlib import Path

from src.config.video_config import PROJECT_ROOT

LOCAL_DIR = PROJECT_ROOT / "local"
PREFS_FILE = LOCAL_DIR / "preferences.json"
PRIVACY = ("private", "unlisted", "public")
CLEANUP = ("ask", "keep", "delete")
DEFAULTS = {
    "youtube": {"channel_url": None, "default_privacy": "private"},
    # Default: a job's disposable generated files are deleted after a CONFIRMED download / upload
    # (job-local only, backend/cleanup.py). Users can switch to "ask" or "keep" in the YouTube panel.
    "cleanup": {"after_download": "delete", "after_upload": "delete",
                "permission": "default (delete after a successful download or upload)"},
}
_lock = threading.Lock()


class PreferenceError(ValueError):
    pass


def load(path: Path | None = None) -> dict:
    path = path or PREFS_FILE
    prefs = copy.deepcopy(DEFAULTS)
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return prefs
    for section, values in stored.items():
        if section in prefs and isinstance(values, dict):
            prefs[section].update({k: v for k, v in values.items() if k in prefs[section]})
    return prefs


def save(prefs: dict, path: Path | None = None) -> None:
    path = path or PREFS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(prefs, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def update(changes: dict, path: Path | None = None) -> dict:
    """Apply validated changes. Automatic deletion needs an explicit ``cleanup.confirm_delete``."""
    with _lock:
        prefs = load(path)
        youtube = changes.get("youtube") or {}
        cleanup = changes.get("cleanup") or {}
        if "default_privacy" in youtube:
            if youtube["default_privacy"] not in PRIVACY:
                raise PreferenceError(f"Privacy must be one of: {', '.join(PRIVACY)}.")
            prefs["youtube"]["default_privacy"] = youtube["default_privacy"]
        for key in ("after_download", "after_upload"):
            if key in cleanup:
                if cleanup[key] not in CLEANUP:
                    raise PreferenceError(f"{key} must be one of: {', '.join(CLEANUP)}.")
                prefs["cleanup"][key] = cleanup[key]
        wants_delete = "delete" in (prefs["cleanup"]["after_download"], prefs["cleanup"]["after_upload"])
        if wants_delete and not prefs["cleanup"]["permission"]:
            if not cleanup.get("confirm_delete"):
                raise PreferenceError("Automatic deletion needs your explicit permission: tick the confirmation.")
            prefs["cleanup"]["permission"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if not wants_delete:
            prefs["cleanup"]["permission"] = None            # permission is only kept while it is used
        save(prefs, path)
        return prefs


def set_channel_url(url: str | None, path: Path | None = None) -> dict:
    with _lock:
        prefs = load(path)
        prefs["youtube"]["channel_url"] = url
        save(prefs, path)
        return prefs
