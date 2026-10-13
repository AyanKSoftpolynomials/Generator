"""Optional YouTube upload, download confirmation and job cleanup (fakes: no Google account needed)."""

import json
import time
from pathlib import Path

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from backend import cleanup as cleanup_module
from backend import preferences, youtube_api
from backend.jobs import Job
from backend.preferences import PreferenceError
from backend.youtube import YouTubeError, YouTubeService, check_link, parse_channel_url

CHANNEL = {"id": "UC" + "a" * 22, "snippet": {"title": "Maths With Prasad", "customUrl": "@mathswithprasad"}}


# ------------------------------------------------------------------ fakes

class FakeCreds:
    scopes = youtube_api.__dict__.get("SCOPES") or ["https://www.googleapis.com/auth/youtube.upload",
                                                     "https://www.googleapis.com/auth/youtube.readonly"]

    def to_json(self):
        return json.dumps({"token": "access", "refresh_token": "refresh", "client_id": "cid", "client_secret": "sec",
                           "expiry": "2099-01-01T00:00:00Z"})   # valid: tests never call Google


class FakeFlow:
    def __init__(self):
        self.credentials = FakeCreds()
        self.codes = []

    def authorization_url(self, **kw):
        return f"https://accounts.google.com/o/oauth2/auth?state={kw['state']}", kw["state"]

    def fetch_token(self, code):
        self.codes.append(code)


class Call:
    def __init__(self, fn):
        self.fn = fn

    def execute(self):
        return self.fn()


class FakeInsert:
    def __init__(self, service):
        self.service = service
        self.calls = 0

    def next_chunk(self):
        self.calls += 1
        if self.service.fail:
            raise YouTubeError("YouTube refused the request: quota", "quota")
        if self.calls < 3:
            time.sleep(0.05)
            status = type("S", (), {"resumable_progress": self.calls * 10, "progress": lambda s: self.calls / 3})()
            self.service.progress_seen.append(int(status.progress() * 100))
            return status, None
        return None, {"id": "vid12345678", "status": {"privacyStatus": "private"}}


class FakeService:
    def __init__(self):
        self.fail = False
        self.inserted = []
        self.progress_seen = []

    def channels(self):
        return type("C", (), {"list": lambda _, **kw: Call(lambda: {"items": [CHANNEL]})})()

    def videos(self):
        service = self

        class Videos:
            def insert(self, part, body, media_body):
                service.inserted.append(body)
                return FakeInsert(service)

        return Videos()


class FakeJobs:
    def __init__(self):
        self.jobs = {}
        self.saved = []

    def get(self, job_id):
        return self.jobs.get(job_id)

    def save_state(self, job):
        self.saved.append(job.id)


@pytest.fixture
def env(tmp_path, monkeypatch):
    jobs_dir, lessons_dir = tmp_path / "jobs", tmp_path / "lessons"
    monkeypatch.setattr(preferences, "PREFS_FILE", tmp_path / "local" / "preferences.json")
    monkeypatch.setattr(youtube_api, "JOBS_DIR", jobs_dir)
    monkeypatch.setattr(youtube_api, "LESSONS_DIR", lessons_dir)
    flow, service = FakeFlow(), FakeService()
    yt = YouTubeService(tmp_path / "local", flow_factory=lambda config, uri: flow,
                        service_factory=lambda creds: service, revoke=lambda token: True)
    jobs = FakeJobs()
    app = FastAPI()

    @app.exception_handler(YouTubeError)
    async def _yt(_: Request, err: YouTubeError):
        return JSONResponse(status_code=409 if err.code in ("channel_mismatch", "channel_unverified") else 422,
                            content={"error": err.message, "detail": err.hint, "code": err.code})

    @app.exception_handler(PreferenceError)
    async def _pref(_: Request, err: PreferenceError):
        return JSONResponse(status_code=400, content={"error": str(err)})

    app.include_router(youtube_api.make_router(jobs, yt))
    return {"client": TestClient(app), "yt": yt, "flow": flow, "service": service, "jobs": jobs,
            "jobs_dir": jobs_dir, "lessons_dir": lessons_dir}


