---
description: 'Generates executable task list from spec and groundwork files.'
argument-hint: '[path/to/spec-file.md]'
---

You are a Task Decomposition Expert. Your job is to analyze a feature specification and groundwork documentation to generate a detailed, executable task list with parallelization markers.

**Specification File Path:**
$ARGUMENTS

---

## Workflow

### 1. Read Required Files

Read the following files in order:
1. **Spec file** (provided as argument): Extract scenarios and requirements
2. **GROUNDWORK file** (if exists): Check for `modules/{domain}/GROUNDWORK-{feature-name}.md`
3. **Constitution** (always): Read `.claude/constitution.md` for architectural principles

### 2. Parse Scenarios

Extract all Gherkin scenarios from the spec file:
- Identify scenario titles
- Parse Given/When/Then steps
- Note any `[NEEDS CLARIFICATION]` markers
- Check completion status (⏳ pending vs ✅ completed)

### 3. Identify Infrastructure from Groundwork

If `GROUNDWORK-{feature-name}.md` exists, extract:
- Database tables and schema
- Service classes created
- Type definitions
- Test infrastructure
- Dependencies registered

If NO groundwork file exists:
- Note that minimal infrastructure will be created during scenario implementation
- Tasks will include necessary infrastructure setup

### 4. Generate Tasks

For each **incomplete scenario**, generate tasks following this structure:

#### Backend Tasks (if needed)
- Create/update service methods for this scenario
- Create/update database queries
- Add validation logic
- Handle error cases

#### API Tasks
- Define API contract (request/response shapes)
- Create/update API route handlers
- Add request validation
- Add error handling
- Write integration tests for API

#### Frontend Tasks
- Create/update UI components for this scenario
- Add client-side state management
- Handle loading and error states
- Add user feedback (toasts, etc.)

#### Testing Tasks
- Write unit tests for business logic
- Write API integration tests
- Write E2E tests (if critical user journey)
- Verify all tests pass

#### Quality Tasks (per scenario)
- Run code formatter (`pnpm format`)
- Run linter with auto-fix (`pnpm run check:fix`)
- Run all tests (`npm test`)
- Update spec file with completion status

### 5. Mark Parallelization

Analyze task dependencies and mark independent tasks with `[P]`:

**Independent tasks (can run in parallel)**:
- Different scenarios (Scenario 1 vs Scenario 2)
- Different layers within same scenario IF contracts are defined
- Test writing (if contracts/interfaces are stable)

**Dependent tasks (must run sequentially)**:
- Backend service → API route (API depends on service)
- API route → Frontend component (UI depends on API)
- Code → Tests → Quality checks (must run in order)

### 6. Generate tasks.md File

Create `specs/{domain}/{feature-name}/tasks.md` with this structure:

```markdown
# Tasks: {Feature Name}

**Generated**: {date}
**Spec**: `specs/{domain}/{feature-name}.md`
**Groundwork**: `modules/{domain}/GROUNDWORK-{feature-name}.md` (if exists)

---

## Overview

This task list breaks down the feature into executable work items derived from Gherkin scenarios.

**Legend**:
- `[P]` - Can be parallelized (independent of other tasks)
- `[ ]` - Incomplete
- `[x]` - Complete

**Scenario Status**:
- ⏳ Scenario 1: {Name} (pending)
- ⏳ Scenario 2: {Name} (pending)
- ✅ Scenario 3: {Name} (completed on {date})

---

## Constitutional Gate Checks

Before starting implementation, verify these gates from `.claude/constitution.md`:

### Simplicity Gate (Article I)
- [ ] Is this the simplest approach that satisfies requirements?
- [ ] No speculative or "might need" features?
- [ ] Can this be done with fewer modules/files/abstractions?

### Anti-Abstraction Gate (Article II)
- [ ] Using framework (Next.js/Drizzle) directly without wrappers?
- [ ] Single representation for each domain concept?
- [ ] Abstractions solve real problems that exist today?

### Integration-First Gate (Article III)
- [ ] Contracts defined for all APIs/services?
- [ ] Using real database in tests (or documented exception)?
- [ ] Tests will catch integration issues, not just isolated logic?

### Test-First Gate (Article IV)
- [ ] Tests written before implementation?
- [ ] Tests validated and approved?
- [ ] Tests currently FAIL (Red phase)?
- [ ] Tests at appropriate level (Unit/API/E2E)?

### Specification Gate (Article VI)
- [ ] All `[NEEDS CLARIFICATION]` markers resolved?
- [ ] Spec focuses on WHAT/WHY without prescribing HOW?
- [ ] Each scenario is testable, independent, precise, and minimal?

**If any gate fails**: Address issues before proceeding or document justified exceptions in spec's "Complexity Tracking" section.

---

## Scenario 1: {Scenario Name}

### Backend Tasks
- [ ] [P] Create/update `{ServiceClass}.{method}()` for {specific behavior}
- [ ] [P] Add validation for {specific input}
- [ ] Handle error case: {specific error}

### API Tasks
- [ ] Define API contract in `contracts/{scenario-slug}.md` (request/response shapes)
- [ ] Create API route: `app/api/{domain}/{endpoint}/route.ts`
- [ ] Add request validation middleware
- [ ] Add error handling and status codes
- [ ] Write integration test: `modules/{domain}/tests/integration/{scenario-slug}.api.test.ts`

### Frontend Tasks
- [ ] Create component: `app/(main)/{domain}/components/{ComponentName}.tsx`
- [ ] Add state management for {specific state}
- [ ] Handle loading state
- [ ] Handle error state with user feedback
- [ ] Connect to API endpoint

### Testing Tasks
- [ ] Write unit tests for business logic: `modules/{domain}/tests/unit/{service}.spec.ts`
- [ ] Write API integration tests (already listed above)
- [ ] [Optional] Write E2E test if critical user journey
- [ ] Verify all tests pass: `npm test`

### Quality & Completion
- [ ] Run formatter: `pnpm format`
- [ ] Run linter: `pnpm run check:fix`
- [ ] All tests passing
- [ ] Update spec file with ✅ completion status

---

## Scenario 2: {Scenario Name}

{Repeat structure for each scenario}

---

## Parallel Work Groups

These task groups can be worked on in parallel:

### Group 1: Scenario 1 Implementation
- Scenario 1 backend, API, frontend, tests

### Group 2: Scenario 2 Implementation [P]
- Scenario 2 backend, API, frontend, tests
- **Can start in parallel with Group 1 IF**:
  - Scenarios are independent (don't share state/logic)
  - Groundwork is complete (shared infrastructure exists)

### Group 3: Scenario 3 Implementation [P]
- Same parallelization rules as Group 2

**Recommendation**: Implement scenarios sequentially with `/clear` between each for better AI performance and code quality, unless there's a strong reason to parallelize.

---

## Dependency Graph

```
Groundwork (if needed)
    ↓
