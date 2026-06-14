# Implementation Patterns

Essential technical patterns for implementing features in this codebase. Follow these patterns for consistency and to avoid common errors.

## When to Write Tests

**Integration Tests (API) - ALWAYS:**
- Write AFTER API route implementation
- Test via HTTP with Supertest
- Use real test database
- Location: `modules/{domain}/tests/integration/{feature}.api.test.ts`
- Coverage: Happy path + key error cases

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
- Location: `tests/e2e/`

## Service Singleton Pattern (Hybrid)

### Using Services in API Routes

**ALWAYS** use singleton service instances in production code. **NEVER** access database directly.

✅ **CORRECT - Production (Simple!):**

```typescript
import { userService } from '@/modules/users/services/user.service';
import { postService } from '@/modules/posts/services/post.service';
import { withAuth } from '@/lib/api/handlers';

export const POST = withAuth(async (session, request) => {
  const result = await userService.createUser(data);
  return result; // Returns Result<T>
});
```

❌ **WRONG - Never access database directly:**

```typescript
// DO NOT DO THIS
import { db } from '@/lib/db';
const [post] = await db.select().from(posts); // ❌ Never access db directly in API routes
```

### Available Services

Import singleton instances directly in production code:

- `userService` - User management operations
- `emailService` - Email operations
- `postService` - Post management operations
- `paymentService` - Payment processing operations

### Factory Functions (Tests Only)

For tests, use factory functions to inject test database context:

- `createUserService(ctx)` - Create with test context
- `createPostService(ctx)` - Create with test context
- `createPaymentService(ctx)` - Create with test context
- `createEmailService()` - Email (no context needed)

### Service Context

Services receive a `ServiceContext` containing:

```typescript
interface ServiceContext {
  db: PostgresJsDatabase<typeof schema>;
  logger: CustomLogger;
}
```

Production uses singleton context:
- `getServiceContext()` - Singleton for production (used internally by service singletons)

Tests create custom context:
- `createServiceContext()` - Create new context for tests (rarely needed)

### Why This Matters

The architecture follows the **KISS/YAGNI Principle**:

- **Services** are stateless singletons - simple and efficient
- **API Routes** import services directly - one line, zero boilerplate
- **Tests** use factory functions - flexible injection for test databases
- **Best of both worlds** - simplicity in production, flexibility in tests

### Service Implementation Pattern

When implementing a service, export both singleton and factory:

✅ **CORRECT:**

```typescript
import type { ServiceContext } from '@/lib/services/context';
import { getServiceContext } from '@/lib/services';
import type { Result } from '@/lib/result';

export class PostService {
  constructor(private ctx: ServiceContext) {}

  private get logger() {
    return this.ctx.logger.child({ service: 'PostService' });
  }

  async getById(id: string): Promise<Result<Post>> {
    try {
      const [post] = await this.ctx.db
        .select()
        .from(posts)
        .where(eq(posts.id, id));

      if (!post) {
        return {
          success: false,
          error: { code: 'POST_NOT_FOUND', message: 'Post not found' },
        };
      }

      return { success: true, data: post };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'DATABASE_ERROR',
          message: 'Failed to fetch post',
          cause: error,
        },
      };
    }
  }
}

// Factory function for tests
export function createPostService(ctx: ServiceContext): PostService {
  return new PostService(ctx);
}

// Singleton for production
export const postService = new PostService(getServiceContext());
```

## Result Type Pattern

### Overview

The codebase uses an explicit `Result<T, E>` type for error handling instead of throwing exceptions. This makes error handling explicit and type-safe.

**File**: `lib/result.ts`

```typescript
import type { AppError } from './errors';

export type Result<T, E = AppError> =
  | { success: true; data: T }
  | { success: false; error: E };
```

### Usage in Services

Services return `Result<T>` instead of throwing:

✅ **CORRECT - Explicit Result:**