def make_job(env, job_id="abcdef123456", lesson="demo"):
    folder = env["jobs_dir"] / job_id
    (folder / "output").mkdir(parents=True)
    (folder / "audio").mkdir()
    video = folder / "output" / "demo_preview.mp4"
    video.write_bytes(b"MP4" * 1000)
    (folder / "audio" / "intro_01.wav").write_bytes(b"RIFF" * 100)
    (folder / "job.json").write_text(json.dumps({"lessonId": lesson}), encoding="utf-8")
    (folder / "state.json").write_text("{}", encoding="utf-8")
    published = env["lessons_dir"] / lesson / "output" / "demo_preview.mp4"
    published.parent.mkdir(parents=True)
    published.write_bytes(video.read_bytes())
    (env["lessons_dir"] / lesson / "animation.py").write_text("# user's lesson", encoding="utf-8")
    job = Job(id=job_id, lesson_id=lesson, lesson_name="Demo", request={}, status="completed",
              result={"title": "Demo", "outputs": {"video": str(video)}})
    env["jobs"].jobs[job_id] = job
    return job, video, published


def connect(env):
    client = env["client"]
    client.post("/api/youtube/client", files={"file": ("client_secret.json", json.dumps(
        {"web": {"client_id": "cid", "client_secret": "sec", "auth_uri": "https://a", "token_uri": "https://t"}}),
        "application/json")})
    url = client.post("/api/youtube/connect").json()["authUrl"]
    state = url.split("state=")[1]
    page = client.get("/api/youtube/oauth/callback", params={"state": state, "code": "the-code"})
    assert page.status_code == 200 and "Connected" in page.text
    return state


def wait_upload(env, job_id):
    for _ in range(100):
        record = env["client"].get(f"/api/generate/{job_id}/youtube").json()
        if record["status"] in ("completed", "failed"):
            return record
        time.sleep(0.05)
    raise AssertionError("upload did not finish")


# ------------------------------------------------------------------ 1-3 channel link

def test_save_change_and_remove_channel_link(env):
    client = env["client"]
    first = client.put("/api/youtube/link", json={"url": "https://www.youtube.com/@mathswithprasad"}).json()
    assert first["channelUrl"] == "https://www.youtube.com/@mathswithprasad"
    changed = client.put("/api/youtube/link", json={"url": f"https://www.youtube.com/channel/{CHANNEL['id']}"}).json()
    assert changed["channelUrl"].endswith(CHANNEL["id"])
    assert preferences.load()["youtube"]["channel_url"].endswith(CHANNEL["id"])
    assert client.delete("/api/youtube/link").json()["channelUrl"] is None
    bad = client.put("/api/youtube/link", json={"url": "https://example.com/@x"})
    assert bad.status_code == 422 and bad.json()["code"] == "invalid_link"


def test_link_is_checked_against_the_authorized_channel():
    channel = {"id": CHANNEL["id"], "title": "Maths With Prasad", "customUrl": "@mathswithprasad"}
    assert check_link("https://www.youtube.com/@MathsWithPrasad", channel)["match"] is True
    assert check_link(f"youtube.com/channel/{CHANNEL['id']}", channel)["match"] is True
    assert check_link("https://www.youtube.com/@someoneelse", channel)["match"] is False
    assert check_link("https://www.youtube.com/c/legacy", channel)["match"] is None
    assert parse_channel_url("https://studio.youtube.com/channel/" + CHANNEL["id"])["kind"] == "id"


# ------------------------------------------------------------------ 4 OAuth state

def test_oauth_state_handling(env):
    client = env["client"]
    no_client = client.post("/api/youtube/connect")
    assert no_client.status_code == 422 and no_client.json()["code"] == "no_client"
    state = connect(env)
    status = client.get("/api/youtube").json()
    assert status["connected"] and status["channel"]["title"] == "Maths With Prasad"
    assert "refresh" not in json.dumps(status) and "access" not in json.dumps(status)      # no tokens to the browser
    assert b"refresh" not in (env["yt"].token_file).read_bytes()                           # encrypted at rest
    replay = client.get("/api/youtube/oauth/callback", params={"state": state, "code": "again"})
    assert "invalid or has expired" in replay.text                                         # a state is used once
    forged = client.get("/api/youtube/oauth/callback", params={"state": "forged", "code": "x"})
    assert "invalid or has expired" in forged.text
    url = client.post("/api/youtube/connect").json()["authUrl"]
    cancelled = client.get("/api/youtube/oauth/callback",
                           params={"state": url.split("state=")[1], "error": "access_denied"})
    assert "cancelled" in cancelled.text
    assert client.post("/api/youtube/disconnect").json()["revoked"] is True
    assert client.get("/api/youtube").json()["connected"] is False


