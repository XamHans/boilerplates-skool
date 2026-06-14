---
name: build
description: Build a complete feature from idea to working code (API + UI + tests)
argument-hint: "[feature description]"
disable-model-invocation: false
user-invocable: true
---

# Build Feature Command

Build a complete feature from idea to working code with proper git workflow in one session (~20-25 minutes).

## Workflow Overview

```
SETUP (1 min) → UNDERSTAND (1 min) → PLAN (1 min) → DATABASE (2 min) →
BACKEND (5 min) → FRONTEND (5 min) → TESTS (3 min) → VERIFY & PR (2 min) → DONE
```

## Phase 0: SETUP (1 minute)

**Goal:** Prepare git environment with latest code and feature branch.

**Actions:**
```bash
# 1. Switch to dev branch and pull latest
git checkout dev
git pull origin dev

# 2. Create feature branch with descriptive name
# Pattern: feature/{domain}/{brief-description}
git checkout -b feature/{domain}/{feature-slug}
```

**Branch naming examples:**
- `feature/posts/archive-functionality`
- `feature/payments/stripe-subscription`
- `feature/auth/two-factor-auth`

**Critical Rules:**
- ✅ Always pull latest dev before branching
- ✅ Use descriptive branch names (kebab-case)
- ✅ Branch from dev, NOT main
- ❌ Don't start work on stale code
- ❌ Don't use vague names like "feature/new-feature"

**Skip this phase if:** User explicitly says to work on current branch

## Phase 1: UNDERSTAND (1 minute)

**Goal:** Scan the codebase to understand existing patterns and identify the domain module.

**Actions:**
1. Parse feature description from user
2. Identify domain module: `modules/{domain}/`
   - If new domain needed, note it for database phase
3. Scan existing patterns:
   - Read `modules/{domain}/schema.ts` (if exists) for DB schema
   - Read `modules/{domain}/services/` for service patterns
   - Glob `app/api/{domain}/**/*.ts` for API route patterns
   - Read `.claude/IMPLEMENTATION-PATTERNS.md` for reference patterns

**Output:** Mental model of where feature fits

## Phase 2: PLAN (1 minute)

**Goal:** Show inline plan and get user approval BEFORE building anything.

**Actions:**
1. Create brief inline plan showing:
   - **Domain:** Which module (`modules/{domain}/`)
   - **Database:** Schema changes needed (if any)
   - **Backend:**
     - Service methods (with Result<T> signatures)
     - API routes (with auth requirements)
     - Zod validation schemas
   - **Frontend:**
     - TanStack Query hooks (useQuery/useMutation)
     - UI components needed
     - Where they'll be used
   - **Tests:**
     - Integration test location and scope
     - Happy path + key error cases

2. Ask 1-2 CRITICAL questions ONLY:
   - Business logic ambiguities
   - Auth/permission requirements
   - Critical UX decisions
   - **Do NOT ask:** Implementation details, tech choices, testing approach

3. Show plan in this format:

```markdown
## Building: {Feature Name}

**Domain:** `modules/{domain}/`

**Database Changes:**
- Add `{field}: {type}` to {table} schema
- OR: No database changes needed

**Backend:**
- Service: `{serviceName}.{method}(params): Promise<Result<T>>`
- Service: `{serviceName}.{method}(params): Promise<Result<T>>`
- API: `{METHOD} /api/{domain}/{route}` (auth: yes/no)
- API: `{METHOD} /api/{domain}/{route}` (auth: yes/no)
- Validation: Zod schemas for {what}

**Frontend:**
- Hook: `use{Feature}()` - {description}
- Component: `{ComponentName}` - {where used}
- UI: {key user-visible changes}

**Tests:**
- Location: `modules/{domain}/tests/integration/{feature}.api.test.ts`
- Coverage: {happy path} + {key error cases}

**Critical Questions:**
1. {Question about business logic}? (yes/no or option A/B)
2. {Question about permissions}? (yes/no or option A/B)

---
Proceed with implementation? (y/n)
```

4. Wait for user approval
5. If user says "no" or suggests changes, revise plan
6. Only proceed to Phase 3 when user approves

**Critical Rules:**
- ⚠️ NEVER start coding before user approves plan
- ⚠️ Ask only questions that affect implementation
- ⚠️ Keep plan brief (5-10 lines per section max)
- ⚠️ Show what will be built, not how it works internally

