# Development Constitution

## Preamble

This constitution establishes the immutable architectural principles that govern how features are specified, planned, and implemented in this project. These principles ensure consistency, maintainability, and quality across all development efforts.

While implementation details may evolve, these core principles remain constant to prevent architectural drift and maintain system integrity.

---

## Article I: Simplicity First

### Section 1.1: Minimal Complexity
Every feature MUST start with the simplest possible implementation that satisfies the requirements.

**Principle**: Complexity is a liability, not an asset.

### Section 1.2: No Future-Proofing
Code SHALL NOT be written to handle hypothetical future requirements.

**Rationale**: YAGNI (You Aren't Gonna Need It) prevents wasted effort and unnecessary complexity.

### Section 1.3: Simplicity Gate
Before implementing any feature, answer these questions:
- [ ] Is this the simplest approach that satisfies the current requirements?
- [ ] Have I removed all speculative or "might need" features?
- [ ] Can this be done with fewer modules/files/abstractions?

**Enforcement**: If any answer is "no", simplify before proceeding.

---

## Article II: Anti-Abstraction Principle

### Section 2.1: Framework Trust
Use framework features directly rather than wrapping them in custom abstractions.

**Examples**:
- ✅ Use Next.js App Router directly
- ✅ Use Drizzle ORM directly
- ❌ Create custom routing wrapper around Next.js
- ❌ Create custom ORM abstraction over Drizzle

### Section 2.2: Single Model Representation
Each domain entity MUST have exactly one source of truth for its structure.

**Rationale**: Multiple representations (DTO, Entity, ViewModel) create maintenance burden and sync issues.

### Section 2.3: Anti-Abstraction Gate
Before adding abstraction layers, answer these questions:
- [ ] Am I using the framework/library directly without unnecessary wrappers?
- [ ] Do I have a single representation for each domain concept?
- [ ] Is this abstraction solving a real problem that exists today?

**Note on Result<T,E> Type**: The `Result<T,E>` type is **not** an abstraction layer - it's explicit error handling that makes success/failure states visible in the type system. This aligns with this article by favoring clarity over hidden control flow (exceptions).

**Enforcement**: Document justified exceptions in complexity tracking.

---

## Article III: Integration-First Testing

### Section 3.1: Real Environments
Tests MUST use realistic environments whenever possible:
- ✅ Use real databases (with test schema)
- ✅ Use actual service instances
- ❌ Mock databases unless absolutely necessary
- ❌ Stub external services that can run locally

**Rationale**: Integration tests catch real-world issues that unit tests miss.

### Section 3.2: Contract Tests Mandatory
Before implementing any API or service integration, contract tests MUST be defined and approved.

**Contract tests define**:
- Request/response shapes
- Error conditions
- Validation rules
- Expected behavior

### Section 3.3: Integration-First Gate
Before writing tests, answer these questions:
- [ ] Are contracts defined for all APIs/services?
- [ ] Am I using a real database (or documented reason why not)?
- [ ] Will these tests catch integration issues, not just isolated logic?

**Enforcement**: No implementation without passing this gate.

---

## Article IV: Test-First Imperative

### Section 4.1: No Code Before Tests
This is NON-NEGOTIABLE: All implementation MUST follow strict Test-Driven Development.

**Test-First Process**:
1. Write tests that capture the scenario behavior
2. Get tests validated and approved
3. Confirm tests FAIL (Red phase)
4. Write minimal code to make tests pass (Green phase)
5. Refactor while keeping tests green

### Section 4.2: Test Types and Strategy
Follow the testing pyramid:
- **Many Unit Tests**: Business logic, validation, edge cases
- **Some API Tests**: HTTP contracts, route handlers, integration
- **Few E2E Tests**: Critical multi-module user journeys only

### Section 4.3: Test-First Gate
Before implementing, answer these questions:
- [ ] Have I written tests that capture the scenario behavior?
- [ ] Have the tests been reviewed and approved?
- [ ] Do the tests currently FAIL (Red phase)?
- [ ] Are tests at the appropriate level (Unit/API/E2E)?

**Testing Result<T> Types**: When testing services that return `Result<T>`:
- Assert `result.success` is `true` or `false`
- For success: access `result.data` after narrowing
- For errors: access `result.error.code` and `result.error.message` after narrowing

**Enforcement**: No implementation code without failing tests.

---

## Article V: Module Structure and Co-location

### Section 5.1: Domain-Driven Modules
Features MUST be organized by domain, not by technical layer.

**Module Structure**:
```
modules/{domain}/
├── services/          # Business logic
├── types/             # TypeScript types
├── schema.ts          # Database schema (Drizzle)
└── tests/
    ├── unit/          # Fast, isolated tests
    └── integration/   # API tests with Supertest
```

### Section 5.2: Test Co-location
Tests MUST live with the code they test within `modules/{domain}/tests/`.

**Rationale**: Improves discoverability, maintainability, and makes refactoring safer.

### Section 5.3: Module Independence
Modules SHOULD minimize dependencies on other modules.

**Guideline**: If Module A needs functionality from Module B, consider:
1. Is this coupling necessary, or can logic be duplicated?
2. Should this functionality be extracted to a shared utility?
3. Is the dependency unidirectional and well-defined?

---

## Article VI: Specification Quality

### Section 6.1: Explicit Uncertainty
Specifications MUST mark all ambiguities with `[NEEDS CLARIFICATION: specific question]`.

**Examples**:
- ❌ "Users can log in" (ambiguous: how? email/password, OAuth, SSO?)
- ✅ "Users can log in `[NEEDS CLARIFICATION: auth method - email/password, OAuth, or SSO?]`"

### Section 6.2: What vs. How Separation
Specifications MUST focus on WHAT and WHY, never HOW.

**In Specifications (✅)**:
- User needs to archive posts without deleting them
- System must respond within 200ms for 95% of requests

**NOT in Specifications (❌)**:
- Implement using Redis cache
- Use React Query for state management
- Create PostArchiver service class

### Section 6.3: Scenario Completeness
Each Gherkin scenario MUST be:
- **Testable**: Clear pass/fail criteria
- **Independent**: Can be implemented and tested in isolation
- **Precise**: No ambiguous terms or undefined behaviors
- **Minimal**: Covers one behavior path without unnecessary complexity

### Section 6.4: Specification Gate
Before moving to implementation, answer these questions:
- [ ] Are all `[NEEDS CLARIFICATION]` markers resolved?
- [ ] Does the spec focus on WHAT/WHY without prescribing HOW?
- [ ] Is each scenario testable, independent, precise, and minimal?

**Enforcement**: Block implementation if clarifications remain.

---

## Article VII: Complexity Tracking and Accountability

### Section 7.1: Justified Exceptions
When violating any constitutional principle, exceptions MUST be documented with:
- **What**: Which principle is being violated
- **Why**: Specific reason this violation is necessary
- **Impact**: What complexity this introduces
- **Alternatives Considered**: Why simpler approaches won't work

### Section 7.2: Complexity Budget
Each feature has an implicit complexity budget. Exceeding this budget requires justification.

**Indicators of Budget Exceeded**:
- More than 5 new files for a single scenario
- More than 3 abstraction layers
- More than 2 new database tables
- Custom framework wrappers or abstractions

### Section 7.3: Technical Debt Register
Justified complexity exceptions MUST be tracked in the specification file under "Complexity Tracking".

**Format**:
```markdown
## Complexity Tracking

### Exception: Custom Cache Abstraction
- **Principle Violated**: Article II (Anti-Abstraction)
- **Justification**: Redis and Memcached have incompatible APIs; we need to swap between them
- **Impact**: +1 abstraction layer, +150 LOC
- **Review Date**: 2025-12-01
```

---

## Article VIII: Vertical Slicing

### Section 8.1: End-to-End Functionality
Each scenario implementation MUST deliver complete, working functionality from UI to database.

**Vertical Slice Includes**:
- ✅ API routes for the scenario
- ✅ UI components for the scenario
- ✅ Service layer logic
- ✅ Database schema changes
- ✅ Tests for all layers

### Section 8.2: No Horizontal Layers
Do NOT implement entire layers (e.g., "all backend services") before moving to the next layer.

**Anti-Pattern**:
1. ❌ Implement all backend services
2. ❌ Then implement all API routes
3. ❌ Then implement all UI components

**Correct Pattern**:
1. ✅ Implement Scenario 1 end-to-end (API + UI + tests)
2. ✅ Implement Scenario 2 end-to-end (API + UI + tests)
3. ✅ Continue until all scenarios complete

### Section 8.3: Incremental Value
Each scenario completion MUST deliver demonstrable user value.

**Rationale**: Vertical slices enable faster feedback, easier testing, and incremental delivery.

---

## Article IX: Groundwork Separation

### Section 9.1: Infrastructure vs. Logic
Groundwork phase MUST establish shared infrastructure ONLY:
- ✅ Database schema and migrations
- ✅ Type definitions for domain entities
- ✅ Service class shells (empty methods)
- ✅ Test infrastructure and utilities
- ✅ Dependency injection registration

**Groundwork MUST NOT include**:
- ❌ Business logic implementation
- ❌ Scenario-specific code
- ❌ API routes or UI components
- ❌ Populated service methods

### Section 9.2: Groundwork Documentation
The `/groundwork` phase MUST produce a `GROUNDWORK-{feature}.md` file documenting:
- What infrastructure was created
- Why specific technology choices were made
- What remains to be implemented in scenarios
- Any architectural decisions or constraints

### Section 9.3: Groundwork Gate
Before starting groundwork, answer these questions:
- [ ] Does this feature have database changes requiring shared schema?
- [ ] Do multiple scenarios share common infrastructure?
- [ ] Is the feature complex enough to justify upfront setup?

**Guideline**: Skip groundwork for simple features with no database changes.

---

## Article X: Context Management

### Section 10.1: Clear Between Phases
After completing major workflow phases, context MUST be cleared to maintain AI performance.

**Clear After**:
- `/groundwork` completion → `/clear` → `/implement`
- Scenario 1 completion → `/clear` → Scenario 2 implementation
- Complex analysis → `/clear` → Implementation

### Section 10.2: Scenario-by-Scenario Implementation
Features with multiple scenarios MUST be implemented one scenario at a time.

**Process**:
1. Implement Scenario 1 (API + UI + tests)
2. Run quality checks (format, lint, test)
3. Update spec with completion status
4. `/clear` context
5. Implement Scenario 2 (fresh context)
6. Repeat until all scenarios complete

**Rationale**: Smaller context windows = better code quality, fewer hallucinations, faster AI responses.

### Section 10.3: Branch per Scenario
Each scenario MUST have its own feature branch:
- `feature/{domain}/{feature-name}/{scenario-slug}`

**Rationale**: Easier review, easier rollback, smaller PRs, clearer git history.

---

## Article XI: Bidirectional Feedback

### Section 11.1: Production Learnings
Production issues, metrics, and incidents MUST inform specification evolution.

**Feedback Loop**:
- Bug in production → Add edge case scenario to spec
- Performance issue → Add non-functional requirement
- User confusion → Clarify acceptance criteria

### Section 11.2: Specification Updates
Specifications are living documents that evolve based on:
- Production incidents
- User feedback
- Performance metrics
- Security findings
- Technical debt discoveries

### Section 11.3: Production Learnings Section
Each spec file SHOULD include a "Production Learnings" section tracking:
- Issues discovered post-deployment
- Metrics and insights
- Spec updates made in response

**Format**:
```markdown
## Production Learnings

### 2025-11-15: Performance Issue
- **Issue**: API response time exceeded 500ms under load
- **Root Cause**: Missing database index on userId
- **Spec Update**: Added non-functional requirement for response time
- **Resolution**: Added index, response time now <100ms
```

---

## Amendment Process

### Modification Requirements
Changes to this constitution require:
- **Explicit Documentation**: Rationale for the change
- **Review and Approval**: Project maintainers must approve
- **Backwards Compatibility**: Assessment of impact on existing features
- **Version Tracking**: Date and amendment number

### Amendment Log

#### Amendment 1 (2025-10-10)
- **Initial Constitution**: Adapted from SDD principles for BDD product development context
- **Key Changes from SDD**:
  - Removed Library-First Principle (not applicable to product features)
  - Removed CLI Interface Mandate (web app context)
  - Added Groundwork Separation article
  - Added Context Management article
  - Added Vertical Slicing article
  - Adapted gates to product development workflow

---

## Conclusion

This constitution serves as the architectural foundation for all development in this project. By adhering to these principles, we ensure:

- **Consistency**: All features follow the same architectural patterns
- **Quality**: Systematic prevention of common failure modes
- **Maintainability**: Simplified codebases that are easier to understand and modify
- **Velocity**: Faster development through clear guidelines and reduced rework
- **Alignment**: Specifications and implementation remain synchronized

When in doubt, return to these principles. They exist to guide decision-making and prevent the accumulation of technical debt disguised as progress.

---

*Constitution Version: 1.0*
*Last Updated: 2025-10-10*
*Next Review: 2026-01-10*
