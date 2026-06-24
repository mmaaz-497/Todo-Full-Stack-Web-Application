# Agentic Execution Discipline Intelligence

## Skill Name
Spec-Driven Development (SDD) Workflow Discipline and Agentic Execution

## Scope
Enforce structured development workflow through specification, planning, task decomposition, and atomic execution with validation gates.

## Trigger Conditions

Apply this skill when:
- Starting any new feature or significant work
- User requests implementation without prior specification
- Scope creep is detected during implementation
- Planning phase is being skipped
- Tasks are not atomic or testable
- Validation is missing before progression
- Context needs to be preserved for future execution

## Core Intelligence Rules

### 1. Mandatory Workflow Sequence
**Rule**: NEVER skip the SDD workflow. Every feature follows: Spec → Plan → Tasks → Implementation.

**Workflow Stages**:
```
1. /sp.specify   → spec.md        (WHAT to build)
2. /sp.plan      → plan.md        (HOW to build)
3. /sp.tasks     → tasks.md       (ATOMIC steps)
4. /sp.implement → code changes   (EXECUTE tasks)
5. /sp.phr       → prompt records (CAPTURE knowledge)
```

**Enforcement**:
```
IF user requests implementation without spec:
   STOP
   Run /sp.specify first
   Get approval
   THEN proceed

IF user requests code without plan:
   STOP
   Run /sp.plan first
   Get approval
   THEN proceed
```

**Rationale**: Spec-first prevents rework, scope creep, and ensures shared understanding.

