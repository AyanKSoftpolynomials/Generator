"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, downloadWithProgress, youtubeApi } from "@/lib/api";
import type { CleanupResult, JobResult, Preferences, Privacy, UploadRecord, YouTubeStatus } from "@/lib/types";
import { connectYouTube } from "@/lib/youtubeConnect";
import { AlertIcon, CheckIcon, DownloadIcon, SpinnerIcon, UploadIcon } from "./icons";
import { Badge, Button } from "./ui";

// After a job succeeded: download the MP4 and/or upload it to YouTube. Both work
// on this job only; the job's generated files are deleted only after a success,
// and only when the user says so (or has allowed it in YouTube settings).

const mb = (bytes?: number | null) => (bytes ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : "");

export function VideoActions({
  jobId,
  result,
  youtube,
  prefs,
  onYouTube,
  onCleaned,
}: {
  jobId: string;
  result: JobResult;
  youtube: YouTubeStatus | null;
  prefs: Preferences | null;
  onYouTube: (s: YouTubeStatus) => void;
  onCleaned: (c: CleanupResult) => void;
}) {
  const cleaned = result.cleanup?.status === "deleted";
  return (
    <div className="space-y-3">
      {cleaned && (
        <p className="rounded-lg bg-white/[0.03] px-3 py-2 text-xs text-slate-400 ring-1 ring-inset ring-white/10">
          This job&apos;s generated files were deleted after a successful {result.cleanup?.after} ({mb(result.cleanup?.freedBytes)} freed).
          Generate again to make the video anew.
        </p>
      )}
      {!cleaned && <Download jobId={jobId} result={result} onCleaned={onCleaned} />}
      <YouTubeUpload jobId={jobId} result={result} youtube={youtube} prefs={prefs} onYouTube={onYouTube}
        onCleaned={onCleaned} disabled={cleaned} />
    </div>
  );
}

function Outcome({ label, ok, text }: { label: string; ok: boolean | null; text: string }) {
  return (
    <p className="flex items-center gap-2 text-xs">
      <span className="w-24 shrink-0 text-slate-500">{label}</span>
      <Badge tone={ok === null ? "slate" : ok ? "emerald" : "rose"}>{ok === null ? "—" : ok ? "SUCCESS" : "FAILED"}</Badge>
      <span className="text-slate-400">{text}</span>
    </p>
  );
}

function CleanupPrompt({ jobId, after, cleanup, onCleaned }: {
  jobId: string;
  after: "download" | "upload";
  cleanup: CleanupResult | null;
  onCleaned: (c: CleanupResult) => void;
}) {
  const [state, setState] = useState<CleanupResult | null>(cleanup);
  const [busy, setBusy] = useState(false);
  if (!state) return null;
  if (state.status === "ask") {
    return (
      <div className="flex flex-wrap items-center gap-2 rounded-lg bg-white/[0.03] p-3 text-xs text-slate-300 ring-1 ring-inset ring-white/10">
        <span className="flex-1">Video {after === "download" ? "downloaded" : "uploaded"} successfully. Delete the generated lesson files of this job?</span>
        <Button size="sm" variant="ghost" disabled={busy} onClick={() => setState({ status: "kept" })}>Keep</Button>
        <Button size="sm" variant="danger" disabled={busy}
          onClick={async () => {
            setBusy(true);
            try {
              const done = await youtubeApi.cleanup(jobId, after);
              setState(done);
              if (done.status === "deleted") onCleaned(done);
            } catch (err) {
              setState({ status: "failed", error: err instanceof Error ? err.message : String(err) });
            } finally {
              setBusy(false);
            }
          }}>
          {busy ? <SpinnerIcon size={13} /> : null} Delete
        </Button>
      </div>
    );
  }
  if (state.status === "kept") return <Outcome label="Cleanup" ok={null} text="Files kept." />;
  if (state.status === "deleted") return <Outcome label="Cleanup" ok text={`Job files deleted (${mb(state.freedBytes)}).`} />;
  return <Outcome label="Cleanup" ok={false} text={state.error ?? "Could not delete the files."} />;
}

