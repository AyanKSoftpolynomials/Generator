// Thin client for the Python API. Requests go to /api/* on this origin and
// are proxied to the backend by next.config.ts, so nothing about the
// backend's location (or the machine's file system) reaches the browser.

import type {
  Analysis,
  CleanupResult,
  Health,
  JobResult,
  JobSnapshot,
  LessonSummary,
  Preferences,
  Privacy,
  Quality,
  UploadRecord,
  Voice,
  YouTubeStatus,
} from "./types";

export class ApiError extends Error {
  detail: string | null;
  line: number | null;
  status: number;
  code: string | null = null; // machine-readable reason (YouTube API errors), when the backend gives one

  constructor(message: string, status: number, detail: string | null = null, line: number | null = null) {
    super(message);
    this.status = status;
    this.detail = detail;
    this.line = line;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      cache: "no-store",
    });
  } catch {
    throw new ApiError("Cannot reach the generator API. Is the backend running (npm run backend)?", 0);
  }
  const text = await response.text();
  let body: unknown = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = null;
  }
  if (!response.ok) {
    const b = (body ?? {}) as { error?: string; detail?: unknown; line?: number; code?: string };
    const message =
      b.error ??
      (typeof b.detail === "string" ? b.detail : null) ??
      (response.status >= 500
        ? "The generator API dropped this request. Check that `npm run dev` is still running, then try again."
        : `Request failed (${response.status})`);
    const detail = b.error && typeof b.detail === "string" ? b.detail : null;
    const error = new ApiError(message, response.status, detail, b.line ?? null);
    error.code = b.code ?? null;
    throw error;
  }
  return body as T;
}

export const api = {
  health: () => request<Health>("/api/health"),
  voices: () => request<{ voices: Voice[] }>("/api/voices").then((r) => r.voices),
  lessons: () => request<{ lessons: LessonSummary[] }>("/api/lessons").then((r) => r.lessons),
  lesson: (id: string) => request<{ id: string; animation: string }>(`/api/lessons/${encodeURIComponent(id)}`),
  analyze: (animation: string, lessonName: string) =>
    request<Analysis>("/api/analyze", { method: "POST", body: JSON.stringify({ animation, lessonName }) }),
  generate: (body: {
    lessonName: string;
    animation: string;
    voiceAssignments: Record<string, string>;
    quality: Quality;
  }) => request<{ jobId: string; lessonId: string }>("/api/generate", { method: "POST", body: JSON.stringify(body) }),
  status: (jobId: string, logsSince = 0) =>
    request<JobSnapshot>(`/api/generate/${jobId}/status?logsSince=${logsSince}`),
  result: (jobId: string) => request<JobResult>(`/api/generate/${jobId}/result`),
  cancel: (jobId: string) => request<{ status: string }>(`/api/generate/${jobId}/cancel`, { method: "POST" }),
};

export type VoiceUpload = {
  file: File;
  name: string;
  speaker: string;
  language: string;
  gender: string;
  category: string;
  description: string;
  consent: boolean;
};

/** Multipart upload with progress (fetch cannot report upload progress). */
export function uploadVoice(data: VoiceUpload, onProgress: (fraction: number) => void): Promise<Voice> {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append("file", data.file, data.file.name);
    for (const key of ["name", "speaker", "language", "gender", "category", "description"] as const) form.append(key, data[key]);
    form.append("consent", String(data.consent));
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/voices");
    xhr.upload.onprogress = (e) => e.lengthComputable && onProgress(e.loaded / e.total);
    xhr.upload.onload = () => onProgress(1);
    xhr.onerror = () => reject(new ApiError("Upload failed: cannot reach the generator API.", 0));
    xhr.onload = () => {
      let body: { voice?: Voice; error?: string; detail?: unknown } = {};
      try {
        body = JSON.parse(xhr.responseText || "{}");
      } catch {
        /* not JSON */
      }
      if (xhr.status >= 200 && xhr.status < 300 && body.voice) return resolve(body.voice);
      const detail = typeof body.detail === "string" ? body.detail : null;
      const fieldErrors = Array.isArray(body.detail) ? "Some fields are missing." : null;
      reject(new ApiError(body.error ?? fieldErrors ?? `Upload failed (${xhr.status})`, xhr.status, detail));
    };
    xhr.send(form);
  });
}