## Phase 3: DATABASE (2 minutes, if needed)

**Goal:** Update database schema with minimal changes needed NOW.

**Actions:**
1. Update `modules/{domain}/schema.ts`:
   - Add new fields to existing tables
   - Create new tables only if absolutely necessary
   - Use Drizzle ORM syntax
   - Follow existing schema patterns in the file

**Example:**
```typescript
// modules/posts/schema.ts
export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id),
  title: text('title').notNull(),
  content: text('content').notNull(),
  // NEW: Add archived timestamp
  archivedAt: timestamp('archived_at'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
});
```

**Critical Rules:**
- ✅ Only add fields needed for THIS feature (YAGNI)
- ✅ Use nullable fields for optional data
- ✅ Follow existing naming conventions (snake_case for DB)
- ❌ No future-proofing or "we might need this later"
- ❌ No complex indexes or constraints unless required

**Skip this phase if:** No database changes needed

## Phase 4: BACKEND (5 minutes)

**Goal:** Build service methods and API routes using established patterns.

### 4a. Service Methods (3 minutes)

**Location:** `modules/{domain}/services/{domain}.service.ts`

**Pattern:**
```typescript
import { db } from '@/lib/db';
import { Result } from '@/lib/types';
import { AppErrors } from '@/lib/errors';
import { {table} } from '../schema';
import { eq } from 'drizzle-orm';

class {Domain}Service {
  async {method}({params}): Promise<Result<{ReturnType}>> {
    try {
      // Business logic here
      const result = await db.{operation}({table})
        .{chainMethods}
        .where(eq({table}.{field}, {value}));

      if (!result) {
        return {
          success: false,
          error: { code: '{ERROR_CODE}' }
        };
      }

      return { success: true, data: result };
    } catch (error) {
      return {
        success: false,
        error: { code: 'INTERNAL_ERROR', message: error.message }
      };
    }
  }
}

// Singleton export
export const {domain}Service = new {Domain}Service();

// Factory for tests
export function create{Domain}Service(context?: TestContext) {
  return new {Domain}Service();
}
```

**Critical Rules:**
- ✅ ALL service methods return `Promise<Result<T>>`
- ✅ Use explicit error codes from `lib/errors.ts`
- ✅ Keep business logic in services, NOT in API routes
- ✅ Export singleton for production use
- ✅ Export factory for test isolation
- ❌ No throwing errors (use Result<T>)
- ❌ No console.log (use proper logging if needed)

### 4b. API Routes (2 minutes)

**Location:** `app/api/{domain}/{route}/route.ts`

**Pattern for authenticated routes:**
```typescript
import { withAuth } from '@/lib/api/with-auth';
import { {domain}Service } from '@/modules/{domain}/services/{domain}.service';
import { parseRequestBody } from '@/lib/api/parse-request';
import { {validationSchema} } from '@/modules/{domain}/schemas';

export const POST = withAuth(async (req, { params, user }) => {
  const { id } = await params;

  // Optional: Parse and validate body
  const body = await parseRequestBody(req, {validationSchema});
  if (!body.success) {
    return body; // Returns 400 with validation errors
  }

  const result = await {domain}Service.{method}(id, user.id);
  return result; // Auto-converts to NextResponse with correct status
});
```

**Pattern for public routes:**
```typescript
import { withHandler } from '@/lib/api/with-handler';

export const GET = withHandler(async (req, { params }) => {
  const { id } = await params;

  const result = await {domain}Service.{method}(id);
  return result;
});
```

**Critical Rules:**
- ✅ Use `withAuth` for authenticated routes (provides `user`)
- ✅ Use `withHandler` for public routes
- ✅ Always await `params` (Next.js 15+ requirement)
- ✅ Use `parseRequestBody` for validation
- ✅ Return Result<T> directly (wrappers handle conversion)
- ❌ No manual NextResponse.json() (wrappers do this)
- ❌ No try/catch (services handle errors)
- ❌ No business logic in routes (use services)

### 4c. Validation Schemas

**Location:** `modules/{domain}/schemas.ts`

