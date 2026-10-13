"use client";

// Follows one generation job: Server-Sent Events first, polling as fallback.

import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "./api";
import type { JobResult, JobSnapshot, LogLine } from "./types";

const TERMINAL = new Set(["completed", "failed", "cancelled"]);

export function useJob(jobId: string | null) {
  const [job, setJob] = useState<JobSnapshot | null>(null);
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [result, setResult] = useState<JobResult | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const logCount = useRef(0);

  useEffect(() => {
    // Reset when following a different job. (Deliberately synchronous: the
    // previous job's state must not flash while the new stream connects.)
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setJob(null);
    setLogs([]);
    setResult(null);
    setConnectionError(null);
    logCount.current = 0;
    if (!jobId) return;

    let closed = false;
    let source: EventSource | null = null;
    let pollTimer: ReturnType<typeof setTimeout> | null = null;

    const apply = (snap: JobSnapshot) => {
      if (closed) return;
      if (snap.logs.length) setLogs((prev) => [...prev, ...snap.logs].slice(-4000));
      logCount.current = snap.logCount;
      setJob(snap);
      setConnectionError(null);
      if (TERMINAL.has(snap.status)) {
        source?.close();
        if (snap.status === "completed") api.result(jobId).then((r) => !closed && setResult(r)).catch(() => {});
        return true;
      }
      return false;
    };

    const poll = async () => {
      if (closed) return;
      try {
        const snap = await api.status(jobId, logCount.current);
        if (apply(snap)) return;
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          // The API restarted and forgot this job: stop following it.
          setConnectionError("This job is no longer known to the generator (the API was restarted)");
          return;
        }
        setConnectionError(err instanceof Error ? err.message : "Lost connection to the generator");
      }
      pollTimer = setTimeout(poll, 1500);
    };

    if (typeof EventSource !== "undefined") {
      source = new EventSource(`/api/generate/${jobId}/events?logsSince=0`);
      source.addEventListener("status", (e) => apply(JSON.parse((e as MessageEvent).data)));
      source.onerror = () => {
        // Proxy/network trouble: fall back to polling (it resumes from the last log line).
        source?.close();
        source = null;
        if (!closed && !pollTimer) poll();
      };
    } else {
      poll();
    }

    return () => {
      closed = true;
      source?.close();
      if (pollTimer) clearTimeout(pollTimer);
    };
  }, [jobId]);

  return { job, logs, result, connectionError };
}
