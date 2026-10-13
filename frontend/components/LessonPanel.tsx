"use client";

import dynamic from "next/dynamic";
import { useRef, useState } from "react";
import type { LessonSummary } from "@/lib/types";
import type { LineMarker, LineTone } from "./CodeEditor";
import { ClipboardIcon, ScanIcon, SpinnerIcon, TrashIcon, UploadIcon } from "./icons";
import { Button, Panel } from "./ui";

const CodeEditor = dynamic(() => import("./CodeEditor").then((m) => m.CodeEditor), {
  ssr: false,
  loading: () => <div className="grid h-full place-items-center text-sm text-slate-500">Loading editor…</div>,
});

export function LessonPanel({
  lessonName,
  onLessonName,
  source,
  onSource,
  onClear,
  lessons,
  onOpenLesson,
  onAnalyze,
  analyzing,
  canAnalyze,
  errorLine,
  markers,
  focus,
  stale,
}: {
  lessonName: string;
  onLessonName: (v: string) => void;
  source: string;
  onSource: (v: string) => void;
  onClear: () => void;
  lessons: LessonSummary[];
  onOpenLesson: (id: string) => void;
  onAnalyze: () => void;
  analyzing: boolean;
  canAnalyze: boolean;
  errorLine: number | null;
  markers?: LineMarker[];
  focus?: { line: number; tone: LineTone; key: number } | null;
  stale: boolean;
}) {
  const fileInput = useRef<HTMLInputElement>(null);
  const [note, setNote] = useState<string | null>(null);

  const upload = async (file: File | undefined) => {
    if (!file) return;
    if (file.size > 1_000_000) return setNote("That file is larger than 1 MB.");
    onSource(await file.text());
    setNote(`Loaded ${file.name}`);
  };

  const paste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (!text.trim()) return setNote("The clipboard is empty.");
      onSource(text);
      setNote("Pasted from clipboard");
    } catch {
      setNote("Clipboard access was blocked. Click in the editor and press Ctrl+V.");
    }
  };

  const lines = source ? source.split("\n").length : 0;

  return (
    <Panel
      eyebrow="Lesson"
      title="Source"
      actions={
        lessons.length > 0 && (
          <label className="flex items-center gap-2 text-xs text-slate-400">
            <span className="hidden sm:inline">Open existing</span>
            <select
              className="h-8 max-w-44 rounded-lg bg-white/[0.04] px-2 text-xs text-slate-200 ring-1 ring-inset ring-white/10 outline-none focus:ring-sky-400/50"
              value=""
              onChange={(e) => e.target.value && onOpenLesson(e.target.value)}
            >
              <option value="">Choose lesson…</option>
              {lessons.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.title}
                </option>
              ))}
            </select>
          </label>
        )
      }
      bodyClassName="p-5 space-y-4"
    >
      <label className="block">
        <span className="mb-1.5 block text-xs font-medium text-slate-400">Lesson name</span>
        <input
          value={lessonName}
          onChange={(e) => onLessonName(e.target.value)}
          placeholder="e.g. Integers"
          maxLength={60}
          className="h-11 w-full rounded-xl bg-ink-900/80 px-3.5 text-[15px] font-medium text-slate-100 ring-1 ring-inset ring-white/10 outline-none placeholder:text-slate-600 focus:ring-2 focus:ring-sky-400/50"
        />
      </label>

      <div>
        <div className="mb-1.5 flex flex-wrap items-center justify-between gap-2">
          <span className="text-xs font-medium text-slate-400">
            animation.py
            {lines > 0 && <span className="ml-2 font-mono text-slate-600">{lines} lines</span>}
          </span>
          <div className="flex flex-wrap items-center gap-1.5">
            <input
              ref={fileInput}
              type="file"
              accept=".py,text/x-python,text/plain"
              className="hidden"
              onChange={(e) => {
                upload(e.target.files?.[0]);
                e.target.value = "";
              }}
            />
            <Button size="sm" onClick={() => fileInput.current?.click()}>
              <UploadIcon size={14} /> Upload
            </Button>
            <Button size="sm" onClick={paste}>
              <ClipboardIcon size={14} /> Paste
            </Button>
            <Button
              size="sm"
              variant="ghost"
              disabled={!source}
              onClick={() => {
                onClear();
                setNote(null);
              }}
            >
              <TrashIcon size={14} /> Clear
            </Button>
          </div>
        </div>
        <div id="lesson-editor" className="relative h-[440px] scroll-mt-24 overflow-hidden rounded-xl ring-1 ring-inset ring-white/10 lg:h-[520px]">
          <CodeEditor value={source} onChange={onSource} errorLine={errorLine} markers={markers} focus={focus} />
          {!source && (
            <div className="pointer-events-none absolute inset-0 grid place-items-center">
              <div className="text-center">
                <p className="text-sm text-slate-400">Paste or upload your lesson&apos;s animation.py</p>
                <p className="mt-1 text-xs text-slate-600">It stays the single source of truth: narration, voices and visuals.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="min-h-5 text-xs text-slate-500" aria-live="polite">
          {stale ? <span className="text-amber-300/90">animation.py changed since the last analysis. Analyze again.</span> : note}
        </p>
        <Button variant={stale ? "primary" : "secondary"} onClick={onAnalyze} disabled={!canAnalyze || analyzing}>
          {analyzing ? <SpinnerIcon size={15} /> : <ScanIcon size={15} />}
          {analyzing ? "Analyzing…" : "Analyze Animation"}
        </Button>
      </div>
    </Panel>
  );
}
