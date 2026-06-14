# Constitutional BDD Quickstart Guide

Welcome! This guide will walk you through building a **support ticketing system** using our constitutional BDD workflow. You'll learn how to go from a rough idea to working code with systematic quality controls.

---

## 📚 What is Constitutional BDD?

Constitutional BDD combines **Behavior-Driven Development** (Gherkin scenarios) with **Constitutional Principles** (architectural gates) to ensure:

✅ **Quality by design** - Phase gates prevent common mistakes
✅ **Clear specifications** - Explicit uncertainty handling
✅ **Consistent architecture** - Constitutional principles enforced
✅ **Better AI output** - Template constraints guide behavior
✅ **Trackable complexity** - Justified exceptions documented

**Key difference from traditional BDD**: We don't just write specs—we enforce architectural principles through gates and checklists at every phase.

---

## 🎯 Prerequisites

Before starting, make sure you have:

- [ ] Read `.claude/constitution.md` (5 minutes)
- [ ] Understood the 4-phase workflow (`.claude/BDD-WORKFLOW.md`)
- [ ] Access to `/create-specs`, `/groundwork`, `/implement` commands

---

## 🎬 The Complete Example: Support Ticketing System

Let's build a support ticketing system from scratch. We'll walk through every phase, showing exactly what happens and what gets created.

---

## Phase 1: Create Specification

### Step 1.1: Run `/create-specs`

```bash
/create-specs "Support ticketing system where users can submit issues, support staff can view and respond to tickets, and users can track ticket status"
```

### Step 1.2: What Happens

The AI will:

1. **Read the constitution** to understand architectural principles
2. **Analyze your idea** and identify ambiguities
3. **Ask clarifying questions** (if critical info is missing):
   ```
   Before creating the spec, I need clarification on a few points:

   1. Ticket priority levels? (e.g., Low/Medium/High/Urgent)
   2. User authentication? (Should be integrated with better-auth or separate?)
   3. Notifications? (Email when ticket status changes?)
   4. File attachments? (Can users attach screenshots?)
   ```

4. **You provide answers**:
   ```
   1. Yes: Low, Medium, High, Urgent
   2. Use existing better-auth integration
   3. Yes, email notifications for status changes
   4. Not in first version (mark as future enhancement)
   ```

### Step 1.3: Generated Spec File

The command creates: `specs/support/ticket-system.md`

```markdown
# Support Ticket System

## Context
Enable users to submit support requests and track resolution progress while allowing support staff to manage and respond to customer issues efficiently.

## Domain
`modules/support/`

## Implementation Progress
⏳ All scenarios pending

## Uncertainties

✅ No ambiguities - all requirements are clear and testable

## Scenarios

### Happy Path: Submit New Support Ticket
```gherkin
Given I am a logged-in user
When I submit a ticket with title "Login not working", description "Cannot access my account", and priority "High"
Then the ticket is created with status "Open"
And I receive a confirmation with ticket number
And I receive an email notification about ticket creation
```

### Happy Path: View Ticket Status
```gherkin
Given I have submitted ticket #12345
When I view my tickets list
Then I see ticket #12345 with current status "Open"
And I see the support staff response if any
And I see when the ticket was last updated
```

### Happy Path: Support Staff Responds to Ticket
```gherkin
Given I am a support staff member
And there is an open ticket #12345
When I add response "Please try resetting your password"
And I change ticket status to "In Progress"
Then the customer sees my response
And the customer receives an email notification
And the ticket status updates to "In Progress"
```

### Edge Case: Close Resolved Ticket
```gherkin
Given I am a support staff member
And ticket #12345 has status "In Progress"
When I mark the ticket as "Resolved"
Then the ticket status changes to "Resolved"
And the customer receives a notification
And the customer can reopen if issue persists
```

## Specification Quality Checklist

### Requirement Completeness (Article VI)
- [x] All `[NEEDS CLARIFICATION]` markers are resolved
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Each scenario has clear pass/fail conditions

### What vs. How Separation (Article VI.2)
- [x] Spec focuses on WHAT users need and WHY
- [x] No implementation details (tech stack, APIs, code structure)
- [x] No prescriptive HOW (e.g., "use Redis", "create service class")
- [x] Behaviors are described, not solutions

### Scenario Quality (Article VI.3)
- [x] Each scenario is independently testable
- [x] Scenarios are precise (no ambiguous terms)
- [x] Scenarios are minimal (no unnecessary complexity)
- [x] Happy path + key edge cases covered (4 scenarios)

### YAGNI Compliance (Article I.2)
- [x] No speculative or "might need" features
- [x] No future-proofing scenarios
- [x] Only solving current, real problems

## Dependencies
- `modules/auth/` - Uses existing better-auth for user authentication
- Email service - For notification delivery

## Notes
- File attachments intentionally excluded from first version (future enhancement)
- Email notifications use existing notification infrastructure

## Complexity Tracking

✅ No complexity exceptions required

## Production Learnings

{Initially empty - to be filled after feature is live}

---
*Generated: 2025-10-10*
*Next step: Review checklist, then run `/groundwork specs/support/ticket-system.md` (DB changes needed)*
```

