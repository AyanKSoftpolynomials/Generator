import { youtubeApi } from "./api";

/**
 * Open Google's consent page in a popup and wait until the user decides.
 * Resolves true when YouTube got connected, false when the user cancelled or
 * closed the window. The OAuth tokens never reach the browser: Google redirects
 * to the backend, which stores them locally (encrypted) and only reports the result.
 */
export async function connectYouTube(): Promise<{ connected: boolean; message: string }> {
  const { authUrl } = await youtubeApi.connect();
  const popup = window.open(authUrl, "youtube-connect", "width=520,height=720");
  if (!popup) {
    window.location.assign(authUrl); // popups blocked: continue in this tab (the callback page links back)
    return { connected: false, message: "Continue in this tab." };
  }
  return new Promise((resolve) => {
    let settled = false;
    const finish = (result: { connected: boolean; message: string }) => {
      if (settled) return;
      settled = true;
      window.removeEventListener("message", onMessage);
      clearInterval(timer);
      resolve(result);
    };
    const onMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin || !event.data?.youtube) return;
      finish({ connected: event.data.youtube === "connected", message: String(event.data.message ?? "") });
    };
    window.addEventListener("message", onMessage);
    // Fallback when the popup cannot message back: watch for it closing, then ask the backend.
    const timer = setInterval(async () => {
      if (!popup.closed) return;
      try {
        const status = await youtubeApi.status();
        finish({ connected: status.connected, message: status.connected ? "YouTube connected" : "Authorization was not completed." });
      } catch {
        finish({ connected: false, message: "Authorization was not completed." });
      }
    }, 800);
  });
}
