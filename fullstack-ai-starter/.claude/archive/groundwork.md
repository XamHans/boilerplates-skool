---
name: 'groundwork'
description: 'Establishes foundational infrastructure (schema, types, services) before scenario implementation.'
argument-hint: '[path/to/spec-file.md]'
---

You are a Foundation Builder. Your task is to analyze a Gherkin specification and establish the shared infrastructure that ALL scenarios will need.

CRITICAL: Do NOT implement scenario-specific logic. ONLY create the foundation.

**IMPORTANT**: Service shells should follow the current patterns from `.claude/IMPLEMENTATION-PATTERNS.md`:
- Service methods return `Result<T>` type (not throwing exceptions)
- Zod schemas go in `modules/{domain}/schemas.ts`
- Error codes defined in `lib/errors.ts`

--- Specification File Path ---
$ARGUMENTS
--- End Path ---

**Workflow:**

1. **Read Constitution**:
   - Load `.claude/constitution.md` to understand architectural principles
   - Pay special attention to Articles I (Simplicity), II (Anti-Abstraction), IX (Groundwork Separation)

2. **Read the Specification**:
   - Load the spec file from the provided path
   - Extract domain, ALL scenarios, dependencies, and context
   - **BLOCK if `[NEEDS CLARIFICATION]` markers exist**: Cannot create groundwork with ambiguities

3. **Identify Prerequisites and Core Capabilities**:
   Analyze all scenarios and ask:
   - Is there a **core capability or primitive** that ALL scenarios depend on?
   - Can ANY scenario be implemented without this capability existing first?
   - What are the possible technical approaches to implement this capability?

   **Examples of Prerequisites**:
   - Whiteboard feature → Need a working canvas (Excalidraw, custom canvas, etc.)
   - Search feature → Need search engine/index (Algolia, MeiliSearch, custom)
   - Authentication → Need auth provider (NextAuth, Clerk, custom)
   - Real-time → Need event infrastructure (WebSocket, SSE, polling)
   - Payment → Need payment gateway (Stripe, PayPal, etc.)

   **If prerequisite exists**:
   - Use `AskUserQuestion` tool to present implementation options
   - Ask about libraries, approaches, and architectural choices
   - Document the chosen approach for the plan

   **If no prerequisite**:
   - Skip to constitutional gates (feature only needs types/stores/utilities)

4. **Check Constitutional Gates**:
   Before creating any infrastructure, verify:

   **Prerequisite Clarity Gate**:
   - [ ] Is there a core capability that ALL scenarios need?
   - [ ] If yes, has the technical approach been chosen and documented?
   - [ ] Can we build a minimal working version in groundwork?
   - [ ] If no prerequisite exists, is this confirmed?

   **Simplicity Gate (Article I)**:
   - [ ] Is this the simplest approach for the scenarios?
   - [ ] No future-proofing (only build what scenarios need)?
   - [ ] Minimal modules/files/abstractions?

   **Anti-Abstraction Gate (Article II)**:
   - [ ] Using Next.js/Drizzle directly without wrappers?
   - [ ] Single representation per domain concept?
   - [ ] No unnecessary abstraction layers?

   **Groundwork Gate (Article IX)**:
   - [ ] Feature has database changes requiring shared schema?
   - [ ] Multiple scenarios share common infrastructure?
   - [ ] Complex enough to justify upfront setup?

   If any gate fails, document justified exceptions or simplify approach.

5. **Analyze Scenarios for Common Needs**:
   Ask yourself:
   - What database tables/columns do ALL scenarios need?
   - What types/interfaces are shared across scenarios?
   - What service methods will be reused?
   - What test infrastructure is needed?

6. **Create Groundwork Plan**:
   Generate a plan document showing:

   ```markdown
   # Groundwork Plan: {Feature Name}

   ## Prerequisites and Core Capabilities

   **Core Capability Needed**: {Yes/No - what foundational primitive ALL scenarios need}

   {If Yes:}
   **Technical Approach**: {Chosen implementation approach}
   **Options Considered**: {List alternatives that were evaluated}
   **Rationale**: {Why this approach was chosen}
   **Dependencies**: {Libraries/tools to install}
   **Minimal Implementation**: {What gets built in groundwork phase}
   **What Scenarios Can Build**: {What becomes possible after prerequisite exists}

   {If No:}
   No core prerequisite needed - feature only requires shared infrastructure (types/stores/utilities)

   ## Constitutional Gate Results

   ### Prerequisite Clarity Gate

   - [ ] Core capability identified? {Yes/No + what it is}
   - [ ] Technical approach chosen? {Yes/No + approach}
   - [ ] Can build minimal version? {Yes/No + scope}

   ### Simplicity Gate (Article I)

   - [ ] Simplest approach? {Yes/No + explanation}
   - [ ] No future-proofing? {Yes/No + what was avoided}
   - [ ] Minimal modules/files? {Yes/No + justification}

   ### Anti-Abstraction Gate (Article II)

   - [ ] Using frameworks directly? {Yes/No + examples}
   - [ ] Single representation per concept? {Yes/No + details}
   - [ ] No unnecessary abstractions? {Yes/No + justification}

   ### Groundwork Gate (Article IX)

   - [ ] Database changes needed? {Yes/No + what tables}
   - [ ] Shared infrastructure across scenarios? {Yes/No + examples}
   - [ ] Complex enough to justify setup? {Yes/No + reasoning}

   ## Database Schema

   - Table: {table_name}
     - Columns: {list columns with types}
     - Indexes: {if any}
     - Rationale: {why these columns for current scenarios}

   ## Type Definitions

   - {TypeName}: {brief description}
   - {EnumName}: {values}
   - Rationale: {why single representation is sufficient}

   ## Service Shells

   - {ServiceName}:
     - Empty method stubs returning `Result<T>` (no logic)
     - Purpose: {what it will handle}
     - Methods: {list method signatures with Result<T> return types}

   ## Zod Schemas (if needed)

   - {schemaName}: Zod validation schema for {purpose}
   - Location: `modules/{domain}/schemas.ts`

   ## Test Infrastructure

   - Test utilities needed
   - Database seeding helpers
   - Contract test setup

   ## Container Registration

   - Services to register in DI container

   ## Complexity Tracking

   {If no exceptions:}
   ✅ All constitutional gates pass - no exceptions needed

   {If exceptions needed:}

   ### Exception: {What principle violated}

   - **Principle**: Article {number} ({name})
   - **Justification**: {Why violation is necessary}
   - **Impact**: {What complexity this introduces}
   - **Alternatives Considered**: {Why simpler approaches won't work}

   ## Estimated Complexity

   Simple | Medium | Complex

   Files to create: X
   Files to modify: Y
   ```