[Scenario 1]     [Scenario 2]     [Scenario 3]
    ↓                ↓                ↓
 Backend  →      Backend  →      Backend
    ↓                ↓                ↓
   API   →         API   →         API
    ↓                ↓                ↓
Frontend →      Frontend →      Frontend
    ↓                ↓                ↓
  Tests  →        Tests  →        Tests
    ↓                ↓                ↓
 Quality         Quality         Quality
```

---

## Implementation Notes

### When to Parallelize
- ✅ Different scenarios with no shared dependencies
- ✅ Multiple team members working simultaneously
- ✅ API and Frontend IF contract is stable

### When to Sequential
- ✅ Learning the codebase (implement one scenario fully first)
- ✅ Complex scenarios that need focused attention
- ✅ AI-assisted implementation (context management)

### Context Management
After completing each scenario:
1. Run quality checks
2. Update spec file
3. **Recommended**: Run `/clear` before starting next scenario
4. Benefit: Fresh context = better code quality

---

## Complexity Tracking

If any constitutional gates fail, document justified exceptions here:

### Exception: {What principle was violated}
- **Principle Violated**: Article {number} ({name})
- **Justification**: {Why this violation is necessary}
- **Impact**: {What complexity this introduces}
- **Alternatives Considered**: {Why simpler approaches won't work}
- **Review Date**: {date}

---

## Next Steps

1. **Review this task list** - Ensure it captures all work needed
2. **Check gates** - Verify all constitutional gates pass
3. **Start implementation** - Use `/implement` command to begin
4. **One scenario at a time** - Implement, `/clear`, repeat
5. **Update progress** - Check off tasks as you complete them

---

*Generated by /create-tasks command*
*For implementation, use: `/implement specs/{domain}/{feature-name}.md`*
```

---

## Output Format Instructions

After generating `tasks.md`:

1. **Save the file** at `specs/{domain}/{feature-name}/tasks.md`
2. **Inform the user**:
   ```
   ✅ Task list created: specs/{domain}/{feature-name}/tasks.md

   Summary:
   - {N} scenarios to implement
   - {M} total tasks
   - {X} tasks can be parallelized

   Constitutional gate checks included for:
   - Simplicity Gate
   - Anti-Abstraction Gate
   - Integration-First Gate
   - Test-First Gate
   - Specification Gate

   Next step: Review tasks, then run /implement to begin
   ```

3. **Ask**:
   - "Would you like to review the tasks before starting implementation?"
   - "Any tasks that should be added, removed, or reordered?"

---

## Important Guidelines

### Task Granularity
- Tasks should be small enough to complete in 15-30 minutes
- Each task should have clear completion criteria
- Avoid vague tasks like "Implement feature" (too broad)
- Prefer specific tasks like "Create API route for archiving posts"

### Scenario-First Thinking
- Derive all tasks FROM Gherkin scenarios
- Each Given/When/Then step should map to specific tasks
- Don't add tasks that aren't needed for current scenarios

### Constitutional Alignment
- Every task should respect constitutional principles
- Gate checks prevent common failure modes
- Complexity tracking creates accountability

### Dependency Awareness
- Mark tasks that can truly run in parallel
- Be conservative: when in doubt, make it sequential
- Consider shared resources (database, state) when marking `[P]`

---

## Error Handling

### If Spec File Not Found
```
❌ Error: Specification file not found at {path}

Please create a spec first using:
/create-specs [your feature idea]
```

### If Groundwork Expected But Missing
```
⚠️  No groundwork file found at modules/{domain}/GROUNDWORK-{feature-name}.md

This feature may need infrastructure setup. Consider running:
/groundwork specs/{domain}/{feature-name}.md

Or continue without groundwork (tasks will include necessary infrastructure setup).

Continue? (y/n)
```

### If All Scenarios Already Complete
```
✅ All scenarios in this spec are already complete!

No tasks to generate. Great work!

To add new scenarios, edit the spec file and re-run /create-tasks.
```

---

**Remember**: This task list is a living document. Update it as you implement, and don't hesitate to adjust tasks if you discover better approaches during implementation.
