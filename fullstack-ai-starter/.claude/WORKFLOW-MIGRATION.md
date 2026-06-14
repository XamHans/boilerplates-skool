# Workflow Migration: Constitutional BDD → Pragmatic /build

**Date:** February 4, 2026
**Migration:** From 4-phase constitutional BDD to single pragmatic `/build` command

## What Changed

### Before (Constitutional BDD)

**4-phase workflow:**
1. `/create-specs [idea]` - Generate formal Gherkin scenarios
2. `/groundwork [spec]` - Build shared infrastructure with gates
3. `/create-tasks [spec]` - Decompose into task list (optional)
4. `/implement [spec]` - Implement with test-first approach

**Required `/clear` between phases** for context management

**11 Constitutional Articles** with formal compliance gates:
- Simplicity First
- Anti-Abstraction
- Integration-First Testing
- Test-First Development
- Vertical Slicing
- Specification Quality
- Complexity Tracking
- Context Management
- Groundwork Separation
- Error Recovery
- Bidirectional Feedback

**Heavy documentation:**
- Formal Gherkin specs with `[NEEDS CLARIFICATION]` markers
- GROUNDWORK-{feature}.md files
- Task decomposition files
- Complexity tracking sections
- Constitutional compliance checklists

**Time:** ~30-45 minutes per feature (across multiple sessions)

### After (Pragmatic /build)

**Single command workflow:**
```bash
/build "feature description"
```

**7-phase execution (one session):**
1. UNDERSTAND (1 min) - Scan patterns
2. PLAN (1 min) - Show inline brief, get approval
3. DATABASE (2 min) - Update schema if needed
4. BACKEND (5 min) - Services + API routes
5. FRONTEND (5 min) - Hooks + components
6. TESTS (3 min) - Integration tests AFTER feature works
7. VERIFY (1 min) - Test, format, commit

**Core principles (not gates):**
- KISS - Keep it simple
- YAGNI - You ain't gonna need it
- Vertical Slicing - API + UI together
- Integration-First - Real databases
- Test After - Verify contracts post-implementation

**Minimal documentation:**
- Inline plan (5-10 lines per section)
- 1-2 critical questions max
- No formal specs or tracking files

**Time:** ~15-20 minutes per feature (single session)

## What Stayed (Proven Patterns)

### Backend Patterns ✅

1. **Result<T>** - Explicit error handling
   ```typescript
   async createPost(data): Promise<Result<Post>> {
     // Returns { success: true, data } or { success: false, error }
   }
   ```

2. **Service Singletons**
   ```typescript
   // Production
   import { postService } from '@/modules/posts/services/post.service';

   // Tests
   const service = createPostService(testContext);
   ```

3. **API Handlers**
   ```typescript
   export const POST = withAuth(async (req, { params, user }) => {
     const result = await postService.method(params, user.id);
     return result; // Auto-converts to NextResponse
   });
   ```

4. **Zod Validation**
   ```typescript
   const body = await parseRequestBody(req, createPostSchema);
   if (!body.success) return body;
   ```

5. **Centralized Errors**
   ```typescript
   export const AppErrors = {
     POST_NOT_FOUND: 'Post not found',
     // ...
   } as const;

   export const errorCodeToStatus = {
     POST_NOT_FOUND: 404,
     // ...
   };
   ```

### Frontend Patterns ✅