```typescript
async createPost(data: CreatePostInput, userId: string): Promise<Result<Post>> {
  try {
    const [post] = await this.deps.db
      .insert(posts)
      .values({ ...data, authorId: userId })
      .returning();

    return { success: true, data: post };
  } catch (error) {
    return {
      success: false,
      error: { code: 'DATABASE_ERROR', message: 'Failed to create post', cause: error }
    };
  }
}
```

❌ **WRONG - Throwing exceptions (deprecated):**

```typescript
async createPost(data: CreatePostInput): Promise<Post> {
  const post = await this.deps.db.insert(posts).values(data).returning();
  if (!post) throw new ApiError(500, 'Failed to create post'); // ❌ Don't throw
  return post;
}
```

### Checking Results

```typescript
const result = await postService.getById(id);

if (!result.success) {
  // Handle error - result.error is AppError
  console.log(result.error.code, result.error.message);
  return result; // Can pass through in handlers
}

// Success - result.data is Post
const post = result.data;
```

## Error Handling Pattern

### Error Codes

**File**: `lib/errors.ts`

Centralized error codes with exhaustive HTTP status mapping:

```typescript
export const ErrorCode = {
  // Validation (400)
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_JSON: 'INVALID_JSON',

  // Auth (401/403)
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',

  // Not Found (404)
  NOT_FOUND: 'NOT_FOUND',
  POST_NOT_FOUND: 'POST_NOT_FOUND',
  USER_NOT_FOUND: 'USER_NOT_FOUND',
  PAYMENT_NOT_FOUND: 'PAYMENT_NOT_FOUND',

  // Server (500/502)
  DATABASE_ERROR: 'DATABASE_ERROR',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  EXTERNAL_SERVICE_ERROR: 'EXTERNAL_SERVICE_ERROR',
} as const;
```

### AppError Interface

```typescript
export interface AppError {
  code: ErrorCode;
  message: string;
  details?: Record<string, unknown>; // Validation details for client
  cause?: unknown; // Original error for logging (not sent to client)
}
```

### Status Code Mapping

HTTP status codes are centralized and type-safe:

```typescript
export const errorCodeToStatus: Record<ErrorCode, number> = {
  VALIDATION_ERROR: 400,
  INVALID_JSON: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  POST_NOT_FOUND: 404,
  // ... etc
};
```

### Adding New Error Codes

1. Add to `ErrorCode` object in `lib/errors.ts`
2. Add status mapping to `errorCodeToStatus`
3. TypeScript enforces completeness (compile error if mapping missing)

## API Route Handlers

### Overview

**File**: `lib/api/handlers.ts`

The codebase provides two handler wrappers that convert `Result<T>` to HTTP responses:

- `withHandler` - For public routes
- `withAuth` - For authenticated routes (checks session automatically)

### API Response Types

```typescript
export type ApiSuccessResponse<T> = {
  success: true;
  data: T;
};

export type ApiErrorResponse = {
  success: false;
  code: string;
  error: string;
  details?: Record<string, unknown>;
};

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;
```

### withAuth - Authenticated Routes

For routes requiring authentication:

```typescript
import { withAuth } from '@/lib/api/handlers';
import { postService } from '@/modules/posts/services/post.service';

export const POST = withAuth(async (session, req, ctx) => {
  // session.user.id is available
  return postService.createPost(data, session.user.id);
});
```

`withAuth` automatically:

- Checks for valid session
- Returns 401 if not authenticated
- Passes session, request, and context to handler
- Converts `Result<T>` to `NextResponse`

### withHandler - Public Routes

For routes not requiring authentication:

```typescript
import { withHandler } from '@/lib/api/handlers';
import { postService } from '@/modules/posts/services/post.service';

export const GET = withHandler(async (req, ctx) => {
  return postService.getPosts();
});
```

### handleResult - Manual Conversion

For edge cases where you need manual control:

```typescript
import { handleResult } from '@/lib/api/handlers';

const result = await postService.createPost(data);
return handleResult(result, 201); // Custom success status
```