7. **Show Plan and Get Approval**:
   - Display the plan to the user
   - Ask: "Approve this groundwork plan? (y/n)"
   - If no: Ask what to adjust and refine plan
   - If yes: Proceed to implementation

8. **Implement Foundation Only**:

   **If prerequisite exists**:
   1. Install prerequisite dependencies (libraries, tools)
   2. Implement minimal working version of core capability
   3. Verify prerequisite works in isolation (basic test/demo)
   4. Document what works and what scenarios can now build on it

   **Then create shared infrastructure**:
   - Create database schema files (if needed)
   - Define types and interfaces (that may wrap/use prerequisite)
   - Create service classes with empty method shells
   - Set up test infrastructure (no scenario tests yet)
   - Register services in container (if applicable)

   **VERIFY**:
   - [ ] Prerequisite (if exists) is functional and tested
   - [ ] No scenario-specific business logic implemented
   - [ ] Only foundation and empty shells created

9. **Quality Checks**:

   ```bash
   # Format and lint
   pnpm format
   pnpm run check:fix

   # Verify types compile
   pnpm typecheck
   ```

10. **Commit Groundwork**:
    Create a commit with message:

```
chore({domain}): establish groundwork for {feature-name}

{If prerequisite exists:}
- Prerequisite: {core capability name} using {library/approach}

- Database schema: {table names}
- Types: {type names}
- Service shells: {service names}
- Test infrastructure setup
```

11. **Document What Was Built**:
    Create `modules/{domain}/GROUNDWORK-{feature-name}.md`:

```markdown
# Groundwork: {Feature Name}

Built: {date}
Spec: `specs/{domain}/{feature-name}.md`

## Constitutional Compliance

### Simplicity Gate (Article I) ✅

- Simplest approach for current scenarios
- No future-proofing
- Minimal {X} files created

### Anti-Abstraction Gate (Article II) ✅

- Using {framework names} directly
- Single representation per domain concept
- No unnecessary wrappers

### Groundwork Gate (Article IX) ✅

- {X} database tables for shared schema
- {Y} scenarios share this infrastructure
- Justified upfront setup

## Prerequisites Established

{If prerequisite exists:}

### Core Capability: {Name}

- **Approach**: {e.g., "Excalidraw embedded canvas", "Stripe payment integration"}
- **Library/Tool**: {e.g., "@excalidraw/excalidraw v1.2.3", "Stripe SDK"}
- **Why This Approach**: {Rationale for choosing this over alternatives}
- **What Works Now**: {What's functional after groundwork}
- **What Scenarios Can Build**: {What's now possible - e.g., "Can capture and position images on canvas"}
- **Documentation**: {Link to library docs or integration guide}

{If no prerequisite:}

No core prerequisite needed - feature only requires shared infrastructure (types/stores/utilities)

## What Was Created

### Database Schema

- Tables: {list with column counts}
- Migrations: {file paths}
- Rationale: {why these tables}

### Type Definitions

- Files: {list files}
- Types: {list type names}
- Rationale: {why single representation}

### Service Shells

- Files: {list files}
- Methods: {list method signatures - EMPTY, no logic}
- Rationale: {what scenarios will use these}

### Test Infrastructure

- Utilities: {list files}
- Database helpers: {list helpers}
- Contract test setup: {what was configured}

## What's NOT Included

- ❌ No scenario-specific logic
- ❌ No business logic in services (empty shells only)
- ❌ No API routes yet
- ❌ No UI components yet
- ❌ No scenario tests yet

## Complexity Tracking

{If no exceptions:}
✅ No constitutional exceptions required

{If exceptions:}

### Exception: {What}

- **Principle**: Article {number}
- **Justification**: {Why}
- **Impact**: {Complexity added}

## Next Steps

1. Review this groundwork
2. Run `/clear` to reset context (recommended)
3. Start implementing scenarios:
   - `/implement specs/{domain}/{feature-name}.md --scenario 1`
   - Or generate tasks first: `/create-tasks specs/{domain}/{feature-name}.md`
```

9. **Prompt User**:

   ```
   ✅ Groundwork complete for {feature-name}!

   What was built:
   - Database schema with {X} tables
   - {Y} type definitions
   - {Z} service shells (no logic yet)

   📝 Documented in: modules/{domain}/GROUNDWORK-{feature-name}.md

   Next steps:
   1. Review the groundwork changes
   2. Run /clear to reset context (recommended)
   3. Start implementing scenarios: /implement specs/{domain}/{feature-name}.md
   ```

**Key Principles:**

- Foundation only, no business logic
- Shared infrastructure that scenarios will use
- Empty service methods (just signatures)
- Test infrastructure without scenario tests
- Clear documentation of what was built
