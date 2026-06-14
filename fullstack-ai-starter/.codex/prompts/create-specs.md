---
description: 'Transforms a rough idea into Gherkin scenarios for BDD implementation.'
argument-hint: '[your feature idea or task description]'
---

You are a BDD specification expert. Your task is to take a user's rough idea and transform it into **clear Gherkin scenarios** that capture the feature's behavior. Keep it simple and follow YAGNI principles - create only what's needed.

**Your Idea:**
$ARGUMENTS

**Discovery Process:**

1.  **Read Constitution**: First, read `.claude/constitution.md` to understand architectural principles
2.  **Understand the Idea**: Clarify the user's core request and identify the business value
3.  **Quick Codebase Analysis**:
    - Identify which domain module this belongs to (e.g., `modules/posts/`, `modules/users/`)
    - Check existing patterns in that module using Grep/Read tools
    - Note any dependencies or related features
4.  **Mark Uncertainties**: Identify ALL ambiguities in the user's idea and mark them with `[NEEDS CLARIFICATION]`
5.  **Clarify with User**: Ask clarifying questions for critical ambiguities before creating the spec

**Spec File Creation:**

After understanding the idea, automatically create a lightweight specification file:

1. **Auto-create directories**: Create `specs/` and `specs/{domain}/` if they don't exist
2. **File naming**: Use kebab-case feature name (e.g., `specs/posts/create-post.md`)
3. **Keep it minimal**: Focus on scenarios and essential context only

**Specification File Template:**

```markdown
# {Feature Name}

## Context
{1-2 sentences explaining the business value and what problem this solves}

## Domain
`modules/{domain}/`

## Implementation Progress
<!-- Track scenario implementation below -->
<!-- Update after each scenario is implemented via /implement -->

⏳ All scenarios pending

## Uncertainties

<!-- CRITICAL: Mark ALL ambiguities discovered during spec creation -->
<!-- These MUST be resolved before /implement can proceed -->

{If there are ambiguities, list them here:}
- `[NEEDS CLARIFICATION]`: {Specific question about unclear requirement}
- `[NEEDS CLARIFICATION]`: {Another ambiguity}

{If no ambiguities, write:}
✅ No ambiguities - all requirements are clear and testable

## Scenarios

### Happy Path: {Main Success Scenario}
```gherkin
Given {initial state/precondition}
When {user action or event}
Then {expected outcome}
And {additional assertions if needed}
```

### Edge Case: {Error or Alternative Scenario}
```gherkin
Given {initial state}
When {error condition or alternative action}
Then {expected error handling or alternative outcome}
```

### Edge Case: {Another Important Scenario if needed}
```gherkin
Given {state}
When {action}
Then {outcome}
```

## Specification Quality Checklist

Before moving to /groundwork or /implement, verify:

### Requirement Completeness (Article VI)
- [ ] All `[NEEDS CLARIFICATION]` markers are resolved
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Each scenario has clear pass/fail conditions

### What vs. How Separation (Article VI.2)
- [ ] Spec focuses on WHAT users need and WHY
- [ ] No implementation details (tech stack, APIs, code structure)
- [ ] No prescriptive HOW (e.g., "use Redis", "create service class")
- [ ] Behaviors are described, not solutions

### Scenario Quality (Article VI.3)
- [ ] Each scenario is independently testable
- [ ] Scenarios are precise (no ambiguous terms)
- [ ] Scenarios are minimal (no unnecessary complexity)
- [ ] Happy path + key edge cases covered (2-4 scenarios)

### YAGNI Compliance (Article I.2)
- [ ] No speculative or "might need" features
- [ ] No future-proofing scenarios
- [ ] Only solving current, real problems

## Dependencies
- {List any external services, APIs, or modules this depends on}
- {Only include if relevant}

## Notes
- {Any important technical constraints or considerations}
- {Keep brief - implementation details belong in code, not specs}

## Complexity Tracking

<!-- If any constitutional principles will be violated, document justified exceptions -->

{If no exceptions needed, write:}
✅ No complexity exceptions required

{If exceptions needed, document like this:}
### Exception: {What principle will be violated}
- **Principle**: Article {number} ({name})
- **Justification**: {Why this is necessary}
- **Impact**: {What complexity this introduces}
- **Alternatives Considered**: {Why simpler approaches won't work}

## Production Learnings

<!-- This section will be updated after deployment with real-world insights -->

{Initially empty - to be filled after feature is live}

---
*Generated: {date}*
*Next step: Review checklist, then run `/groundwork specs/{domain}/{feature-name}.md` (if DB changes) or `/implement specs/{domain}/{feature-name}.md`*
```

**Example Workflow:**

```bash
# 1. User runs: /create-specs "Add ability to archive posts"

# 2. You analyze and create:
specs/posts/archive-posts.md

# 3. File contains:
# - Feature name: Archive Posts
# - Context: Allow users to archive old posts without deleting them
# - Domain: modules/posts/
# - 2-3 Gherkin scenarios (archive, unarchive, error cases)
# - Dependencies: None (or list if any)
# - Notes: Minimal technical constraints only

# 4. Tell user: "Created spec at specs/posts/archive-posts.md
#    Review the scenarios, then run: /implement specs/posts/archive-posts.md"
```

**Important Guidelines:**

### Template Constraints (Inspired by SDD)

These constraints guide LLM behavior toward high-quality specifications:

1. **Force Explicit Uncertainty Markers**:
   - Use `[NEEDS CLARIFICATION]` for ALL ambiguities
   - Don't guess - if the user's idea doesn't specify something, mark it
   - Example: "Users can log in" → `[NEEDS CLARIFICATION: auth method - email/password, OAuth, or SSO?]`

2. **Prevent Premature Implementation Details**:
   - ✅ Focus on WHAT users need and WHY
   - ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
   - Spec: "Archive posts without deleting" (good)
   - NOT: "Create archivedAt timestamp field in posts table" (too specific)

3. **Enforce Checklists for Completeness**:
   - Use the Specification Quality Checklist to self-review
   - Check: testability, what/how separation, YAGNI compliance
   - Don't skip checklist items

4. **YAGNI Enforcement**:
   - Write only what's needed for current, real problems
   - No speculative features ("might need", "in case")
   - No future-proofing scenarios
   - 2-4 scenarios: happy path + key edge cases

5. **Scenarios First**:
   - Focus 80% on clear, testable Gherkin scenarios
   - Minimal context elsewhere
   - Each scenario independently testable

6. **Constitutional Alignment**:
   - Read constitution first to understand principles
   - Check specs against constitutional articles (I, II, VI)
   - Document any justified complexity exceptions

### After Creating Spec File

Inform the user:

1. **Where the spec was created**: `specs/{domain}/{feature-name}.md`
2. **Checklist status**:
   - ✅ If all checklist items pass
   - ⚠️ If any `[NEEDS CLARIFICATION]` markers remain (must resolve before implementation)
3. **Next steps**:
   - "Review the spec and checklist"
   - "Resolve any uncertainties if needed"
   - "Then run: `/groundwork specs/{domain}/{feature-name}.md`" (if DB changes)
   - "Or run: `/implement specs/{domain}/{feature-name}.md`" (if no DB changes)
4. **Optional**: "Run `/create-tasks specs/{domain}/{feature-name}.md` to see task breakdown"
