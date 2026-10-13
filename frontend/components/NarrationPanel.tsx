"use client";

import { useEffect, useMemo, useState } from "react";
import { clipUrl } from "@/lib/api";
import { seconds, VOICE_SOURCE_TEXT } from "@/lib/format";
import type { AudioPreview } from "@/lib/useAudioPreview";
import type { Analysis, Narration, Voice } from "@/lib/types";
import { AlertIcon, ChevronIcon, LayersIcon, PlayIcon, SpinnerIcon, StopIcon, WaveIcon } from "./icons";
import { Badge, Button, Panel } from "./ui";

export function NarrationPanel({
  analysis,
  analyzeError,
  analyzing,
  voices,
  assignments,
  onAssign,
  selectedVoice,
  preview,
}: {
  analysis: Analysis | null;
  analyzeError: { message: string; detail: string | null } | null;
  analyzing: boolean;
  voices: Voice[];
  assignments: Record<string, string>;
  onAssign: (ids: string[], voice: string) => void;
  selectedVoice: string | null;
  preview: AudioPreview;
}) {
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const voiceById = useMemo(() => Object.fromEntries(voices.map((v) => [v.id, v])), [voices]);

  const groups = useMemo(() => {
    if (!analysis) return [];
    const order = analysis.scenes.map((s) => s.id);
    const byScene = new Map<string, Narration[]>();
    for (const n of analysis.narrations) {
      const key = n.scene ?? "__none__";
      if (!byScene.has(key)) byScene.set(key, []);
      byScene.get(key)!.push(n);
    }
    const keys = [...order.filter((k) => byScene.has(k)), ...[...byScene.keys()].filter((k) => !order.includes(k))];
    return keys.map((key) => ({
      key,
      scene: analysis.scenes.find((s) => s.id === key) ?? null,
      items: byScene.get(key)!,
    }));
  }, [analysis]);

  const total = analysis?.narrations.length ?? 0;
  const overridden = analysis ? analysis.narrations.filter((n) => assignments[n.id] && assignments[n.id] !== n.voice).length : 0;
  const unresolved = analysis ? analysis.narrations.filter((n) => !voiceById[assignments[n.id]]?.usable).length : 0;
  const allOpen = total > 0 && analysis!.narrations.every((n) => open[n.id]);
  const selectedName = selectedVoice ? voiceById[selectedVoice]?.name ?? selectedVoice : null;

  return (
    <Panel
      eyebrow="Narration blocks"
      title={
        analysis ? (
          <span className="flex flex-wrap items-center gap-2">
            {analysis.lesson.title ?? analysis.lesson.id}
            <span className="font-mono text-xs font-normal text-slate-500">{analysis.lesson.className}</span>
          </span>
        ) : (
          "Not analyzed yet"
        )
      }
      actions={
        analysis && (
          <>
            {selectedName && (
              <Button size="sm" variant="secondary" onClick={() => onAssign(analysis.narrations.map((n) => n.id), selectedVoice!)}>
                Apply {selectedName} to all
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setOpen(allOpen ? {} : Object.fromEntries(analysis.narrations.map((n) => [n.id, true])))}
            >
              {allOpen ? "Collapse all" : "Expand all"}
            </Button>
          </>
        )
      }
      bodyClassName=""
    >
      {analyzeError && (
        <div className="m-5 rounded-xl bg-rose-500/10 p-4 ring-1 ring-inset ring-rose-400/25">
          <p className="flex items-start gap-2 text-sm font-medium text-rose-100">
            <AlertIcon size={16} className="mt-0.5 shrink-0 text-rose-300" />
            <span className="whitespace-pre-wrap break-words">{analyzeError.message}</span>
          </p>
          {analyzeError.detail && <ErrorDetail detail={analyzeError.detail} />}
        </div>
      )}

      {!analysis && !analyzeError && (
        <div className="flex flex-col items-center gap-2 px-6 py-14 text-center">
          {analyzing ? <SpinnerIcon size={22} className="text-sky-300" /> : <WaveIcon size={22} className="text-slate-600" />}
          <p className="text-sm text-slate-400">
            {analyzing ? "Reading narrate() calls from animation.py…" : "Click Analyze Animation to detect narration blocks."}
          </p>
          {analyzing ? (
            <AnalyzeTimer />
          ) : (
            <p className="max-w-md text-xs text-slate-600">
              IDs, text, scenes and voices come straight from your code. Nothing is typed by hand.
            </p>
          )}
        </div>
      )}

      {analysis && (
        <>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-b border-line px-5 py-2.5 text-xs text-slate-400">
            <span>
              <b className="font-semibold text-slate-200">{total}</b> blocks
            </span>
            <span>
              <b className="font-semibold text-slate-200">{analysis.scenes.length}</b> scenes
            </span>
            <span>
              <b className="font-semibold text-slate-200">{new Set(Object.values(assignments)).size}</b> voices
            </span>
            {overridden > 0 && <Badge tone="violet">{overridden} overridden</Badge>}
            {unresolved > 0 && <Badge tone="amber">{unresolved} need a voice</Badge>}
            <span className="ml-auto text-slate-600">analyzed in {seconds(analysis.seconds)}</span>
          </div>
          {analysis.warnings.length > 0 && (
            <ul className="space-y-1 border-b border-line bg-amber-400/[0.04] px-5 py-2.5">
              {analysis.warnings.map((w) => (
                <li key={w} className="flex gap-2 text-xs text-amber-200/90">
                  <AlertIcon size={13} className="mt-px shrink-0" /> {w}
                </li>
              ))}
            </ul>
          )}
          <div className="scroll-thin max-h-[640px] overflow-y-auto">
            {groups.map(({ key, scene, items }) => (
              <div key={key}>
                <div className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-2 border-b border-line bg-ink-900/90 px-5 py-2 backdrop-blur">
                  <div className="flex min-w-0 items-center gap-2">
                    <LayersIcon size={14} className="shrink-0 text-slate-500" />
                    <span className="truncate text-xs font-semibold text-slate-200">{scene?.title ?? key}</span>
                    <span className="font-mono text-[11px] text-slate-500">{scene ? scene.id : "no scene"}</span>
                    {scene?.engine === "BLENDER" && <Badge tone="violet" >3D · Blender</Badge>}
                    {scene?.voice && <Badge>scene voice: {scene.voice}</Badge>}
                  </div>
                  {selectedName && (
                    <Button size="sm" variant="ghost" onClick={() => onAssign(items.map((n) => n.id), selectedVoice!)}>
                      Apply {selectedName} to scene
                    </Button>
                  )}
                </div>
                <ul className="divide-y divide-line">
                  {items.map((n) => (
                    <NarrationCard
                      key={n.id}
                      narration={n}
                      lessonId={analysis.lessonId}
                      voices={voices}
                      voice={assignments[n.id] ?? ""}
                      onVoice={(v) => onAssign([n.id], v)}
                      open={!!open[n.id]}
                      onToggle={() => setOpen((o) => ({ ...o, [n.id]: !o[n.id] }))}
                      preview={preview}
                    />
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </>
      )}
    </Panel>
  );
}

function NarrationCard({
  narration: n,
  lessonId,
  voices,
  voice,
  onVoice,
  open,
  onToggle,
  preview,
}: {
  narration: Narration;
  lessonId: string;
  voices: Voice[];
  voice: string;
  onVoice: (voice: string) => void;
  open: boolean;
  onToggle: () => void;
  preview: AudioPreview;
}) {
  const current = voices.find((v) => v.id === voice);
  const overridden = voice !== (n.voice ?? "");
  const hasClip = n.lastDuration != null && n.lastVoice === voice;
  const voiceKey = `voice:${voice}`;
  const clipKey = `clip:${n.id}`;
  const duration = hasClip ? seconds(n.lastDuration) : `~${seconds(n.estimatedDuration)}`;

  return (
    <li className={`px-5 py-3.5 transition ${open ? "bg-white/[0.02]" : "hover:bg-white/[0.015]"}`}>
      <div className="flex flex-wrap items-start gap-x-3 gap-y-2">
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={open}
          className="group flex min-w-0 flex-1 basis-64 items-start gap-2 text-left"
        >
          <ChevronIcon size={14} className={`mt-1 shrink-0 text-slate-500 transition ${open ? "rotate-90" : ""}`} />
          <span className="min-w-0 flex-1">
            <span className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-[13px] font-medium text-sky-200">{n.id}</span>
              <span
                className={`font-mono text-[11px] ${hasClip ? "text-slate-400" : "text-slate-600"}`}
                title={hasClip ? "Duration of the last generated clip" : "Estimated from the text"}
              >
                {duration}
              </span>
              {!n.subtitle && <Badge>no subtitle</Badge>}
            </span>
            <span className={`mt-1 block text-sm leading-relaxed text-slate-300 ${open ? "" : "line-clamp-2"}`}>{n.text}</span>
          </span>
        </button>

        <div className="flex w-full items-center gap-2 pl-6 sm:w-auto sm:pl-0">
          <select
            value={voice}
            onChange={(e) => onVoice(e.target.value)}
            aria-label={`Voice for ${n.id}`}
            className={`h-9 min-w-0 flex-1 rounded-lg bg-ink-900/80 px-2.5 text-sm ring-1 ring-inset outline-none focus:ring-2 focus:ring-sky-400/50 sm:w-48 sm:flex-none ${
              !current ? "text-amber-200 ring-amber-400/40" : overridden ? "text-violet-100 ring-violet-400/40" : "text-slate-200 ring-white/10"
            }`}
          >
            {!current && <option value="">{n.voice ? `${n.voice} (missing)` : "Choose voice…"}</option>}
            {voices.map((v) => (
              <option key={v.id} value={v.id} disabled={!v.usable}>
                {v.name}
                {v.id === n.voice ? " · default" : ""}
              </option>
            ))}
          </select>
          <Button
            size="sm"
            className="size-9 !px-0"
            aria-label={`Preview ${current?.name ?? "voice"}`}
            title={current?.preview ? `Preview ${current.name}` : "No preview available"}
            disabled={!current?.preview}
            onClick={() => preview.toggle(voiceKey, current?.preview ?? null)}
          >
            {preview.loading === voiceKey ? <SpinnerIcon size={14} /> : preview.playing === voiceKey ? <StopIcon size={14} /> : <PlayIcon size={14} />}
          </Button>
        </div>
      </div>

      {open && (
        <div className="mt-3 ml-6 flex flex-wrap items-center gap-2 text-xs text-slate-400">
          <Badge>{n.voice ?? "no voice"} · {VOICE_SOURCE_TEXT[n.voiceSource] ?? n.voiceSource}</Badge>
          {overridden && (
            <>
              <Badge tone="violet">override → {voice || "none"}</Badge>
              {n.voice && (
                <button type="button" onClick={() => onVoice(n.voice!)} className="text-sky-300 hover:underline">
                  reset to animation.py
                </button>
              )}
            </>
          )}
          <Badge>pause {n.pauseAfter}s</Badge>
          {hasClip && (
            <Button size="sm" variant="ghost" onClick={() => preview.toggle(clipKey, clipUrl(lessonId, n.id))}>
              {preview.playing === clipKey ? <StopIcon size={12} /> : <WaveIcon size={13} />}
              {preview.playing === clipKey ? "Stop" : "Play generated clip"}
            </Button>
          )}
        </div>
      )}
      {(preview.failed[voiceKey] || preview.failed[clipKey]) && (
        <p className="mt-1.5 ml-6 text-[11px] text-rose-300">{preview.failed[voiceKey] ?? preview.failed[clipKey]}</p>
      )}
    </li>
  );
}

const RAW_OUTPUT_MARKER = "Manim output (last lines):";

// Hint first; the raw Manim output only on request.
function ErrorDetail({ detail }: { detail: string }) {
  const [raw, setRaw] = useState(false);
  const at = detail.indexOf(RAW_OUTPUT_MARKER);
  const hint = (at >= 0 ? detail.slice(0, at) : detail).trim();
  const output = at >= 0 ? detail.slice(at + RAW_OUTPUT_MARKER.length).trim() : "";
  return (
    <>
      {hint && <p className="mt-3 text-sm whitespace-pre-wrap text-rose-100/80">{hint}</p>}
      {output && (
        <>
          <button type="button" onClick={() => setRaw((r) => !r)} className="mt-3 text-xs text-rose-200/70 hover:text-rose-100 hover:underline">
            {raw ? "Hide Manim output" : "Show Manim output"}
          </button>
          {raw && (
            <pre className="scroll-thin mt-2 max-h-72 overflow-auto rounded-lg bg-black/30 p-3 font-mono text-[11px] leading-relaxed whitespace-pre-wrap text-rose-100/70">
              {output}
            </pre>
          )}
        </>
      )}
    </>
  );
}

function AnalyzeTimer() {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const started = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - started) / 1000)), 1000);
    return () => clearInterval(timer);
  }, []);
  return (
    <p className="max-w-md text-xs text-slate-500">
      <span className="font-mono text-slate-400">{elapsed}s</span>
      {elapsed >= 8 &&
        " · The first analysis of a lesson runs the whole scene once and compiles every formula with LaTeX; a long lesson can take a minute or two. Re-analyzing unchanged code is instant."}
    </p>
  );
}