### Step 1.4: Review the Spec

The AI will inform you:

```
✅ Specification created: specs/support/ticket-system.md

Summary:
- 4 scenarios (3 happy paths, 1 edge case)
- Domain: modules/support/
- Dependencies: auth module, email service
- All quality checklists passed ✅

Next steps:
1. Review the spec and scenarios
2. No uncertainties to resolve (all clear!)
3. Run: `/groundwork specs/support/ticket-system.md` (DB changes needed)
4. Or run: `/create-tasks specs/support/ticket-system.md` to see task breakdown
```

---

## Phase 2: Generate Tasks (Optional)

### Step 2.1: Run `/create-tasks`

```bash
/create-tasks specs/support/ticket-system.md
```

### Step 2.2: Generated Tasks File

Creates: `specs/support/ticket-system/tasks.md`

```markdown
# Tasks: Support Ticket System

**Generated**: 2025-10-10
**Spec**: `specs/support/ticket-system.md`
**Groundwork**: Will be created in next phase

---

## Constitutional Gate Checks

### Simplicity Gate (Article I)
- [x] Simplest approach? Yes - CRUD operations for tickets
- [x] No speculative features? Yes - file attachments excluded
- [x] Minimal modules? Yes - single support module

### Anti-Abstraction Gate (Article II)
- [x] Using frameworks directly? Yes - Drizzle for DB, Next.js for routes
- [x] Single representation per concept? Yes - one Ticket type
- [x] No unnecessary abstractions? Yes - direct framework usage

### Integration-First Gate (Article III)
- [x] Contracts defined? Will define in groundwork
- [x] Using real database? Yes - test schema with Drizzle
- [x] Tests catch integration issues? Yes - API integration tests planned

### Test-First Gate (Article IV)
- [x] Tests before code? Yes - following Red-Green-Refactor
- [x] Tests validated? Will be reviewed before implementation
- [x] Tests FAIL first? Yes - TDD approach

### Specification Gate (Article VI)
- [x] All clarifications resolved? Yes
- [x] WHAT/WHY not HOW? Yes
- [x] Testable scenarios? Yes

---

## Scenario 1: Submit New Support Ticket

### Backend Tasks
- [ ] [P] Create Ticket service with `createTicket()` method
- [ ] [P] Add validation for ticket title (required, max 200 chars)
- [ ] [P] Add validation for priority (enum: low/medium/high/urgent)
- [ ] Handle error case: Missing required fields

### API Tasks
- [ ] Define API contract: `POST /api/support/tickets`
- [ ] Create API route: `app/api/support/tickets/route.ts`
- [ ] Add request validation (title, description, priority)
- [ ] Return ticket with generated ID and ticket number
- [ ] Write integration test: `modules/support/tests/integration/create-ticket.api.test.ts`

### Frontend Tasks
- [ ] Create component: `app/(main)/support/components/CreateTicketForm.tsx`
- [ ] Add form fields: title, description, priority dropdown
- [ ] Handle loading state
- [ ] Handle error state with user feedback
- [ ] Show success message with ticket number

### Testing Tasks
- [ ] Write unit tests: `modules/support/tests/unit/ticket.service.spec.ts`
- [ ] Write API integration tests
- [ ] Verify all tests pass: `npm test`

### Quality & Completion
- [ ] Run formatter: `pnpm format`
- [ ] Run linter: `pnpm run check:fix`
- [ ] All tests passing
- [ ] Update spec with ✅ completion status

---

## Scenario 2: View Ticket Status

{Similar structure for each remaining scenario}

---

## Parallel Work Groups

### Group 1: Scenario 1 Implementation
- Submit ticket (backend, API, frontend, tests)

### Group 2: Scenario 2 Implementation [P]
- View ticket status (can parallelize if scenarios independent)

**Recommendation**: Implement sequentially with `/clear` between each for better AI performance.

---
```