## Zod Validation Pattern

### Overview

**File**: `lib/validation/parse.ts`

Request validation uses Zod schemas with helpers that return `Result<T>`:

### Schema Definition

Define schemas in `modules/{domain}/schemas.ts`:

```typescript
// modules/posts/schemas.ts
import { z } from 'zod';

export const createPostSchema = z.object({
  title: z.string().min(1, 'Title required').max(200),
  content: z.string().min(1, 'Content required'),
  published: z.boolean().default(false),
});

export const updatePostSchema = createPostSchema.partial();

export type CreatePostSchema = z.infer<typeof createPostSchema>;
export type UpdatePostSchema = z.infer<typeof updatePostSchema>;
```

### Validating Request Body

```typescript
import { parseRequestBody } from '@/lib/validation/parse';
import { createPostSchema } from '@/modules/posts/schemas';

export const POST = withAuth(async (session, req) => {
  const bodyResult = await parseRequestBody(req, createPostSchema);
  if (!bodyResult.success) return bodyResult; // Returns validation error

  const { postService } = withServices('postService');
  return postService.createPost(bodyResult.data, session.user.id);
});
```

### Validating Search Params

```typescript
import { parseSearchParams } from '@/lib/validation/parse';

const paginationSchema = z.object({
  limit: z.coerce.number().optional().default(10),
  offset: z.coerce.number().optional().default(0),
  search: z.string().optional(),
});

export const GET = withHandler(async (req) => {
  const paramsResult = parseSearchParams(req.url, paginationSchema);
  if (!paramsResult.success) return paramsResult;

  const { postService } = withServices('postService');
  return postService.getPosts(paramsResult.data);
});
```

### Generic Validation

```typescript
import { parseWith } from '@/lib/validation/parse';

const result = parseWith(mySchema, someData);
if (!result.success) {
  // result.error.details.issues contains validation errors
}
```

## TanStack Query Pattern

### Overview

Client-side data fetching uses TanStack Query (React Query) for caching, refetching, and mutations.

**Location**: `modules/{domain}/hooks/use-{entity}.ts`

### API Helper

```typescript
// modules/posts/hooks/use-posts.ts
'use client';

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.error);
  return json.data;
}
```

### Query Hooks (Read)

```typescript
export function usePosts(filters?: {
  search?: string;
  limit?: number;
  offset?: number;
}) {
  const params = new URLSearchParams();
  if (filters?.search) params.set('search', filters.search);
  if (filters?.limit) params.set('limit', String(filters.limit));

  const queryString = params.toString();
  const url = queryString ? `/api/posts?${queryString}` : '/api/posts';

  return useQuery({
    queryKey: ['posts', filters],
    queryFn: () => fetchApi<Post[]>(url),
  });
}

export function usePost(id: string) {
  return useQuery({
    queryKey: ['posts', id],
    queryFn: () => fetchApi<Post>(`/api/posts/${id}`),
    enabled: !!id,
  });
}
```

### Mutation Hooks (Create/Update/Delete)

```typescript
export function useCreatePost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreatePostInput) =>
      fetchApi<Post>('/api/posts', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['posts'] }),
  });
}

export function useUpdatePost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: UpdatePostInput & { id: string }) =>
      fetchApi<Post>(`/api/posts/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      queryClient.invalidateQueries({ queryKey: ['posts', id] });
    },
  });
}

export function useDeletePost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      fetchApi<void>(`/api/posts/${id}`, { method: 'DELETE' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['posts'] }),
  });
}
```

### Using Hooks in Components

```typescript
'use client';

import { usePosts, useCreatePost } from '@/modules/posts/hooks/use-posts';

