# Project Commands and Guidelines

## Feature Development Workflow

Build complete features from idea to working code in one pragmatic session.

### Primary Command

**`/build [feature description]`** - Build a complete feature (API + UI + tests) in ~15-20 minutes

**Example:**
```bash
/build "add like button to posts"
/build "archive posts without deleting them"
/build "add payment subscription with Stripe"
```

### How It Works

The `/build` command follows this flow:

1. **SETUP** (1 min) - Pull latest dev, create feature branch
2. **UNDERSTAND** (1 min) - Scan domain module and existing patterns
3. **PLAN** (1 min) - Show inline brief plan and ask 1-2 critical questions
4. **DATABASE** (2 min) - Update schema if needed
5. **BACKEND** (5 min) - Build services (Result<T>) and API routes
6. **FRONTEND** (5 min) - Build TanStack Query hooks and UI components
7. **TESTS** (3 min) - Write integration tests (after feature works)
8. **VERIFY & PR** (2 min) - Run tests, format, commit, push, create PR to dev

**Total time:** ~20-25 minutes for typical features

### What You Get

Each `/build` delivers:
- ✅ **Git Workflow:** Feature branch from latest dev
- ✅ **Backend:** Service methods with Result<T>, API routes with auth/validation
- ✅ **Frontend:** TanStack Query hooks, UI components
- ✅ **Tests:** Integration tests via HTTP with real database
- ✅ **Pull Request:** Auto-formatted, tested, PR created to dev branch

### When to Write Tests

**Integration Tests (API) - ALWAYS:**
- Write AFTER API route implementation
- Test via HTTP with Supertest
- Use real test database
- Location: `modules/{domain}/tests/integration/{feature}.api.test.ts`

**Unit Tests (Service) - WHEN COMPLEX:**
- Write AFTER service implementation
- Only for complex business logic with edge cases
- Location: `modules/{domain}/tests/unit/{service}.test.ts`

**Frontend Tests - AFTER FEATURE STABLE:**
- Not upfront, only when feature is being used
- Test critical user interactions
- Location: `modules/{domain}/tests/{component}.test.tsx`

**E2E Tests - RARELY:**
- Only critical multi-step flows (checkout, signup)
- After feature complete and stable
- Use Chrome DevTools MCP tools (see `/build` skill documentation)
- Location: `tests/e2e/`

### Core Development Principles

1. **KISS** - Keep it simple, no future-proofing
2. **YAGNI** - Only build what's needed NOW
3. **Vertical Slicing** - Ship end-to-end functionality (API + UI together)
4. **Integration-First Testing** - Real databases, verify contracts
5. **Use Framework Patterns** - Next.js/Drizzle/TanStack directly, no wrappers

### Additional Commands

- **`/fix-bug [description]`** - Bug fix workflow with root cause analysis
- **`/create-policy`** - Generate privacy policy page from codebase analysis

## Development Commands

```bash
# Run all tests
npm test

# Run specific test file
npm test path/to/test.spec.ts

# Run tests in watch mode
npm test -- --watch

# Format code
pnpm format

# Lint and fix
pnpm run check:fix

# Type check
pnpm typecheck

# Start dev server
pnpm dev

# Build for production
pnpm build
```

## Code Style and Patterns

- Use TypeScript strict mode
- Prefer functional components with hooks
- Co-locate tests with the code they test in `modules/{domain}/tests/`
- Use Result<T> for all service method return values
- Use withAuth/withHandler wrappers for API routes
- Use TanStack Query for frontend data fetching
- Use Zod for validation schemas
- Use Drizzle ORM for database operations
- Use better-auth for authentication

## Module Structure

```
modules/
└── {domain}/
    ├── services/
    │   └── {domain}.service.ts    # Business logic, returns Result<T>
    ├── hooks/
    │   └── use-{feature}.ts       # TanStack Query hooks
    ├── components/
    │   └── {Component}.tsx        # Reusable domain components
    ├── types/
    │   └── {domain}.types.ts      # TypeScript types
    ├── schemas.ts                 # Zod validation schemas
    ├── schema.ts                  # Drizzle database schema
    └── tests/
        ├── unit/                  # Service tests (when complex)
        ├── integration/           # API tests (always)
        └── {component}.test.tsx   # Component tests (when stable)
```

## Essential Patterns

### Backend: Result<T>

All service methods return `Result<T>` for explicit error handling:

```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: AppError };

// Service method
async archivePost(postId: string): Promise<Result<Post>> {
  const result = await db.update(posts)
    .set({ archivedAt: new Date() })
    .where(eq(posts.id, postId));

  if (!result) {
    return { success: false, error: { code: 'POST_NOT_FOUND' } };
  }

  return { success: true, data: result };
}
```

### Backend: API Routes

Use `withAuth` for authenticated routes, `withHandler` for public routes:

```typescript
import { withAuth } from '@/lib/api/with-auth';

export const POST = withAuth(async (req, { params, user }) => {
  const { id } = await params; // Next.js 15+ async params
  const result = await postService.archivePost(id, user.id);
  return result; // Auto-converts to NextResponse
});
```

### Frontend: TanStack Query

Use hooks for data fetching and mutations:

```typescript
// Query (GET)
export function usePosts() {
  return useQuery({
    queryKey: ['posts'],
    queryFn: async () => {
      const res = await fetch('/api/posts');
      return res.json();
    },
  });
}

// Mutation (POST/PUT/DELETE)
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

## Key Resources

- `.claude/IMPLEMENTATION-PATTERNS.md` - Complete technical patterns reference
- `.claude/skills/build/SKILL.md` - Full `/build` command workflow
- `modules/` - Example domain modules showing patterns in practice
