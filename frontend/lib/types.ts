// Shapes returned by the Python API (backend/app.py).

export type Voice = {
  id: string;
  name: string;
  category: string;
  language: string;
  languageCode: string;
  description: string;
  referenceAudioFiles: string[];
  referenceSeconds: number;
  synthetic: boolean;
  speaker: string | null;
  gender: string | null;
  uploaded: boolean;
  created: string | null;
  preview: string | null;
  usable: boolean;
  problems: string[];
};

export type Narration = {
  id: string;
  scene: string | null;
  sceneTitle: string | null;
  text: string;
  voice: string | null;
  voiceSource: string;
  voiceMissing: boolean;
  subtitle: boolean;
  pauseAfter: number;
  estimatedDuration: number;
  lastDuration: number | null;
  lastVoice: string | null;
};

export type SceneInfo = { id: string; title: string | null; voice: string | null; engine: "MANIM" | "BLENDER"; narrations: number };

// Layout validation (src/validation): found while animation.py is read, before any rendering.
export type LayoutSeverity = "ERROR" | "WARNING" | "INFO";

export type LayoutIssue = {
  severity: LayoutSeverity;
  code: string;
  message: string;
  scene?: string;
  time?: number;
  line?: number;
  objects?: string[];
  boxes?: Record<string, number[]>;
  fix?: string;
  count?: number;
  similar?: number;
};

export type LayoutResults = {
  summary: Record<LayoutSeverity, number>;
  issues: LayoutIssue[];
  config: Record<string, number | boolean>;
};

export type Analysis = {
  lessonId: string;
  lesson: {
    id: string;
    title: string | null;
    className: string;
    language: string;
    defaultVoice: string | null;
    subtitles: Record<string, unknown> | null;
  };
  scenes: SceneInfo[];
  narrations: Narration[];
  warnings: string[];
  layout: LayoutResults | null;
  lessonExists: boolean;
  matchesSavedLesson: boolean;
  seconds: number;
};

export type LessonSummary = { id: string; title: string; hasVideo: boolean; updated: number };

export type StageName = "Script" | "TTS" | "WhisperX" | "Manim" | "Subtitles" | "FFmpeg";

export type StageState = {
  state: "pending" | "running" | "done" | "failed" | "skipped";
  seconds?: number;
  status?: string | null;
  done?: number;
  total?: number;
  cache?: { generated?: number; cached?: number; estimated?: boolean; skipped?: string };
};

export type LogLine = { t: number; message: string; milestone: boolean };

export type JobStatus = "queued" | "running" | "cancelling" | "completed" | "failed" | "cancelled";

export type JobSnapshot = {
  jobId: string;
  lessonId: string;
  lessonName: string;
  quality: "preview" | "final";
  status: JobStatus;
  stage: StageName | null;
  progress: number;
  queuePosition: number | null;
  pid: number | null;
  startedAt: string | null;
  completedAt: string | null;
  message: string;
  stages: Record<StageName, StageState>;
  elapsed: number;
  started: number | null;
  finished: number | null;
  logCount: number;
  logs: LogLine[];
  error: { stage: StageName | null; message: string; hint: string | null; traceback?: string | null } | null;
  // Incremental render: one segment per scene_start() section, real status from the backend.
  segments?: Segment[] | null;
  segmentSummary?: SegmentSummary | null;
  version: number;
};

export type SegmentStatus = "cached" | "changed" | "queued" | "regenerating" | "completed" | "failed";

export type Segment = { segment_id: string; segment_order: number; segment_name: string; status: SegmentStatus };

export type SegmentSummary = {
  total_segments: number;
  cached_segments: number;
  changed_segments: number;
  queued_segments: number;
  regenerating_segments: number;
  completed_segments: number;
  failed_segments: number;
};

export type JobResult = {
  status: JobStatus;
  lesson: string;
  lessonId: string;
  title: string | null;
  videoUrl: string;
  downloadUrl: string;
  narrationUrl: string | null;
  fileName: string;
  stageStatus: Record<string, string>;
  steps: Record<string, number>;
  totalSeconds: number;
  generated: string[];
  cached: string[];
  warnings: string[];
  layout: LayoutResults | null;
  summary: string;
  fileSize: number | null;
  downloaded: { bytes: number; at: string } | null;
  cleanup: CleanupResult | null; // set once this job's generated files were deleted
};

// ---- optional YouTube upload + cleanup (backend/youtube_api.py) ----

export type Privacy = "private" | "unlisted" | "public";
export type CleanupChoice = "ask" | "keep" | "delete";

export type CleanupResult = {
  status: "deleted" | "failed" | "ask" | "kept";
  after?: "download" | "upload";
  deleted?: string[];
  freedBytes?: number;
  kept?: string[];
  error?: string;
  at?: string;
};

export type YouTubeChannel = { id: string; title: string; customUrl: string | null; checked: string };

export type YouTubeStatus = {
  clientConfigured: boolean;
  connected: boolean;
  channel: YouTubeChannel | null;
  channelUrl: string | null;
  linkCheck: { match: boolean | null; message: string };
  redirectUri: string;
  defaultPrivacy: Privacy;
};

export type Preferences = {
  youtube: { channel_url: string | null; default_privacy: Privacy };
  cleanup: { after_download: CleanupChoice; after_upload: CleanupChoice; permission: string | null };
};

export type UploadRecord = {
  jobId: string;
  title: string;
  privacy: Privacy;
  status: "starting" | "uploading" | "completed" | "failed";
  progress: number;
  bytesSent: number;
  totalBytes: number;
  videoId: string | null;
  url: string | null;
  privacyApplied: Privacy | null;
  error: string | null;
  code: string | null;
  hint: string | null;
  cleanup: CleanupResult | null;
  channel?: YouTubeChannel;
};

export type Health = {
  status: "ready" | "degraded";
  busy: boolean;
  running: string[];
  maxConcurrentJobs: number;
  queued: number;
  voices: number;
  engine?: string;
  ffmpeg?: boolean;
  device?: string;
};

export type Quality = "preview" | "final";