export function PostList() {
  const { data: posts, isLoading, error } = usePosts({ limit: 10 });
  const createPost = useCreatePost();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const handleCreate = async () => {
    await createPost.mutateAsync({ title: 'New Post', content: '...' });
  };

  return (
    <div>
      <button onClick={handleCreate} disabled={createPost.isPending}>
        {createPost.isPending ? 'Creating...' : 'Create Post'}
      </button>
      {posts?.map(post => <PostCard key={post.id} post={post} />)}
    </div>
  );
}
```

## Next.js 15+ Patterns

### Route Params are Promises

In Next.js 15+, `context.params` is a **Promise** and must be awaited.

✅ **CORRECT:**

```typescript
export const GET = withAuth(async (session, request, context) => {
  // MUST await context.params in Next.js 15+
  const params = await context.params;
  const id = params?.id as string;

  if (!id) {
    return {
      success: false,
      error: { code: 'VALIDATION_ERROR', message: 'ID is required' },
    };
  }

  const { postService } = withServices('postService');
  return postService.getById(id);
});
```

❌ **WRONG:**

```typescript
export const GET = withAuth(async (session, request, context) => {
  // This will be undefined in Next.js 15+!
  const id = context.params.id; // ❌ Not awaited
});
```

### Search Params Pattern

Similarly, use `useSearchParams` hook properly in client components:

```typescript
'use client';

import { useSearchParams } from 'next/navigation';

export default function Page() {
  const searchParams = useSearchParams();
  const userId = searchParams.get('userId');
  const index = parseInt(searchParams.get('index') || '0');

  // ... component logic
}
```

## Complete API Route Template

Here's a complete example showing all patterns together:

```typescript
// app/api/posts/route.ts
import { withAuth, withHandler } from '@/lib/api/handlers';
import { parseRequestBody, parseSearchParams } from '@/lib/validation/parse';
import { postService } from '@/modules/posts/services/post.service';
import { createPostSchema } from '@/modules/posts/schemas';
import { z } from 'zod';

const listQuerySchema = z.object({
  limit: z.coerce.number().optional().default(10),
  offset: z.coerce.number().optional().default(0),
  search: z.string().optional(),
});

// GET /api/posts - Public route
export const GET = withHandler(async (req) => {
  const paramsResult = parseSearchParams(req.url, listQuerySchema);
  if (!paramsResult.success) return paramsResult;

  return postService.getPosts(paramsResult.data);
});

// POST /api/posts - Authenticated route
export const POST = withAuth(async (session, req) => {
  const bodyResult = await parseRequestBody(req, createPostSchema);
  if (!bodyResult.success) return bodyResult;

  return postService.createPost(bodyResult.data, session.user.id);
});
```

```typescript
// app/api/posts/[id]/route.ts
import { withAuth } from '@/lib/api/handlers';
import { parseRequestBody } from '@/lib/validation/parse';
import { postService } from '@/modules/posts/services/post.service';
import { updatePostSchema } from '@/modules/posts/schemas';

// GET /api/posts/[id]
export const GET = withAuth(async (session, req, ctx) => {
  const params = await ctx.params;
  const id = params?.id as string;

  return postService.getById(id);
});

// PUT /api/posts/[id]
export const PUT = withAuth(async (session, req, ctx) => {
  const params = await ctx.params;
  const id = params?.id as string;

  const bodyResult = await parseRequestBody(req, updatePostSchema);
  if (!bodyResult.success) return bodyResult;

  return postService.updatePost(id, bodyResult.data, session.user.id);
});

// DELETE /api/posts/[id]
export const DELETE = withAuth(async (session, req, ctx) => {
  const params = await ctx.params;
  const id = params?.id as string;

  return postService.deletePost(id, session.user.id);
});
```

## Testing Patterns

### Using Service Context in Tests

In tests, create services with test context:

```typescript
import { getTestDb } from '@/tests/utils/test-database';
import { createLogger } from '@/lib/logger';
import { createPostService } from '@/modules/posts/services/post.service';
import type { ServiceContext } from '@/lib/services/context';

