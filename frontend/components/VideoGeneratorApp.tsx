"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api, ApiError, youtubeApi } from "@/lib/api";
import { useAudioPreview } from "@/lib/useAudioPreview";
import { useJob } from "@/lib/useJob";
import type {
  Analysis,
  CleanupResult,
  LayoutSeverity,
  LessonSummary,
  Preferences,
  Quality,
  Voice,
  YouTubeStatus,
} from "@/lib/types";
import { AppHeader } from "./AppHeader";
import { GenerationPanel } from "./GenerationPanel";
import { LayoutReport, layoutMarkers, TONE } from "./LayoutReport";
import { LessonPanel } from "./LessonPanel";
import { NarrationPanel } from "./NarrationPanel";
import { VideoResult } from "./VideoResult";
import { VoiceLibrary } from "./VoiceLibrary";
import { YouTubeSettings } from "./YouTubeSettings";

const DRAFT_KEY = "lms-video-generator:draft";

type Draft = { lessonName: string; source: string; quality: Quality; overrides: Record<string, string>; jobId: string | null };

// Each browser tab keeps its own draft and job (sessionStorage is per tab and
// survives a reload), so several tabs can generate different videos at once
// and each follows only its own jobId. A new tab starts from the most recent
// draft (localStorage), without any job.
function loadDraft(): Partial<Draft> {
  try {
    const tab = sessionStorage.getItem(DRAFT_KEY);
    if (tab) return JSON.parse(tab);
    return { ...JSON.parse(localStorage.getItem(DRAFT_KEY) ?? "{}"), jobId: null };
  } catch {
    return {};
  }
}

function saveDraft(draft: Draft) {
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  localStorage.setItem(DRAFT_KEY, JSON.stringify({ ...draft, jobId: null }));
}