**Pattern:**
```typescript
import { z } from 'zod';

export const {action}Schema = z.object({
  {field}: z.string().{validator}(),
  {field2}: z.number().optional(),
});

export type {Action}Input = z.infer<typeof {action}Schema>;
```

**Critical Rules:**
- ✅ One schema per API operation
- ✅ Use Zod's built-in validators
- ✅ Export TypeScript types with `z.infer`
- ✅ Keep schemas focused (only validate what API receives)

### 4d. Error Codes

**If new errors needed, add to:** `lib/errors.ts`

```typescript
export const AppErrors = {
  // Existing errors...
  {NEW_ERROR_CODE}: '{Human readable message}',
} as const;

export const errorCodeToStatus = {
  // Existing mappings...
  {NEW_ERROR_CODE}: {HTTP_STATUS_CODE},
};
```

## Phase 5: FRONTEND (5 minutes)

**Goal:** Build TanStack Query hooks and UI components.

### 5a. TanStack Query Hooks (2 minutes)

**Location:** `modules/{domain}/hooks/use-{feature}.ts`

**Pattern for queries (GET data):**
```typescript
import { useQuery } from '@tanstack/react-query';

export function use{Feature}({params}) {
  return useQuery({
    queryKey: ['{domain}', {params}],
    queryFn: async () => {
      const res = await fetch(`/api/{domain}/{route}`);
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    },
  });
}
```

**Pattern for mutations (POST/PUT/DELETE):**
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function use{Action}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({params}) => {
      const res = await fetch(`/api/{domain}/{route}`, {
        method: '{METHOD}',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({params}),
      });
      if (!res.ok) throw new Error('Failed to {action}');
      return res.json();
    },
    onSuccess: () => {
      // Invalidate related queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['{domain}'] });
    },
  });
}
```

**Critical Rules:**
- ✅ One hook per API operation
- ✅ Use `useQuery` for GET operations
- ✅ Use `useMutation` for POST/PUT/DELETE
- ✅ Invalidate queries on mutation success
- ✅ Use descriptive queryKey arrays
- ❌ No manual state management (TanStack handles it)
- ❌ No inline fetch in components (use hooks)

### 5b. UI Components (3 minutes)

**Location:** Depends on scope:
- Page-specific: `app/(routes)/{page}/components/{Component}.tsx`
- Reusable: `modules/{domain}/components/{Component}.tsx`
- Global: `components/{Component}.tsx`

**Pattern:**
```typescript
'use client';

import { use{Action} } from '@/modules/{domain}/hooks/use-{action}';

export function {Component}({ {props} }) {
  const {actionName} = use{Action}();

  const handleAction = () => {
    {actionName}.mutate({params});
  };

  return (
    <div>
      <button
        onClick={handleAction}
        disabled={{actionName}.isPending}
      >
        {actionName}.isPending ? 'Loading...' : '{Action}'}
      </button>

      {{actionName}.isError && (
        <p className="text-red-500">
          Error: {{actionName}.error.message}
        </p>
      )}
    </div>
  );
}
```

**Critical Rules:**
- ✅ Add `'use client'` for interactive components
- ✅ Use mutation states (isPending, isError, isSuccess)
- ✅ Disable buttons during loading
- ✅ Show error messages to users
- ✅ Keep components focused (single responsibility)
- ❌ No complex logic in components (use hooks/services)
- ❌ No inline styles (use Tailwind classes)

## Phase 6: TESTS (3 minutes)

**Goal:** Write integration tests AFTER feature works to verify API contracts.

**Timing:** Write tests AFTER implementing backend + frontend, not before.

### Integration Tests (API)

**Location:** `modules/{domain}/tests/integration/{feature}.api.test.ts`

**Pattern:**
```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import request from 'supertest';
import { setupTestDatabase, cleanupTestDatabase } from '@/lib/testing/db';
import { createTestUser } from '@/lib/testing/factories';
import type { TestContext } from '@/lib/testing/types';

