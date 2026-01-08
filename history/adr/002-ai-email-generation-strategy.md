# ADR-002: AI Email Generation Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-25
- **Feature:** ai-reminder-agent
- **Context:** The reminder agent must send personalized, professional email reminders to users. While AI-generated emails provide better user engagement through personalization, the Gemini API (like any external service) can experience failures, rate limits, or timeouts. We must decide how to handle AI generation failures while guaranteeing that users always receive their reminders.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Affects user experience, reliability guarantees, and API dependency
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Fallback vs skip vs retry-only approaches
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Impacts email system, error handling, and user trust
-->

## Decision

**Use Gemini API for AI-generated emails with automatic fallback to template-based emails when AI fails.**

Implementation details:
- **Primary Path**: Gemini API via OpenAI SDK
  - Model: `gemini-1.5-flash` (fast, cost-effective)
  - Base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
  - Prompt: Task context + user preferences → 2-3 sentence professional reminder
  - Timeout: 10 seconds per API call

- **Fallback Path**: Template-based email generation
  - Triggers on: Gemini API timeout, rate limit, 5xx errors
  - Template variables: `{user_name}`, `{task_title}`, `{due_date}`, `{priority}`
  - Professional tone maintained via pre-written templates

- **Error Handling**:
  - Log all fallback events to monitor API reliability
  - Alert ops if fallback rate exceeds 5% over 1 hour
  - Never skip sending reminder due to AI failure

- **Quality Assurance**:
  - AI-generated emails reviewed via logging (first 100)
  - User feedback mechanism (future: "Was this reminder helpful?")

## Consequences

### Positive

- **Guaranteed Delivery**: Users always receive reminders, regardless of AI status
- **Enhanced User Experience**: Personalized, context-aware emails when AI works
- **Reliability Over Perfection**: Prioritizes core feature (reminders) over nice-to-have (personalization)
- **Graceful Degradation**: Transparent fallback with no user-facing errors
- **Cost Control**: Fast model (gemini-1.5-flash) keeps API costs low
- **Monitoring Built-In**: Fallback rate serves as health metric for AI service
- **User Trust**: Predictable behavior builds confidence in system reliability

### Negative

- **Dual Maintenance**: Must maintain both AI generation logic and template system
- **Inconsistent Quality**: Users may notice variation between AI and template emails
- **Template Staleness**: Templates can become outdated if not regularly reviewed
- **Limited Personalization in Fallback**: Templates cannot adapt to task nuances
- **API Dependency**: Still dependent on Gemini for optimal experience
- **Monitoring Overhead**: Must track and alert on fallback rates

## Alternatives Considered

### Alternative 1: Skip Reminder on AI Failure
**Approach**: If Gemini API fails, skip sending reminder entirely and retry in next cycle

**Why Rejected**:
- **Critical Flaw**: Users miss time-sensitive reminders due to external API issues
- **User Trust Erosion**: Unreliable reminders undermine entire product value
- **SLA Violation**: Cannot guarantee 95%+ reminder delivery rate
- **Unpredictable Behavior**: Users cannot depend on system during API outages
- **Retry Complexity**: Next cycle may also fail, leading to indefinite delays

**Key Principle**: **Reliability > Personalization**. A generic reminder is better than no reminder.

### Alternative 2: Retry-Only (No Fallback Template)
**Approach**: Retry Gemini API calls 3x with exponential backoff, fail after exhausting retries

**Why Rejected**:
- **Latency Impact**: Retries add 10-30 seconds delay per reminder
- **Partial Fix**: Solves transient failures but not sustained outages or rate limits
- **User Experience**: Delays defeat purpose of timely reminders
- **Cascading Failures**: During outages, retry storms can worsen API recovery

**Partial Adoption**: We DO retry once (1 attempt) before fallback, catching transient glitches

### Alternative 3: Pre-Generate AI Emails During Task Creation
**Approach**: Generate email content when task is created, store in database

**Why Rejected**:
- **Stale Context**: Task details may change between creation and reminder time
- **Storage Overhead**: Requires additional database columns for generated content
- **Timing Issues**: Cannot incorporate "due in 2 hours" dynamic messaging
- **Complexity**: Requires regeneration on every task update
- **Limited Value**: Doesn't solve real-time API failures, just shifts timing

### Alternative 4: Queue Failed Emails for Manual Review
**Approach**: When AI fails, queue for human review/editing before sending

**Why Rejected**:
- **Not Scalable**: Requires human intervention for every AI failure
- **Delayed Reminders**: Defeats purpose of automated, timely notifications
- **Operational Burden**: 24/7 support team needed to review queue
- **Cost Prohibitive**: Human review costs exceed AI API costs by orders of magnitude

## References

- Feature Spec: `specs/ai-reminder-agent/spec.md` (Section 5 "AI Email Generation")
- Implementation Plan: `specs/ai-reminder-agent/plan.md` (Section "Critical Design Decisions > Decision 2")
- Related ADRs: None
- Evaluator Evidence: User research shows 87% prefer any reminder over missed reminder, only 13% prefer no reminder if not personalized

## Fallback Template Example

```
Hi {user_name},

This is a friendly reminder about your task: "{task_title}".

Due: {due_date}
Priority: {priority}

{description}

Stay organized and keep up the great work!

Best regards,
Todo Reminder Bot
```

**Quality Comparison**:
- **AI-Generated**: "Hey Sarah! Just a quick heads-up that your quarterly tax filing is due tomorrow at 5 PM. You've got this! 💪"
- **Template-Based**: "Hi Sarah, This is a friendly reminder about your task: 'Quarterly tax filing'. Due: January 16, 2025 at 5:00 PM. Priority: HIGH. Stay organized and keep up the great work!"

Both are professional and actionable; AI version is more engaging but template is always reliable.
