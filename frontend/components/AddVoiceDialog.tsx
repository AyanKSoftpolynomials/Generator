"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ApiError, uploadVoice } from "@/lib/api";
import type { Voice } from "@/lib/types";
import { AlertIcon, CheckIcon, SpinnerIcon, UploadIcon, XIcon } from "./icons";
import { Button } from "./ui";

const FORMATS = [".wav", ".mp3", ".m4a", ".ogg", ".oga", ".flac", ".webm", ".aac", ".opus"];
const MAX_MB = 25;
const MIN_SECONDS = 2;
const RECOMMENDED_SECONDS = 6;
const MAX_SECONDS = 300;

// XTTS v2 languages (must match backend/voices.py LANGUAGE_NAMES).
const LANGUAGES: [string, string][] = [
  ["en", "English"], ["hi", "Hindi"], ["es", "Spanish"], ["fr", "French"], ["de", "German"], ["it", "Italian"],
  ["pt", "Portuguese"], ["pl", "Polish"], ["tr", "Turkish"], ["ru", "Russian"], ["nl", "Dutch"], ["cs", "Czech"],
  ["ar", "Arabic"], ["zh-cn", "Chinese"], ["ja", "Japanese"], ["hu", "Hungarian"], ["ko", "Korean"],
];

type Phase = "form" | "uploading" | "processing" | "done";