export function VideoGeneratorApp() {
  const [lessonName, setLessonName] = useState("");
  const [source, setSource] = useState("");
  const [quality, setQuality] = useState<Quality>("preview");
  // Optional YouTube upload + cleanup preferences (nothing here is needed to generate or download).
  const [youtube, setYouTube] = useState<YouTubeStatus | null>(null);
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [cleaned, setCleaned] = useState<Record<string, CleanupResult>>({});
  const [voices, setVoices] = useState<Voice[]>([]);
  const [voicesError, setVoicesError] = useState<string | null>(null);
  const [lessons, setLessons] = useState<LessonSummary[]>([]);

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [analyzedSource, setAnalyzedSource] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<{ message: string; detail: string | null; line: number | null } | null>(null);

  // Only the user's choices; everything else comes from animation.py.
  const [overrides, setOverrides] = useState<Record<string, string>>({});
  const [selectedVoice, setSelectedVoice] = useState<string | null>(null);

  const [jobId, setJobId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const { job, logs, result, connectionError } = useJob(jobId);
  const preview = useAudioPreview();
  const restored = useRef(false);
  const latestAnalysis = useRef(0);
  const [draftReady, setDraftReady] = useState(false);
  // "Show in editor" on a layout issue: scroll to the editor and highlight that line.
  const [focus, setFocus] = useState<{ line: number; tone: "error" | "warning" | "info"; key: number } | null>(null);

  const voiceById = useMemo(() => Object.fromEntries(voices.map((v) => [v.id, v])), [voices]);

  // Effective voice per narration: user override > animation.py (resolved hierarchy).
  const assignments = useMemo(() => {
    const out: Record<string, string> = {};
    for (const n of analysis?.narrations ?? []) {
      const own = overrides[n.id];
      out[n.id] = own && voiceById[own] ? own : n.voice && voiceById[n.voice] ? n.voice : "";
    }
    return out;
  }, [analysis, overrides, voiceById]);

  const usage = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const v of Object.values(assignments)) if (v) counts[v] = (counts[v] ?? 0) + 1;
    return counts;
  }, [assignments]);

  const analyze = useCallback(
    async (text: string, name: string, quiet = false) => {
      // Only the newest request may update the page: a slow earlier one (e.g. the
      // quiet re-analysis of a restored draft) must not overwrite a lesson opened since.
      const request = ++latestAnalysis.current;
      if (!quiet) {
        setAnalyzing(true);
        setAnalyzeError(null);
      }
      try {
        const result = await api.analyze(text, name);
        if (request !== latestAnalysis.current) return;
        setAnalysis(result);
        setAnalyzedSource(text);
        setAnalyzeError(null);
      } catch (err) {
        if (quiet || request !== latestAnalysis.current) return;
        const e = err instanceof ApiError ? err : new ApiError(String(err), 0);
        setAnalysis(null);
        setAnalyzedSource(null);
        setAnalyzeError({ message: e.message, detail: e.detail, line: e.line });
      } finally {
        if (!quiet && request === latestAnalysis.current) setAnalyzing(false);
      }
    },
    [],
  );

  // Initial data + restore the last session's draft (per browser).
  useEffect(() => {
    api.voices().then(setVoices).catch((e) => setVoicesError(e.message));
    api.lessons().then(setLessons).catch(() => {});
    youtubeApi.status().then(setYouTube).catch(() => {});
    youtubeApi.preferences().then(setPrefs).catch(() => {});
    // Once only (StrictMode runs effects twice in development).
    if (restored.current) return;
    restored.current = true;
    const d = loadDraft();
    /* eslint-disable react-hooks/set-state-in-effect -- one-time restore from localStorage */
    if (d.lessonName) setLessonName(d.lessonName);
    if (d.source) setSource(d.source);
    if (d.quality) setQuality(d.quality);
    if (d.overrides) setOverrides(d.overrides);
    if (d.jobId) setJobId(d.jobId);
    /* eslint-enable react-hooks/set-state-in-effect */
    if (d.source && d.lessonName) analyze(d.source, d.lessonName, true);
    setDraftReady(true);
  }, [analyze]);

  // Save only after the restored draft is in state, never the empty initial state.
  useEffect(() => {
    if (!draftReady) return;
    try {
      const draft: Draft = { lessonName, source, quality, overrides, jobId };
      saveDraft(draft);
    } catch {
      /* storage unavailable (private window): the page still works */
    }
  }, [draftReady, lessonName, source, quality, overrides, jobId]);

  // After a finished job, refresh the analysis so real clip durations appear.
  const finished = job?.status === "completed";
  useEffect(() => {
    if (finished && analyzedSource) {
      // Quiet mode only sets state after the request resolves.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      analyze(analyzedSource, lessonName, true);
      api.lessons().then(setLessons).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once per completed job
  }, [finished]);

  // After adding/deleting a voice: the library and every narration dropdown update.
  const reloadVoices = async () => {
    try {
      setVoices(await api.voices());
      setVoicesError(null);
    } catch (e) {
      setVoicesError(e instanceof Error ? e.message : String(e));
    }
  };

  const openLesson = async (id: string) => {
    try {
      const lesson = await api.lesson(id);
      const title = lessons.find((l) => l.id === id)?.title ?? id;
      setLessonName(title);
      setSource(lesson.animation);
      setOverrides({});
      analyze(lesson.animation, title);
    } catch (err) {
      setAnalyzeError({ message: err instanceof Error ? err.message : String(err), detail: null, line: null });
    }
  };

  const assign = (ids: string[], voice: string) => {
    const byId = Object.fromEntries((analysis?.narrations ?? []).map((n) => [n.id, n]));
    setOverrides((prev) => {
      const next = { ...prev };
      for (const id of ids) {
        if (byId[id]?.voice === voice) delete next[id];
        else next[id] = voice;
      }
      return next;
    });
  };

  const stale = !!analysis && analyzedSource !== source;
  const active = !!job && ["queued", "running", "cancelling"].includes(job.status);
  const unresolved = (analysis?.narrations ?? []).filter((n) => !voiceById[assignments[n.id]]?.usable);

  const blockers: string[] = [];
  if (!lessonName.trim()) blockers.push("Enter a lesson name");
  if (!source.trim()) blockers.push("Paste or upload animation.py");
  else if (!analysis) blockers.push("Analyze the animation");
  else if (stale) blockers.push("Analyze again: animation.py changed");
  if (analysis && !stale && unresolved.length) blockers.push(`Choose a voice for ${unresolved.length} narration block(s)`);
  if (analysis && !stale && analysis.narrations.length === 0) blockers.push("No narrate() calls found");

  const generate = async () => {
    if (blockers.length || !analysis) return;
    setSubmitting(true);
    setSubmitError(null);
    preview.stop();
    try {
      const { jobId } = await api.generate({ lessonName: lessonName.trim(), animation: source, voiceAssignments: assignments, quality });
      setJobId(jobId);
    } catch (err) {
      const e = err instanceof ApiError ? err : null;
      setSubmitError([err instanceof Error ? err.message : String(err), e?.detail].filter(Boolean).join("\n\n"));
    } finally {
      setSubmitting(false);
    }
  };

  const cancel = () => jobId && api.cancel(jobId).catch(() => {});

  // "Clear": back to a completely fresh page. The backend drops this script's cached
  // analysis and deletes this job's generated files (no other job or lesson is touched).
  const clearAll = () => {
    const previous = { jobId, animation: source, lessonName };
    latestAnalysis.current++;                 // ignore any analysis still in flight
    preview.stop();
    setSource("");
    setLessonName("");
    setAnalysis(null);
    setAnalyzedSource(null);
    setAnalyzing(false);
    setAnalyzeError(null);
    setOverrides({});
    setSelectedVoice(null);
    setFocus(null);
    setSubmitError(null);
    setJobId(null);                           // clears progress, logs, result, player, download/upload state
    setCleaned({});
    if (previous.jobId || previous.animation.trim()) youtubeApi.reset(previous).catch(() => {});
  };
  const onCleaned = useCallback(
    (c: CleanupResult) => { if (jobId) setCleaned((prev) => ({ ...prev, [jobId]: c })); },
    [jobId],
  );

  const showLine = (line: number, severity: LayoutSeverity) => {
    setFocus({ line, tone: TONE[severity], key: Date.now() });
    document.getElementById("lesson-editor")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  // Markers only while the editor shows the analyzed code (line numbers would be off otherwise).
  const markers = useMemo(() => (stale ? [] : layoutMarkers(analysis?.layout)), [analysis, stale]);

  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader />
      <main className="mx-auto grid w-full max-w-[1500px] flex-1 gap-5 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-start xl:grid-cols-[minmax(0,1fr)_400px]">
        <div className="min-w-0 lg:col-start-1">
          <LessonPanel
            lessonName={lessonName}
            onLessonName={setLessonName}
            source={source}
            onSource={setSource}
            onClear={clearAll}
            lessons={lessons}
            onOpenLesson={openLesson}
            onAnalyze={() => analyze(source, lessonName)}
            analyzing={analyzing}
            canAnalyze={!!source.trim()}
            errorLine={analyzeError?.line ?? null}
            markers={markers}
            focus={focus}
            stale={stale}
          />
        </div>
        <div className="min-w-0 lg:col-start-1">
          <NarrationPanel
            analysis={analysis}
            analyzeError={analyzeError}
            analyzing={analyzing}
            voices={voices}
            assignments={assignments}
            onAssign={assign}
            selectedVoice={selectedVoice}
            preview={preview}
          />
        </div>
        {analysis?.layout && (
          <div className="min-w-0 lg:col-start-1">
            <LayoutReport layout={analysis.layout} onShowLine={stale ? undefined : showLine} />
          </div>
        )}
        <aside className="min-w-0 lg:sticky lg:top-[5.25rem] lg:col-start-2 lg:row-span-4 lg:row-start-1">
          <VoiceLibrary
            voices={voices}
            error={voicesError}
            selected={selectedVoice}
            onSelect={setSelectedVoice}
            usage={usage}
            preview={preview}
            onVoicesChanged={reloadVoices}
          />
          <div className="mt-5">
            <YouTubeSettings status={youtube} prefs={prefs} onStatus={setYouTube} onPrefs={setPrefs} />
          </div>
        </aside>
        <div className="min-w-0 lg:col-start-1">
          <GenerationPanel
            quality={quality}
            onQuality={setQuality}
            onGenerate={generate}
            onCancel={cancel}
            onRetry={generate}
            blockers={blockers}
            submitting={submitting}
            submitError={submitError}
            job={job}
            logs={logs}
            connectionError={connectionError}
          />
        </div>
        {result && result.status === "completed" && (
          <div className="min-w-0 lg:col-start-1">
            <VideoResult
              result={jobId && cleaned[jobId] ? { ...result, cleanup: cleaned[jobId] } : result}
              onGenerateAgain={generate}
              busy={active || submitting || blockers.length > 0}
              onShowLine={stale ? undefined : showLine}
              jobId={jobId ?? ""}
              youtube={youtube}
              prefs={prefs}
              onYouTube={setYouTube}
              onCleaned={onCleaned}
            />
          </div>
        )}
      </main>
      <footer className="border-t border-line px-6 py-4 text-center text-[11px] text-slate-600">
        Same engine as <span className="font-mono text-slate-500">python generate.py lessons/&lt;lesson&gt;/animation.py</span> · runs locally · only
        use voice samples you own or have permission to clone
      </footer>
    </div>
  );
}