function Download({ jobId, result, onCleaned }: { jobId: string; result: JobResult; onCleaned: (c: CleanupResult) => void }) {
  const [progress, setProgress] = useState<number | null>(null);
  const [outcome, setOutcome] = useState<{ ok: boolean; text: string; cleanup: CleanupResult | null } | null>(null);

  const start = async () => {
    setOutcome(null);
    setProgress(0);
    try {
      const bytes = await downloadWithProgress(result.downloadUrl, result.fileName, setProgress);
      const confirmed = await youtubeApi.downloaded(jobId, bytes);
      setOutcome({ ok: true, text: `${result.fileName} (${mb(bytes)})`, cleanup: confirmed.cleanup });
      if (confirmed.cleanup.status === "deleted") onCleaned(confirmed.cleanup);
    } catch (err) {
      setOutcome({ ok: false, text: `${err instanceof Error ? err.message : String(err)} Nothing was deleted.`, cleanup: null });
    } finally {
      setProgress(null);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-3">
        <Button variant="primary" onClick={start} disabled={progress !== null}>
          {progress !== null ? <SpinnerIcon size={15} /> : <DownloadIcon size={15} />}
          {progress !== null ? `Downloading… ${Math.round(progress * 100)}%` : "Download Video"}
        </Button>
        <span className="text-xs text-slate-500">{result.fileName} {mb(result.fileSize)}</span>
      </div>
      {outcome && <Outcome label="Download" ok={outcome.ok} text={outcome.text} />}
      {outcome?.ok && (
        <CleanupPrompt key={JSON.stringify(outcome.cleanup)} jobId={jobId} after="download" cleanup={outcome.cleanup} onCleaned={onCleaned} />
      )}
    </div>
  );
}

function YouTubeUpload({ jobId, result, youtube, prefs, onYouTube, onCleaned, disabled }: {
  jobId: string;
  result: JobResult;
  youtube: YouTubeStatus | null;
  prefs: Preferences | null;
  onYouTube: (s: YouTubeStatus) => void;
  onCleaned: (c: CleanupResult) => void;
  disabled: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState((result.title ?? result.lesson).slice(0, 100));
  const [description, setDescription] = useState("");
  const [privacy, setPrivacy] = useState<Privacy | null>(null);
  const [record, setRecord] = useState<UploadRecord | null>(null);
  const [error, setError] = useState<{ text: string; code: string | null } | null>(null);
  const [busy, setBusy] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const chosenPrivacy = privacy ?? prefs?.youtube.default_privacy ?? "private";

  // A previous upload of this job (e.g. after a reload).
  useEffect(() => {
    youtubeApi.uploadStatus(jobId).then(setRecord).catch(() => {});
    return () => { if (timer.current) clearInterval(timer.current); };
  }, [jobId]);

  const active = !!record && ["starting", "uploading"].includes(record.status);
  useEffect(() => {
    if (!active) return;
    timer.current = setInterval(async () => {
      try {
        const next = await youtubeApi.uploadStatus(jobId);
        setRecord(next);
        if (next?.cleanup?.status === "deleted") onCleaned(next.cleanup);
      } catch { /* keep polling */ }
    }, 1000);
    return () => { if (timer.current) clearInterval(timer.current); };
  }, [active, jobId, onCleaned]);

  const upload = async (confirmChannel = false) => {
    setBusy(true);
    setError(null);
    try {
      let status = youtube;
      if (!status?.connected) {
        const connected = await connectYouTube();
        status = await youtubeApi.status();
        onYouTube(status);
        if (!connected.connected) throw new ApiError(connected.message || "YouTube is not connected.", 0);
      }
      setRecord(await youtubeApi.upload(jobId, { title, description, privacy: chosenPrivacy, confirmChannel }));
      setOpen(false);
    } catch (err) {
      const e = err instanceof ApiError ? err : new ApiError(String(err), 0);
      setError({ text: [e.message, e.detail].filter(Boolean).join(" "), code: e.code });
    } finally {
      setBusy(false);
    }
  };

  if (!youtube?.clientConfigured && !record) {
    return <p className="text-xs text-slate-500">Upload to YouTube: set it up in the YouTube panel (optional).</p>;
  }
  const field = "w-full rounded-lg bg-ink-900/80 px-3 text-sm text-slate-100 ring-1 ring-inset ring-white/10 outline-none focus:ring-2 focus:ring-sky-400/50";

  return (
    <div className="space-y-2 rounded-xl p-3 ring-1 ring-inset ring-white/10">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs font-semibold text-slate-200">YouTube</span>
        {!record || record.status === "failed" ? (
          <Button size="sm" onClick={() => setOpen((v) => !v)} disabled={disabled}>
            <UploadIcon size={13} /> Upload to YouTube
          </Button>
        ) : null}
      </div>

      {open && (!record || record.status === "failed") && (
        <div className="space-y-2">
          <input className={`${field} h-9`} value={title} maxLength={100} onChange={(e) => setTitle(e.target.value)} aria-label="YouTube title" />
          <textarea className={`${field} h-20 py-2`} value={description} placeholder="Description (optional)"
            onChange={(e) => setDescription(e.target.value)} aria-label="YouTube description" />
          <div className="flex flex-wrap items-center gap-2">
            <select className={`${field} h-9 w-auto`} value={chosenPrivacy} onChange={(e) => setPrivacy(e.target.value as Privacy)} aria-label="Privacy">
              <option value="private">Private</option>
              <option value="unlisted">Unlisted</option>
              <option value="public">Public</option>
            </select>
            <Button variant="primary" size="sm" onClick={() => upload(false)} disabled={busy || !title.trim()}>
              {busy ? <SpinnerIcon size={13} /> : <UploadIcon size={13} />}
              {youtube?.connected ? `Upload to ${youtube.channel?.title ?? "YouTube"}` : "Connect and upload"}
            </Button>
          </div>
          <p className="text-[11px] leading-snug text-slate-600">
            Uploads from Google API projects that have not passed Google&apos;s audit are kept private by YouTube, whatever
            privacy you choose here.
          </p>
        </div>
      )}

      {error && (
        <div className="space-y-1.5 text-xs text-rose-200">
          <p className="flex gap-1.5"><AlertIcon size={13} className="mt-px shrink-0" /> {error.text}</p>
          {(error.code === "channel_mismatch" || error.code === "channel_unverified") && (
            <Button size="sm" variant="danger" onClick={() => upload(true)} disabled={busy}>
              Upload to {youtube?.channel?.title ?? "the connected channel"} anyway
            </Button>
          )}
        </div>
      )}

      {record && active && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-slate-300">
            <span>Uploading to YouTube…</span>
            <span className="font-mono">{record.progress}%</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
            <div className="h-full rounded-full bg-rose-400 transition-all" style={{ width: `${record.progress}%` }} />
          </div>
          <p className="text-[11px] text-slate-500">{mb(record.bytesSent)} of {mb(record.totalBytes)} · the video stays on this PC</p>
        </div>
      )}

      {record?.status === "completed" && (
        <div className="space-y-1.5">
          <Outcome label="YouTube upload" ok text="Upload complete" />
          <p className="flex flex-wrap items-center gap-2 text-xs text-slate-300">
            <CheckIcon size={13} className="text-emerald-300" />
            <span className="font-mono">{record.videoId}</span>
            <a className="text-sky-300 underline-offset-2 hover:underline" href={record.url ?? "#"} target="_blank" rel="noreferrer">{record.url}</a>
          </p>
          {record.privacyApplied && record.privacyApplied !== record.privacy && (
            <p className="text-[11px] text-amber-200/90">
              You chose {record.privacy}; YouTube set it to {record.privacyApplied} (unverified API project).
            </p>
          )}
          <CleanupPrompt key={JSON.stringify(record.cleanup)} jobId={jobId} after="upload" cleanup={record.cleanup} onCleaned={onCleaned} />
        </div>
      )}
      {record?.status === "failed" && !open && (
        <Outcome label="YouTube upload" ok={false} text={[record.error, record.hint].filter(Boolean).join(" ")} />
      )}
    </div>
  );
}