# ------------------------------------------------------------------ 5-7 upload

def test_upload_success_with_progress(env):
    job, video, _ = make_job(env)
    preferences.update({"cleanup": {"after_download": "ask", "after_upload": "ask"}})
    connect(env)
    started = env["client"].post(f"/api/generate/{job.id}/youtube",
                                 json={"title": "Demo", "description": "A lesson", "privacy": "unlisted"})
    assert started.status_code == 200 and started.json()["channel"]["title"] == "Maths With Prasad"
    record = wait_upload(env, job.id)
    assert record["status"] == "completed" and record["videoId"] == "vid12345678"
    assert record["url"] == "https://www.youtube.com/watch?v=vid12345678" and record["progress"] == 100
    assert record["privacy"] == "unlisted" and record["privacyApplied"] == "private"      # reported, not hidden
    assert env["service"].progress_seen[:2] == [33, 66]
    body = env["service"].inserted[0]
    assert body["status"]["privacyStatus"] == "unlisted" and body["snippet"]["title"] == "Demo"
    assert json.loads((env["jobs_dir"] / job.id / "youtube.json").read_text())["videoId"] == "vid12345678"
    assert video.exists()                                                                   # cleanup is "ask"


def test_upload_failure_keeps_everything(env):
    job, video, published = make_job(env)
    connect(env)
    preferences.update({"cleanup": {"after_upload": "delete", "confirm_delete": True}})
    env["service"].fail = True
    env["client"].post(f"/api/generate/{job.id}/youtube", json={"title": "Demo", "privacy": "private"})
    record = wait_upload(env, job.id)
    assert record["status"] == "failed" and record["code"] == "quota" and record["cleanup"] is None
    assert video.exists() and published.exists() and job.cleanup is None                    # 13. no cleanup
    refused = env["client"].post(f"/api/generate/{job.id}/cleanup", json={"after": "upload"})
    assert refused.status_code == 422 and refused.json()["code"] == "not_allowed"


def test_upload_needs_connection_and_a_matching_channel(env):
    job, _, _ = make_job(env)
    not_connected = env["client"].post(f"/api/generate/{job.id}/youtube", json={"title": "Demo"})
    assert not_connected.status_code == 422 and not_connected.json()["code"] == "not_connected"
    connect(env)
    env["client"].put("/api/youtube/link", json={"url": "https://www.youtube.com/@someoneelse"})
    mismatch = env["client"].post(f"/api/generate/{job.id}/youtube", json={"title": "Demo"})
    assert mismatch.status_code == 409 and mismatch.json()["code"] == "channel_mismatch"
    assert env["service"].inserted == []                                                    # nothing uploaded blindly
    ok = env["client"].post(f"/api/generate/{job.id}/youtube", json={"title": "Demo", "confirmChannel": True})
    assert ok.status_code == 200
    wait_upload(env, job.id)                   # finish here: the upload thread must not outlive the test
    bad = env["client"].post(f"/api/generate/{job.id}/youtube", json={"title": "<b>", "privacy": "secret"})
    assert bad.status_code == 422


# ------------------------------------------------------------------ 8-9 download

def test_download_confirmation(env):
    job, video, _ = make_job(env)
    preferences.update({"cleanup": {"after_download": "ask", "after_upload": "ask"}})
    short = env["client"].post(f"/api/generate/{job.id}/downloaded", json={"bytes": 10})
    assert short.status_code == 422 and short.json()["code"] == "incomplete_download"       # 9. failure
    assert job.downloaded is None and video.exists()
    ok = env["client"].post(f"/api/generate/{job.id}/downloaded", json={"bytes": video.stat().st_size}).json()
    assert ok["download"] == "ok" and ok["cleanup"] == {"status": "ask"}                    # 8. success, asks
    assert job.downloaded["bytes"] == video.stat().st_size and video.exists()


