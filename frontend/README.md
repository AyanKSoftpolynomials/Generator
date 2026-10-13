# LMS Video Generator — web UI

Next.js (App Router) + TypeScript + Tailwind + Monaco. It is only a control
panel: all work happens in the Python generator, reached through the API in
`../backend` (`/api/*` is proxied to `http://127.0.0.1:8765`, override with
`LMS_API_URL`).

From the project root:

```powershell
npm run setup   # install
npm run dev     # API + UI  → http://127.0.0.1:3000
```

- `components/VideoGeneratorApp.tsx` — page state (lesson, analysis, voice overrides, job)
- `components/` — LessonPanel (editor), NarrationPanel, VoiceLibrary, GenerationPanel, VideoResult
- `lib/api.ts` — API client · `lib/useJob.ts` — job progress (SSE, polling fallback)
- `scripts/copy-monaco.mjs` — serves Monaco from `public/monaco` (no CDN)

See the main README, section "Web control panel".
