export const STAGES = [
  { key: "Script", label: "Validating", detail: "Read narration from animation.py" },
  { key: "TTS", label: "TTS", detail: "XTTS narration audio" },
  { key: "WhisperX", label: "WhisperX", detail: "Word-level alignment" },
  { key: "Manim", label: "Manim", detail: "Animation render" },
  { key: "Subtitles", label: "Subtitles", detail: "SRT / VTT" },
  { key: "FFmpeg", label: "FFmpeg", detail: "Final composition" },
] as const;

export function seconds(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "–";
  if (value < 60) return `${value < 10 ? value.toFixed(1) : Math.round(value)}s`;
  const m = Math.floor(value / 60);
  const s = Math.round(value % 60);
  return `${m}m ${s.toString().padStart(2, "0")}s`;
}

export function clock(t: number): string {
  return new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
}

export const VOICE_SOURCE_TEXT: Record<string, string> = {
  narration: "set in narrate()",
  scene: "scene voice",
  lesson: "lesson default",
  global: "global default",
  override: "--voice override",
  assigned: "assigned",
};

export function initials(name: string): string {
  const parts = name.split(/[\s_]+/).filter(Boolean);
  return ((parts[0]?.[0] ?? "") + (parts[1]?.[0] ?? parts[0]?.[1] ?? "")).toUpperCase();
}

export const CATEGORY_TONE: Record<string, string> = {
  teacher: "from-sky-400 to-blue-600",
  student: "from-fuchsia-400 to-violet-600",
  narrator: "from-teal-300 to-cyan-600",
};

export function categoryTone(category: string): string {
  return CATEGORY_TONE[category] ?? "from-slate-400 to-slate-600";
}