1. **TanStack Query Hooks**
   ```typescript
   export function useArchivePost() {
     const queryClient = useQueryClient();
     return useMutation({
       mutationFn: async (postId) => {
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

2. **Component Usage**
   ```typescript
   function PostCard({ post }) {
     const archiveMutation = useArchivePost();
     return (
       <button onClick={() => archiveMutation.mutate(post.id)}>
         Archive
       </button>
     );
   }
   ```

### Architecture Patterns ✅

1. **Vertical Slicing** - Each feature delivers API + UI + tests together
2. **Domain Modules** - Organized by business domain
3. **Test Co-Location** - Tests live with domain code

## What Left (Bureaucracy)

### Removed ❌

1. **Formal Specifications**
   - No Gherkin Given/When/Then scenarios
   - No `[NEEDS CLARIFICATION]` marker system
   - No spec files in `specs/{domain}/{feature}.md`

2. **Constitutional Gates**
   - No quality checklists at each phase
   - No complexity tracking sections
   - No justified exceptions documentation
   - No compliance verification

3. **Separate Groundwork Phase**
   - No upfront infrastructure planning
   - No GROUNDWORK-{feature}.md files
   - No approval gates for shared code
   - Schema built inline when needed

4. **Multi-Phase Workflow**
   - No `/clear` between phases
   - No separate planning/implementation
   - No task decomposition files
   - No scenario-by-scenario approach

5. **Test-First Dogma**
   - Tests written AFTER implementation
   - Focus on integration tests (API contracts)
   - Frontend tests only when feature stable
   - E2E tests only for critical flows

### Archived (Not Deleted) 📦

Moved to `.claude/archive/`:
- `commands/create-specs.md`
- `commands/groundwork.md`
- `commands/create-tasks.md`
- `commands/implement.md`
- `commands/plan-spec.md`
- `constitution.md`
- `BDD-WORKFLOW.md`
- `agents/bdd-dev.md`

**Still available:**
- `/fix-bug` - Bug fix workflow (unchanged)
- `/create-policy` - Privacy policy generator (unchanged)

## Testing Strategy Shift

### Before: Test-First (TDD/BDD)

- Write tests BEFORE implementation
- Red-Green-Refactor cycle
- Formal scenarios drive tests
- Tests at all levels upfront

### After: Test-Verified (Pragmatic)

**Integration Tests (API) - ALWAYS:**
- Write AFTER API implementation
- Test via HTTP with Supertest
- Real test database
- Location: `modules/{domain}/tests/integration/{feature}.api.test.ts`
- Coverage: Happy path + key error cases

**Unit Tests - WHEN COMPLEX:**
- Write AFTER service implementation
- Only for complex business logic
- Location: `modules/{domain}/tests/unit/{service}.test.ts`

**Frontend Tests - AFTER STABLE:**
- Not upfront, only when feature is used
- Test critical interactions
- Location: `modules/{domain}/tests/{component}.test.tsx`

**E2E Tests - RARELY:**
- Only critical multi-step flows
- After feature complete
- Use Chrome DevTools MCP tools
- Location: `tests/e2e/`

## Migration Guide

### For Existing Features

**No action needed.** Existing code follows the same patterns.

### For New Features

**Old way:**
```bash
/create-specs "archive posts"
# Review spec, resolve [NEEDS CLARIFICATION] markers
/groundwork specs/posts/archive-posts.md
# Review groundwork
/clear
/implement specs/posts/archive-posts.md
```

**New way:**
```bash
/build "archive posts without deleting them"
# Review inline plan, answer 1-2 questions
# Feature complete in ~15-20 minutes
```

### Key Differences

| Aspect | Before | After |
|--------|--------|-------|
| **Command** | 4 commands | 1 command |
| **Sessions** | 3-4 with `/clear` | 1 session |
| **Planning** | Formal Gherkin | Inline brief |
| **Questions** | Resolve all ambiguities | 1-2 critical only |
| **Tests** | Before code (TDD) | After code (verify) |
| **Groundwork** | Separate phase | Inline when needed |
| **Documentation** | Specs + groundwork + tasks | None (code is doc) |
| **Time** | 30-45 min | 15-20 min |
| **Complexity** | High (gates, checklists) | Low (KISS/YAGNI) |

## Philosophy Shift

### From: Process Ensures Quality

- Formal specifications catch ambiguities
- Constitutional gates prevent mistakes
- Test-first ensures correctness
- Documentation tracks decisions

### To: Working Code Proves Quality

- Code demonstrates what was built
- Integration tests verify contracts
- Proven patterns prevent mistakes
- Fast iteration over heavy planning

## Success Criteria

The migration is successful when:

✅ `/build` command works end-to-end
✅ Features complete in ~15-20 minutes
✅ Inline planning shows and waits for approval
✅ No formal specs or documentation files created
✅ Integration tests written and pass
✅ Result<T> pattern used consistently
✅ Vertical slicing (API + UI together)
✅ Developer experience feels fast and pragmatic
✅ Code quality maintained through patterns
✅ Old commands archived (not lost)

## Trade-offs

### What We Gained 🎉

1. **Speed** - 4 phases → 1 command, 50% faster
2. **Simplicity** - No bureaucracy, no gates
3. **Developer Joy** - Build features, not documentation
4. **Flexibility** - Pragmatic choices over rigid rules
5. **Same Quality** - Patterns + integration tests ensure correctness

### What We Lost 🤔

1. **Formal Specifications** - No Gherkin scenarios
   - *Trade-off:* Inline plans sufficient for most features
2. **Upfront Test Design** - Tests after implementation
   - *Trade-off:* Integration tests still catch bugs effectively
3. **Constitutional Safeguards** - No compliance checks
   - *Trade-off:* Trust developers + proven patterns
4. **Separate Groundwork** - Schema built inline
   - *Trade-off:* Faster, schema evolves with feature
5. **Complexity Tracking** - No justified exceptions docs
   - *Trade-off:* If it's complex, simplify it instead

### What We Kept 💎

1. ✅ **Result<T>** - Explicit error handling
2. ✅ **Service Pattern** - Clean separation
3. ✅ **Vertical Slicing** - Ship end-to-end value
4. ✅ **Integration Tests** - Verify contracts
5. ✅ **Domain Modules** - Organized codebase
6. ✅ **Test Co-Location** - Tests with domain
7. ✅ **Proven Patterns** - withAuth, TanStack Query, Zod

## Using the New Workflow

### Quick Start

```bash
/build "add like button to posts"
```

**What happens:**
1. Shows inline plan (DB, API, UI, tests)
2. Asks 1-2 critical questions
3. Builds feature vertically (API + UI)
4. Writes integration tests
5. Formats and commits
6. **Done in ~15 minutes**

### Example Session

```
User: /build "archive posts without deleting them"

