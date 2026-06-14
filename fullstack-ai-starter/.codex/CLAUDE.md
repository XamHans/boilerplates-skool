# Project Commands and Guidelines

## Constitutional BDD Workflow

This project uses a **constitutional BDD workflow** with architectural principles that prevent common failure modes. See `.claude/constitution.md` for the complete constitutional foundation.

### Workflow Commands

1. `/create-specs [idea]` - Generate Gherkin scenarios with quality gates and uncertainty markers
2. `/create-tasks [spec-path]` - Generate executable task list (optional)
3. `/groundwork [spec-path]` - Build shared infrastructure with constitutional gates (run /clear after)
4. `/plan-spec [spec-path]` - Create implementation plan (optional)
5. `/implement [spec-path]` - Implement scenarios one-by-one with constitutional principles (suggest /clear between)

### Constitutional Principles

All development MUST adhere to these principles from `.claude/constitution.md`:

1. **Simplicity First** - Minimal complexity, no future-proofing
2. **Anti-Abstraction** - Use frameworks (Next.js/Drizzle) directly, avoid wrappers
3. **Integration-First Testing** - Real databases, contract tests mandatory
4. **Test-First** - No code before tests (Red-Green-Refactor)
5. **Vertical Slicing** - End-to-end functionality (API + UI + tests) per scenario
6. **Specification Quality** - Mark ambiguities with `[NEEDS CLARIFICATION]`
7. **Complexity Tracking** - Document justified exceptions
8. **Context Management** - /clear between phases for AI performance

### Quality Gates

**Before `/implement`**:
- ✅ All `[NEEDS CLARIFICATION]` markers resolved
- ✅ Spec focuses on WHAT/WHY, not HOW
- ✅ Scenarios are testable, independent, precise, minimal

**During `/groundwork`**:
- ✅ Simplicity Gate: Minimal complexity, no future-proofing
- ✅ Anti-Abstraction Gate: Using frameworks directly
- ✅ Groundwork Gate: Justified upfront infrastructure

**During `/implement`**:
- ✅ Test-First: Write tests before code
- ✅ Vertical Slicing: API + UI + tests together
- ✅ No guessing: Stop and ask for clarification if ambiguous

### BDD Best Practices

- **ALWAYS** run `/groundwork` before implementing scenarios with database changes
- **Use /clear** between workflow phases to keep context focused and improve performance
- **Implement one scenario at a time** for better code quality and easier review
- **Groundwork = shared infrastructure only** - NO business logic, NO scenario-specific code
- **Each scenario gets its own branch**: `feature/{domain}/{feature}/{scenario-slug}`
- **Review specs before implementing** to ensure scenarios pass quality gates
- **Mark ambiguities** with `[NEEDS CLARIFICATION]` instead of guessing
- **Document complexity** when violating constitutional principles

### When to Skip Groundwork

- Simple features with no database changes
- Single-file utilities or helpers
- When prototyping and speed matters most

## Testing Commands

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
```

## Code Style

- Use TypeScript strict mode
- Prefer functional components with hooks
- Co-locate tests with the code they test in `modules/{domain}/tests/`
- Follow testing pyramid: Many unit tests, some API tests, few E2E tests
- Use Drizzle ORM for database operations
- Use better-auth for authentication

## Module Structure

```
modules/
└── {domain}/
    ├── services/          # Business logic
    ├── types/             # TypeScript types
    ├── schema.ts          # Database schema (Drizzle)
    └── tests/
        ├── unit/          # Fast, isolated tests (Vitest)
        └── integration/   # API tests (Vitest + Supertest)
```

## Workflow Patterns

### After Groundwork
```bash
/groundwork specs/posts/archive-posts.md
# Review changes, then:
/clear
/implement specs/posts/archive-posts.md
```

### Between Scenarios
```bash
# After completing scenario 1:
/clear
# Then implement scenario 2 with fresh context:
/implement specs/posts/archive-posts.md --scenario 2
```

## Important Notes

- **Context management is critical** - Use /clear frequently
- **Test-first development** - Write failing tests before implementation (Article IV)
- **Vertical slicing** - Each scenario should deliver end-to-end functionality (API + UI) (Article VIII)
- **YAGNI principle** - Only build what's needed for current scenarios (Article I)
- **Documentation** - Update GROUNDWORK.md and spec files as you go
- **Uncertainty handling** - Mark ambiguities with `[NEEDS CLARIFICATION]` instead of guessing (Article VI)
- **Constitutional compliance** - Check gates and document justified exceptions
- **Bidirectional feedback** - Update specs with production learnings (Article XI)

## Key Resources

- `.claude/constitution.md` - Architectural principles and phase gates
- `.claude/BDD-WORKFLOW.md` - Complete workflow guide with constitutional BDD details
- `.claude/commands/` - Command templates with quality constraints
