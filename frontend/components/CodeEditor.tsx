"use client";

import Editor, { loader, type BeforeMount, type OnMount } from "@monaco-editor/react";
import { useEffect, useRef, useState } from "react";

// Served from public/monaco (copied from node_modules by scripts/copy-monaco.mjs): no CDN.
loader.config({ paths: { vs: "/monaco/vs" } });

const beforeMount: BeforeMount = (monaco) => {
  monaco.editor.defineTheme("lms-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "comment", foreground: "5f6f8f", fontStyle: "italic" },
      { token: "string", foreground: "7dd3fc" },
      { token: "keyword", foreground: "c4b5fd" },
      { token: "number", foreground: "f0abfc" },
    ],
    colors: {
      "editor.background": "#0a0f1c",
      "editor.lineHighlightBackground": "#111a2d",
      "editorLineNumber.foreground": "#334155",
      "editorLineNumber.activeForeground": "#94a3b8",
      "editorGutter.background": "#0a0f1c",
      "editor.selectionBackground": "#1e3a5f",
      "editorIndentGuide.background1": "#1a2540",
      "scrollbarSlider.background": "#94a3b822",
      "scrollbarSlider.hoverBackground": "#94a3b844",
    },
  });
};

export type LineTone = "error" | "warning" | "info";
export type LineMarker = { line: number; tone: LineTone; message: string };

// Marker colours: the gutter bar (CSS in globals.css) and the scrollbar ruler.
const RULER: Record<LineTone, string> = { error: "#f43f5e", warning: "#f59e0b", info: "#38bdf8" };
// Plain class names: Monaco strips characters such as "/" (so no Tailwind opacity classes here).
const FOCUS_BG: Record<LineTone, string> = { error: "lms-line-error", warning: "lms-line-warning", info: "lms-line-info" };
const NO_MARKERS: LineMarker[] = [];

export function CodeEditor({
  value,
  onChange,
  errorLine,
  markers = NO_MARKERS,
  focus = null,
}: {
  value: string;
  onChange: (value: string) => void;
  errorLine?: number | null;
  // Lines with a layout problem: a coloured bar in the gutter and on the scrollbar.
  markers?: LineMarker[];
  // A line to jump to and highlight ("Show in editor"); a new key re-reveals the same line.
  focus?: { line: number; tone: LineTone; key: number } | null;
}) {
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const monacoRef = useRef<Parameters<OnMount>[1] | null>(null);
  const decorations = useRef<string[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    if (!editor || !monaco) return;
    const lines = editor.getModel()?.getLineCount() ?? 0;
    const valid = (line: number) => line >= 1 && line <= lines;
    const list: Parameters<typeof editor.deltaDecorations>[1] = markers.filter((m) => valid(m.line)).map((m) => ({
      range: new monaco.Range(m.line, 1, m.line, 1),
      options: {
        isWholeLine: true,
        linesDecorationsClassName: `lms-mark lms-mark-${m.tone}`,
        hoverMessage: { value: m.message },
        overviewRuler: { color: RULER[m.tone], position: monaco.editor.OverviewRulerLane.Left },
      },
    }));
    if (focus && valid(focus.line)) {
      list.push({ range: new monaco.Range(focus.line, 1, focus.line, 1), options: { isWholeLine: true, className: FOCUS_BG[focus.tone] } });
    }
    if (errorLine && valid(errorLine)) {
      list.push({
        range: new monaco.Range(errorLine, 1, errorLine, 1),
        options: { isWholeLine: true, className: "lms-line-error" },
      });
    }
    decorations.current = editor.deltaDecorations(decorations.current, list);
  }, [errorLine, markers, focus, mounted, value]);

  useEffect(() => {
    if (errorLine) editorRef.current?.revealLineInCenter(errorLine);
  }, [errorLine, mounted]);

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor || !focus) return;
    editor.revealLineInCenter(focus.line);
    editor.setPosition({ lineNumber: focus.line, column: 1 });
  }, [focus, mounted]);

  return (
    <Editor
      height="100%"
      language="python"
      theme="lms-dark"
      value={value}
      beforeMount={beforeMount}
      onMount={(editor, monaco) => {
        editorRef.current = editor;
        monacoRef.current = monaco;
        setMounted(true);
      }}
      onChange={(v) => onChange(v ?? "")}
      loading={<div className="grid h-full place-items-center text-sm text-slate-500">Loading editor…</div>}
      options={{
        fontFamily: "var(--font-geist-mono), ui-monospace, monospace",
        fontSize: 13,
        lineHeight: 20,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        smoothScrolling: true,
        padding: { top: 14, bottom: 14 },
        renderLineHighlight: "line",
        tabSize: 4,
        insertSpaces: true,
        wordWrap: "off",
        automaticLayout: true,
        scrollbar: { verticalScrollbarSize: 10, horizontalScrollbarSize: 10 },
      }}
    />
  );
}