Claude:
## Building: Archive Posts

**Domain:** `modules/posts/`

**Database Changes:**
- Add `archivedAt: timestamp('archived_at')` to posts schema

**Backend:**
- Service: `postService.archivePost(postId, userId): Promise<Result<Post>>`
- Service: `postService.unarchivePost(postId, userId): Promise<Result<Post>>`
- API: `POST /api/posts/[id]/archive` (auth: yes)
- API: `POST /api/posts/[id]/unarchive` (auth: yes)
- Validation: Zod schema for post ID

**Frontend:**
- Hook: `useArchivePost()` - Archive post mutation
- Hook: `useUnarchivePost()` - Unarchive post mutation
- Component: Archive button on PostCard
- UI: Show archived badge, filter toggle

**Tests:**
- Location: `modules/posts/tests/integration/archive.api.test.ts`
- Coverage: Archive/unarchive via HTTP + database verification

**Critical Questions:**
1. Should archived posts be hidden from public lists by default? (yes/no)
2. Can users unarchive their own posts? (yes/no)

---
Proceed with implementation? (y/n)

User: 1. yes, 2. yes - go ahead

Claude:
[Implements database schema]
[Implements service methods]
[Implements API routes]
[Implements frontend hooks]
[Implements UI components]
[Writes integration tests]
[Runs tests - all pass]
[Formats code]
[Commits changes]

Done! Feature "Archive Posts" complete.
- Database: Added archivedAt field to posts
- Backend: 2 services, 2 API routes
- Frontend: 2 hooks, updated PostCard component
- Tests: 4 integration tests (all passing)
- Commit: feat(posts): add archive functionality
```

## Common Questions

### Q: What if I want formal specifications?

**A:** You can still write them yourself in `docs/` or use tools like Notion. The `/build` command focuses on implementation, not documentation.

### Q: What about complex features requiring planning?

**A:** The `/build` command includes a planning phase with user approval. For very complex features, you can:
1. Break into smaller features
2. Use `/build` iteratively
3. Write your own plan document first

### Q: Are tests really written after code?

**A:** Yes. Integration tests are written AFTER the API works to verify contracts. This is pragmatic - we verify the code works, not guess what it should do.

### Q: What about groundwork for shared infrastructure?

**A:** Build it inline when needed. The `/build` command handles database schema updates. If you need complex shared infrastructure, build it as a separate feature first.

### Q: Can I still use the old workflow?

**A:** The old commands are archived in `.claude/archive/` for reference, but they're not active. The `/build` command replaces them completely.

### Q: What if I disagree with this approach?

**A:** The old files are in `.claude/archive/` and can be restored. However, give `/build` a try - it's designed to be faster and more pragmatic while maintaining code quality.

## Resources

### New Documentation

- `.claude/CLAUDE.md` - Updated project guidelines
- `.claude/IMPLEMENTATION-PATTERNS.md` - Streamlined technical patterns
- `.claude/skills/build/SKILL.md` - Complete `/build` command workflow
- `.claude/WORKFLOW-MIGRATION.md` - This document

### Archived Documentation

- `.claude/archive/constitution.md` - Constitutional BDD principles
- `.claude/archive/BDD-WORKFLOW.md` - Old 4-phase workflow
- `.claude/archive/commands/` - Old command templates
- `.claude/archive/agents/bdd-dev.md` - BDD agent definition

### Reference Implementations

- `modules/posts/` - Example domain module
- `app/api/posts/` - Example API routes
- `lib/api/handlers.ts` - API handler utilities
- `lib/result.ts` - Result type definition
- `lib/errors.ts` - Error codes and status mapping

## Next Steps

1. **Try `/build`** on a simple feature to get familiar
2. **Review patterns** in `.claude/IMPLEMENTATION-PATTERNS.md`
3. **Check examples** in `modules/posts/` for reference
4. **Provide feedback** on what works and what doesn't

**The goal:** Fast, pragmatic development with proven patterns and integration tests.

---

**Last Updated:** February 4, 2026
**Migration Complete:** Constitutional BDD → Pragmatic /build