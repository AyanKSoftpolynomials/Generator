"use client";

import { useState } from "react";
import type { LayoutIssue, LayoutResults, LayoutSeverity } from "@/lib/types";
import type { LineMarker, LineTone } from "./CodeEditor";
import { AlertIcon, CheckIcon, ChevronIcon } from "./icons";
import { Badge, Button, Panel } from "./ui";

// Layout validation results (text fits its box, stays in frame, no collisions,
// readable sizes): found while animation.py is read, before anything renders.

export const TONE: Record<LayoutSeverity, LineTone> = { ERROR: "error", WARNING: "warning", INFO: "info" };

const STYLE: Record<LayoutSeverity, { badge: string; bar: string; text: string }> = {
  ERROR: { badge: "rose", bar: "bg-rose-400", text: "text-rose-100" },
  WARNING: { badge: "amber", bar: "bg-amber-400", text: "text-amber-100" },
  INFO: { badge: "sky", bar: "bg-sky-400", text: "text-slate-300" },
};

const CODE_LABEL: Record<string, string> = {
  text_overflow: "Text overflows its box",
  text_too_large: "Text fills its box",
  tight_fit: "Tight fit",
  frame_overflow: "Outside the frame",
  safe_area: "Too close to the edge",
  off_screen: "Off screen",
  overlap: "Overlapping text",
  box_overlap: "Overlapping boxes",
  text_too_small: "Text too small",
  auto_fit: "Fitted automatically",
  spacing: "Spacing",
  size: "Size",
  skipped_3d: "3D scene",
};

/** Editor markers for every issue that points at a line of animation.py. */
export function layoutMarkers(layout: LayoutResults | null | undefined): LineMarker[] {
  return (layout?.issues ?? [])
    .filter((i) => i.line)
    .map((i) => ({ line: i.line!, tone: TONE[i.severity], message: `**${i.severity}**: ${i.message}` }));
}

export function LayoutReport({
  layout,
  onShowLine,
  bare = false,
}: {
  layout: LayoutResults;
  onShowLine?: (line: number, severity: LayoutSeverity) => void;
  bare?: boolean;
}) {
  const [showInfo, setShowInfo] = useState(false);
  const counts = layout.summary ?? { ERROR: 0, WARNING: 0, INFO: 0 };
  const main = layout.issues.filter((i) => i.severity !== "INFO");
  const info = layout.issues.filter((i) => i.severity === "INFO");
  const stops = layout.config?.fail_on_error === true;

  const badges = (
    <span className="flex flex-wrap items-center gap-1.5">
      {counts.ERROR > 0 && <Badge tone="rose">{counts.ERROR} error{counts.ERROR === 1 ? "" : "s"}</Badge>}
      {counts.WARNING > 0 && <Badge tone="amber">{counts.WARNING} warning{counts.WARNING === 1 ? "" : "s"}</Badge>}
      {counts.INFO > 0 && <Badge tone="sky">{counts.INFO} info</Badge>}
      {layout.issues.length === 0 && <Badge tone="emerald">passed</Badge>}
    </span>
  );

  const body =
    layout.issues.length === 0 ? (
      <p className="flex items-center gap-2 px-5 py-3 text-xs text-emerald-200/90">
        <CheckIcon size={13} className="shrink-0 text-emerald-300" />
        No layout problems: text fits its boxes, stays inside the frame and nothing collides.
      </p>
    ) : (
      <>
        {counts.ERROR > 0 && (
          <p className={`border-b border-line px-5 py-2 text-xs ${stops ? "bg-rose-500/[0.06] text-rose-200" : "text-slate-400"}`}>
            {stops
              ? "Generation stops at these errors (validation.fail_on_error is on). Fix them first."
              : "Errors don't stop generation: fix them, or they will be visible in the video."}
          </p>
        )}
        {main.length > 0 && (
          <ul className="divide-y divide-line">
            {main.map((issue, n) => (
              <IssueRow key={n} issue={issue} onShowLine={onShowLine} />
            ))}
          </ul>
        )}
        {info.length > 0 && (
          <div className={main.length > 0 ? "border-t border-line" : ""}>
            <button
              type="button"
              onClick={() => setShowInfo((v) => !v)}
              className="flex w-full items-center gap-1.5 px-5 py-2 text-left text-xs text-slate-500 hover:text-slate-300"
            >
              <ChevronIcon size={12} className={`transition ${showInfo ? "rotate-90" : ""}`} />
              {showInfo ? "Hide" : "Show"} {info.length} info note{info.length === 1 ? "" : "s"}
            </button>
            {showInfo && (
              <ul className="divide-y divide-line border-t border-line">
                {info.map((issue, n) => (
                  <IssueRow key={n} issue={issue} onShowLine={onShowLine} />
                ))}
              </ul>
            )}
          </div>
        )}
      </>
    );

  if (bare) {
    return (
      <div className="overflow-hidden rounded-xl ring-1 ring-inset ring-white/10">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line bg-white/[0.02] px-5 py-2.5">
          <span className="text-xs font-semibold text-slate-200">Layout check</span>
          {badges}
        </div>
        {body}
      </div>
    );
  }
  return (
    <Panel
      eyebrow="Layout check"
      title={counts.ERROR ? "Layout problems found" : counts.WARNING ? "Layout warnings" : "Layout looks good"}
      actions={badges}
      bodyClassName=""
    >
      {body}
    </Panel>
  );
}

function IssueRow({ issue, onShowLine }: { issue: LayoutIssue; onShowLine?: (line: number, severity: LayoutSeverity) => void }) {
  const style = STYLE[issue.severity];
  const where = [
    issue.scene && `scene ${issue.scene}`,
    issue.time != null && `~${issue.time.toFixed(1)}s`,
    issue.line && `line ${issue.line}`,
  ].filter(Boolean);
  return (
    <li className="relative flex gap-3 px-5 py-3">
      <span className={`absolute inset-y-2 left-0 w-[3px] rounded-r ${style.bar}`} aria-hidden />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone={style.badge}>
            {issue.severity === "ERROR" && <AlertIcon size={11} />} {issue.severity}
          </Badge>
          <span className="text-xs font-semibold text-slate-200">{CODE_LABEL[issue.code] ?? issue.code}</span>
          {issue.similar ? <span className="text-[11px] text-slate-500">+{issue.similar} more like it</span> : null}
        </div>
        <p className={`mt-1 text-[13px] leading-relaxed break-words ${style.text}`}>{issue.message}</p>
        {where.length > 0 && <p className="mt-1 font-mono text-[11px] text-slate-500">{where.join(" · ")}</p>}
        {issue.fix && (
          <pre className="mt-2 overflow-x-auto rounded-lg bg-black/30 px-3 py-2 font-mono text-[11px] whitespace-pre-wrap text-slate-400">
            {issue.fix}
          </pre>
        )}
      </div>
      {issue.line && onShowLine && (
        <Button size="sm" variant="ghost" className="self-start" onClick={() => onShowLine(issue.line!, issue.severity)}>
          Show in editor
        </Button>
      )}
    </li>
  );
}
