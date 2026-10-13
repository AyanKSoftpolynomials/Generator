"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api, ApiError, voiceApi } from "@/lib/api";
import type { AudioPreview } from "@/lib/useAudioPreview";
import { categoryTone, initials, seconds } from "@/lib/format";
import type { Voice } from "@/lib/types";
import { AddVoiceDialog } from "./AddVoiceDialog";
import { AlertIcon, CheckIcon, PlayIcon, SearchIcon, SpinnerIcon, StopIcon, TrashIcon, UploadIcon, WaveIcon } from "./icons";
import { Badge, Button, Panel } from "./ui";

type TestState = { jobId: string | null; status: "queued" | "running" | "ready" | "failed"; message: string };

export function VoiceLibrary({
  voices,
  error,
  selected,
  onSelect,
  usage,
  preview,
  onVoicesChanged,
}: {
  voices: Voice[];
  error: string | null;
  selected: string | null;
  onSelect: (id: string | null) => void;
  usage: Record<string, number>;
  preview: AudioPreview;
  onVoicesChanged: () => Promise<void>;
}) {
  const [query, setQuery] = useState("");
  const [adding, setAdding] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [cardError, setCardError] = useState<Record<string, { message: string; detail: string | null }>>({});
  const [tests, setTests] = useState<Record<string, TestState>>({});
  const [highlight, setHighlight] = useState<string | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => () => timers.current.forEach(clearTimeout), []);

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return voices;
    return voices.filter((v) =>
      [v.id, v.name, v.category, v.language, v.description, v.speaker ?? ""].some((s) => s.toLowerCase().includes(q)),
    );
  }, [voices, query]);

  const setError = (id: string, err: unknown) => {
    const e = err instanceof ApiError ? err : new ApiError(String(err), 0);
    setCardError((c) => ({ ...c, [id]: { message: e.message, detail: e.detail } }));
  };

  const remove = async (voice: Voice) => {
    setDeleting(voice.id);
    setCardError((c) => omit(c, voice.id));
    try {
      await voiceApi.remove(voice.id);
      if (selected === voice.id) onSelect(null);
      await onVoicesChanged();
    } catch (err) {
      setError(voice.id, err);
    } finally {
      setDeleting(null);
      setConfirmDelete(null);
    }
  };

  // "Test voice": XTTS speaks a short sentence (queued like a generation job).
  const test = useCallback(
    async (voice: Voice) => {
      const key = `test:${voice.id}`;
      const current = tests[voice.id];
      if (current?.status === "ready" && current.jobId) return preview.toggle(key, voiceApi.testAudioUrl(current.jobId));
      if (current && (current.status === "queued" || current.status === "running")) return;
      setCardError((c) => omit(c, voice.id));
      setTests((t) => ({ ...t, [voice.id]: { jobId: null, status: "queued", message: "Starting…" } }));
      try {
        const { jobId } = await voiceApi.test(voice.id);
        const poll = async () => {
          try {
            const snap = await api.status(jobId, 999999);
            if (snap.status === "completed") {
              setTests((t) => ({ ...t, [voice.id]: { jobId, status: "ready", message: "" } }));
              preview.toggle(key, voiceApi.testAudioUrl(jobId));
              return;
            }
            if (snap.status === "failed" || snap.status === "cancelled") {
              setTests((t) => omit(t, voice.id));
              setCardError((c) => ({ ...c, [voice.id]: { message: snap.error?.message ?? "The voice test failed.", detail: snap.error?.hint ?? null } }));
              return;
            }
            setTests((t) => ({
              ...t,
              [voice.id]: {
                jobId,
                status: snap.status === "queued" ? "queued" : "running",
                message: snap.status === "queued" ? "Waiting for the current job…" : snap.message,
              },
            }));
          } catch {
            /* transient: keep polling */
          }
          timers.current.push(setTimeout(poll, 1500));
        };
        poll();
      } catch (err) {
        setTests((t) => omit(t, voice.id));
        setError(voice.id, err);
      }
    },
    [tests, preview],
  );

  return (
    <Panel
      eyebrow="Voice library"
      title={`${voices.length} voice${voices.length === 1 ? "" : "s"}`}
      actions={
        <Button size="sm" variant="primary" onClick={() => setAdding(true)}>
          <UploadIcon size={13} /> Add voice
        </Button>
      }
      className="flex max-h-none flex-col lg:max-h-[calc(100vh-6.5rem)]"
      bodyClassName="flex min-h-0 flex-1 flex-col"
    >
      <div className="border-b border-line p-3">
        <label className="relative block">
          <SearchIcon size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search voices…"
            className="h-9 w-full rounded-lg bg-ink-900/80 pl-9 pr-3 text-sm text-slate-200 ring-1 ring-inset ring-white/10 outline-none placeholder:text-slate-600 focus:ring-sky-400/50"
          />
        </label>
        <p className="mt-2 px-0.5 text-[11px] leading-relaxed text-slate-500">
          Select a voice, then apply it to a scene or to every block. Only use voices you own or have permission to clone.
        </p>
      </div>

      <ul className="scroll-thin min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
        {error && (
          <li className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-200 ring-1 ring-inset ring-rose-400/25">{error}</li>
        )}
        {!error && shown.length === 0 && (
          <li className="p-4 text-center text-sm text-slate-500">
            {voices.length ? "No voice matches your search." : "No voices yet. Add one with “Add voice”."}
          </li>
        )}
        {shown.map((voice) => {
          const key = `voice:${voice.id}`;
          const testKey = `test:${voice.id}`;
          const t = tests[voice.id];
          const isSelected = selected === voice.id;
          const err = cardError[voice.id];
          return (
            <li
              key={voice.id}
              className={`group rounded-xl p-3 ring-1 ring-inset transition ${
                isSelected
                  ? "bg-sky-400/[0.07] ring-sky-400/40"
                  : highlight === voice.id
                    ? "bg-emerald-400/[0.06] ring-emerald-400/40"
                    : "bg-white/[0.02] ring-white/[0.07] hover:ring-white/15"
              }`}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`grid size-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br ${categoryTone(voice.category)} text-[13px] font-bold text-white/95 shadow-inner`}
                >
                  {initials(voice.name)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span className="truncate text-sm font-semibold text-slate-100">{voice.name}</span>
                    {usage[voice.id] ? <Badge tone="sky">{usage[voice.id]} in use</Badge> : null}
                    {voice.uploaded && <Badge tone="violet">uploaded</Badge>}
                  </div>
                  {voice.speaker && <div className="mt-0.5 truncate text-xs text-slate-300">{voice.speaker}</div>}
                  <div className="mt-0.5 flex flex-wrap items-center gap-x-1.5 text-xs text-slate-400">
                    <span>{voice.language}</span>
                    <span className="text-slate-600">·</span>
                    <span className="capitalize">{voice.category}</span>
                    {voice.gender && (
                      <>
                        <span className="text-slate-600">·</span>
                        <span className="capitalize">{voice.gender}</span>
                      </>
                    )}
                    <span className="text-slate-600">·</span>
                    <span className="font-mono text-[11px] text-slate-500">{voice.id}</span>
                  </div>
                  <div className="mt-1 text-[11px] text-slate-500">
                    {seconds(voice.referenceSeconds)} of reference audio · {voice.referenceAudioFiles.length} sample
                    {voice.referenceAudioFiles.length === 1 ? "" : "s"}
                    {voice.synthetic ? " · synthetic" : ""}
                  </div>
                </div>
              </div>
              {voice.problems.length > 0 && (
                <p className={`mt-2 flex gap-1.5 text-[11px] ${voice.usable ? "text-amber-300/80" : "text-rose-300"}`}>
                  <AlertIcon size={13} className="mt-px shrink-0" />
                  <span>{voice.problems[0]}</span>
                </p>
              )}

              <div className="mt-2.5 grid grid-cols-2 gap-2">
                <Button
                  size="sm"
                  onClick={() => preview.toggle(key, voice.preview)}
                  disabled={!voice.preview}
                  title={voice.preview ? "Play the reference recording" : "No preview audio for this voice"}
                >
                  {preview.loading === key ? <SpinnerIcon size={13} /> : preview.playing === key ? <StopIcon size={13} /> : <PlayIcon size={13} />}
                  {voice.preview ? (preview.playing === key ? "Stop" : "Preview") : "No preview"}
                </Button>
                <Button
                  size="sm"
                  variant={isSelected ? "primary" : "secondary"}
                  disabled={!voice.usable}
                  onClick={() => onSelect(isSelected ? null : voice.id)}
                >
                  {isSelected ? <CheckIcon size={13} /> : null}
                  {isSelected ? "Selected" : "Select"}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  disabled={!voice.usable}
                  onClick={() => test(voice)}
                  title="Hear this voice cloned by XTTS saying a test sentence"
                >
                  {t && t.status !== "ready" ? (
                    <SpinnerIcon size={13} />
                  ) : preview.playing === testKey ? (
                    <StopIcon size={13} />
                  ) : (
                    <WaveIcon size={13} />
                  )}
                  {t && t.status !== "ready" ? "Testing…" : preview.playing === testKey ? "Stop" : "Test voice"}
                </Button>
                {voice.uploaded ? (
                  confirmDelete === voice.id ? (
                    <Button size="sm" variant="danger" disabled={deleting === voice.id} onClick={() => remove(voice)}>
                      {deleting === voice.id ? <SpinnerIcon size={13} /> : <TrashIcon size={13} />}
                      {deleting === voice.id ? "Deleting…" : "Confirm delete"}
                    </Button>
                  ) : (
                    <Button size="sm" variant="ghost" onClick={() => setConfirmDelete(voice.id)}>
                      <TrashIcon size={13} /> Delete
                    </Button>
                  )
                ) : (
                  <span className="grid place-items-center text-[11px] text-slate-600" title="Built-in voices are managed with scripts/voice.py">
                    built-in
                  </span>
                )}
              </div>
              {t && t.status !== "ready" && <p className="mt-1.5 text-[11px] text-sky-300/90">{t.message}</p>}
              {(preview.failed[key] || preview.failed[testKey]) && (
                <p className="mt-1.5 text-[11px] text-rose-300">{preview.failed[key] ?? preview.failed[testKey]}</p>
              )}
              {err && (
                <div className="mt-2 rounded-lg bg-rose-500/10 p-2 text-[11px] text-rose-200 ring-1 ring-inset ring-rose-400/25">
                  <p className="font-medium">{err.message}</p>
                  {err.detail && <p className="mt-1 whitespace-pre-wrap text-rose-100/70">{err.detail}</p>}
                </div>
              )}
            </li>
          );
        })}
      </ul>

      {adding && (
        <AddVoiceDialog
          onClose={() => setAdding(false)}
          onAdded={async (voice) => {
            await onVoicesChanged();
            setHighlight(voice.id);
            setQuery("");
          }}
        />
      )}
    </Panel>
  );
}

function omit<T>(record: Record<string, T>, key: string): Record<string, T> {
  const next = { ...record };
  delete next[key];
  return next;
}