describe('{METHOD} /api/{domain}/{route}', () => {
  let testContext: TestContext;
  let sessionCookie: string;
  let userId: string;

  beforeEach(async () => {
    testContext = await setupTestDatabase();
    const { user, cookie } = await createTestUser(testContext);
    sessionCookie = cookie;
    userId = user.id;
  });

  afterEach(async () => {
    await cleanupTestDatabase(testContext);
  });

  it('should {happy path behavior}', async () => {
    // Arrange: Create test data
    const testData = await create{TestData}(testContext);

    // Act: Make HTTP request
    const res = await request(testContext.app)
      .{method}(`/api/{domain}/{route}`)
      .set('Cookie', sessionCookie)
      .send({ {body} })
      .expect({expectedStatus});

    // Assert: Verify response
    expect(res.body.success).toBe(true);
    expect(res.body.data).toMatchObject({
      {expectedFields}: {expectedValues},
    });

    // Assert: Verify database state
    const dbRecord = await testContext.db
      .select()
      .from({table})
      .where(eq({table}.id, res.body.data.id));

    expect(dbRecord[0]).toMatchObject({
      {expectedDbFields}: {expectedDbValues},
    });
  });

  it('should return error when {error case}', async () => {
    // Act: Make request with invalid data
    const res = await request(testContext.app)
      .{method}(`/api/{domain}/{route}`)
      .set('Cookie', sessionCookie)
      .send({ {invalidBody} })
      .expect({errorStatus});

    // Assert: Verify error response
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('{ERROR_CODE}');
  });

  it('should require authentication', async () => {
    const res = await request(testContext.app)
      .{method}(`/api/{domain}/{route}`)
      // No cookie = unauthenticated
      .expect(401);

    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('UNAUTHORIZED');
  });
});
```

**Critical Rules:**
- ✅ Test via HTTP using Supertest (not direct service calls)
- ✅ Use real test database (not mocks)
- ✅ Test happy path first
- ✅ Test key error cases (validation, auth, not found)
- ✅ Verify both response AND database state
- ✅ Clean up test data in afterEach
- ❌ No testing implementation details
- ❌ No testing every possible edge case
- ❌ No mocking database or services

**Coverage targets:**
- ✅ Happy path (success case)
- ✅ Validation errors (bad input)
- ✅ Authentication/authorization errors
- ✅ Not found errors (invalid IDs)
- ⚠️ Complex business logic edge cases (if any)

### When to Write Other Tests

**Unit Tests (Service):**
- **When:** Complex business logic with multiple edge cases
- **Location:** `modules/{domain}/tests/unit/{service}.test.ts`
- **Not needed for:** Simple CRUD operations

**Frontend Tests:**
- **When:** After feature is stable and being used
- **Location:** `modules/{domain}/tests/{component}.test.tsx`
- **Not needed for:** Simple forms or buttons

**E2E Tests:**
- **When:** Critical multi-step flows (checkout, signup)
- **Location:** `tests/e2e/{flow}.e2e.test.ts`
- **See:** Browser Automation section below

## Phase 7: VERIFY & PR (2 minutes)

**Goal:** Ensure tests pass, code is formatted, committed, and PR created to dev branch.

**Actions:**
```bash
# 1. Run tests
npm test modules/{domain}/tests/integration/{feature}.api.test.ts

# 2. Format code
pnpm format

# 3. Type check (optional but recommended)
pnpm typecheck

# 4. Commit changes
git add .
git commit -m "feat({domain}): {brief description}

- {What was added/changed}
- {Key implementation details}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 5. Push feature branch to origin
git push -u origin feature/{domain}/{feature-slug}

# 6. Create PR to dev branch
gh pr create \
  --base dev \
  --title "feat({domain}): {brief description}" \
  --body "$(cat <<'EOF'
## Summary
{Brief description of what was built}

## Changes
- {Database changes if any}
- {Backend changes}
- {Frontend changes}

## Testing
- ✅ Integration tests passing
- ✅ Manual testing completed

## Type
- [x] New feature
- [ ] Bug fix
- [ ] Enhancement

