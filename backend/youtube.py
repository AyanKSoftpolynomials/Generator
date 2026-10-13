"""Optional YouTube upload through the official YouTube Data API v3 (OAuth 2.0 + videos.insert).

    local/youtube_client.bin    your Google Cloud OAuth client (client_secret.json), encrypted
    local/youtube_token.bin     the authorization Google gave this app, encrypted (DPAPI)
    local/youtube_account.json  the authorized channel (id, title, handle): public info, no secrets

The saved channel link (preferences.youtube.channel_url) is only a reference.
It is never used to authenticate; after authorization the API tells us which
channel the account really is (channels.list mine=true), and an upload is refused
with a clear warning when the saved link points somewhere else.

Scopes: youtube.upload (videos.insert) and youtube.readonly (to read the
authorized channel's identity). Nothing here scrapes YouTube, automates a
browser or stores a password.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from backend import secure_store
from backend.preferences import LOCAL_DIR, PRIVACY

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
CATEGORY_EDUCATION = "27"
STATE_TTL = 600                 # seconds an authorization link stays valid
CHUNK = 8 * 1024 * 1024         # resumable upload chunk size
RETRYABLE = {500, 502, 503, 504}


class YouTubeError(Exception):
    """A readable problem for the UI (never contains tokens or secrets)."""

    def __init__(self, message: str, code: str = "error", hint: str | None = None):
        super().__init__(message)
        self.message, self.code, self.hint = message, code, hint


# ------------------------------------------------------------------ channel links

def parse_channel_url(url: str) -> dict:
    """What a YouTube channel link points at: a channel id, a @handle, or a legacy /c/ or /user/ name."""
    raw = (url or "").strip()
    if not raw:
        raise YouTubeError("Enter a YouTube channel link.", "invalid_link")
    parsed = urlparse(raw if "://" in raw else "https://" + raw)
    host = (parsed.hostname or "").lower()
    if host not in ("youtube.com", "www.youtube.com", "m.youtube.com", "studio.youtube.com"):
        raise YouTubeError("That is not a YouTube link.", "invalid_link",
                           "Use your channel's address, e.g. https://www.youtube.com/@yourchannel")
    parts = [p for p in parsed.path.split("/") if p]
    if parts and parts[0].startswith("@") and len(parts[0]) > 1:
        return {"kind": "handle", "value": parts[0].lower()}
    if len(parts) >= 2 and parts[0] == "channel" and re.fullmatch(r"UC[\w-]{22}", parts[1]):
        return {"kind": "id", "value": parts[1]}
    if len(parts) >= 2 and parts[0] in ("c", "user"):
        return {"kind": parts[0], "value": parts[1].lower()}
    raise YouTubeError("This YouTube link is not a channel link.", "invalid_link",
                       "Open your channel and copy its address (…/@handle or …/channel/UC…).")


def check_link(saved_url: str | None, channel: dict | None) -> dict:
    """Does the saved link point at the authorized channel? match True/False, or None when unknown."""
    if not saved_url:
        return {"match": None, "message": "No channel link saved: videos go to the connected account's channel."}
    if not channel:
        return {"match": None, "message": "Connect YouTube to check the saved link."}
    target = parse_channel_url(saved_url)
    if target["kind"] == "id":
        match = target["value"] == channel["id"]
    elif target["kind"] == "handle":
        match = target["value"] == (channel.get("customUrl") or "").lower()
    else:
        return {"match": None, "message": "Legacy /c/ or /user/ links cannot be verified. Save the channel's "
                                          "@handle or /channel/ link to let uploads be checked."}
    if match:
        return {"match": True, "message": f"The saved link is the connected channel ({channel['title']})."}
    return {"match": False, "message": f"The saved link is not the connected channel ({channel['title']}"
                                       f"{', ' + channel['customUrl'] if channel.get('customUrl') else ''}). "
                                       "Reconnect with the right Google account, or change the saved link."}


def validate_metadata(title: str, description: str, privacy: str) -> dict:
    title = " ".join((title or "").split())
    description = (description or "").strip()
    if not title:
        raise YouTubeError("The video needs a title.", "invalid_metadata")
    if len(title) > 100:
        raise YouTubeError("YouTube titles can have at most 100 characters.", "invalid_metadata")
    if len(description.encode("utf-8")) > 5000:
        raise YouTubeError("YouTube descriptions can have at most 5000 bytes.", "invalid_metadata")
    if any(ch in title + description for ch in "<>"):
        raise YouTubeError("YouTube does not allow < or > in titles and descriptions.", "invalid_metadata")
    if privacy not in PRIVACY:
        raise YouTubeError(f"Privacy must be one of: {', '.join(PRIVACY)}.", "invalid_metadata")
    return {"title": title, "description": description, "privacy": privacy}


# ------------------------------------------------------------------ uploads

@dataclass
class Upload:
    job_id: str
    title: str
    privacy: str
    status: str = "starting"                # starting / uploading / completed / failed
    progress: int = 0
    bytes_sent: int = 0
    total_bytes: int = 0
    video_id: str | None = None
    url: str | None = None
    privacy_applied: str | None = None      # what YouTube actually set (unverified projects: private)
    error: str | None = None
    code: str | None = None
    hint: str | None = None
    started: float = field(default_factory=time.time)
    finished: float | None = None
    cleanup: dict | None = None
    settled: bool = False                   # on_done (cleanup preference, youtube.json) has run

    def public(self) -> dict:
        return {"jobId": self.job_id, "title": self.title, "privacy": self.privacy, "status": self.status,
                "progress": self.progress, "bytesSent": self.bytes_sent, "totalBytes": self.total_bytes,
                "videoId": self.video_id, "url": self.url, "privacyApplied": self.privacy_applied,
                "error": self.error, "code": self.code, "hint": self.hint, "started": self.started,
                "finished": self.finished, "cleanup": self.cleanup}


class YouTubeService:
    def __init__(self, folder: Path = LOCAL_DIR, flow_factory=None, service_factory=None, revoke=None):
        self.folder = Path(folder)
        self.client_file = self.folder / "youtube_client.bin"
        self.token_file = self.folder / "youtube_token.bin"
        self.account_file = self.folder / "youtube_account.json"
        self._flow_factory = flow_factory or self._google_flow
        self._service_factory = service_factory or self._google_service
        self._revoke = revoke or self._google_revoke
        self._pending: dict[str, tuple[float, object]] = {}      # OAuth state -> (created, flow)
        self.uploads: dict[str, Upload] = {}                       # job id -> its (latest) upload
        self.lock = threading.Lock()

    # -- OAuth client ----------------------------------------------------------

    def save_client(self, raw: bytes) -> dict:
        try:
            config = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, ValueError) as err:
            raise YouTubeError("That file is not a Google OAuth client JSON.", "invalid_client") from err
        kind = next((k for k in ("web", "installed") if isinstance(config.get(k), dict)), None)
        section = config.get(kind) if kind else None
        if not section or not section.get("client_id") or not section.get("client_secret"):
            raise YouTubeError("That file is not a Google OAuth client JSON (client_secret_….json).", "invalid_client",
                               "Download it from Google Cloud Console > APIs & Services > Credentials.")
        secure_store.write_secret(self.client_file, json.dumps(config).encode("utf-8"))
        return {"type": kind, "clientId": section["client_id"]}

    def client_config(self) -> dict | None:
        raw = secure_store.read_secret(self.client_file)
        return json.loads(raw) if raw else None

    # -- connection ----------------------------------------------------------------

    def start_authorization(self, redirect_uri: str) -> str:
        config = self.client_config()
        if not config:
            raise YouTubeError("The Google OAuth client is not set up yet.", "no_client",
                               "Add your client_secret.json in YouTube settings (see README > YouTube).")
        flow = self._flow_factory(config, redirect_uri)
        state = secrets.token_urlsafe(24)
        url, _ = flow.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="true",
                                        state=state)
        with self.lock:
            now = time.time()
            self._pending = {s: v for s, v in self._pending.items() if now - v[0] < STATE_TTL}
            self._pending[state] = (now, flow)
        return url

    def finish_authorization(self, state: str | None, code: str | None, error: str | None) -> dict:
        with self.lock:
            entry = self._pending.pop(state or "", None)
        if error:
            raise YouTubeError("YouTube authorization was cancelled." if error == "access_denied"
                               else f"Google refused the authorization ({error}).", "oauth_" + error)
        if entry is None or time.time() - entry[0] > STATE_TTL:
            raise YouTubeError("This authorization link is invalid or has expired.", "oauth_state",
                               "Start again with Connect YouTube.")
        if not code:
            raise YouTubeError("Google did not return an authorization code.", "oauth_code")
        flow = entry[1]
        try:
            flow.fetch_token(code=code)
        except Exception as err:  # the library raises several types; never echo tokens
            raise YouTubeError(f"Could not complete the authorization ({type(err).__name__}).", "oauth_token") from err
        credentials = flow.credentials
        granted = set(getattr(credentials, "granted_scopes", None) or getattr(credentials, "scopes", None) or SCOPES)
        if not set(SCOPES) <= granted:
            raise YouTubeError("YouTube upload permission was not granted.", "insufficient_scope",
                               "Connect again and allow uploading videos and viewing your YouTube account.")
        secure_store.write_secret(self.token_file, credentials.to_json().encode("utf-8"))
        return self.refresh_account()

    def credentials(self):
        raw = secure_store.read_secret(self.token_file)
        if not raw:
            raise YouTubeError("YouTube is not connected.", "not_connected", "Click Connect YouTube.")
        from google.auth.exceptions import RefreshError
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = Credentials.from_authorized_user_info(json.loads(raw), SCOPES)
        if not creds.valid:
            if not creds.refresh_token:
                raise YouTubeError("The YouTube authorization has expired.", "expired", "Reconnect YouTube.")
            try:
                creds.refresh(Request())
            except RefreshError as err:
                self._forget()
                raise YouTubeError("The YouTube authorization is no longer valid (revoked or expired).", "expired",
                                   "Reconnect YouTube.") from err
            except Exception as err:
                raise YouTubeError("Could not reach Google to renew the authorization.", "network",
                                   "Check the internet connection and try again.") from err
            secure_store.write_secret(self.token_file, creds.to_json().encode("utf-8"))
        return creds

    def refresh_account(self) -> dict:
        """Ask the API which channel the authorized account is (never guessed from the saved link)."""
        service = self._service_factory(self.credentials())
        try:
            reply = service.channels().list(part="snippet", mine=True).execute()
        except Exception as err:
            raise _api_error(err) from err
        items = reply.get("items") or []
        if not items:
            raise YouTubeError("This Google account has no YouTube channel.", "no_channel",
                               "Create a channel on YouTube first, or connect another account.")
        snippet = items[0].get("snippet", {})
        account = {"id": items[0]["id"], "title": snippet.get("title", ""), "customUrl": snippet.get("customUrl"),
                   "checked": time.strftime("%Y-%m-%d %H:%M:%S")}
        self.account_file.parent.mkdir(parents=True, exist_ok=True)
        self.account_file.write_text(json.dumps(account, indent=2), encoding="utf-8")
        return account

    def account(self) -> dict | None:
        try:
            return json.loads(self.account_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def connected(self) -> bool:
        return self.token_file.exists()

    def disconnect(self) -> dict:
        """Revoke this app's access at Google (best effort) and forget it locally. Videos are not touched."""
        raw = secure_store.read_secret(self.token_file)
        revoked = False
        if raw:
            token = json.loads(raw)
            try:
                revoked = bool(self._revoke(token.get("refresh_token") or token.get("token")))
            except Exception:
                revoked = False
        self._forget()
        return {"revoked": revoked}

    def _forget(self) -> None:
        secure_store.delete_secret(self.token_file)
        self.account_file.unlink(missing_ok=True)

    # -- uploads ---------------------------------------------------------------------

    def start_upload(self, job_id: str, video: Path, meta: dict, on_done=None) -> Upload:
        with self.lock:
            current = self.uploads.get(job_id)
            if current and current.status in ("starting", "uploading"):
                raise YouTubeError("This video is already being uploaded.", "busy")
            upload = Upload(job_id=job_id, title=meta["title"], privacy=meta["privacy"],
                            total_bytes=video.stat().st_size)
            self.uploads[job_id] = upload
        threading.Thread(target=self._upload, args=(upload, video, meta, on_done), daemon=True).start()
        return upload

    def _upload(self, upload: Upload, video: Path, meta: dict, on_done) -> None:
        media = None
        try:
            service = self._service_factory(self.credentials())
            from googleapiclient.http import MediaFileUpload

            body = {"snippet": {"title": meta["title"], "description": meta["description"],
                                "categoryId": CATEGORY_EDUCATION},
                    "status": {"privacyStatus": meta["privacy"]}}
            media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=CHUNK, resumable=True)
            request = service.videos().insert(part="snippet,status", body=body, media_body=media)
            upload.status = "uploading"
            response, retries = None, 0
            while response is None:
                try:
                    status, response = request.next_chunk()
                    retries = 0
                    if status:
                        upload.bytes_sent = int(status.resumable_progress)
                        upload.progress = min(99, int(status.progress() * 100))
                except Exception as err:
                    code = getattr(getattr(err, "resp", None), "status", None)
                    transient = code in RETRYABLE or isinstance(err, (ConnectionError, TimeoutError, OSError))
                    if transient and retries < 5:
                        retries += 1
                        time.sleep(min(30, 2 ** retries))
                        continue
                    raise
            upload.video_id = response["id"]
            upload.url = f"https://www.youtube.com/watch?v={upload.video_id}"
            upload.privacy_applied = (response.get("status") or {}).get("privacyStatus") or meta["privacy"]
            upload.progress, upload.bytes_sent, upload.status = 100, upload.total_bytes, "completed"
        except YouTubeError as err:
            upload.status, upload.error, upload.code, upload.hint = "failed", err.message, err.code, err.hint
        except Exception as err:
            api = _api_error(err)
            upload.status, upload.error, upload.code, upload.hint = "failed", api.message, api.code, api.hint
        finally:
            if media is not None:
                try:
                    media.stream().close()        # MediaFileUpload keeps the MP4 open; Windows would block cleanup
                except Exception:
                    pass
            upload.finished = time.time()
            try:
                if on_done:
                    on_done(upload)
            finally:
                upload.settled = True

    # -- Google plumbing (replaced by fakes in tests) ---------------------------------

    @staticmethod
    def _google_flow(config: dict, redirect_uri: str):
        from google_auth_oauthlib.flow import Flow

        if urlparse(redirect_uri).hostname in ("127.0.0.1", "localhost"):
            os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")   # Google allows http for loopback only
        os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")
        return Flow.from_client_config(config, scopes=SCOPES, redirect_uri=redirect_uri,
                                       autogenerate_code_verifier=True)   # PKCE

    @staticmethod
    def _google_service(credentials):
        from googleapiclient.discovery import build

        return build("youtube", "v3", credentials=credentials, cache_discovery=False)

    @staticmethod
    def _google_revoke(token: str | None) -> bool:
        if not token:
            return False
        import requests

        reply = requests.post("https://oauth2.googleapis.com/revoke", params={"token": token},
                              headers={"content-type": "application/x-www-form-urlencoded"}, timeout=15)
        return reply.status_code == 200