### Step 2.3: Review Tasks

```
✅ Task list created: specs/support/ticket-system/tasks.md

Summary:
- 4 scenarios to implement
- ~25 total tasks
- 8 tasks can be parallelized (marked [P])
- All constitutional gates pass

Next step: Review tasks, then run /groundwork to begin
```

---

## Phase 3: Establish Groundwork

### Step 3.1: Run `/groundwork`

```bash
/groundwork specs/support/ticket-system.md
```

### Step 3.2: Constitutional Gate Checks

The AI first checks gates and shows you the plan:

```
# Groundwork Plan: Support Ticket System

## Constitutional Gate Results

### Simplicity Gate (Article I)
- [x] Simplest approach? Yes - Single tickets table with status enum
- [x] No future-proofing? Yes - No attachment storage, no complex workflows
- [x] Minimal modules/files? Yes - 5 files (schema, types, 2 services, tests)

### Anti-Abstraction Gate (Article II)
- [x] Using frameworks directly? Yes - Drizzle ORM, no wrapper
- [x] Single representation per concept? Yes - One Ticket interface
- [x] No unnecessary abstractions? Yes - Direct database access

### Groundwork Gate (Article IX)
- [x] Database changes needed? Yes - tickets table, ticket_responses table
- [x] Shared infrastructure across scenarios? Yes - All scenarios use same tables
- [x] Complex enough to justify setup? Yes - 2 tables, enums, relationships

## Database Schema

### Table: tickets
- id (uuid, primary key)
- ticketNumber (varchar, unique, auto-generated: "TKT-00001")
- userId (uuid, foreign key → auth.users)
- title (varchar, 200, required)
- description (text, required)
- priority (enum: low, medium, high, urgent)
- status (enum: open, in_progress, resolved, closed)
- createdAt (timestamp)
- updatedAt (timestamp)
- Indexes: userId, status, createdAt
- Rationale: Covers all 4 scenarios, no extra fields

### Table: ticket_responses
- id (uuid, primary key)
- ticketId (uuid, foreign key → tickets)
- staffId (uuid, foreign key → auth.users)
- message (text, required)
- createdAt (timestamp)
- Rationale: Supports staff responses in scenario 3

## Type Definitions

### TicketPriority (enum)
- Values: "low" | "medium" | "high" | "urgent"
- Rationale: Single source of truth for priority levels

### TicketStatus (enum)
- Values: "open" | "in_progress" | "resolved" | "closed"
- Rationale: Matches scenario requirements exactly

### Ticket (interface)
- All fields from tickets table
- Rationale: Single representation, no DTOs

### TicketResponse (interface)
- All fields from ticket_responses table
- Rationale: Single representation

## Service Shells

### TicketService
- Methods (EMPTY, no logic):
  - `createTicket(data: CreateTicketInput): Promise<Ticket>`
  - `getTicketById(id: string): Promise<Ticket | null>`
  - `getTicketsByUserId(userId: string): Promise<Ticket[]>`
  - `updateTicketStatus(id: string, status: TicketStatus): Promise<Ticket>`
- Purpose: Scenarios 1, 2, 4 will use these

### TicketResponseService
- Methods (EMPTY, no logic):
  - `addResponse(ticketId: string, staffId: string, message: string): Promise<TicketResponse>`
  - `getResponsesByTicketId(ticketId: string): Promise<TicketResponse[]>`
- Purpose: Scenario 3 will use these

## Test Infrastructure
- Database seeding helper for test tickets
- Test user creation utilities
- Contract test setup for ticket APIs

## Complexity Tracking

✅ All constitutional gates pass - no exceptions needed

## Estimated Complexity
Medium

Files to create: 5
Files to modify: 1 (DI container registration)

---

Approve this groundwork plan? (y/n)
```

