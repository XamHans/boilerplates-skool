# BDD Workflow Guide

This project uses a **4-phase BDD workflow** to guide feature development from idea to implementation.

## 🎯 The Four Phases

```
User Idea → [Phase 1: Spec] → [Phase 2: Groundwork] → [Phase 3: Implement] → [Phase 4: Polish] → Working Feature
                                                              ↑_______________|
                                                              (Loop per scenario)
```

### Phase 1: Create Specification (Required)
**Command**: `/create-specs [your feature idea]`

**What it does**:
- Takes your rough idea and creates structured Gherkin scenarios
- Generates a lightweight spec file in `specs/{domain}/{feature-name}.md`
- Focuses on behavior (Given/When/Then), not implementation details
- Follows YAGNI: minimal, actionable, testable scenarios

**Output**:
- A spec file with 2-4 Gherkin scenarios covering happy path and key edge cases

**Example**:
```bash
/create-specs "Add ability to archive posts without deleting them"
```

Creates: `specs/posts/archive-posts.md` with scenarios like:
- Archive a published post
- Unarchive a post
- Handle errors (archive non-existent post)

---

### Phase 2: Establish Groundwork (Recommended)
**Command**: `/groundwork specs/{domain}/{feature-name}.md`

**What it does**:
- Analyzes ALL scenarios to identify shared infrastructure
- Creates database schema, types, and service shells
- Sets up test infrastructure
- Registers services in dependency injection
- Documents what foundation was built

**Output**:
- Database tables and migrations
- Type definitions for domain entities
- Service classes with empty method stubs (no logic)
- Test utilities and helpers
- Groundwork documentation file

**When to use**:
- For any feature with database changes (recommended)
- When multiple scenarios share infrastructure
- For complex features touching multiple layers

**When to skip**:
- Simple features with no database changes
- Single-file utilities or helpers
- When prototyping and speed matters most

**Example**:
```bash
/groundwork specs/workflow/spec-kanban-board.md
```

Creates:
- `modules/workflow/schema.ts` (specs table)
- `modules/workflow/types.ts` (Spec, WorkflowStage types)
- `modules/workflow/services/*.service.ts` (empty shells)
- Test infrastructure setup
- Commits as: "chore(workflow): establish groundwork for spec-kanban-board"

**After groundwork**: Run `/clear` to reset context, then start implementing scenarios.

---

### Phase 3: Create Implementation Plan (Optional)
**Command**: `/plan-spec specs/{domain}/{feature-name}.md`

**What it does**:
- Analyzes the Gherkin spec and existing codebase
- Strategically selects test layers (Unit/API/E2E) for each scenario
- Identifies files to create/modify
- Estimates complexity and implementation order
- Provides a roadmap before writing code

**Output**:
- A detailed implementation plan showing test strategy, file changes, and prerequisites

**When to use**:
- For complex features that touch multiple parts of the system
- When you want to review the approach before implementation
- To understand impact and effort required

**When to skip**:
- For simple features with obvious implementation
- When you trust the BDD agent to make good decisions
- When you want to move fast (go directly to Phase 3)

**Example**:
```bash
/plan-spec specs/posts/archive-posts.md
```

Shows:
- Archive scenario → Unit test (service logic)
- API endpoint scenario → API integration test
- Files to create/modify in `modules/posts/`
- Database schema change (add `archivedAt` field)

---

### Phase 4: Implement Scenarios One-by-One (Required)
**Command**: `/implement specs/{domain}/{feature-name}.md`

**What it does**:
- Shows list of scenarios with completion status
- Prompts you to select ONE scenario
- Creates scenario-specific branch
- Implements ONLY that scenario (API + UI)
- Runs quality checks
- Updates spec with completion status
- Prompts to continue with next scenario OR clear context

**What changed**:
- ✨ Now implements ONE scenario at a time (not all at once)
- ✨ Prompts to /clear context between scenarios
- ✨ Better progress tracking in spec file
- ✨ Smaller, focused implementations
- ✨ Uses `Result<T>` type for explicit error handling (not throwing)
- ✨ TanStack Query hooks for client-side data fetching
- ✨ Zod schemas for request validation

**Output per scenario**:
- Scenario-specific branch: `feature/{domain}/{feature}/{scenario-slug}`
- API routes for that scenario
- UI components for that scenario
- Tests for that scenario
- Updated spec file with completion status

**What the bdd-dev agent does**:
1. Analyzes the selected Gherkin scenario
2. Chooses optimal test layer (Unit/API/E2E)
3. Writes failing test first (Red)
4. Implements minimal code to pass (Green)
5. Refactors while keeping tests green
6. Co-locates tests within `modules/{domain}/tests/`