# ------------------------------------------------------------------ 10-15 cleanup

def test_cleanup_disabled_keeps_files(env):
    job, video, _ = make_job(env)
    preferences.update({"cleanup": {"after_download": "keep"}})
    reply = env["client"].post(f"/api/generate/{job.id}/downloaded", json={"bytes": video.stat().st_size}).json()
    assert reply["cleanup"] == {"status": "kept"} and video.exists()


def test_automatic_deletion_needs_explicit_permission(env):
    preferences.update({"cleanup": {"after_download": "ask", "after_upload": "ask"}})
    with pytest.raises(PreferenceError, match="permission"):
        preferences.update({"cleanup": {"after_download": "delete"}})
    prefs = preferences.update({"cleanup": {"after_download": "delete", "confirm_delete": True}})
    assert prefs["cleanup"]["permission"]
    assert preferences.update({"cleanup": {"after_download": "ask"}})["cleanup"]["permission"] is None


def test_cleanup_after_successful_download(env):
    job, video, published = make_job(env)
    preferences.update({"cleanup": {"after_download": "delete", "confirm_delete": True}})
    reply = env["client"].post(f"/api/generate/{job.id}/downloaded", json={"bytes": video.stat().st_size}).json()
    assert reply["cleanup"]["status"] == "deleted" and reply["cleanup"]["after"] == "download"
    folder = env["jobs_dir"] / job.id
    assert sorted(p.name for p in folder.iterdir()) == ["job.json", "state.json"]
    assert not published.exists()                                                           # its own published copy
    assert (env["lessons_dir"] / "demo" / "animation.py").exists()                          # the lesson is kept


def test_cleanup_after_successful_upload(env):
    job, video, _ = make_job(env)
    connect(env)
    preferences.update({"cleanup": {"after_upload": "delete", "confirm_delete": True}})
    env["client"].post(f"/api/generate/{job.id}/youtube", json={"title": "Demo"})
    record = wait_upload(env, job.id)
    assert record["status"] == "completed" and record["cleanup"]["status"] == "deleted", record["cleanup"]
    assert not video.exists() and (env["jobs_dir"] / job.id / "youtube.json").exists()     # record kept
    gone = env["client"].post(f"/api/generate/{job.id}/downloaded", json={"bytes": 1})
    assert gone.json()["code"] == "cleaned"


def test_manual_cleanup_after_ask(env):
    job, video, _ = make_job(env)
    preferences.update({"cleanup": {"after_download": "ask", "after_upload": "ask"}})
    env["client"].post(f"/api/generate/{job.id}/downloaded", json={"bytes": video.stat().st_size})
    done = env["client"].post(f"/api/generate/{job.id}/cleanup", json={"after": "download"}).json()
    assert done["status"] == "deleted" and not video.exists()


def test_no_cleanup_without_a_successful_download(env):
    job, video, _ = make_job(env)
    refused = env["client"].post(f"/api/generate/{job.id}/cleanup", json={"after": "download"})
    assert refused.status_code == 422 and video.exists()


def test_cleanup_is_limited_to_the_job_workspace(env):
    job, video, _ = make_job(env)
    other, other_video, _ = make_job(env, job_id="0123456789ab", lesson="other")
    # The lesson's published copy was replaced by a later job: it is not this job's file.
    (env["lessons_dir"] / "demo" / "output" / "demo_preview.mp4").write_bytes(b"newer build")
    result = cleanup_module.cleanup_job(env["jobs_dir"], job.id, str(video), env["lessons_dir"])
    assert not video.exists() and other_video.exists()
    assert (env["lessons_dir"] / "demo" / "output" / "demo_preview.mp4").read_bytes() == b"newer build"
    assert result["freedBytes"] > 0
    for bad in ("../lessons", "..", "abc", "ABCDEF123456", str(env["jobs_dir"])):
        with pytest.raises(ValueError):
            cleanup_module.job_workspace(env["jobs_dir"], bad)


# ------------------------------------------------------------------ 16 unaffected generation