### Step 3.3: You Approve

```
y
```

### Step 3.4: Infrastructure Created

The AI creates:

**1. Database Schema** (`modules/support/schema.ts`):
```typescript
import { pgTable, uuid, varchar, text, timestamp, pgEnum } from 'drizzle-orm/pg-core';
import { users } from '../auth/schema';

export const ticketPriority = pgEnum('ticket_priority', ['low', 'medium', 'high', 'urgent']);
export const ticketStatus = pgEnum('ticket_status', ['open', 'in_progress', 'resolved', 'closed']);

export const tickets = pgTable('tickets', {
  id: uuid('id').primaryKey().defaultRandom(),
  ticketNumber: varchar('ticket_number', { length: 20 }).notNull().unique(),
  userId: uuid('user_id').references(() => users.id).notNull(),
  title: varchar('title', { length: 200 }).notNull(),
  description: text('description').notNull(),
  priority: ticketPriority('priority').notNull().default('medium'),
  status: ticketStatus('status').notNull().default('open'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

export const ticketResponses = pgTable('ticket_responses', {
  id: uuid('id').primaryKey().defaultRandom(),
  ticketId: uuid('ticket_id').references(() => tickets.id).notNull(),
  staffId: uuid('staff_id').references(() => users.id).notNull(),
  message: text('message').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
```

**2. Type Definitions** (`modules/support/types.ts`):
```typescript
import { InferSelectModel } from 'drizzle-orm';
import { tickets, ticketResponses } from './schema';

export type Ticket = InferSelectModel<typeof tickets>;
export type TicketResponse = InferSelectModel<typeof ticketResponses>;

export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed';

export interface CreateTicketInput {
  userId: string;
  title: string;
  description: string;
  priority: TicketPriority;
}
```

**3. Service Shells** (`modules/support/services/ticket.service.ts`):
```typescript
import { CreateTicketInput, Ticket, TicketStatus } from '../types';

export class TicketService {
  // EMPTY - No logic yet, just signatures
  async createTicket(data: CreateTicketInput): Promise<Ticket> {
    throw new Error('Not implemented');
  }

  async getTicketById(id: string): Promise<Ticket | null> {
    throw new Error('Not implemented');
  }

  async getTicketsByUserId(userId: string): Promise<Ticket[]> {
    throw new Error('Not implemented');
  }

  async updateTicketStatus(id: string, status: TicketStatus): Promise<Ticket> {
    throw new Error('Not implemented');
  }
}
```