**Example**:
```bash
# First scenario
/implement specs/workflow/spec-kanban-board.md
# Select scenario 1, implement, then /clear

# Second scenario (fresh context)
/implement specs/workflow/spec-kanban-board.md --scenario 2
# Implement, then /clear

# Continue until all scenarios done...
```

Creates (per scenario):
- `app/api/workflow/specs/route.ts` (API for that scenario)
- `app/(main)/workflow/page.tsx` (UI for that scenario)
- `modules/workflow/tests/integration/*.api.test.ts` (tests)
- Scenario-specific branch: `feature/workflow/kanban/view-by-stage`

---

## 🏗️ Architecture Overview

### Module Structure
```
modules/
└── {domain}/
    ├── services/          # Business logic
    ├── types/             # TypeScript types
    ├── schema.ts          # Database schema
    └── tests/
        ├── unit/          # Fast, isolated tests
        └── integration/   # API tests with Supertest
```

### Spec Structure
```
specs/
└── {domain}/
    └── {feature-name}.md  # Gherkin scenarios
```

### Testing Pyramid
```
        E2E (Few)
      ┌─────────┐
     │  Full    │
    │  User     │
   │  Journeys  │
  └────────────┘

     API Tests (Some)
  ┌──────────────────┐
 │  HTTP Contracts   │
│  Route Handlers    │
└────────────────────┘

      Unit Tests (Many)
  ┌────────────────────────┐
 │  Business Logic         │
│  Validation, Services    │
│  Fast, Isolated          │
└──────────────────────────┘
```

---

## 📋 Example Workflow

### Scenario: User wants to add post archiving

**Step 1: Create Spec**
```bash
/create-specs "Add ability to archive posts"
```

**Result**: `specs/posts/archive-posts.md` created with 4 scenarios

**Step 2a: Review Spec (Manual)**
- Read the generated scenarios
- Adjust if needed
- Confirm they capture the behavior

**Step 2b: Create Plan (Optional)**
```bash
/plan-spec specs/posts/archive-posts.md
```

**Result**: Implementation plan showing test strategy and file changes

**Step 3: Implement**
```bash
/implement specs/posts/archive-posts.md
```

**Result**:
- Feature implemented on `feature/posts/archive-posts` branch
- All tests passing ✅
- Code formatted and linted ✅
- Ready for review

**Step 4: Review and Merge**
```bash
git diff main
# Review changes, then merge when ready
```

---

## 🎨 Key Principles

### YAGNI (You Aren't Gonna Need It)
- Write only what's needed for the current scenarios
- Don't over-engineer or plan for future features
- Keep specs focused and minimal

### Vibe Coding
- Guided by existing codebase patterns
- Uses MCP tools to discover conventions
- Adapts to project structure, not rigid templates

### Test-First BDD
- Red: Write failing test that captures Gherkin scenario
- Green: Write minimal code to make test pass
- Refactor: Clean up while keeping tests green

### Strategic Test Selection
- **Unit** for business logic and validation
- **API** for HTTP contracts and endpoints
- **E2E** only for critical multi-module user journeys

### Co-located Tests
- Tests live with the code they test
- Improves discoverability and maintainability
- Makes refactoring safer

---

## 🚀 Quick Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/create-specs [idea]` | Generate Gherkin scenarios with quality gates | Always (Phase 1) |
| `/create-tasks [spec-path]` | Generate executable task list from spec | Optional, to see task breakdown |
| `/groundwork [spec-path]` | Build shared infrastructure with constitutional gates | Recommended for features with DB changes (Phase 2) |
| `/plan-spec [spec-path]` | Create implementation plan | Optional, for complex features (Phase 3) |
| `/implement [spec-path]` | Implement scenarios one-by-one with constitutional principles | Always (Phase 4) |

---

## 💡 Tips

1. **Start small**: Write 2-3 scenarios, not 10. Add more later if needed.

2. **Use groundwork for shared infrastructure**: Prevents rebuilding foundation per scenario.

3. **Clear context between scenarios**: Keeps AI focused and performant - use `/clear`.

4. **One scenario at a time**: Smaller increments = better code quality.

5. **Review groundwork before scenarios**: Ensures foundation is correct.

6. **Skip groundwork for simple features**: Don't over-engineer.

7. **Skip planning for simple features**: Go directly from spec to groundwork to implement.

8. **Use planning for complex features**: Understand impact before writing code.

9. **Trust the BDD agent**: It will choose appropriate test layers and patterns.