def test_generation_and_video_work_without_youtube(tmp_path):
    """The real app: no YouTube setup needed; the video endpoint is unchanged until a cleanup."""
    from backend import app as app_module

    client = TestClient(app_module.app)
    assert client.get("/api/youtube").json()["connected"] in (False, True)
    job = Job(id="fedcba654321", lesson_id="x", lesson_name="X", request={}, status="completed",
              result={"outputs": {"video": "cache/jobs/fedcba654321/output/x.mp4"}})
    video = app_module.JOBS_DIR / job.id / "output" / "x.mp4"
    video.parent.mkdir(parents=True, exist_ok=True)
    video.write_bytes(b"0" * 100)
    try:
        app_module.jobs.jobs[job.id] = job
        assert client.get(f"/api/generate/{job.id}/video").status_code == 200
        assert client.get(f"/api/generate/{job.id}/result").json()["fileSize"] == 100
        job.cleanup = {"status": "deleted", "after": "download"}
        assert client.get(f"/api/generate/{job.id}/video").status_code == 410
    finally:
        app_module.jobs.jobs.pop(job.id, None)
        import shutil

        shutil.rmtree(app_module.JOBS_DIR / job.id, ignore_errors=True)


# ------------------------------------------------------------------ hotfix: clear/reset + default delivery cleanup

SCRIPT_V1 = "from src.animation import LMSScene\n\nclass A(LMSScene):\n    def construct(self):\n        self.narrate('a', 'One.')\n"


def test_clear_resets_analysis_and_only_the_current_job(env, monkeypatch):
    from backend import analysis

    monkeypatch.setattr(analysis, "ANALYZE_DIR", env["jobs_dir"].parent / "analyze")
    cached = analysis.ANALYZE_DIR / analysis.analysis_digest(SCRIPT_V1, "demo", {}) / "demo"
    cached.mkdir(parents=True)
    (cached / "extracted.json").write_text("{}", encoding="utf-8")
    shared_tex = analysis.ANALYZE_DIR / "_tex"
    shared_tex.mkdir()
    job, video, published = make_job(env)
    other, other_video, _ = make_job(env, job_id="0123456789ab", lesson="other")
    monkeypatch.setattr(youtube_api, "load_settings", lambda: {})
    reply = env["client"].post("/api/reset", json={"jobId": job.id, "animation": SCRIPT_V1, "lessonName": "Demo"}).json()
    assert reply["analysis"] is True and not cached.parent.exists() and shared_tex.exists()
    assert reply["job"]["status"] == "deleted" and reply["job"]["after"] == "reset"
    assert sorted(p.name for p in (env["jobs_dir"] / job.id).iterdir()) == ["job.json", "state.json"]
    assert not video.exists() and not published.exists()
    assert (env["lessons_dir"] / "demo" / "animation.py").exists()                            # lesson source kept
    assert other_video.exists() and other.cleanup is None                                     # other job untouched
    again = env["client"].post("/api/reset", json={"jobId": job.id}).json()                    # idempotent
    assert again["job"]["status"] == "deleted"
    gone = env["client"].get(f"/api/generate/{job.id}/youtube")
    assert gone.status_code == 200


def test_changed_script_gets_a_fresh_analysis():
    from backend import analysis

    v2 = SCRIPT_V1.replace("One.", "Two.")
    assert analysis.analysis_digest(SCRIPT_V1, "demo", {}) == analysis.analysis_digest(SCRIPT_V1, "demo", {})
    assert analysis.analysis_digest(SCRIPT_V1, "demo", {}) != analysis.analysis_digest(v2, "demo", {})


def test_default_deletes_after_successful_download_and_upload(env):
    job, video, _ = make_job(env)                                   # no preference set: the default applies
    reply = env["client"].post(f"/api/generate/{job.id}/downloaded", json={"bytes": video.stat().st_size}).json()
    assert reply["cleanup"]["status"] == "deleted" and not video.exists()
    job2, video2, _ = make_job(env, job_id="fedcba654321", lesson="demo2")
    connect(env)
    env["client"].post(f"/api/generate/{job2.id}/youtube", json={"title": "Demo"})
    record = wait_upload(env, job2.id)
    assert record["status"] == "completed" and record["cleanup"]["status"] == "deleted" and not video2.exists()
