"use client";

// One shared audio element: starting a preview stops the previous one.

import { useCallback, useEffect, useRef, useState } from "react";

export type PreviewState = { key: string | null; loading: boolean; failed: Record<string, string> };

export function useAudioPreview() {
  const audio = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState<string | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [failed, setFailed] = useState<Record<string, string>>({});

  useEffect(() => () => audio.current?.pause(), []);

  const stop = useCallback(() => {
    audio.current?.pause();
    setPlaying(null);
    setLoading(null);
  }, []);

  const toggle = useCallback(
    (key: string, url: string | null) => {
      if (playing === key || loading === key) return stop();
      stop();
      if (!url) {
        setFailed((f) => ({ ...f, [key]: "No preview audio for this voice" }));
        return;
      }
      if (!audio.current) audio.current = new Audio();
      const el = audio.current;
      el.onended = () => setPlaying(null);
      el.onplaying = () => {
        setLoading(null);
        setPlaying(key);
      };
      el.onerror = () => {
        setLoading(null);
        setPlaying(null);
        setFailed((f) => ({ ...f, [key]: "Preview could not be played" }));
      };
      el.src = url;
      setLoading(key);
      setFailed((f) => {
        const next = { ...f };
        delete next[key];
        return next;
      });
      el.play().catch(() => {
        setLoading(null);
        setFailed((f) => ({ ...f, [key]: "Preview could not be played" }));
      });
    },
    [playing, loading, stop],
  );

  return { playing, loading, failed, toggle, stop };
}

export type AudioPreview = ReturnType<typeof useAudioPreview>;
