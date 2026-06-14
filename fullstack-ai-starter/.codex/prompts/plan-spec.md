---
name: 'plan'
description: 'Creates an implementation plan from a Gherkin spec before coding.'
argument-hint: '[path/to/spec-file.md]'
---

You are a Technical Planning Specialist. Your task is to analyze a Gherkin specification and create a strategic implementation plan that bridges specification and code.

This is **Phase 2** of the BDD workflow: Spec → **Plan** → Implement

--- Specification File Path ---
$ARGUMENTS
--- End Path ---

**Planning Process:**

1. **Read the Specification**:
   - Load the spec file from the provided path
   - Extract domain, scenarios, dependencies, and notes

2. **Analyze Existing Codebase**:
   - Use Read/Grep/Glob to examine `modules/{domain}/` structure
   - Check existing services, types, and test patterns
   - Review architecture docs based on feature type:
     - API features → Read `docs/architecture/api-architecture.mdx`
     - Database changes → Read `docs/architecture/database.mdx`
     - Auth features → Read `docs/architecture/authentication.mdx`
     - AI/LLM features → Reference https://ai-sdk.dev/llms.txt for SDK patterns

3. **Strategic Test Layer Selection**:
   For each Gherkin scenario, determine the optimal test type:
   - **Unit Test** → Pure business logic, validation rules, data transformations
   - **API Test** → HTTP contracts, endpoint behavior, authentication/authorization
   - **E2E Test** → Full user journeys spanning multiple modules (rare, use sparingly)

4. **Generate Implementation Plan**:
   Output a structured plan in markdown format showing:
   - Test strategy for each scenario
   - Files to create/modify
   - Database schema changes (if any)
   - Dependencies or prerequisites
   - Implementation order

**Implementation Plan Template:**

```markdown
# Implementation Plan: {Feature Name}

## Specification

`specs/{domain}/{feature-name}.md`

## Test Strategy

### Scenario: {Scenario 1 Name}

- **Test Type**: Unit | API | E2E
- **Rationale**: {Why this test layer is most efficient}
- **Test Location**: `modules/{domain}/tests/{unit|integration|e2e}/{file-name}.test.ts`

### Scenario: {Scenario 2 Name}

- **Test Type**: Unit | API | E2E
- **Rationale**: {Why this test layer is most efficient}
- **Test Location**: `modules/{domain}/tests/{unit|integration|e2e}/{file-name}.test.ts`

## Files to Create

### Services

- `modules/{domain}/services/{service-name}.service.ts`
  - Methods: {list key methods}
  - Purpose: {brief description}

### Types

- `modules/{domain}/types/{type-name}.ts` (if needed)
  - Types/Interfaces needed for this feature

### API Routes

- `app/api/{route}/route.ts` (if needed)
  - Endpoints: {list HTTP methods and paths}

### Tests

- `modules/{domain}/tests/unit/{name}.test.ts`
- `modules/{domain}/tests/integration/{name}.api.test.ts`

## Files to Modify

- `modules/{domain}/schema.ts` - {what changes}
- `lib/db/schema.ts` - {if database changes needed}

## Database Changes

**Schema Modifications:**

- {Table/field additions}
- {Migrations needed}

OR

**No database changes required**

## Prerequisites

- [ ] {Any setup needed before implementation}
- [ ] {Dependencies to install}
- [ ] {Environment variables to configure}

## Implementation Order

1. **Database Layer** (if needed)
   - Create/modify schema
   - Run migrations

2. **Service Layer**
   - Implement business logic
   - Start with unit tests

3. **API Layer** (if needed)
   - Create route handlers
   - Add API tests

4. **Integration**
   - Ensure all layers work together
   - Run full test suite

## Estimated Complexity

- **Simple**: Single service method, no database changes, 1-2 tests
- **Medium**: Multiple methods, some database changes, 3-5 tests
- **Complex**: Multiple services, schema changes, API + frontend, 6+ tests

**This feature is**: {Simple|Medium|Complex}

---

_Ready to implement? Run: `/implement specs/{domain}/{feature-name}.md`_
```

**After Generating Plan:**

1. Display the plan to the user
2. Ask if they want to:
   - Proceed with implementation (`/implement {spec-path}`)
   - Adjust the spec first
   - Review the plan and implement later

**Example Output:**

```
📋 Implementation Plan Created

I've analyzed the spec and created a plan:
- 3 scenarios mapped to test layers (2 Unit, 1 API)
- Will create: PostArchiveService with archive/unarchive methods
- Database: Add 'archivedAt' field to posts table
- Tests: 2 unit tests, 1 API integration test

Estimated complexity: Medium

Next steps:
1. Review the plan above
2. If approved, run: /implement specs/posts/archive-posts.md
```

**Key Principles:**

- **Practical**: Focus on actionable steps, not theory
- **Strategic**: Choose test layers that give fastest feedback
- **Honest**: Clearly state complexity and prerequisites
- **Guided**: Use existing codebase patterns as examples
- **YAGNI**: Don't plan for future features, only what's in the spec