export const voiceApi = {
  remove: (id: string) => request<{ deleted: string }>(`/api/voices/${encodeURIComponent(id)}`, { method: "DELETE" }),
  test: (id: string, text?: string) =>
    request<{ jobId: string; text: string }>(`/api/voices/${encodeURIComponent(id)}/test`, {
      method: "POST",
      body: JSON.stringify({ text: text || null }),
    }),
  testAudioUrl: (jobId: string) => `/api/voice-tests/${jobId}/audio`,
};

export const clipUrl =(lessonId: string, narrationId: string) =>
  `/api/lessons/${encodeURIComponent(lessonId)}/audio/${encodeURIComponent(narrationId)}`;

// ---- optional YouTube upload, download confirmation and job cleanup ----

export const youtubeApi = {
  status: () => request<YouTubeStatus>("/api/youtube"),
  saveLink: (url: string) => request<YouTubeStatus>("/api/youtube/link", { method: "PUT", body: JSON.stringify({ url }) }),
  removeLink: () => request<YouTubeStatus>("/api/youtube/link", { method: "DELETE" }),
  connect: () => request<{ authUrl: string }>("/api/youtube/connect", { method: "POST" }),
  refresh: () => request<YouTubeStatus>("/api/youtube/refresh", { method: "POST" }),
  disconnect: () => request<YouTubeStatus & { revoked: boolean }>("/api/youtube/disconnect", { method: "POST" }),
  saveClient: async (file: File): Promise<YouTubeStatus> => {
    const form = new FormData();
    form.append("file", file, file.name);
    const response = await fetch("/api/youtube/client", { method: "POST", body: form, cache: "no-store" });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new ApiError(body.error ?? `Upload failed (${response.status})`, response.status, body.detail ?? null);
    return body;
  },
  preferences: () => request<Preferences>("/api/preferences"),
  savePreferences: (changes: { youtube?: Partial<Preferences["youtube"]>; cleanup?: Record<string, unknown> }) =>
    request<Preferences>("/api/preferences", { method: "PUT", body: JSON.stringify(changes) }),
  upload: (jobId: string, body: { title: string; description: string; privacy: Privacy; confirmChannel?: boolean }) =>
    request<UploadRecord>(`/api/generate/${jobId}/youtube`, { method: "POST", body: JSON.stringify(body) }),
  uploadStatus: (jobId: string) => request<UploadRecord | null>(`/api/generate/${jobId}/youtube`), // null: never uploaded
  downloaded: (jobId: string, bytes: number) =>
    request<{ download: "ok"; bytes: number; cleanup: CleanupResult }>(`/api/generate/${jobId}/downloaded`, {
      method: "POST",
      body: JSON.stringify({ bytes }),
    }),
  cleanup: (jobId: string, after: "download" | "upload") =>
    request<CleanupResult>(`/api/generate/${jobId}/cleanup`, { method: "POST", body: JSON.stringify({ after }) }),
  // animation.py cleared: drop that script's cached analysis and the current job's generated files.
  reset: (body: { jobId: string | null; animation: string; lessonName: string }) =>
    request<unknown>("/api/reset", { method: "POST", body: JSON.stringify(body) }),
};

/** Download the whole MP4 with progress, save it, and return the number of bytes received. */
export async function downloadWithProgress(url: string, fileName: string, onProgress: (fraction: number) => void) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok || !response.body) throw new ApiError(`Download failed (${response.status})`, response.status);
  const total = Number(response.headers.get("Content-Length") || 0);
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let received = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    received += value.length;
    if (total) onProgress(received / total);
  }
  if (total && received !== total) throw new ApiError(`Download incomplete (${received} of ${total} bytes)`, 0);
  const blob = new Blob(chunks as BlobPart[], { type: "video/mp4" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(link.href), 60_000);
  return received;
}