**4. Groundwork Documentation** (`modules/support/GROUNDWORK-ticket-system.md`):
```markdown
# Groundwork: Support Ticket System

Built: 2025-10-10
Spec: `specs/support/ticket-system.md`

## Constitutional Compliance

### Simplicity Gate (Article I) ✅
- Simplest approach for current scenarios
- No future-proofing (no attachments, no workflows)
- Minimal 5 files created

### Anti-Abstraction Gate (Article II) ✅
- Using Drizzle ORM directly
- Single representation per domain concept
- No unnecessary wrappers

### Groundwork Gate (Article IX) ✅
- 2 database tables for shared schema
- All 4 scenarios share this infrastructure
- Justified upfront setup

## What Was Created

### Database Schema
- Tables: `tickets` (8 columns), `ticket_responses` (4 columns)
- Enums: `ticket_priority`, `ticket_status`
- Rationale: Minimal schema covering all scenarios

### Type Definitions
- Files: `modules/support/types.ts`
- Types: Ticket, TicketResponse, TicketPriority, TicketStatus
- Rationale: Single source of truth, no DTOs

### Service Shells
- Files: `modules/support/services/ticket.service.ts`, `ticket-response.service.ts`
- Methods: 6 empty method signatures
- Rationale: Scenarios will implement these

### Test Infrastructure
- Utilities: Database seeding for test tickets
- Helpers: Test user creation
- Contract test setup configured

## What's NOT Included

- ❌ No scenario-specific logic
- ❌ No business logic in services (empty shells only)
- ❌ No API routes yet
- ❌ No UI components yet
- ❌ No scenario tests yet

## Complexity Tracking

✅ No constitutional exceptions required

## Next Steps

1. Review this groundwork
2. Run `/clear` to reset context (recommended)
3. Start implementing scenarios:
   - `/implement specs/support/ticket-system.md --scenario 1`
   - Or generate tasks first: `/create-tasks specs/support/ticket-system.md`
```

### Step 3.5: Groundwork Complete

```
✅ Groundwork complete for ticket-system!

What was built:
- Database schema with 2 tables (tickets, ticket_responses)
- 4 type definitions
- 2 service shells (6 empty methods)
- Test infrastructure

📝 Documented in: modules/support/GROUNDWORK-ticket-system.md

✅ All code formatted and type-checked
✅ Committed: "chore(support): establish groundwork for ticket-system"

Next steps:
1. Review the groundwork changes
2. Run /clear to reset context (recommended)
3. Start implementing scenarios: /implement specs/support/ticket-system.md
```

**Important**: Now run `/clear` to reset context before implementing scenarios!

---

## Phase 4: Implement Scenarios

### Step 4.1: Clear Context

```bash
/clear
```

### Step 4.2: Run `/implement`

```bash
/implement specs/support/ticket-system.md
```

### Step 4.3: Select Scenario

```
Available scenarios in ticket-system:

1. ⏳ Submit New Support Ticket
2. ⏳ View Ticket Status
3. ⏳ Support Staff Responds to Ticket
4. ⏳ Close Resolved Ticket

Select scenario to implement (1-4):
```

You type: `1`

### Step 4.4: Scenario Implementation

The bdd-dev agent implements Scenario 1 with:

**✅ Test-First Approach (Red-Green-Refactor)**

1. **Creates API Integration Test** (`modules/support/tests/integration/create-ticket.api.test.ts`):
```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import request from 'supertest';
import { app } from '@/app';
import { db } from '@/lib/db';

describe('POST /api/support/tickets', () => {
  beforeEach(async () => {
    // Clear test data
    await db.delete(tickets);
  });

  it('creates a new ticket with valid data', async () => {
    const response = await request(app)
      .post('/api/support/tickets')
      .send({
        title: 'Login not working',
        description: 'Cannot access my account',
        priority: 'high',
      })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      ticketNumber: expect.stringMatching(/^TKT-\d{5}$/),
      title: 'Login not working',
      priority: 'high',
      status: 'open',
    });
  });

  it('validates required fields', async () => {
    await request(app)
      .post('/api/support/tickets')
      .send({ title: 'Test' }) // Missing description
      .expect(400);
  });
});
```

2. **Implements Service Logic** (`modules/support/services/ticket.service.ts`):
```typescript
async createTicket(data: CreateTicketInput): Promise<Ticket> {
  const ticketNumber = await this.generateTicketNumber();

  const [ticket] = await db.insert(tickets).values({
    ...data,
    ticketNumber,
    status: 'open',
  }).returning();

  return ticket;
}

private async generateTicketNumber(): Promise<string> {
  const count = await db.select({ count: sql`count(*)` }).from(tickets);
  const num = (count[0].count as number) + 1;
  return `TKT-${String(num).padStart(5, '0')}`;
}
```