### 2. Specification Completeness
**Rule**: Specifications must answer WHO, WHAT, WHY, WHEN. Not HOW (that's in plan.md).

**spec.md Structure**:
```markdown
# Feature Name

## Problem Statement
[Why this feature exists, what problem it solves]

## User Stories
- As a [user type], I want [goal] so that [benefit]

## Requirements
### Functional Requirements
- MUST: Critical requirements
- SHOULD: Important but not blocking
- COULD: Nice-to-have

### Non-Functional Requirements
- Performance: [latency, throughput targets]
- Security: [authentication, authorization, data protection]
- Reliability: [uptime, error handling]

## Acceptance Criteria
- [ ] Testable criterion 1
- [ ] Testable criterion 2

## Out of Scope
[Explicitly state what is NOT included]

## Open Questions
[Clarifications needed before planning]
```

**Validation Gates**:
- [ ] Problem statement is clear
- [ ] Acceptance criteria are testable
- [ ] Out-of-scope is explicitly defined
- [ ] Open questions are resolved or flagged

### 3. Planning Rigor
**Rule**: Plans must include architecture decisions, component design, API contracts, data models, and risk analysis.

**plan.md Structure**:
```markdown
# Implementation Plan: [Feature Name]

## Architecture Decisions
### Decision 1: [Choice]
- Options Considered: A, B, C
- Trade-offs: ...
- Rationale: ...

## Component Design
### Component 1: [Name]
- Responsibility: ...
- Dependencies: ...
- Interfaces: ...

## API Contracts
### Endpoint: POST /api/tasks
Request:
```json
{ "title": "string", ... }
```
Response:
```json
{ "id": "int", ... }
```

## Data Model
### Table: tasks
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  ...
);
```

## Risk Analysis
### Risk 1: [Description]
- Impact: High/Medium/Low
- Mitigation: ...

## Implementation Phases
1. Phase 1: [Description] (Deliverables: ...)
2. Phase 2: ...
```

**Validation Gates**:
- [ ] Architectural decisions documented with rationale
- [ ] API contracts defined (no ambiguity)
- [ ] Data model complete
- [ ] Risks identified with mitigation
- [ ] Phases break work into deployable increments

### 4. Atomic Task Decomposition
**Rule**: Every task in tasks.md must be atomic (1-2 hours max), testable, and have clear acceptance criteria.

**Task Format**:
```markdown
- [ ] T001 Create backend/api-service/app/models/priority.py with Priority enum
  - Acceptance: File exists, enum has 4 values (low, medium, high, urgent)
  - Test: Import succeeds, values accessible
```

**Atomic Task Characteristics**:
- **Single Responsibility**: One clear deliverable
- **Time-Bound**: 1-2 hours maximum
- **Testable**: Clear success criteria
- **Independent**: Minimal dependencies on other tasks
- **Reversible**: Can be rolled back if needed

**Task Anti-Patterns**:
```
❌ "Implement user authentication" (too large)
✓ "Create backend/auth-service/app/auth.py with verify_token function"

❌ "Fix bugs" (not specific)
✓ "Fix NullPointerException in TaskService.getTaskById at line 42"

❌ "Improve performance" (not measurable)
✓ "Add index on tasks.user_id to reduce query time from 500ms to <50ms"
```

### 5. Task Execution Discipline
**Rule**: Execute tasks in order. Mark complete ONLY when acceptance criteria met.

**Execution Pattern**:
```
FOR EACH task in tasks.md:
   1. Read task and acceptance criteria
   2. Execute task
   3. Validate acceptance criteria
   4. IF criteria met:
        Mark task [X]
        Commit changes
      ELSE:
        Fix issues
        Retry validation
   5. Move to next task
```

**Progress Tracking**:
```markdown
# tasks.md
- [X] T001 Create models/priority.py ✓ Completed
- [X] T002 Update models.py to import Priority ✓ Completed
- [ ] T003 Add priority field to Task model (IN PROGRESS)
- [ ] T004 Create migration script
```

**Enforcement**:
- Update tasks.md in real-time as tasks complete
- NEVER mark incomplete tasks as done
- NEVER skip tasks without justification

### 6. Scope Control
**Rule**: Reject scope creep. If new requirements emerge, update spec.md and re-plan.

**Scope Creep Detection**:
```
IF implementing feature not in spec.md:
   STOP
   Ask: "This is not in spec. Should we add it?"
   IF yes:
      Update spec.md
      Update plan.md
      Update tasks.md
      Get approval
      Resume
   ELSE:
      Skip and document as future work
```

**Examples**:
```
User: "Also add email notifications for task completion"
Agent: "Email notifications are not in spec.md. This is scope creep. Options:
        1. Add to spec, re-plan (adds 2-3 days)
        2. Defer to Phase 2
        Which do you prefer?"

User: "Let's defer to Phase 2"
Agent: "Noted. Added to spec.md 'Out of Scope' section."
```

### 7. Validation Before Progression
**Rule**: Do not proceed to next phase without validation and approval.

**Validation Gates**:
```
After /sp.specify:
   ✓ spec.md complete and reviewed
   ✓ Acceptance criteria testable
   ✓ Open questions resolved
   → Get user approval before /sp.plan

After /sp.plan:
   ✓ plan.md complete with architecture, data model, API contracts
   ✓ Risks identified
   → Get user approval before /sp.tasks

After /sp.tasks:
   ✓ tasks.md has atomic, testable tasks
   ✓ All phases mapped to tasks
   → Get user approval before /sp.implement

After /sp.implement:
   ✓ All tasks marked [X]
   ✓ Acceptance criteria met
   ✓ Tests pass
   → Feature complete
```

**Checkpoint Questions**:
- "Spec complete. Does this capture all requirements?"
- "Plan complete. Does this approach make sense?"
- "391 tasks identified. Ready to start implementation?"

### 8. Knowledge Capture via PHRs
**Rule**: After completing work, create Prompt History Record (PHR) to preserve context and decisions.

**PHR Triggers**:
- Completed feature implementation
- Significant architectural decision
- Debugging session with learnings
- Planning or specification work
- Multi-step workflows

**PHR Content**:
```markdown
---
id: 001
title: Phase V Kafka Event Backbone Implementation
stage: implementation
date: 2026-01-03
feature: phase-v-cloud-deployment
model: claude-sonnet-4-5
---

## User Prompt
[Complete user request verbatim]

## Response Summary
[Key actions taken, decisions made]

## Outcomes
- Created 6 Kubernetes YAML manifests for Kafka
- Implemented DaprPublisher with event publishing
- Integrated event publishing into API CRUD operations

## Key Decisions
1. Redpanda over Strimzi for local dev (66% memory reduction)
2. Single dlq-events topic for all failures (simpler ops)

## Files Changed
- kubernetes/kafka/local/strimzi-operator.yaml (created)
- backend/api-service/app/events/publisher.py (created)
- backend/api-service/routes/tasks.py (modified)

## Tests
- Manual: Imported publisher successfully
- Pending: Integration tests with Dapr sidecar
```

**Routing**:
```
Constitution changes → history/prompts/constitution/
Feature work → history/prompts/{feature-name}/
General → history/prompts/general/
```

### 9. ADR Suggestion Discipline
**Rule**: Suggest ADR creation for architecturally significant decisions. Never auto-create.

**ADR Significance Test**:
```
IF (decision has long-term consequences)
   AND (multiple options were considered)
   AND (decision affects system design across components)
THEN suggest ADR
ELSE document in plan.md only
```

**ADR Suggestion Pattern**:
```
Agent: "📋 Architectural decision detected: Redpanda vs Strimzi for Kafka deployment.
        This affects local dev experience and resource usage.
        Document reasoning and tradeoffs? Run `/sp.adr kafka-deployment-choice`"

User: "Yes, create ADR"
Agent: Runs /sp.adr kafka-deployment-choice
```

**When to Suggest ADR**:
- Choice of framework (React vs Vue, FastAPI vs Django)
- Data model design (SQL vs NoSQL, schema choices)
- Authentication/authorization approach
- Deployment strategy (Kubernetes, serverless, VMs)
- Integration pattern (REST, gRPC, events)

**When NOT to Suggest ADR**:
- Variable naming
- Code formatting
- Minor refactoring
- Trivial configuration changes

### 10. Error Recovery and Rollback
**Rule**: If errors occur, do not continue blindly. Fix, validate, then resume.

**Error Handling Pattern**:
```
IF error during task execution:
   1. Analyze error (syntax, logic, dependency)
   2. Determine impact (task only, or cascade)
   3. Fix error
   4. Re-validate acceptance criteria
   5. IF fixed:
        Mark task complete
        Continue
      ELSE:
        Ask user for guidance
```

**Rollback Strategy**:
```
IF breaking change introduced:
   1. Git revert or rollback
   2. Document issue in PHR
   3. Update plan.md with new approach
   4. Resume from last known good state
```

## Anti-Patterns to Avoid

### ❌ Jumping Straight to Code
**Anti-Pattern**: User says "implement feature X" → Agent writes code immediately.
**Fix**: Run /sp.specify → /sp.plan → /sp.tasks → implement.

### ❌ Skipping Planning
**Anti-Pattern**: Spec exists, but agent starts coding without plan.
**Fix**: Always create plan.md before implementation.

### ❌ Vague Tasks
**Anti-Pattern**: "Implement authentication" as single task.
**Fix**: Break into atomic tasks: create models, implement JWT, add middleware, etc.

### ❌ Marking Incomplete Work Done
**Anti-Pattern**: Task says "Add tests", no tests written, marked [X].
**Fix**: Only mark [X] when acceptance criteria fully met.

### ❌ Undocumented Decisions
**Anti-Pattern**: Major architectural choice made, no record of rationale.
**Fix**: Document in plan.md or create ADR.

### ❌ Ignoring Validation Gates
**Anti-Pattern**: Moving from spec to tasks without plan.
**Fix**: Enforce plan.md creation and approval.

### ❌ No PHR After Work
**Anti-Pattern**: Completing feature, moving to next without creating PHR.
**Fix**: Always create PHR to capture context.

### ❌ Scope Creep Acceptance
**Anti-Pattern**: User adds requirement mid-implementation, agent complies without updating spec.
**Fix**: Flag scope creep, update spec, re-plan.

## Decision Heuristics

### When to Run /sp.specify
```
IF (new feature request OR significant change):
   Run /sp.specify
ELSE IF (trivial change like typo fix):
   Skip, document in commit message
ELSE IF (unclear if trivial):
   Default to /sp.specify (better safe than sorry)
```

### When to Run /sp.plan
```
IF spec exists AND no plan exists:
   MUST run /sp.plan
ELSE IF spec changed significantly:
   Re-run /sp.plan
ELSE:
   Use existing plan
```

### When to Run /sp.tasks
```
IF plan exists AND no tasks exist:
   MUST run /sp.tasks
ELSE IF plan changed:
   Re-run /sp.tasks
ELSE:
   Use existing tasks
```

### When to Create ADR
```
IF (decision affects > 1 component OR long-term impact OR multiple valid options):
   Suggest ADR
ELSE:
   Document in plan.md
```

### When to Create PHR
```
IF (completed implementation OR planning OR multi-turn debugging):
   Create PHR
ELSE IF (single trivial command):
   Skip PHR
ELSE (default):
   Create PHR
```

## Workflow Examples

### Example 1: New Feature Request
```
User: "Add task priority feature"

Agent:
1. "No spec found. Running /sp.specify..."
2. Creates spec.md with requirements, acceptance criteria
3. "Spec complete. Review and approve?"
4. User: "Approved"
5. "Running /sp.plan..."
6. Creates plan.md with data model, API changes
7. "Plan complete. Approve?"
8. User: "Approved"
9. "Running /sp.tasks..."
10. Creates tasks.md with 12 atomic tasks
11. "391 tasks total. Start implementation?"
12. User: "Yes"
13. Executes tasks, marks complete in real-time
14. "All tasks complete. Creating PHR..."
15. Creates PHR in history/prompts/task-priority/
```

### Example 2: Mid-Implementation Scope Change
```
User: "Also add task tags"

Agent:
1. "Task tags are not in spec.md. This is scope creep."
2. "Options:
    - Add to current spec (requires re-planning, +2 days)
    - Defer to Phase 2
    Which do you prefer?"
3. User: "Add to current spec"
4. "Updating spec.md with task tags requirement..."
5. "Re-running /sp.plan to incorporate tags..."
6. "Plan updated. 8 new tasks added to tasks.md."
7. "Resuming implementation..."
```

### Example 3: Error During Implementation
```
Task: "T042 Create strimzi-operator.yaml"

Agent:
1. Creates file
2. Validation: Syntax error on line 15
3. "Error detected: Invalid YAML syntax"
4. Fixes error
5. Re-validates: File is valid
6. Marks task [X]
7. Continues to T043
```

## Validation Checklist

Before marking phase complete:
- [ ] /sp.specify run and spec.md created
- [ ] /sp.plan run and plan.md created with architecture, API contracts, data model
- [ ] /sp.tasks run and tasks.md created with atomic tasks
- [ ] All tasks have clear acceptance criteria
- [ ] No task takes > 2 hours to complete
- [ ] Validation gates passed at each phase
- [ ] Scope creep detected and handled
- [ ] PHR created after significant work
- [ ] ADR suggested for architectural decisions
- [ ] All [X] tasks meet acceptance criteria
- [ ] No tasks skipped without justification

## Progress Reporting Template

```
Progress Report: [Feature Name]

Phase: [Specification/Planning/Tasks/Implementation]

Status:
- Total Tasks: 391
- Completed: 66 (16.9%)
- In Progress: 1
- Pending: 324

Current Task: T067 - Create Dapr pub/sub component YAML

Recent Completions:
- ✓ Phase 1: Spec Validation (17 tasks)
- ✓ Phase 2: Advanced Features (24 tasks)
- ✓ Phase 3: Kafka Event Backbone (25 tasks)

Next Milestone: Phase 4 - Dapr Integration (20 tasks)

Blockers: None

Risks:
- Risk 1: [Description, Mitigation]
```

## Time Estimation Guidelines

```
Specification:    10-15% of total effort
Planning:         15-20% of total effort
Task Breakdown:   5-10% of total effort
Implementation:   50-60% of total effort
Validation:       10-15% of total effort
Documentation:    5-10% of total effort
```

**Example**: 100-hour feature
- Spec: 10-15 hours
- Plan: 15-20 hours
- Tasks: 5-10 hours
- Implementation: 50-60 hours
- Validation: 10-15 hours
- Docs: 5-10 hours