10. **Document as you go**: GROUNDWORK.md and spec status tracking helps.

11. **Branch per scenario**: Easy to review, easy to rollback.

---

## 📚 Further Reading

- `.claude/IMPLEMENTATION-PATTERNS.md` - **CRITICAL**: Technical patterns (Result<T>, handlers, validation, TanStack Query)
- `.claude/constitution.md` - Architectural principles and phase gates
- `.claude/commands/create-specs.md` - Spec generation with SDD quality constraints
- `.claude/commands/create-tasks.md` - Task decomposition with parallelization
- `.claude/commands/groundwork.md` - Infrastructure setup with constitutional gates
- `.claude/commands/implement.md` - Scenario implementation with uncertainty handling
- `docs/api-architecture.mdx` - API design patterns with Result<T> and Zod validation
- `docs/architecture/testing-strategy.mdx` - Testing patterns and philosophy
- `docs/architecture/code-architecture.mdx` - Module structure and organization
- `.claude/agents/bdd-dev.md` - BDD agent implementation details

---

## 🆕 What's New: Constitutional BDD

This workflow now includes a **constitutional foundation** inspired by Specification-Driven Development (SDD) that systematically prevents common failure modes:

### Constitutional Principles

The `.claude/constitution.md` defines 11 immutable articles that govern development:

1. **Simplicity First** - Minimal complexity, no future-proofing
2. **Anti-Abstraction** - Use frameworks directly, avoid wrappers
3. **Integration-First Testing** - Real databases, contract tests mandatory
4. **Test-First Imperative** - No code before tests (Red-Green-Refactor)
5. **Module Structure** - Domain-driven organization
6. **Specification Quality** - Explicit uncertainties, what/how separation
7. **Complexity Tracking** - Document justified exceptions
8. **Vertical Slicing** - End-to-end functionality per scenario
9. **Groundwork Separation** - Infrastructure only, no business logic
10. **Context Management** - /clear between phases for AI performance
11. **Bidirectional Feedback** - Production learnings update specs

### Quality Gates

Each workflow phase now includes **phase gates** that check constitutional compliance:

**In `/create-specs`**:
- ✅ Requirement Completeness Checklist
- ✅ What vs. How Separation
- ✅ Scenario Quality (testable, independent, precise, minimal)
- ✅ YAGNI Compliance
- ✅ Explicit `[NEEDS CLARIFICATION]` markers for ambiguities

**In `/groundwork`**:
- ✅ Simplicity Gate (minimal complexity, no future-proofing)
- ✅ Anti-Abstraction Gate (frameworks directly, single representation)
- ✅ Groundwork Gate (justified upfront setup)
- ✅ Blocks if spec has unresolved clarifications

**In `/implement`**:
- ✅ Blocks if `[NEEDS CLARIFICATION]` markers exist
- ✅ Constitutional principles passed to bdd-dev agent
- ✅ Vertical slicing enforced (API + UI + tests per scenario)
- ✅ Test-first imperative (Red-Green-Refactor)

### New Features

1. **`/create-tasks` Command** - Generates executable task lists with:
   - Tasks derived from Gherkin scenarios
   - Parallelization markers `[P]` for independent work
   - Constitutional gate checks
   - Complexity tracking
   - Dependency graphs

2. **Uncertainty Handling** - Prevents guessing:
   - Specs mark ambiguities with `[NEEDS CLARIFICATION]`
   - Implementation blocked until resolved
   - Forces clarifying questions instead of assumptions

3. **Complexity Accountability**:
   - Justified exceptions documented in specs
   - Tracks when/why constitutional principles violated
   - Creates technical debt visibility

4. **Production Learnings** - Bidirectional feedback:
   - Spec files track post-deployment insights
   - Production issues → new edge case scenarios
   - Performance metrics → non-functional requirements

### Benefits

✅ **Systematic quality** - Gates prevent common mistakes
✅ **Less guessing** - Explicit uncertainty markers
✅ **Consistent architecture** - Constitutional principles enforced
✅ **Better AI output** - Template constraints guide LLM behavior
✅ **Trackable complexity** - Justified exceptions documented
✅ **Continuous improvement** - Production feedback loop

### Migration Guide

Existing specs work as-is. To adopt constitutional BDD:

1. **Read the constitution**: `.claude/constitution.md`
2. **Use enhanced commands**: Updated `/create-specs`, `/groundwork`, `/implement` now include gates
3. **Optional**: Add `[NEEDS CLARIFICATION]` markers to existing specs
4. **Optional**: Use `/create-tasks` for task breakdown
5. **Optional**: Add "Production Learnings" sections to deployed features