def _api_error(err: Exception) -> YouTubeError:
    """A readable YouTubeError from a googleapiclient HttpError (or a network error)."""
    if isinstance(err, YouTubeError):
        return err
    status = getattr(getattr(err, "resp", None), "status", None)
    reason, message = "", str(err)
    content = getattr(err, "content", None)
    if content:
        try:
            info = json.loads(content.decode("utf-8") if isinstance(content, bytes) else content)["error"]
            message = info.get("message", message)
            reason = ((info.get("errors") or [{}])[0]).get("reason", "")
        except (ValueError, KeyError, TypeError, AttributeError):
            pass
    if reason in ("quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded", "userRateLimitExceeded"):
        return YouTubeError("The YouTube API quota is used up for now.", "quota",
                            "Try again later (the daily quota resets at midnight Pacific time).")
    if reason == "uploadLimitExceeded":
        return YouTubeError("This channel has reached YouTube's upload limit for now.", "upload_limit",
                            "Try again later.")
    if status == 401:
        return YouTubeError("YouTube rejected the authorization.", "expired", "Reconnect YouTube.")
    if status == 403:
        return YouTubeError(f"YouTube refused the request: {message}", "forbidden",
                            "Check that the account may upload and that the YouTube Data API is enabled.")
    if status == 400:
        return YouTubeError(f"YouTube rejected the video details: {message}", "invalid_metadata")
    if status:
        return YouTubeError(f"YouTube error {status}: {message}", "api")
    return YouTubeError(f"Could not reach YouTube ({type(err).__name__}).", "network",
                        "Check the internet connection and try again.")
