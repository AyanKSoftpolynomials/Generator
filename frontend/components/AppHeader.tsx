"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Health } from "@/lib/types";
import { FilmIcon } from "./icons";

export function AppHeader() {
  const [health, setHealth] = useState<Health | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    let alive = true;
    const check = () =>
      api
        .health()
        .then((h) => alive && (setHealth(h), setOffline(false)))
        .catch(() => alive && setOffline(true));
    check();
    const timer = setInterval(check, 4000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  const status = offline
    ? { text: "Generator offline", dot: "bg-rose-400 text-rose-400", hint: "Start it with: npm run backend" }
    : !health
      ? { text: "Connecting…", dot: "bg-slate-500 text-slate-500", hint: "" }
      : health.status !== "ready"
        ? { text: "FFmpeg missing", dot: "bg-amber-400 text-amber-400", hint: "Install FFmpeg (see README)" }
        : health.busy
          ? {
              text: `${health.running.length} generating${health.queued ? ` · ${health.queued} queued` : ""}`,
              dot: "bg-sky-400 text-sky-400 animate-pulse-dot",
              hint: `Up to ${health.maxConcurrentJobs} jobs run at the same time; others wait in the queue.`,
            }
          : { text: "Generator Ready", dot: "bg-emerald-400 text-emerald-400 animate-pulse-dot", hint: "" };

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-ink-950/75 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1500px] items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <div className="grid size-9 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-sky-400 via-blue-500 to-violet-500 text-white shadow-[0_6px_20px_-6px_rgb(99_102_241/0.7)]">
            <FilmIcon size={18} />
          </div>
          <div className="min-w-0">
            <h1 className="truncate text-[15px] font-semibold tracking-tight text-slate-50">LMS Video Generator</h1>
            <p className="hidden truncate text-xs text-slate-500 sm:block">animation.py → narrated MP4 · XTTS · WhisperX · Manim · FFmpeg</p>
          </div>
        </div>
        <div className="flex items-center gap-3 text-xs">
          {health?.device && !offline && (
            <span className="hidden rounded-md bg-white/[0.04] px-2 py-1 font-mono text-[11px] uppercase text-slate-400 ring-1 ring-inset ring-white/10 md:inline">
              {health.device}
            </span>
          )}
          <span className="flex items-center gap-2 rounded-full bg-white/[0.04] px-3 py-1.5 ring-1 ring-inset ring-white/10" title={status.hint}>
            <span className={`size-2 rounded-full ${status.dot}`} />
            <span className="whitespace-nowrap font-medium text-slate-200">{status.text}</span>
          </span>
        </div>
      </div>
    </header>
  );
}
