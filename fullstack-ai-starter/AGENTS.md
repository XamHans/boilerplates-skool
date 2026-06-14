# Agent Instructions

## Project Workflow

Build complete vertical slices: API, UI, and tests together. Keep scope narrow, favor existing patterns, and avoid speculative abstractions.

For feature work, follow this sequence:

1. Inspect the relevant domain module and existing route/service/component patterns.
2. Make a short implementation plan and resolve any blocking ambiguity before editing.
3. Update Drizzle schema and migrations only when the feature requires persistence changes.
4. Implement backend service logic first, returning `Result<T>` from service methods.
5. Add API routes with the established auth and handler wrappers.
6. Add frontend hooks with TanStack Query and UI components that match the existing design system.
7. Add integration tests for API behavior; add unit tests only for complex business logic.
8. Run focused verification, then broader checks when the change touches shared behavior.

## Commands

```bash
pnpm dev
pnpm build
pnpm test
pnpm test path/to/test.spec.ts
pnpm test -- --watch
pnpm format
pnpm run check:fix
pnpm typecheck
```

Database commands:

```bash
pnpm db:generate
pnpm db:migrate
pnpm db:seed
pnpm db:studio
pnpm db:push
```

## Code Style

- Use TypeScript strict mode.
- Prefer functional React components with hooks.
- Use existing shadcn/Radix component patterns before adding new UI primitives.
- Use Zod for validation schemas.
- Use Drizzle ORM directly for database access.
- Use better-auth for authentication.
- Use TanStack Query for client data fetching and mutations.
- Keep comments sparse and useful; do not narrate obvious code.

## Module Layout

Domain code belongs under `modules/{domain}/`:

```text
modules/
`-- {domain}/
    |-- services/
    |   `-- {domain}.service.ts
    |-- hooks/
    |   `-- use-{feature}.ts
    |-- components/
    |   `-- {Component}.tsx
    |-- types/
    |   `-- {domain}.types.ts
    |-- schemas.ts
    |-- schema.ts
    `-- tests/
        |-- unit/
        |-- integration/
        `-- {component}.test.tsx
```

## Backend Patterns

Service methods should return explicit success or failure:

```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: AppError };
```

Use `withAuth` for authenticated API routes and `withHandler` for public routes. In Next.js 15+ route handlers, await `params` before reading values:

```typescript
export const POST = withAuth(async (req, { params, user }) => {
  const { id } = await params;
  const result = await postService.archivePost(id, user.id);
  return result;
});
```

## Frontend Patterns

Encapsulate data access in hooks:

```typescript
export function usePosts() {
  return useQuery({
    queryKey: ['posts'],
    queryFn: async () => {
      const res = await fetch('/api/posts');
      return res.json();
    },
  });
}
```

Invalidate related queries after successful mutations:

```typescript
export function useArchivePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: string) => {
      const res = await fetch(`/api/posts/${postId}/archive`, {
        method: 'POST',
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
}
```

## Testing Guidance

- Always add integration tests for new or changed API behavior.
- Use real test databases for integration coverage.
- Add unit tests for edge-heavy business logic.
- Add frontend tests after UI behavior is stable and user-facing.
- Reserve E2E tests for critical multi-step flows.

Test locations:

- API integration tests: `modules/{domain}/tests/integration/{feature}.api.test.ts`
- Service unit tests: `modules/{domain}/tests/unit/{service}.test.ts`
- Component tests: `modules/{domain}/tests/{component}.test.tsx`
- E2E tests: `tests/e2e/`

## Key References

- `.claude/IMPLEMENTATION-PATTERNS.md` for detailed technical patterns.
- `.claude/skills/build/SKILL.md` for the complete feature build workflow.
- `modules/` for examples of domain-level structure and conventions.