🤖 Generated with Claude Code
EOF
)"
```

**Success criteria:**
- ✅ All tests pass
- ✅ Code is formatted
- ✅ No TypeScript errors
- ✅ Commit follows conventional commits format
- ✅ Feature branch pushed to origin
- ✅ PR created targeting dev branch

**If tests fail:**
- Debug and fix
- Re-run tests
- Do not commit until tests pass

**If PR creation fails:**
- Ensure `gh` CLI is installed and authenticated
- Check that dev branch exists on remote
- Manually create PR via GitHub UI if needed

## Complete! Feature is Ready

**What was delivered:**
- ✅ Feature branch created from latest dev
- ✅ Database schema (if needed)
- ✅ Service methods with Result<T>
- ✅ API routes with auth/validation
- ✅ TanStack Query hooks
- ✅ UI components
- ✅ Integration tests
- ✅ Formatted, tested, committed code
- ✅ PR created to dev branch

**Next steps:**
- Review PR with team
- Test manually in development environment
- Merge PR to dev when approved
- Deploy dev to staging for further testing
- Eventually promote to production

---

## Browser Automation (E2E Tests)

For critical flows requiring E2E testing, use Chrome DevTools MCP tools.

### When to Use E2E Tests

- **Payment flows** - Stripe checkout, subscription management
- **Auth flows** - Signup, login, password reset
- **Critical paths** - Core user journeys that break business if broken
- **After feature works** - Not during development

### Available Tools

**Navigation:**
```typescript
mcp__chrome-devtools__navigate_page(url)
mcp__chrome-devtools__new_page()
mcp__chrome-devtools__list_pages()
mcp__chrome-devtools__select_page(pageId)
mcp__chrome-devtools__close_page(pageId)
```

**Interaction:**
```typescript
mcp__chrome-devtools__click(selector)
mcp__chrome-devtools__fill(selector, value)
mcp__chrome-devtools__fill_form(formData)
mcp__chrome-devtools__press_key(key)
mcp__chrome-devtools__hover(selector)
```

**Verification:**
```typescript
mcp__chrome-devtools__wait_for(selector | condition)
mcp__chrome-devtools__take_screenshot(path)
mcp__chrome-devtools__take_snapshot() // DOM snapshot
```

**Advanced:**
```typescript
mcp__chrome-devtools__evaluate_script(code)
mcp__chrome-devtools__list_network_requests()
mcp__chrome-devtools__get_network_request(requestId)
mcp__chrome-devtools__list_console_messages()
mcp__chrome-devtools__handle_dialog(accept: boolean, promptText?: string)
```

### E2E Test Example

```typescript
// tests/e2e/archive-posts.e2e.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

describe('Archive Posts E2E', () => {
  beforeAll(async () => {
    // Start dev server
    await startDevServer();
  });

  afterAll(async () => {
    await stopDevServer();
  });

  it('should archive post via UI', async () => {
    // Navigate to app
    await mcp__chrome-devtools__navigate_page({
      url: 'http://localhost:3000/posts',
    });

    // Login
    await mcp__chrome-devtools__fill({
      selector: '#email',
      value: 'user@example.com',
    });
    await mcp__chrome-devtools__fill({
      selector: '#password',
      value: 'password123',
    });
    await mcp__chrome-devtools__click({
      selector: '#login-button',
    });

    // Wait for posts page
    await mcp__chrome-devtools__wait_for({
      selector: '[data-testid="posts-list"]',
    });

    // Archive first post
    await mcp__chrome-devtools__click({
      selector: '[data-testid="archive-button"]:first-of-type',
    });

    // Wait for archived badge
    await mcp__chrome-devtools__wait_for({
      selector: '[data-testid="archived-badge"]',
    });

    // Take screenshot for evidence
    await mcp__chrome-devtools__take_screenshot({
      path: './screenshots/post-archived.png',
    });

    // Verify network request was successful
    const requests = await mcp__chrome-devtools__list_network_requests();
    const archiveRequest = requests.find(r =>
      r.url.includes('/api/posts') && r.url.includes('/archive')
    );
    expect(archiveRequest.status).toBe(200);
  });
});
```

### E2E Best Practices

- ✅ Use `data-testid` attributes for stable selectors
- ✅ Wait for elements before interacting
- ✅ Take screenshots for visual evidence
- ✅ Verify network requests for API calls
- ✅ Test complete user flows (login → action → verification)
- ❌ No testing CSS or styling
- ❌ No testing every button click
- ❌ No replacing integration tests with E2E

---

## Essential Patterns Reference

### Result<T> Type

```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: AppError };