3. **Creates API Route** (`app/api/support/tickets/route.ts`):
```typescript
import { NextRequest } from 'next/server';
import { ticketService } from '@/lib/container';
import { auth } from '@/lib/auth';

export async function POST(req: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await req.json();

  // Validation
  if (!body.title || !body.description) {
    return Response.json({ error: 'Title and description required' }, { status: 400 });
  }

  const ticket = await ticketService.createTicket({
    userId: session.user.id,
    title: body.title,
    description: body.description,
    priority: body.priority || 'medium',
  });

  return Response.json(ticket, { status: 201 });
}
```

4. **Creates UI Component** (`app/(main)/support/components/CreateTicketForm.tsx`):
```typescript
'use client';

import { useState } from 'react';
import { toast } from 'sonner';

export function CreateTicketForm() {
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const data = {
      title: formData.get('title'),
      description: formData.get('description'),
      priority: formData.get('priority'),
    };

    try {
      const response = await fetch('/api/support/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error('Failed to create ticket');

      const ticket = await response.json();
      toast.success(`Ticket created: ${ticket.ticketNumber}`);
      e.currentTarget.reset();
    } catch (error) {
      toast.error('Failed to create ticket');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          name="title"
          required
          maxLength={200}
          className="w-full border rounded px-3 py-2"
        />
      </div>

      <div>
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          name="description"
          required
          rows={4}
          className="w-full border rounded px-3 py-2"
        />
      </div>

      <div>
        <label htmlFor="priority">Priority</label>
        <select id="priority" name="priority" className="w-full border rounded px-3 py-2">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Creating...' : 'Submit Ticket'}
      </button>
    </form>
  );
}
```

5. **Runs Quality Checks**:
```bash
pnpm format     # ✅ Code formatted
pnpm run check:fix  # ✅ Linting passed
npm test        # ✅ All tests passing (3/3)
```

6. **Updates Spec File**:
```markdown
### Happy Path: Submit New Support Ticket
**Status**: ✅ Completed | **Branch**: `feature/support/ticket-system/submit-ticket` | **Date**: 2025-10-10

```gherkin
Given I am a logged-in user
...
```

### Step 4.5: Scenario Complete

```
✅ Scenario 1 completed: "Submit New Support Ticket"

What was built:
- API routes: POST /api/support/tickets
- UI components: CreateTicketForm
- Tests: 3 tests added, all passing ✅
- Files modified: 6

Remaining scenarios: 3

Continue with next scenario? (y/n)
```

You type: `y`

```
Clear context with /clear before continuing? (Recommended for better performance) (y/n)
```

You type: `y`

```
👉 Please run /clear now, then restart with:
/implement specs/support/ticket-system.md --scenario 2

This keeps context focused and improves AI performance.
```

### Step 4.6: Repeat for Each Scenario

```bash
/clear
/implement specs/support/ticket-system.md --scenario 2
# Implement, then /clear

/clear
/implement specs/support/ticket-system.md --scenario 3
# Implement, then /clear

/clear
/implement specs/support/ticket-system.md --scenario 4
# Done!
```

---

## 🎉 Result: Working Feature

After all scenarios are implemented, you have:

### ✅ Database
- `tickets` table with all fields
- `ticket_responses` table for staff replies
- Migrations applied

### ✅ Backend
- `TicketService` with full CRUD logic
- `TicketResponseService` for replies
- All business logic tested

### ✅ API Routes
- `POST /api/support/tickets` - Create ticket
- `GET /api/support/tickets` - List user's tickets
- `GET /api/support/tickets/[id]` - Get ticket details
- `POST /api/support/tickets/[id]/responses` - Add staff response
- `PATCH /api/support/tickets/[id]/status` - Update status

### ✅ Frontend
- Create ticket form
- Ticket list view
- Ticket detail page
- Staff response interface
- Status update UI

### ✅ Tests
- 15 unit tests (services)
- 12 API integration tests (routes)
- All passing ✅

### ✅ Documentation
- Spec file with all scenarios marked ✅
- GROUNDWORK.md documenting infrastructure
- Production Learnings section ready for feedback

---

## 📖 Quick Reference

### Command Cheat Sheet

```bash
# Phase 1: Create specification
/create-specs "your feature idea"

