"use client";

import { seconds } from "@/lib/format";
import type { CleanupResult, JobResult, LayoutSeverity, Preferences, YouTubeStatus } from "@/lib/types";
import { CheckIcon, RefreshIcon } from "./icons";
import { LayoutReport } from "./LayoutReport";
import { NarratedVideo } from "./NarratedVideo";
import { VideoActions } from "./VideoActions";
import { Badge, Button, Panel } from "./ui";

const ORDER = ["TTS", "WhisperX", "Manim", "Subtitles", "FFmpeg"];

export function VideoResult({
  result,
  onGenerateAgain,
  busy,
  onShowLine,
  jobId,
  youtube,
  prefs,
  onYouTube,
  onCleaned,
}: {
  result: JobResult;
  onGenerateAgain: () => void;
  busy: boolean;
  onShowLine?: (line: number, severity: LayoutSeverity) => void;
  jobId: string;
  youtube: YouTubeStatus | null;
  prefs: Preferences | null;
  onYouTube: (s: YouTubeStatus) => void;
  onCleaned: (c: CleanupResult) => void;
}) {
  const cleaned = result.cleanup?.status === "deleted";
  return (
    <Panel
      eyebrow="Video ready"
      title={
        <span className="flex items-center gap-2">
          <span className="grid size-5 place-items-center rounded-full bg-emerald-400/15 text-emerald-300">
            <CheckIcon size={12} />
          </span>
          {result.title ?? result.lesson}
        </span>
      }
      actions={
        <>
          <Button size="sm" onClick={onGenerateAgain} disabled={busy}>
            <RefreshIcon size={14} /> Generate Again
          </Button>
        </>
      }
      bodyClassName="p-5 space-y-4"
    >
      {/* The generator's MP4, streamed as-is (no re-encoding). */}
      {!cleaned && <NarratedVideo key={result.videoUrl} src={result.videoUrl} narrationUrl={result.narrationUrl} />}
      {/* Download and the optional YouTube upload (this job only; cleanup only after a success). */}
      <VideoActions jobId={jobId} result={result} youtube={youtube} prefs={prefs} onYouTube={onYouTube} onCleaned={onCleaned} />
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
        <span className="font-mono text-slate-300">{result.fileName}</span>
        <span className="text-slate-600">·</span>
        <span>built in {seconds(result.totalSeconds)}</span>
        <span className="text-slate-600">·</span>
        <span>
          speech: {result.generated?.length ?? 0} generated, {result.cached?.length ?? 0} reused
        </span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {ORDER.filter((k) => result.stageStatus?.[k]).map((k) => (
          <Badge key={k} tone={/^(Cached|Rendered: 0|Generated: 0)/.test(result.stageStatus[k]) ? "emerald" : "slate"}>
            {k}: {result.stageStatus[k].replace(/\n\s*/g, " · ")}
          </Badge>
        ))}
      </div>
      {result.layout && result.layout.issues.some((i) => i.severity !== "INFO") && (
        <LayoutReport layout={result.layout} onShowLine={onShowLine} bare />
      )}
      {result.warnings?.length > 0 && (
        <ul className="space-y-1 text-xs text-amber-200/80">
          {result.warnings.map((w) => (
            <li key={w}>⚠ {w}</li>
          ))}
        </ul>
      )}
    </Panel>
  );
}