export function AddVoiceDialog({ onClose, onAdded }: { onClose: () => void; onAdded: (voice: Voice) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [duration, setDuration] = useState<number | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [form, setForm] = useState({ name: "", speaker: "", language: "en", gender: "", category: "teacher", description: "" });
  const [consent, setConsent] = useState(false);
  const [phase, setPhase] = useState<Phase>("form");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<{ message: string; detail: string | null } | null>(null);
  const [added, setAdded] = useState<Voice | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const busy = phase === "uploading" || phase === "processing";

  useEffect(() => () => void (fileUrl && URL.revokeObjectURL(fileUrl)), [fileUrl]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && !busy && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [busy, onClose]);

  const choose = (f: File | undefined) => {
    setError(null);
    setDuration(null);
    if (!f) return;
    const ext = f.name.includes(".") ? f.name.slice(f.name.lastIndexOf(".")).toLowerCase() : "";
    if (!FORMATS.includes(ext)) {
      setFile(null);
      return setFileError(`"${f.name}" is not a supported audio file. Use ${FORMATS.join(", ")}.`);
    }
    if (f.size > MAX_MB * 1024 * 1024) {
      setFile(null);
      return setFileError(`The file is ${(f.size / 1024 / 1024).toFixed(1)} MB; the maximum is ${MAX_MB} MB.`);
    }
    if (f.size === 0) {
      setFile(null);
      return setFileError("The file is empty.");
    }
    setFileError(null);
    setFile(f);
    setFileUrl(URL.createObjectURL(f));
    if (!form.name) setForm((s) => ({ ...s, name: f.name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").slice(0, 60) }));
  };

  // Browser-side duration check (the server checks again after converting).
  const durationProblem =
    duration == null
      ? null
      : duration < MIN_SECONDS
        ? `This recording is only ${duration.toFixed(1)} s long; at least ${MIN_SECONDS} s is required (${RECOMMENDED_SECONDS}-30 s recommended).`
        : duration > MAX_SECONDS
          ? `This recording is ${(duration / 60).toFixed(1)} minutes long; the maximum is ${MAX_SECONDS / 60} minutes.`
          : null;
  const shortWarning = duration != null && !durationProblem && duration < RECOMMENDED_SECONDS;

  const missing = [
    !file && "an audio file",
    !form.name.trim() && "a voice name",
    !form.speaker.trim() && "the speaker's name",
    !consent && "the permission confirmation",
  ].filter(Boolean) as string[];
  const canSubmit = missing.length === 0 && !durationProblem && !fileError && !busy;

  const submit = async () => {
    if (!file || !canSubmit) return;
    setPhase("uploading");
    setProgress(0);
    setError(null);
    try {
      const voice = await uploadVoice({ file, ...form, consent }, (f) => {
        setProgress(f);
        if (f >= 1) setPhase("processing");
      });
      setAdded(voice);
      setPhase("done");
      onAdded(voice);
    } catch (err) {
      const e = err instanceof ApiError ? err : new ApiError(String(err), 0);
      setError({ message: e.message, detail: e.detail });
      setPhase("form");
    }
  };

  const field =
    "h-10 w-full rounded-lg bg-ink-900/80 px-3 text-sm text-slate-100 ring-1 ring-inset ring-white/10 outline-none placeholder:text-slate-600 focus:ring-2 focus:ring-sky-400/50 disabled:opacity-60";

  // Portal: .panel ancestors use backdrop-filter, which would trap position:fixed.
  return createPortal(
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/60 p-4 backdrop-blur-sm sm:items-center" role="dialog" aria-modal="true" aria-labelledby="add-voice-title">
      <div className="panel my-8 w-full max-w-lg !bg-ink-850">
        <header className="flex items-center justify-between border-b border-line px-5 py-3.5">
          <div>
            <div className="eyebrow">Voice library</div>
            <h2 id="add-voice-title" className="mt-0.5 text-[15px] font-semibold text-slate-100">
              {phase === "done" ? "Voice added" : "Add a voice"}
            </h2>
          </div>
          <Button size="sm" variant="ghost" onClick={onClose} disabled={busy} aria-label="Close">
            <XIcon size={15} />
          </Button>
        </header>

        {phase === "done" && added ? (
          <div className="space-y-4 p-5">
            <p className="flex items-center gap-2 text-sm text-emerald-200">
              <CheckIcon size={16} /> <b className="font-semibold">{added.name}</b> is in the library as{" "}
              <code className="font-mono text-xs text-emerald-100">{added.id}</code>.
            </p>
            <p className="text-sm text-slate-400">
              It is available in every narration dropdown now. Use <b className="text-slate-200">Test voice</b> on its card to hear
              how XTTS clones it before you generate.
            </p>
            {added.problems.length > 0 && <p className="text-xs text-amber-300/90">⚠ {added.problems[0]}</p>}
            <div className="flex justify-end">
              <Button variant="primary" onClick={onClose}>
                Done
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4 p-5">
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                if (!busy) choose(e.dataTransfer.files?.[0]);
              }}
              className={`rounded-xl border border-dashed p-4 text-center transition ${
                dragging ? "border-sky-400/70 bg-sky-400/[0.06]" : "border-white/15 bg-white/[0.02]"
              }`}
            >
              <input
                ref={input}
                type="file"
                accept={[...FORMATS, "audio/*"].join(",")}
                className="hidden"
                onChange={(e) => {
                  choose(e.target.files?.[0]);
                  e.target.value = "";
                }}
              />
              {file && fileUrl ? (
                <div className="space-y-2 text-left">
                  <div className="flex items-center justify-between gap-2">
                    <span className="min-w-0 truncate text-sm font-medium text-slate-200">{file.name}</span>
                    <span className="shrink-0 font-mono text-xs text-slate-500">
                      {(file.size / 1024 / 1024).toFixed(1)} MB{duration != null ? ` · ${duration.toFixed(1)} s` : ""}
                    </span>
                  </div>
                  {/* Listen before uploading; also measures the duration. */}
                  <audio
                    src={fileUrl}
                    controls
                    className="h-9 w-full"
                    onLoadedMetadata={(e) => {
                      const d = e.currentTarget.duration;
                      if (Number.isFinite(d)) setDuration(d);
                    }}
                  />
                  <button type="button" onClick={() => input.current?.click()} disabled={busy} className="text-xs text-sky-300 hover:underline disabled:opacity-50">
                    Choose a different file
                  </button>
                </div>
              ) : (
                <div className="py-3">
                  <UploadIcon size={22} className="mx-auto text-slate-500" />
                  <p className="mt-2 text-sm text-slate-300">Drop a recording here, or</p>
                  <Button size="sm" className="mt-2" onClick={() => input.current?.click()}>
                    Choose audio file
                  </Button>
                  <p className="mt-2 text-[11px] text-slate-500">
                    WAV, MP3, M4A, OGG, FLAC or WebM · up to {MAX_MB} MB · 6-30 s of clear speech works best
                  </p>
                </div>
              )}
            </div>
            {(fileError || durationProblem) && <p className="text-xs text-rose-300">{fileError ?? durationProblem}</p>}
            {shortWarning && (
              <p className="text-xs text-amber-300/90">
                Short recording: it will work, but {RECOMMENDED_SECONDS}-30 s of speech gives a more faithful voice.
              </p>
            )}

            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-slate-400">Voice name *</span>
                <input className={field} value={form.name} maxLength={60} disabled={busy} placeholder="e.g. Maths Teacher Priya"
                  onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </label>
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-slate-400">Speaker / team member *</span>
                <input className={field} value={form.speaker} maxLength={80} disabled={busy} placeholder="Whose voice is this?"
                  onChange={(e) => setForm({ ...form, speaker: e.target.value })} />
              </label>
              <label className="block">
                <span className="mb-1 block text-xs font-medium text-slate-400">Language *</span>
                <select className={field} value={form.language} disabled={busy} onChange={(e) => setForm({ ...form, language: e.target.value })}>
                  {LANGUAGES.map(([code, label]) => (
                    <option key={code} value={code}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="mb-1 block text-xs font-medium text-slate-400">Gender</span>
                  <select className={field} value={form.gender} disabled={busy} onChange={(e) => setForm({ ...form, gender: e.target.value })}>
                    <option value="">—</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="other">Other</option>
                  </select>
                </label>
                <label className="block">
                  <span className="mb-1 block text-xs font-medium text-slate-400">Role</span>
                  <select className={field} value={form.category} disabled={busy} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                    <option value="teacher">Teacher</option>
                    <option value="student">Student</option>
                    <option value="narrator">Narrator</option>
                    <option value="other">Other</option>
                  </select>
                </label>
              </div>
              <label className="block sm:col-span-2">
                <span className="mb-1 block text-xs font-medium text-slate-400">Description</span>
                <input className={field} value={form.description} maxLength={300} disabled={busy} placeholder="Optional, e.g. warm, calm, for primary classes"
                  onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </label>
            </div>

            <label className="flex items-start gap-2.5 rounded-lg bg-white/[0.02] p-3 text-xs text-slate-300 ring-1 ring-inset ring-white/10">
              <input type="checkbox" className="mt-0.5 accent-sky-400" checked={consent} disabled={busy} onChange={(e) => setConsent(e.target.checked)} />
              <span>
                I own this recording or have the speaker&apos;s permission to clone and synthesize their voice. <span className="text-slate-500">(required)</span>
              </span>
            </label>

            {error && (
              <div className="rounded-lg bg-rose-500/10 p-3 ring-1 ring-inset ring-rose-400/25">
                <p className="flex gap-2 text-sm text-rose-100">
                  <AlertIcon size={15} className="mt-0.5 shrink-0 text-rose-300" /> {error.message}
                </p>
                {error.detail && <p className="mt-1 ml-6 text-xs whitespace-pre-wrap text-rose-100/70">{error.detail}</p>}
              </div>
            )}

            {busy && (
              <div>
                <div className="mb-1 flex justify-between text-xs text-slate-400">
                  <span>{phase === "uploading" ? "Uploading…" : "Checking and converting the recording…"}</span>
                  {phase === "uploading" && <span className="font-mono">{Math.round(progress * 100)}%</span>}
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r from-sky-400 to-violet-500 transition-[width] ${phase === "processing" ? "progress-stripes animate-shimmer" : ""}`}
                    style={{ width: `${phase === "processing" ? 100 : Math.max(2, progress * 100)}%` }}
                  />
                </div>
              </div>
            )}

            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-[11px] text-slate-500">{missing.length > 0 && !busy ? `Still needed: ${missing.join(", ")}` : ""}</p>
              <div className="flex gap-2">
                <Button variant="ghost" onClick={onClose} disabled={busy}>
                  Cancel
                </Button>
                <Button variant="primary" onClick={submit} disabled={!canSubmit}>
                  {busy ? <SpinnerIcon size={15} /> : <UploadIcon size={15} />}
                  {busy ? "Saving…" : "Save voice"}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
}