type AppError = {
  code: keyof typeof AppErrors;
  message?: string;
};
```

**Usage in services:**
```typescript
async getPost(id: string): Promise<Result<Post>> {
  const post = await db.select().from(posts).where(eq(posts.id, id));

  if (!post[0]) {
    return { success: false, error: { code: 'POST_NOT_FOUND' } };
  }

  return { success: true, data: post[0] };
}
```

**Usage in API routes:**
```typescript
export const GET = withHandler(async (req, { params }) => {
  const { id } = await params;
  const result = await postService.getPost(id);
  return result; // withHandler converts to NextResponse
});
```

### Service Singleton Pattern

```typescript
class PostService {
  // Methods here
}

// Production: singleton export
export const postService = new PostService();

// Tests: factory export
export function createPostService(context?: TestContext) {
  return new PostService();
}
```

### Domain Module Structure

```
modules/
└── posts/
    ├── services/
    │   └── post.service.ts          # Business logic
    ├── hooks/
    │   ├── use-posts.ts              # TanStack Query hooks
    │   └── use-archive-post.ts
    ├── components/
    │   └── PostCard.tsx              # Reusable components
    ├── types/
    │   └── post.types.ts             # TypeScript types
    ├── schemas.ts                    # Zod validation schemas
    ├── schema.ts                     # Drizzle database schema
    └── tests/
        ├── unit/
        │   └── post.service.test.ts
        ├── integration/
        │   └── posts.api.test.ts
        └── posts.test.tsx            # Component tests
```

### Error Handling

```typescript
// lib/errors.ts
export const AppErrors = {
  POST_NOT_FOUND: 'Post not found',
  UNAUTHORIZED: 'You must be logged in',
  FORBIDDEN: 'You do not have permission',
  INVALID_INPUT: 'Invalid input data',
  INTERNAL_ERROR: 'Internal server error',
} as const;

export const errorCodeToStatus = {
  POST_NOT_FOUND: 404,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  INVALID_INPUT: 400,
  INTERNAL_ERROR: 500,
};
```

---

## Execution Checklist

Use this checklist to ensure you complete all phases:

- [ ] **SETUP:** Switched to dev and pulled latest (`git checkout dev && git pull`)
- [ ] **SETUP:** Created feature branch (`git checkout -b feature/{domain}/{slug}`)
- [ ] **UNDERSTAND:** Scanned domain module and existing patterns
- [ ] **PLAN:** Showed inline plan with critical questions
- [ ] **PLAN:** Got user approval to proceed
- [ ] **DATABASE:** Updated schema (or skipped if not needed)
- [ ] **BACKEND:** Created service methods with Result<T>
- [ ] **BACKEND:** Created API routes with auth/validation
- [ ] **BACKEND:** Added Zod validation schemas
- [ ] **FRONTEND:** Created TanStack Query hooks
- [ ] **FRONTEND:** Created UI components
- [ ] **TESTS:** Wrote integration tests (API via HTTP)
- [ ] **TESTS:** Tests pass and verify contracts
- [ ] **VERIFY:** Ran tests (`npm test`)
- [ ] **VERIFY:** Formatted code (`pnpm format`)
- [ ] **VERIFY:** Committed changes with conventional commit message
- [ ] **VERIFY:** Pushed feature branch to origin
- [ ] **VERIFY:** Created PR to dev branch

**Time estimate:** ~20-25 minutes for typical feature (including git workflow)

---

## Tips for Success

1. **Ask minimal questions** - Only ask what affects implementation
2. **Show your plan** - Let user see what you'll build before building
3. **Build vertically** - API + UI together, not "backend then frontend"
4. **Test after** - Write integration tests after feature works
5. **Keep it simple** - YAGNI principle, no future-proofing
6. **Use patterns** - Result<T>, withAuth, TanStack Query consistently
7. **Trust the process** - This workflow has built hundreds of features

**Most common mistakes:**
- ❌ Forgetting to pull latest dev before starting
- ❌ Working directly on dev instead of feature branch
- ❌ Starting to code before user approves plan
- ❌ Asking too many questions (>2 is too many)
- ❌ Adding "nice to have" features not in description
- ❌ Writing tests before implementation
- ❌ Building backend completely before starting frontend
- ❌ Creating new patterns instead of using existing ones
- ❌ Creating PR to main instead of dev

**When in doubt:**
- Read `.claude/IMPLEMENTATION-PATTERNS.md`
- Look at existing code in `modules/{domain}/`
- Ask user ONE clear question
- Keep it simple
