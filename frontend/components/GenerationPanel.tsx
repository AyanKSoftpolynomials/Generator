"use client";

import { useEffect, useRef, useState } from "react";
import { clock, seconds, STAGES } from "@/lib/format";
import type { JobSnapshot, LogLine, Quality, Segment, StageState } from "@/lib/types";
import { AlertIcon, CheckIcon, DotIcon, FilmIcon, RefreshIcon, SpinnerIcon, TerminalIcon, XIcon } from "./icons";
import { Badge, Button, Panel } from "./ui";

export function GenerationPanel({
  quality,
  onQuality,
  onGenerate,
  onCancel,
  onRetry,
  blockers,
  submitting,
  submitError,
  job,
  logs,
  connectionError,
}: {
  quality: Quality;
  onQuality: (q: Quality) => void;
  onGenerate: () => void;
  onCancel: () => void;
  onRetry: () => void;
  blockers: string[];
  submitting: boolean;
  submitError: string | null;
  job: JobSnapshot | null;
  logs: LogLine[];
  connectionError: string | null;
}) {
  const active = job && ["queued", "running", "cancelling"].includes(job.status);
  const canGenerate = blockers.length === 0 && !active && !submitting;

  return (
    <Panel eyebrow="Generation" title="Render the lesson video" bodyClassName="p-5 space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <span className="mb-1.5 block text-xs font-medium text-slate-400">Quality</span>
          <div className="inline-flex rounded-xl bg-ink-900/80 p-1 ring-1 ring-inset ring-white/10" role="radiogroup">
            {(
              [
                ["preview", "Preview", "480p · fast"],
                ["final", "Final", "1080p · Full HD"],
              ] as const
            ).map(([value, label, hint]) => (
              <button
                key={value}
                type="button"
                role="radio"
                aria-checked={quality === value}
                disabled={!!active}
                onClick={() => onQuality(value)}
                className={`rounded-lg px-3.5 py-1.5 text-left transition disabled:cursor-not-allowed ${
                  quality === value ? "bg-white/[0.08] text-slate-100 ring-1 ring-inset ring-white/15" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <span className="block text-sm font-medium">{label}</span>
                <span className="block text-[11px] text-slate-500">{hint}</span>
              </button>
            ))}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {active && (
            <Button variant="danger" onClick={onCancel} disabled={job?.status === "cancelling"}>
              {job?.status === "cancelling" ? "Cancelling…" : "Cancel"}
            </Button>
          )}
          <Button variant="primary" size="lg" onClick={onGenerate} disabled={!canGenerate} className="min-w-52">
            {submitting || active ? <SpinnerIcon size={18} /> : <FilmIcon size={18} />}
            {job?.status === "queued" ? "Queued…" : active ? "Generating…" : "Generate Video"}
          </Button>
        </div>
      </div>

      {blockers.length > 0 && !active && (
        <ul className="space-y-1 text-xs text-slate-500">
          {blockers.map((b) => (
            <li key={b} className="flex items-center gap-2">
              <DotIcon size={10} className="text-slate-600" /> {b}
            </li>
          ))}
        </ul>
      )}
      {submitError && (
        <p className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm whitespace-pre-wrap text-rose-200 ring-1 ring-inset ring-rose-400/25">
          {submitError}
        </p>
      )}

      {job && <Progress job={job} connectionError={connectionError} />}
      {job?.status === "failed" && <FailureCard job={job} logs={logs} onRetry={onRetry} />}
      {job && <Logs logs={logs} running={!!active} />}
    </Panel>
  );
}

// Incremental render: progress from the backend's real per-scene states, not a time estimate.
function segmentProgress(job: JobSnapshot): { label: string; message: string | null; percent: number } | null {
  const s = job.segmentSummary;
  if (!s || !s.total_segments) return null;
  const total = s.total_segments;
  const ready = s.cached_segments + s.completed_segments;
  const toRender = s.changed_segments + s.regenerating_segments + s.completed_segments + s.failed_segments;
  if (job.status === "completed") return { label: `${ready}/${total} segments ready`, message: "Video ready", percent: 100 };
  if (job.status !== "running") return null;
  if (job.stage === "Subtitles" || job.stage === "FFmpeg")
    return { label: `${ready}/${total} segments ready`, message: "Segments complete — assembling final video…", percent: 100 };
  let label = `${s.cached_segments}/${total} reused`;
  if (s.regenerating_segments) label += ` • regenerating ${s.completed_segments + 1}/${toRender}`;
  else if (s.completed_segments) label += ` • ${s.completed_segments}/${toRender} regenerated`;
  else if (s.changed_segments) label += ` • ${s.changed_segments} changed`;
  return { label, message: null, percent: Math.round((ready / total) * 100) };
}

function Progress({ job, connectionError }: { job: JobSnapshot; connectionError: string | null }) {
  const running = job.status === "running" || job.status === "cancelling";
  const segments = segmentProgress(job);
  const barTone =
    job.status === "failed" ? "from-rose-500 to-rose-400" : job.status === "cancelled" ? "from-slate-500 to-slate-400" : "from-sky-400 via-blue-500 to-violet-500";
  return (
    <div className="space-y-4">
      <ol className="grid gap-1.5">
        {STAGES.map((s) => (
          <StageRow key={s.key} stage={s.key} label={s.label} detail={s.detail} info={job.stages[s.key]} current={job.stage === s.key && running} />
        ))}
        <li className="flex items-center gap-3 rounded-lg px-3 py-2">
          <StageIcon state={job.status === "completed" ? "done" : "pending"} />
          <span className={`text-sm font-medium ${job.status === "completed" ? "text-emerald-200" : "text-slate-500"}`}>Completed</span>
        </li>
      </ol>

      <div>
        <div className="mb-1.5 flex items-baseline justify-between gap-3 text-xs">
          <span className="min-w-0 truncate text-slate-300" aria-live="polite">
            {job.status === "queued"
              ? `Queued${job.queuePosition ? ` (position ${job.queuePosition})` : ""}: waiting for a free generation slot. Not running yet.`
              : (segments?.message ?? job.message)}
          </span>
          <span className="shrink-0 font-mono text-slate-400">
            <span className="text-slate-600" title="This tab follows only this job">job {job.jobId}{job.pid ? ` · pid ${job.pid}` : ""} · </span>
            {segments ? segments.label : `${job.progress}%`} · <Elapsed job={job} />
          </span>
        </div>
        <div className="h-2.5 overflow-hidden rounded-full bg-white/[0.06] ring-1 ring-inset ring-white/5">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${barTone} transition-[width] duration-500 ease-out ${running ? "progress-stripes animate-shimmer" : ""}`}
            style={{ width: `${Math.max(segments ? segments.percent : job.progress, running ? 2 : 0)}%` }}
          />
        </div>
        {connectionError && <p className="mt-1.5 text-[11px] text-amber-300">{connectionError}. Retrying…</p>}
      </div>
      {job.segments && job.segments.length > 0 && job.segmentSummary && <Segments job={job} />}
    </div>
  );
}

const SEGMENT_LOOK: Record<Segment["status"], { text: string; className: string }> = {
  cached: { text: "✓ Reused", className: "text-emerald-300" },
  changed: { text: "Changed · waiting", className: "text-amber-300" },
  queued: { text: "Queued", className: "text-slate-400" },
  regenerating: { text: "↻ Regenerating", className: "text-sky-300" },
  completed: { text: "✓ Regenerated", className: "text-sky-200" },
  failed: { text: "✕ Failed", className: "text-rose-300" },
};

function Segments({ job }: { job: JobSnapshot }) {
  const s = job.segmentSummary!;
  const segments = [...(job.segments ?? [])].sort((a, b) => a.segment_order - b.segment_order);
  const current = segments.filter((x) => x.status === "regenerating").map((x) => x.segment_name);
  const counts: [number, string][] = [
    [s.total_segments, "segments"],
    [s.cached_segments, "reused"],
    [s.changed_segments, "changed"],
    [s.regenerating_segments, "regenerating"],
    [s.completed_segments, "regenerated"],
    [s.failed_segments, "failed"],
  ];
  return (
    <div className="rounded-xl bg-ink-900/60 p-3 ring-1 ring-inset ring-white/10">
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <span className="text-xs font-semibold tracking-wide text-slate-300">Incremental generation</span>
        <span className="text-[11px] text-slate-400">
          {counts.filter(([n], i) => i < 2 || n > 0).map(([n, label]) => `${n} ${label}`).join(" · ")}
        </span>
      </div>
      {current.length > 0 && (
        <p className="mb-2 text-xs text-sky-200">
          Current: <span className="font-medium">{current.join(", ")}</span>
        </p>
      )}
      <ol className="grid max-h-56 gap-0.5 overflow-auto">
        {segments.map((x) => (
          <li key={x.segment_id} className="flex items-center justify-between gap-3 rounded-md px-2 py-1 text-xs">
            <span className="min-w-0 truncate text-slate-300">
              <span className="mr-2 font-mono text-slate-600">{String(x.segment_order).padStart(2, "0")}</span>
              {x.segment_name}
            </span>
            <span className={`shrink-0 font-medium ${SEGMENT_LOOK[x.status].className}`}>
              {x.status === "regenerating" && <SpinnerIcon size={11} className="mr-1 inline" />}
              {SEGMENT_LOOK[x.status].text}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}

function StageRow({ stage, label, detail, info, current }: { stage: string; label: string; detail: string; info: StageState; current: boolean }) {
  const state = info?.state ?? "pending";
  return (
    <li
      className={`flex flex-wrap items-center gap-x-3 gap-y-1 rounded-lg px-3 py-2 transition ${
        current ? "bg-sky-400/[0.06] ring-1 ring-inset ring-sky-400/20" : ""
      }`}
    >
      <StageIcon state={state} />
      <span className={`w-24 text-sm font-medium ${state === "pending" ? "text-slate-500" : state === "failed" ? "text-rose-200" : "text-slate-100"}`}>
        {label}
      </span>
      <span className="hidden text-xs text-slate-500 sm:inline">{detail}</span>
      <span className="ml-auto flex items-center gap-2">
        {state === "running" && info.total ? (
          <span className="font-mono text-xs text-sky-200">
            {info.done ?? 0} / {info.total}
          </span>
        ) : null}
        <CacheBadge info={info} stage={stage} />
        {info?.seconds != null && state === "done" && <span className="w-12 text-right font-mono text-xs text-slate-500">{seconds(info.seconds)}</span>}
      </span>
    </li>
  );
}

// Incremental builds: only changed scenes / clips are regenerated; the rest is reused from the cache.
const UNITS: Record<string, [string, string]> = { Manim: ["scenes", "re-rendered"], TTS: ["clips", "new"], WhisperX: ["clips", "aligned"] };

function CacheBadge({ info, stage }: { info?: StageState; stage: string }) {
  const c = info?.cache;
  if (!c) return null;
  if (c.skipped) return <Badge>skipped · {c.skipped}</Badge>;
  const generated = c.generated ?? 0;
  const cached = c.cached ?? 0;
  if (c.estimated) return <Badge tone="amber">estimated timing</Badge>;
  if (generated === 0 && cached > 0) return <Badge tone="emerald">Cached{cached > 1 ? ` · ${cached}` : ""}</Badge>;
  if (cached === 0) return <Badge tone="sky">Generated{generated > 1 ? ` · ${generated}` : ""}</Badge>;
  const unit = UNITS[stage];
  return (
    <Badge tone="sky">
      {unit ? `${generated + cached} ${unit[0]} · ${generated} ${unit[1]} · ${cached} reused` : `${cached} cached / ${generated} generated`}
    </Badge>
  );
}

function StageIcon({ state }: { state: StageState["state"] }) {
  const base = "grid size-6 shrink-0 place-items-center rounded-full";
  if (state === "done") return <span className={`${base} bg-emerald-400/15 text-emerald-300`}><CheckIcon size={14} /></span>;
  if (state === "running") return <span className={`${base} bg-sky-400/15 text-sky-300`}><SpinnerIcon size={14} /></span>;
  if (state === "failed") return <span className={`${base} bg-rose-400/15 text-rose-300`}><XIcon size={13} /></span>;
  if (state === "skipped") return <span className={`${base} bg-white/[0.04] text-slate-500`}>–</span>;
  return <span className={`${base} ring-1 ring-inset ring-white/15`} />;
}

function FailureCard({ job, logs, onRetry }: { job: JobSnapshot; logs: LogLine[]; onRetry: () => void }) {
  const [details, setDetails] = useState(false);
  const err = job.error;
  const stageLabel = STAGES.find((s) => s.key === err?.stage)?.label ?? err?.stage ?? "Unknown";
  return (
    <div className="rounded-xl bg-rose-500/[0.07] p-4 ring-1 ring-inset ring-rose-400/25">
      <div className="flex items-start gap-3">
        <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-rose-500/15 text-rose-300">
          <AlertIcon size={18} />
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold text-rose-100">Generation failed</h3>
          <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
            <dt className="text-rose-200/60">Stage</dt>
            <dd className="text-rose-100">{stageLabel}</dd>
            <dt className="text-rose-200/60">Error</dt>
            <dd className="break-words whitespace-pre-wrap text-rose-100">{err?.message ?? "Unknown error"}</dd>
          </dl>
          {err?.hint && (
            <p className="mt-2 text-xs whitespace-pre-wrap text-rose-100/70">{err.hint.split("Manim output (last lines):")[0].trim()}</p>
          )}
          <div className="mt-3 flex flex-wrap gap-2">
            <Button size="sm" variant="danger" onClick={onRetry}>
              <RefreshIcon size={13} /> Retry
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setDetails((d) => !d)}>
              <TerminalIcon size={13} /> {details ? "Hide details" : "View details"}
            </Button>
          </div>
          {details && (
            <pre className="scroll-thin mt-3 max-h-80 overflow-auto rounded-lg bg-black/40 p-3 font-mono text-[11px] leading-relaxed whitespace-pre-wrap text-rose-100/80">
              {err?.traceback ?? logs.slice(-60).map((l) => l.message).join("\n")}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

function Logs({ logs, running }: { logs: LogLine[]; running: boolean }) {
  const [open, setOpen] = useState(false);
  const [full, setFull] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  const shown = full ? logs : logs.filter((l) => l.milestone);

  useEffect(() => {
    const el = box.current;
    if (el && open && running) el.scrollTop = el.scrollHeight;
  }, [shown.length, open, running]);

  return (
    <div className="rounded-xl ring-1 ring-inset ring-white/[0.07]">
      <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-2">
        <button type="button" onClick={() => setOpen((o) => !o)} className="flex items-center gap-2 text-sm text-slate-300 hover:text-slate-100">
          <TerminalIcon size={15} className="text-slate-500" />
          Generation logs
          <span className="font-mono text-[11px] text-slate-500">{logs.length}</span>
        </button>
        {open && (
          <label className="flex items-center gap-2 text-xs text-slate-400">
            <input type="checkbox" checked={full} onChange={(e) => setFull(e.target.checked)} className="accent-sky-400" />
            Full generator output
          </label>
        )}
      </div>
      {open && (
        <div ref={box} className="scroll-thin max-h-80 overflow-auto border-t border-line bg-black/30 px-3 py-2 font-mono text-[12px] leading-relaxed">
          {shown.length === 0 && <p className="text-slate-600">No log lines yet.</p>}
          {shown.map((l, i) => (
            <div key={i} className="flex gap-3 whitespace-pre-wrap">
              <span className="shrink-0 text-slate-600">[{clock(l.t)}]</span>
              <span
                className={
                  l.message.startsWith("ERROR")
                    ? "text-rose-300"
                    : l.message.includes("[CACHE HIT]")
                      ? "text-emerald-300/80"
                      : l.message.includes("[CACHE MISS]")
                        ? "text-sky-300/90"
                        : l.milestone
                          ? "text-slate-200"
                          : "text-slate-400"
                }
              >
                {l.message}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Ticks locally between server updates (server clock for start/finish).
function Elapsed({ job }: { job: JobSnapshot }) {
  const [now, setNow] = useState(() => Date.now() / 1000);
  const running = !job.finished && !!job.started;
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => setNow(Date.now() / 1000), 1000);
    return () => clearInterval(timer);
  }, [running]);
  if (!job.started) return <>{seconds(0)}</>;
  const value = job.finished ? job.finished - job.started : Math.max(job.elapsed, now - job.started);
  return <>{seconds(value)}</>;
}
