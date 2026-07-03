# CLAUDE.md — ui

Next.js (App Router) frontend for the voice agent, built on **LiveKit Components React**. Connects to the LiveKit room, renders the audio/chat session UI, and streams transcripts. Package manager is **pnpm**.

## Commands (`pnpm` only)

```bash
pnpm dev            # next dev --turbopack (http://localhost:3000)
pnpm build          # production build
pnpm lint           # next lint
pnpm format         # prettier --write .  (formatting is Prettier here, NOT Biome)
pnpm format:check   # prettier --check .
pnpm shadcn:install # (re)install the LiveKit agents-ui component set from the shadcn registry
```

## Structure

```
app/                     # App Router entry (layout.tsx, page.tsx, opengraph-image.tsx)
app-config.ts            # ← branding + capability flags (companyName, page text, chat/video/screenshare toggles)
components/
  agents-ui/             # LiveKit agent components (audio visualizers, control bar, transcript) — from the shadcn registry
  ai-elements/           # chat/message/conversation primitives
  app/                   # this app's composed views (session-view, welcome-view, opening-hours, ...)
  ui/                    # shadcn/ui primitives (button, select, tooltip, ...)
hooks/                   # React hooks (agents-ui visualizer hooks, useAgentErrors, useDebug)
lib/utils.ts             # getAppConfig(), getSandboxTokenSource(), getStyles(), cn helpers
```

## Rules

- **Customize the app through `app-config.ts`** (title, company name, logo, accent colors, `supportsChatInput`/`supportsVideoInput`/`supportsScreenShare`). Don't scatter branding constants across components.
- **`components/agents-ui/*` and `components/ui/*` are generated from the shadcn registry** — prefer re-installing/regenerating (`pnpm shadcn:install`) or composing wrappers in `components/app/` over hand-editing generated files.
- **Consume LiveKit state via `@livekit/components-react` hooks/context**, not manual WebRTC — session wiring lives in `agent-session-provider`. New feature UI goes in `components/app/`.
- Interactive components need `'use client'`. Merge classes with `cn` from `lib/utils`; theme via `next-themes`.
- User-facing copy is **German** (matches the agent). Toasts via `sonner`.
- Format with **Prettier** before finishing (`pnpm format`) — this package does not use Biome.