describe('PostService', () => {
  let postService: PostService;

  beforeEach(() => {
    const ctx: ServiceContext = {
      db: getTestDb(),
      logger: createLogger(), // No context - let services set their own
    };
    postService = createPostService(ctx);
  });

  it('should create post', async () => {
    const result = await postService.createPost(
      { title: 'Test', content: 'Content', published: false },
      'user-123'
    );

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.title).toBe('Test');
    }
  });

  it('should return error for non-existent post', async () => {
    const result = await postService.getById('non-existent-id');

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.code).toBe('POST_NOT_FOUND');
    }
  });
});
```

## Logging Best Practices

### Log Levels by Environment

The logger automatically configures itself based on the environment:

- **Production**: `info` (business events only) - JSON format for log aggregation
- **Development**: `debug` (verbose for debugging) - Pretty format with colors
- **Tests**: `silent` (clean output by default) - Use `npm run test:verbose` for debugging

### Using Logger in Services

Services get the logger from their context and create a child logger with service identification:

```typescript
export class PostService {
  constructor(private ctx: ServiceContext) {}

  private get logger() {
    return this.ctx.logger.child({ service: 'PostService' });
  }

  async createPost(data: CreatePostInput, authorId: string): Promise<Result<Post>> {
    // Log business events at appropriate levels
    this.logger.info('Creating new post', {
      operation: 'createPost',
      authorId,
      title: data.title
    }); // Mutations = info

    try {
      const [post] = await this.ctx.db.insert(posts).values({ ...data, authorId }).returning();

      this.logger.info('Post created successfully', {
        postId: post.id,
        authorId
      });

      return { success: true, data: post };
    } catch (error) {
      this.logger.error('Failed to create post', {
        error: error instanceof Error ? error : new Error(String(error)),
        context: { operation: 'createPost', authorId }
      }); // Errors = error

      return {
        success: false,
        error: { code: 'DATABASE_ERROR', message: 'Failed to create post', cause: error }
      };
    }
  }

  async getPostById(id: string): Promise<Result<Post>> {
    this.logger.debug('Fetching post by ID', { postId: id }); // Reads = debug
    // ... implementation
  }
}
```

### Log Level Guidelines

- **`debug`**: Read operations, queries, retrievals (only visible in development/when LOG_LEVEL=debug)
- **`info`**: Mutations, business events (create, update, delete, state changes)
- **`warn`**: Recoverable issues, deprecated usage, fallbacks
- **`error`**: Failures, exceptions, unrecoverable errors

### Environment Variables

Control log output with `LOG_LEVEL` environment variable:

- `LOG_LEVEL=silent` - No logs (tests)
- `LOG_LEVEL=debug` - Verbose (debugging)
- `LOG_LEVEL=info` - Normal (default in prod)
- `LOG_LEVEL=warn` - Warnings only
- `LOG_LEVEL=error` - Errors only

### Running Tests with Logs

```bash
# Clean output (default) - no logs
npm test

# Verbose logging for debugging
npm run test:verbose

# Or set environment variable directly
LOG_LEVEL=debug npm test

# Watch mode with verbose logging
npm run test:watch:verbose
```

### Output Examples

**Test Environment (Silent by default)**:
```
✓ modules/posts/tests/post.service.test.ts (16 tests) 1.2s
  ✓ PostService > createPost > should create a new post
  ✓ PostService > getPostById > should find post by id
```

**Test Environment (LOG_LEVEL=debug - Pretty format)**:
```
14:31:24 INFO [PostService]: Creating new post
  operation: createPost
  authorId: test-author-id
  title: "Published Post 2"

14:31:24 INFO [PostService]: Post created successfully
  postId: "d8f675e8-4584-47b1-951b-416128279526"
  authorId: test-author-id
```

**Development (Pretty format with colors)**:
```
14:31:24 INFO [PostService]: Creating new post
  operation: createPost
  userId: user-123
  title: "My First Post"
  published: true
