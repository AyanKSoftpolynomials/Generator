"""Web API for the optional YouTube upload, download confirmation and job cleanup.

    GET    /api/youtube                         connection status, saved link, link check
    PUT    /api/youtube/link   DELETE ...        save / change / remove the channel link
    POST   /api/youtube/client                  add the Google OAuth client (client_secret.json)
    POST   /api/youtube/connect                 start authorization -> {"authUrl"}
    GET    /api/youtube/oauth/callback          Google redirects here after the user decides
    POST   /api/youtube/refresh                 re-check which channel is connected
    POST   /api/youtube/disconnect              revoke + forget the authorization (videos untouched)
    GET    /api/preferences  PUT ...            cleanup and privacy preferences
    POST   /api/generate/{job}/youtube          upload this job's MP4 -> progress via GET
    GET    /api/generate/{job}/youtube
    POST   /api/generate/{job}/downloaded       the browser saved the whole MP4 (bytes checked)
    POST   /api/generate/{job}/cleanup          delete this job's generated files (after a success only)

Generation itself is untouched: none of this runs unless the user asks for it.
"""

from __future__ import annotations

import html
import json
import threading
import time
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.config.settings import load_settings
from src.config.video_config import PROJECT_ROOT

from backend import preferences
from backend.cleanup import cleanup_job
from backend.jobs import JOBS_DIR, TERMINAL
from backend.analysis import forget_analysis
from backend.lessons import LESSONS_DIR, slugify
from backend.youtube import YouTubeError, YouTubeService, check_link, parse_channel_url, validate_metadata

MAX_CLIENT_BYTES = 64 * 1024


class LinkRequest(BaseModel):
    url: str


class PreferencesRequest(BaseModel):
    youtube: dict | None = None
    cleanup: dict | None = None


class UploadRequest(BaseModel):
    title: str
    description: str = ""
    privacy: str = "private"
    confirmChannel: bool = False         # the user saw the channel warning and chose to upload anyway


class DownloadedRequest(BaseModel):
    bytes: int


class CleanupRequest(BaseModel):
    after: str                           # "download" or "upload": the success that allows it


class ResetRequest(BaseModel):
    jobId: str | None = None             # the page's current job (its generated files are deleted)
    animation: str | None = None         # the script whose cached analysis is dropped
    lessonName: str | None = None


