"use client";

// The generator's MP4, played as-is. Some browsers (notably embedded /
// Electron ones such as VS Code's Simple Browser) decode the H.264 video but
// not the AAC audio, and play the video silently. After a moment of playback
// the player checks whether audio is really being decoded; if not, it plays
// the generator's narration track (the PCM WAV the MP4's audio was encoded
// from) in sync with the video instead.

import { useCallback, useEffect, useRef, useState } from "react";

type AudioSource = "mp4" | "track";
type Check = "idle" | "ok" | "no-audio" | "unknown";

type MediaWithCounters = HTMLVideoElement & {
  webkitAudioDecodedByteCount?: number;
  webkitVideoDecodedByteCount?: number;
  mozHasAudio?: boolean;
  audioTracks?: { length: number };
};

/** true/false when the browser can tell us, null when it cannot. */
function decodesAudio(v: MediaWithCounters): boolean | null {
  if (typeof v.webkitAudioDecodedByteCount === "number") return v.webkitAudioDecodedByteCount > 0;
  if (typeof v.mozHasAudio === "boolean") return v.mozHasAudio;
  if (v.audioTracks) return v.audioTracks.length > 0;
  return null;
}

export function NarratedVideo({ src, narrationUrl }: { src: string; narrationUrl: string | null }) {
  const video = useRef<HTMLVideoElement>(null);
  const track = useRef<HTMLAudioElement>(null);
  const [source, setSource] = useState<AudioSource>("mp4");
  const [check, setCheck] = useState<Check>("idle");
  const [muted, setMuted] = useState(false);

  // Keep the narration track in step with the video.
  const sync = useCallback(
    (force = false) => {
      const v = video.current;
      const a = track.current;
      if (!v || !a || source !== "track") return;
      a.volume = v.volume;
      a.muted = v.muted;
      a.playbackRate = v.playbackRate;
      if (force || Math.abs(a.currentTime - v.currentTime) > 0.25) a.currentTime = v.currentTime;
      if (v.paused || v.ended || v.seeking) a.pause();
      else if (a.paused) a.play().catch(() => {});
    },
    [source],
  );

  useEffect(() => {
    const v = video.current;
    if (!v) return;
    let timer: ReturnType<typeof setTimeout> | null = null;
    const onPlaying = () => {
      sync(true);
      if (check !== "idle" || timer) return;
      // Give the decoder a moment, then look at what it actually decoded.
      timer = setTimeout(() => {
        timer = null;
        if (v.paused) return;
        const result = decodesAudio(v as MediaWithCounters);
        if (result === false) {
          setCheck("no-audio");
          if (narrationUrl) setSource("track");
        } else setCheck(result ? "ok" : "unknown");
      }, 1500);
    };
    const onPause = () => sync();
    const onSeek = () => sync(true);
    const onVolume = () => {
      setMuted(v.muted || v.volume === 0);
      sync();
    };
    const onTime = () => sync();
    v.addEventListener("playing", onPlaying);
    v.addEventListener("pause", onPause);
    v.addEventListener("seeking", onSeek);
    v.addEventListener("seeked", onSeek);
    v.addEventListener("ratechange", onTime);
    v.addEventListener("volumechange", onVolume);
    v.addEventListener("timeupdate", onTime);
    v.addEventListener("ended", onPause);
    return () => {
      if (timer) clearTimeout(timer);
      v.removeEventListener("playing", onPlaying);
      v.removeEventListener("pause", onPause);
      v.removeEventListener("seeking", onSeek);
      v.removeEventListener("seeked", onSeek);
      v.removeEventListener("ratechange", onTime);
      v.removeEventListener("volumechange", onVolume);
      v.removeEventListener("timeupdate", onTime);
      v.removeEventListener("ended", onPause);
    };
  }, [sync, check, narrationUrl]);

  // Switching source: start/stop the track at the video's position.
  useEffect(() => {
    if (source === "track") sync(true);
    else track.current?.pause();
  }, [source, sync]);

  const status =
    muted
      ? { tone: "text-amber-300", text: "The player is muted: use the speaker button in the controls." }
      : source === "track"
        ? {
            tone: "text-sky-300",
            text:
              check === "no-audio"
                ? "This browser plays the video but cannot decode its AAC audio, so the narration track is played in sync instead. The MP4 itself is fine (Chrome/Edge play it directly)."
                : "Playing the narration track in sync with the video.",
          }
        : check === "ok"
          ? { tone: "text-emerald-300/80", text: "Audio: MP4 soundtrack." }
          : check === "no-audio"
            ? { tone: "text-rose-300", text: "This browser cannot decode the MP4's audio. Open the page in Chrome or Edge, or download the video." }
            : null;

  return (
    <div className="space-y-2">
      <div className="overflow-hidden rounded-xl bg-black ring-1 ring-white/10">
        <video ref={video} key={src} src={src} controls preload="metadata" playsInline className="aspect-video w-full bg-black" />
        {narrationUrl && <audio ref={track} src={source === "track" ? narrationUrl : undefined} preload="auto" className="hidden" />}
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <span className={status?.tone ?? "text-slate-500"}>{status?.text ?? "Press play. The player checks that the audio is decoding."}</span>
        {/* Only when audio decoding is not confirmed: otherwise both would play. */}
        {narrationUrl && (check === "no-audio" || check === "unknown") && (
          <button
            type="button"
            onClick={() => setSource((s) => (s === "mp4" ? "track" : "mp4"))}
            className="text-slate-400 underline-offset-2 hover:text-slate-200 hover:underline"
            title="Use this if you see the video but hear nothing"
          >
            {source === "mp4" ? "No sound? Use the narration track" : "Use the MP4 soundtrack"}
          </button>
        )}
      </div>
    </div>
  );
}