```

**Production (JSON for log aggregation)**:
```json
{"level":"info","time":"2026-01-27T14:31:24.732Z","service":"PostService","operation":"createPost","userId":"user-123","msg":"Post created successfully"}
```

### Testing Pattern with Logger

In tests, create services without setting the service context field - let services set their own:

```typescript
import { getTestDb } from '@/tests/utils/test-database';
import { createLogger } from '@/lib/logger';
import { createPostService } from '@/modules/posts/services/post.service';
import type { ServiceContext } from '@/lib/services/context';

describe('PostService', () => {
  let postService: PostService;

  beforeEach(() => {
    const ctx: ServiceContext = {
      db: getTestDb(),
      logger: createLogger(), // No context - let services set their own
    };
    postService = createPostService(ctx);
  });

  // Tests run silently by default, use npm run test:verbose to see logs
});
```

## Migration Guide: Old vs New Patterns

| Aspect          | Before (Deprecated)                               | After (Current)                               |
| --------------- | ------------------------------------------------- | --------------------------------------------- |
| Error handling  | `throw new ApiError(...)`                         | `return { success: false, error: {...} }`     |
| Validation      | `parseRequestBody()` + `validateRequiredFields()` | Zod schemas + `parseRequestBody(req, schema)` |
| Service returns | `T` (throws on error)                             | `Result<T>` (explicit)                        |
| API handlers    | `withErrorHandling` + `withAuthentication`        | `withHandler` + `withAuth`                    |
| Status codes    | Scattered in `ApiError` calls                     | Centralized `errorCodeToStatus`               |
| Client fetching | `useState` + `useEffect` + `fetch`                | TanStack Query hooks                          |
| Reference file  | `lib/api/base.ts`                                 | `lib/api/handlers.ts`                         |

## Common Pitfalls Summary

### ❌ What NOT to Do

1. **Never access `db` directly** - use service factory functions instead
2. **Never throw errors in services** - return `Result<T>` instead
3. **Never access `context.params.id` without await** - params is a Promise in Next.js 15+
4. **Never use direct database queries in API routes** - use services instead
5. **Never use `ApiError` class** - use `Result<T>` with error codes instead
6. **Never use `withErrorHandling` or `withAuthentication`** - use `withHandler` or `withAuth`

### ✅ What to Do

1. **Always import singleton services** (`postService`, `userService`, etc.) in API routes - simple and direct
2. **Always return `Result<T>` from service methods** - explicit success/error
3. **Always await `context.params`** in Next.js 15+ dynamic routes
4. **Always validate with Zod schemas** - use `parseRequestBody` and `parseSearchParams`
5. **Always use TanStack Query** for client-side data fetching
6. **Always add new error codes** to `ErrorCode` and `errorCodeToStatus`
7. **In tests, use factory functions** (`createPostService(ctx)`) with test database context

## Core Principles

These patterns follow essential development principles:

- **Simplicity First**: Use framework patterns directly, minimal abstractions
- **YAGNI**: Services encapsulate needed logic only, no wrapper layers
- **Integration-First Testing**: Test with real database
- **Test After**: Write tests after implementation to verify contracts

Note: The `Result<T,E>` type is explicit error handling that makes success/failure states visible in the type system - this improves clarity and type safety.

## Reference Implementation

For complete working examples, see:

- `app/api/posts/route.ts` - GET (public) and POST (authenticated) with Zod validation
- `app/api/posts/[id]/route.ts` - Dynamic route with params handling
- `modules/posts/services/post.service.ts` - Service with Result<T> returns
- `modules/posts/hooks/use-posts.ts` - TanStack Query hooks
- `modules/posts/schemas.ts` - Zod schema definitions
- `lib/api/handlers.ts` - API handler utilities
- `lib/result.ts` - Result type definition
- `lib/errors.ts` - Error codes and status mapping
- `lib/validation/parse.ts` - Zod validation helpers

---

**Last Updated**: Based on functional programming patterns with Result<T>, TanStack Query, and Zod validation.
