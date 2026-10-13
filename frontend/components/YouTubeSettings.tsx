"use client";

import { useRef, useState } from "react";
import { ApiError, youtubeApi } from "@/lib/api";
import type { CleanupChoice, Preferences, Privacy, YouTubeStatus } from "@/lib/types";
import { connectYouTube } from "@/lib/youtubeConnect";
import { AlertIcon, CheckIcon, SpinnerIcon, UploadIcon } from "./icons";
import { Badge, Button, Panel } from "./ui";

// Optional: nothing here is needed to generate or download videos.
// The saved channel link is only a reference; the connection is the OAuth
// authorization, and the API says which channel it really is.

const field =
  "h-9 w-full rounded-lg bg-ink-900/80 px-3 text-sm text-slate-100 ring-1 ring-inset ring-white/10 outline-none placeholder:text-slate-600 focus:ring-2 focus:ring-sky-400/50 disabled:opacity-60";

export function YouTubeSettings({
  status,
  prefs,
  onStatus,
  onPrefs,
}: {
  status: YouTubeStatus | null;
  prefs: Preferences | null;
  onStatus: (s: YouTubeStatus) => void;
  onPrefs: (p: Preferences) => void;
}) {
  const [link, setLink] = useState<string | null>(null); // null = show the saved value
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<{ text: string; error: boolean } | null>(null);
  const clientInput = useRef<HTMLInputElement>(null);

  const run = async (label: string, action: () => Promise<void>) => {
    setBusy(label);
    setMessage(null);
    try {
      await action();
    } catch (err) {
      const e = err instanceof ApiError ? err : new ApiError(String(err), 0);
      setMessage({ text: [e.message, e.detail].filter(Boolean).join(" "), error: true });
    } finally {
      setBusy(null);
    }
  };

  const value = link ?? status?.channelUrl ?? "";
  const dirty = link !== null && link.trim() !== (status?.channelUrl ?? "");
  const check = status?.linkCheck;

  return (
    <Panel eyebrow="YouTube" title="Upload destination" bodyClassName="p-4 space-y-4 text-sm">
      {/* Channel link */}
      <div className="space-y-1.5">
        <label className="block text-xs font-medium text-slate-400" htmlFor="yt-link">
          Channel link
        </label>
        <div className="flex gap-2">
          <input id="yt-link" className={field} value={value} placeholder="https://www.youtube.com/@yourchannel"
            onChange={(e) => setLink(e.target.value)} disabled={!!busy} />
          <Button size="sm" disabled={!dirty || !value.trim() || !!busy}
            onClick={() => run("link", async () => {
              onStatus(await youtubeApi.saveLink(value.trim()));
              setLink(null);
              setMessage({ text: "Channel link saved.", error: false });
            })}>
            {busy === "link" ? <SpinnerIcon size={13} /> : null} Save
          </Button>
        </div>
        {status?.channelUrl && !dirty && (
          <button type="button" className="text-[11px] text-slate-500 hover:text-rose-300" disabled={!!busy}
            onClick={() => run("unlink", async () => {
              onStatus(await youtubeApi.removeLink());
              setLink(null);
            })}>
            Remove saved link
          </button>
        )}
        <p className="text-[11px] leading-snug text-slate-600">A reference only: it is never used to sign in.</p>
      </div>

      {/* Connection */}
      <div className="space-y-2 border-t border-line pt-3">
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs font-medium text-slate-400">Status</span>
          {status?.connected ? <Badge tone="emerald">Connected</Badge> : <Badge>Not connected</Badge>}
        </div>
        {!status?.clientConfigured ? (
          <div className="space-y-2 rounded-lg bg-white/[0.02] p-3 text-xs text-slate-400 ring-1 ring-inset ring-white/10">
            <p>
              Connecting needs your own Google Cloud OAuth client (free): enable the YouTube Data API v3, create an OAuth
              client of type <b className="text-slate-300">Web application</b> with this redirect URI, then add its JSON
              file here (README &gt; YouTube).
            </p>
            <code className="block break-all rounded bg-black/30 px-2 py-1 text-[11px] text-slate-300">{status?.redirectUri}</code>
            <input ref={clientInput} type="file" accept=".json,application/json" className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                e.target.value = "";
                if (file) run("client", async () => onStatus(await youtubeApi.saveClient(file)));
              }} />
            <Button size="sm" onClick={() => clientInput.current?.click()} disabled={!!busy}>
              {busy === "client" ? <SpinnerIcon size={13} /> : <UploadIcon size={13} />} Add client_secret.json
            </Button>
          </div>
        ) : (
          <>
            {status.connected && status.channel && (
              <p className="text-xs text-slate-300">
                {status.channel.title}
                {status.channel.customUrl && <span className="ml-1 text-slate-500">{status.channel.customUrl}</span>}
              </p>
            )}
            {check && (
              <p className={`flex gap-1.5 text-[11px] leading-snug ${
                check.match === true ? "text-emerald-300/90" : check.match === false ? "text-amber-200" : "text-slate-500"}`}>
                {check.match === false ? <AlertIcon size={12} className="mt-px shrink-0" /> : check.match ? <CheckIcon size={12} className="mt-px shrink-0" /> : null}
                {check.message}
              </p>
            )}
            <div className="flex flex-wrap gap-2">
              <Button size="sm" variant={status.connected ? "secondary" : "primary"} disabled={!!busy}
                onClick={() => run("connect", async () => {
                  const result = await connectYouTube();
                  onStatus(await youtubeApi.status());
                  setMessage({ text: result.message, error: !result.connected });
                })}>
                {busy === "connect" ? <SpinnerIcon size={13} /> : null}
                {status.connected ? "Change account / Reconnect" : "Connect YouTube"}
              </Button>
              {status.connected && (
                <>
                  <Button size="sm" variant="ghost" disabled={!!busy}
                    onClick={() => run("refresh", async () => onStatus(await youtubeApi.refresh()))}>
                    Check again
                  </Button>
                  <Button size="sm" variant="ghost" disabled={!!busy}
                    onClick={() => run("disconnect", async () => {
                      const result = await youtubeApi.disconnect();
                      onStatus(result);
                      setMessage({ text: result.revoked ? "Disconnected; access revoked at Google." :
                        "Disconnected here (Google could not be reached to revoke; remove the app in your Google account if needed).",
                      error: false });
                    })}>
                    Disconnect
                  </Button>
                </>
              )}
            </div>
          </>
        )}
      </div>

      {prefs && <UploadAndCleanup prefs={prefs} onPrefs={onPrefs} setMessage={setMessage} />}

      {message && (
        <p className={`text-xs ${message.error ? "text-rose-200" : "text-emerald-200/90"}`} aria-live="polite">{message.text}</p>
      )}
    </Panel>
  );
}