def make_router(jobs, youtube: YouTubeService | None = None) -> APIRouter:
    router = APIRouter()
    yt = youtube or YouTubeService()
    router.youtube = yt                  # tests reach the service through the router

    def status() -> dict:
        prefs = preferences.load()
        account = yt.account() if yt.connected() else None
        return {
            "clientConfigured": yt.client_config() is not None,
            "connected": yt.connected(),
            "channel": account,
            "channelUrl": prefs["youtube"]["channel_url"],
            "linkCheck": check_link(prefs["youtube"]["channel_url"], account),
            "redirectUri": load_settings()["youtube"]["redirect_uri"],
            "defaultPrivacy": prefs["youtube"]["default_privacy"],
        }

    # -- settings --------------------------------------------------------------------

    @router.get("/api/youtube")
    def get_status():
        return status()

    @router.put("/api/youtube/link")
    def save_link(body: LinkRequest):
        parse_channel_url(body.url)                     # validates; raises YouTubeError
        preferences.set_channel_url(body.url.strip())
        return status()

    @router.delete("/api/youtube/link")
    def remove_link():
        preferences.set_channel_url(None)
        return status()

    @router.post("/api/youtube/client")
    async def save_client(file: UploadFile = File(...)):
        raw = await file.read(MAX_CLIENT_BYTES + 1)
        if len(raw) > MAX_CLIENT_BYTES:
            raise YouTubeError("That file is too large to be an OAuth client JSON.", "invalid_client")
        yt.save_client(raw)
        return status()

    @router.post("/api/youtube/connect")
    def connect():
        return {"authUrl": yt.start_authorization(load_settings()["youtube"]["redirect_uri"])}

    @router.get("/api/youtube/oauth/callback", response_class=HTMLResponse)
    def oauth_callback(state: str | None = None, code: str | None = None, error: str | None = None):
        try:
            account = yt.finish_authorization(state, code, error)
            ok, message = True, f"YouTube connected: {account['title']}"
        except YouTubeError as err:
            ok, message = False, err.message + (f" {err.hint}" if err.hint else "")
        payload = json.dumps({"youtube": "connected" if ok else "failed", "message": message})
        return HTMLResponse(f"""<!doctype html><meta charset="utf-8"><title>YouTube</title>
<body style="font-family:system-ui;background:#0b1020;color:#e2e8f0;display:grid;place-items:center;height:90vh">
<div><h2>{'Connected' if ok else 'Not connected'}</h2><p>{html.escape(message)}</p>
<p style="color:#94a3b8">You can close this window.</p></div>
<script>try {{ window.opener && window.opener.postMessage({payload}, window.location.origin); }} catch (e) {{}}
setTimeout(function () {{ window.close(); }}, 1500);</script></body>""")

    @router.post("/api/youtube/refresh")
    def refresh():
        yt.refresh_account()
        return status()

    @router.post("/api/youtube/disconnect")
    def disconnect():
        return {**yt.disconnect(), **status()}

    @router.get("/api/preferences")
    def get_preferences():
        return preferences.load()

    @router.put("/api/preferences")
    def put_preferences(body: PreferencesRequest):
        return preferences.update({"youtube": body.youtube or {}, "cleanup": body.cleanup or {}})

    # -- per job ---------------------------------------------------------------------

    def finished_job(job_id: str):
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "Unknown job")
        if job.status != "completed":
            raise YouTubeError("This job has no finished video.", "not_ready")
        if job.cleanup:
            raise YouTubeError("This job's generated files were deleted (cleanup).", "cleaned")
        return job

    def video_path(job) -> Path:
        relative = (job.result or {}).get("outputs", {}).get("video")
        path = (PROJECT_ROOT / relative).resolve() if relative else None
        if not path or (JOBS_DIR / job.id).resolve() not in path.parents or not path.is_file():
            raise YouTubeError("The generated MP4 is missing (the job workspace was removed).", "missing_video")
        return path

    def upload_record(job_id: str) -> dict | None:
        upload = yt.uploads.get(job_id)
        if upload:
            record = upload.public()
            if not upload.settled and record["status"] in ("completed", "failed"):
                record["status"] = "uploading"          # until the cleanup preference has been applied
            return record
        try:
            return json.loads((JOBS_DIR / job_id / "youtube.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def apply_preference(job, after: str) -> dict:
        """After a SUCCESS only: follow the user's cleanup choice (ask / keep / delete)."""
        prefs = preferences.load()["cleanup"]
        choice = prefs["after_download" if after == "download" else "after_upload"]
        if choice == "delete" and prefs["permission"]:
            return run_cleanup(job, after)
        return {"status": "ask" if choice == "ask" else "kept"}

    def run_cleanup(job, after: str) -> dict:
        if job.cleanup:
            return job.cleanup
        if job.status not in TERMINAL:
            return {"status": "failed", "error": "The job is still running."}
        upload = yt.uploads.get(job.id)
        if upload and upload.status in ("starting", "uploading"):
            return {"status": "failed", "error": "A YouTube upload of this video is still running."}
        try:
            result = cleanup_job(JOBS_DIR, job.id, (job.result or {}).get("outputs", {}).get("video"), LESSONS_DIR)
        except Exception as err:          # cleanup failing never undoes the download/upload success
            return {"status": "failed", "error": f"{type(err).__name__}: {err}"}
        job.cleanup = {"status": "deleted", "after": after, **result}
        jobs.save_state(job)
        return job.cleanup

    @router.post("/api/generate/{job_id}/youtube")
    def start_upload(job_id: str, body: UploadRequest):
        job = finished_job(job_id)
        meta = validate_metadata(body.title, body.description, body.privacy)
        video = video_path(job)
        account = yt.refresh_account()                  # the real channel, asked from the API now
        link = check_link(preferences.load()["youtube"]["channel_url"], account)
        if link["match"] is not True and preferences.load()["youtube"]["channel_url"] and not body.confirmChannel:
            raise YouTubeError(link["message"], "channel_mismatch" if link["match"] is False else "channel_unverified",
                               f"Upload anyway to {account['title']}? Confirm to continue.")

        def done(upload):
            record = upload.public()
            if upload.status == "completed":
                upload.cleanup = apply_preference(job, "upload")
                record = upload.public()
            (JOBS_DIR / job_id / "youtube.json").write_text(json.dumps(record, indent=2), encoding="utf-8")

        upload = yt.start_upload(job_id, video, meta, on_done=done)
        return {**upload.public(), "channel": account}

    @router.get("/api/generate/{job_id}/youtube")
    def upload_status(job_id: str):
        return upload_record(job_id)                    # null: this job was never uploaded

    @router.post("/api/generate/{job_id}/downloaded")
    def downloaded(job_id: str, body: DownloadedRequest):
        job = finished_job(job_id)
        size = video_path(job).stat().st_size
        if body.bytes != size:
            raise YouTubeError(f"The download was incomplete ({body.bytes} of {size} bytes); nothing was deleted.",
                               "incomplete_download", "Download again.")
        job.downloaded = {"bytes": size, "at": time.strftime("%Y-%m-%d %H:%M:%S")}
        jobs.save_state(job)
        return {"download": "ok", "bytes": size, "cleanup": apply_preference(job, "download")}

    @router.post("/api/generate/{job_id}/cleanup")
    def cleanup(job_id: str, body: CleanupRequest):
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "Unknown job")
        if job.cleanup:
            return job.cleanup
        if body.after == "download":
            allowed = bool(job.downloaded)
        elif body.after == "upload":
            allowed = (upload_record(job_id) or {}).get("status") == "completed"
        else:
            raise YouTubeError("after must be 'download' or 'upload'.", "invalid")
        if not allowed:
            raise YouTubeError(f"Nothing is deleted without a successful {body.after} of this job's video.",
                               "not_allowed")
        return run_cleanup(job, body.after)

    @router.post("/api/reset")
    def reset(body: ResetRequest):
        """The user cleared animation.py: drop this script's analysis and this job's generated files.
        Only the given job and the given script are touched (never other jobs, lessons, voices or models)."""
        out: dict = {"analysis": False, "job": None}
        if body.animation and body.lessonName:
            try:
                out["analysis"] = forget_analysis(body.animation, slugify(body.lessonName), load_settings())
            except Exception:                       # an invalid lesson name has no cached analysis
                pass
        job = jobs.get(body.jobId) if body.jobId else None
        if job is None:
            return out
        if job.status not in TERMINAL:
            jobs.cancel(job.id)                     # its own process tree only; files deleted once it has stopped

            def later():
                for _ in range(600):
                    if job.status in TERMINAL:
                        run_cleanup(job, "reset")
                        return
                    time.sleep(0.5)

            threading.Thread(target=later, daemon=True).start()
            out["job"] = {"status": "cancelling"}
            return out
        out["job"] = run_cleanup(job, "reset")      # idempotent: a cleaned job returns its earlier result
        return out

    return router