# Phase 2: Generate tasks (optional)
/create-tasks specs/{domain}/{feature}.md

# Phase 3: Establish groundwork
/groundwork specs/{domain}/{feature}.md

# Phase 4: Implement scenarios
/implement specs/{domain}/{feature}.md --scenario 1
/clear  # After each scenario
/implement specs/{domain}/{feature}.md --scenario 2
# Repeat...
```

### Constitutional Principles (11 Articles)

1. **Simplicity First** - Minimal complexity, no future-proofing
2. **Anti-Abstraction** - Use frameworks directly
3. **Integration-First Testing** - Real databases, contract tests
4. **Test-First** - Red-Green-Refactor
5. **Module Structure** - Domain-driven
6. **Specification Quality** - Explicit uncertainties
7. **Complexity Tracking** - Document exceptions
8. **Vertical Slicing** - End-to-end per scenario
9. **Groundwork Separation** - Infrastructure only
10. **Context Management** - /clear between phases
11. **Bidirectional Feedback** - Production learnings

### Quality Gates

| Phase | Gates |
|-------|-------|
| `/create-specs` | Requirement completeness, What/How separation, YAGNI |
| `/groundwork` | Simplicity, Anti-abstraction, Justified infrastructure |
| `/implement` | Test-first, Vertical slicing, No guessing |

---

## 💡 Tips & Best Practices

### 1. Start Simple
Don't specify 10 scenarios. Start with 2-3 core scenarios. You can always add more later.

### 2. Mark Uncertainties
When in doubt, use `[NEEDS CLARIFICATION]` instead of letting the AI guess. Better to ask than to build the wrong thing.

### 3. Review Groundwork Carefully
The groundwork phase creates your foundation. Review it before moving on, because all scenarios will build on it.

### 4. One Scenario at a Time
Resist the urge to implement all scenarios at once. Smaller increments = better quality.

### 5. Use /clear Religiously
Context window degradation is real. `/clear` between phases keeps the AI sharp.

### 6. Trust the Process
The gates exist to prevent mistakes. If a gate fails, there's usually a good reason. Fix it before proceeding.

### 7. Document Exceptions
If you must violate a constitutional principle, document why in the "Complexity Tracking" section. Future you will thank you.

### 8. Production Feedback
After deploying, update the "Production Learnings" section in your spec. Real-world insights improve future features.

---

## 🆘 Troubleshooting

### "Specification has unresolved ambiguities"

**Problem**: `/implement` blocks because spec has `[NEEDS CLARIFICATION]` markers.

**Solution**: Edit the spec file and resolve all markers before running `/implement`.

### "Groundwork gate failed: Too complex"

**Problem**: Simplicity Gate failed because you're creating too much infrastructure.

**Solution**: Review what you're building. Are you future-proofing? Remove speculative features.

### "Tests are failing after implementation"

**Problem**: Implementation doesn't match the Gherkin scenario.

**Solution**: Review the scenario's Given/When/Then. Tests should directly map to these. Fix implementation or clarify scenario.

### "AI is making assumptions"

**Problem**: AI implemented something you didn't specify.

**Solution**: Add uncertainty markers to spec. The enhanced commands force the AI to ask instead of guess.

---

## 📚 Further Learning

- **Constitution**: `.claude/constitution.md` - Read all 11 articles
- **Full Workflow**: `.claude/BDD-WORKFLOW.md` - Complete guide
- **Commands**: `.claude/commands/` - Detailed command documentation
- **Architecture**: `docs/architecture/` - System design patterns

---

## 🎯 Next Steps

1. **Try the example**: Build the support ticketing system following this guide
2. **Build your own feature**: Pick a simple feature and go through all phases
3. **Experiment with gates**: Try violating a gate to see what happens
4. **Share feedback**: Update this quickstart with your learnings

---

**Happy coding!** 🚀

The constitutional BDD workflow is designed to help you build better software, faster, with systematic quality controls. Trust the process, follow the gates, and watch your code quality improve.
