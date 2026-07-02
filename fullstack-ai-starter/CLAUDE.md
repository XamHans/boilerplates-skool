# CLAUDE.md

Fullstack AI SaaS starter: Next.js 16 (App Router) · TypeScript · Drizzle/Postgres · Better Auth · Vercel AI SDK · TanStack Query · shadcn/ui · Biome · Vitest.

## Commands

```bash
pnpm dev              # start dev server (localhost:3000)
pnpm build            # production build
pnpm check            # Biome lint + format (run before finishing)
pnpm check:fix        # auto-fix lint + format
pnpm test             # vitest unit tests
pnpm test:integration # vitest integration tests
pnpm test:e2e         # playwright e2e tests (auto-starts the dev server)
pnpm test:e2e:ui      # playwright interactive UI mode
pnpm test:e2e:codegen # record a test by clicking through the app
pnpm db:generate      # generate migration from schema changes
pnpm db:migrate       # apply migrations
pnpm db:studio        # drizzle studio
```

Package manager is **pnpm**. Path alias: `@/*` → repo root.

## Architecture: the feature slice

Features are vertical slices layered strictly. **`modules/posts` is the reference implementation — copy it.**

1. **DB** — `modules/{feature}/schema.ts`: Drizzle table. IDs are `text` UUIDs via `$defaultFn(() => crypto.randomUUID())`.
2. **Domain** — `modules/{feature}/types.ts` (TS interfaces) + `schemas.ts` (Zod). `schema.ts` = database, `schemas.ts` = validation. Keep them separate.
3. **Service** — `modules/{feature}/services/{feature}.service.ts`: a class holding business logic. Framework-agnostic (no `NextResponse`).
4. **API** — `app/api/{feature}/route.ts`: thin Next.js route handlers.
5. **UI** — `app/(main)/{feature}/` with colocated `hooks/` and `components/`.

Data flows one way: Component → hook (`fetchApi`) → route handler → service → Drizzle. Types are shared top-to-bottom from `modules/{feature}/types.ts`.

## Backend rules

- **Return `Result<T>`, never throw for expected errors.** Services and route handlers return `{ success: true, data }` or `{ success: false, error: { code, message, cause? } }` (see `lib/result.ts`). `error.code` is an `ErrorCode` from `lib/errors.ts` — add new codes there (they map to HTTP status).
- **Services take `ServiceContext` via constructor** (`{ db, logger }`). Export both a factory `createXService(ctx)` (for tests) and a singleton `export const xService = new XService(getServiceContext())` (for routes). Never call `getServiceContext()` inside a service.
- **Wrap routes**, don't hand-roll them: `withAuth` for authenticated routes (gives you `session`), `withHandler` for public ones (`lib/api/handlers.ts`). Return the service `Result` directly; `handleResult` turns it into the HTTP response. Do not build `NextResponse` in routes.
- **Validate all input with Zod** at the route boundary: `parseRequestBody(req, schema)` / `parseSearchParams(req.url, schema)` (`lib/validation/parse.ts`). Bail on `!result.success`.
- **Log through `this.ctx.logger.child({ service })`** with a structured `{ operation, ...context }` object. Do not use `console.*` (Biome warns; only allowed in infra bootstrap like `lib/db`).
- **Never leak `error.cause` to the client** — it's logged server-side only.

## Frontend rules

- **All server data goes through TanStack Query hooks — never `fetch`/`useEffect` in components.** Put hooks in `app/(main)/{feature}/hooks/use-{feature}.ts`. Model them on `app/(main)/posts/hooks/use-posts.ts`.
- **Call the API only via `fetchApi<T>`** (`lib/api/client.ts`). It unwraps `{ success, data }` and throws `Error(message)` on failure — so query/mutation `error` is already a clean message.
- **Queries**: stable `queryKey` (`['posts', filters]`); list key + detail key (`['posts', id]`). **Mutations**: `invalidateQueries` the affected keys in `onSuccess`. Query defaults live in `lib/query/client.ts`.
- **Loading/error come from the hook** (`isPending`, `isError`, `error`) — drive skeletons and disabled states off them, not local `useState` flags.
- **UI**: shadcn/ui primitives from `components/ui/*`; user feedback via `toast` from `sonner`. Client components need `'use client'`.

## Code style

- Biome enforces: 2-space indent, single quotes, semicolons, trailing commas, 100-col width, `const`, template literals, organized imports. Run `pnpm check:fix`.
- Prefer `type`/`interface` in `modules/{feature}/types.ts`; derive DB row types with `typeof table.$inferSelect`.
- Keep route handlers to a few lines: parse → delegate to service → return.

## Testing

- Unit-test services with Vitest against a real test DB: build a `ServiceContext` with `getTestDb()` + `createLogger()`, then `createXService(ctx)` (see `modules/posts/tests/post.service.test.ts`).
- Assert on the `Result` shape: check `result.success`, then narrow before reading `data`/`error.code`.
- Schema uses the `test` Postgres schema when `NODE_ENV=test` (see `modules/*/schema.ts`).
- **E2E** lives in `e2e/*.spec.ts` (Playwright, config in `playwright.config.ts`) — kept separate from Vitest, which excludes `e2e/**`. `webServer` boots `pnpm dev` automatically on a dedicated port (`3131`, override with `PORT`/`PLAYWRIGHT_BASE_URL`) so it never collides with a `pnpm dev` you already have on `3000`. Prefer role/text locators (`getByRole`, `getByText`); for authenticated flows use a `storageState` fixture rather than logging in per test. The `@playwright/mcp` MCP server (in `.mcp.json`) lets an agent drive the browser to explore and author these tests.

## Gotchas

- **`lib/api/base.ts` is deprecated and its `withAuthentication` is a broken stub (returns 500).** Never import from it. Use `lib/api/handlers.ts` + `lib/validation/parse.ts`. Some AI/upload routes still reference it — migrate them to the new pattern when you touch them.
- The chat route (`app/api/ai/chat/route.ts`) streams via the AI SDK and legitimately does not use `Result` — streaming responses are the one exception.