function UploadAndCleanup({
  prefs,
  onPrefs,
  setMessage,
}: {
  prefs: Preferences;
  onPrefs: (p: Preferences) => void;
  setMessage: (m: { text: string; error: boolean } | null) => void;
}) {
  const [pending, setPending] = useState<{ after_download: CleanupChoice; after_upload: CleanupChoice } | null>(null);
  const [allow, setAllow] = useState(false);
  const choice = pending ?? { after_download: prefs.cleanup.after_download, after_upload: prefs.cleanup.after_upload };
  const needsPermission = !prefs.cleanup.permission && Object.values(choice).includes("delete");
  const changed = pending !== null;

  const save = async (changes: Parameters<typeof youtubeApi.savePreferences>[0]) => {
    try {
      onPrefs(await youtubeApi.savePreferences(changes));
      setMessage({ text: "Saved.", error: false });
      return true;
    } catch (err) {
      setMessage({ text: err instanceof Error ? err.message : String(err), error: true });
      return false;
    }
  };

  const select = (key: "after_download" | "after_upload", label: string) => (
    <label className="flex items-center justify-between gap-2 text-xs text-slate-400">
      {label}
      <select className="h-8 rounded-lg bg-ink-900/80 px-2 text-xs text-slate-100 ring-1 ring-inset ring-white/10"
        value={choice[key]} onChange={(e) => setPending({ ...choice, [key]: e.target.value as CleanupChoice })}>
        <option value="ask">Ask each time</option>
        <option value="keep">Keep the files</option>
        <option value="delete">Delete automatically</option>
      </select>
    </label>
  );

  return (
    <div className="space-y-3 border-t border-line pt-3">
      <label className="flex items-center justify-between gap-2 text-xs text-slate-400">
        Default privacy
        <select className="h-8 rounded-lg bg-ink-900/80 px-2 text-xs text-slate-100 ring-1 ring-inset ring-white/10"
          value={prefs.youtube.default_privacy}
          onChange={(e) => save({ youtube: { default_privacy: e.target.value as Privacy } })}>
          <option value="private">Private</option>
          <option value="unlisted">Unlisted</option>
          <option value="public">Public</option>
        </select>
      </label>
      <div className="space-y-2">
        <span className="block text-xs font-medium text-slate-400">Generated files of a job</span>
        {select("after_download", "After a successful download")}
        {select("after_upload", "After a successful upload")}
        <p className="text-[11px] leading-snug text-slate-600">
          Only this job&apos;s generated files are deleted (video, audio, renders), never after a failure. Your
          animation.py, voices, templates and caches are always kept.
        </p>
        {changed && needsPermission && (
          <label className="flex items-start gap-2 rounded-lg bg-rose-500/[0.06] p-2 text-[11px] text-rose-100 ring-1 ring-inset ring-rose-400/20">
            <input type="checkbox" className="mt-0.5 accent-rose-400" checked={allow} onChange={(e) => setAllow(e.target.checked)} />
            I allow deleting a job&apos;s generated files automatically after a successful download/upload.
          </label>
        )}
        {changed && (
          <div className="flex gap-2">
            <Button size="sm" disabled={needsPermission && !allow}
              onClick={async () => {
                if (await save({ cleanup: { ...choice, confirm_delete: allow } })) {
                  setPending(null);
                  setAllow(false);
                }
              }}>
              Save
            </Button>
            <Button size="sm" variant="ghost" onClick={() => { setPending(null); setAllow(false); }}>Cancel</Button>
          </div>
        )}
      </div>
    </div>
  );
}
