# ADR-004: AI Integration and Email Delivery Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-25
- **Feature:** ai-reminder-agent
- **Context:** The reminder agent requires integration with two external service categories: (1) AI/LLM for generating personalized email content, and (2) email delivery for sending reminders to users. The technology choices for these services must work together and align with project constraints (Python backend, cost-effectiveness, reliability). The integration patterns affect development velocity, operational costs, and system reliability.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - API costs, vendor dependencies, email deliverability
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Multiple LLM and email providers evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects costs, integrations, monitoring, and user experience
-->

## Decision

**Use Gemini API (via OpenAI SDK) for AI generation and SMTP (Gmail/SendGrid/SES) for email delivery.**

Implementation details:

### AI Integration Stack
- **LLM Provider**: Google Gemini API
  - Model: `gemini-1.5-flash` (primary), `gemini-1.5-pro` (fallback for complex cases)
  - Reasoning: Cost-effective ($0.075/1M input tokens), fast inference, competitive quality

- **Integration Library**: OpenAI Python SDK
  - Base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
  - Reasoning: Gemini supports OpenAI-compatible API, allowing easy migration if needed

- **Configuration**:
  ```python
  from openai import OpenAI

  client = OpenAI(
      api_key=os.getenv("GEMINI_API_KEY"),
      base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
  )
  ```

### Email Delivery Stack
- **Protocol**: SMTP with STARTTLS encryption

- **Provider Strategy** (tiered by scale):
  - **MVP (0-1k emails/day)**: Gmail SMTP with App Password
    - Free tier sufficient
    - Easy setup with existing Google Workspace account
    - 500 emails/day limit acceptable for MVP

  - **Growth (1k-10k emails/day)**: SendGrid or AWS SES
    - SendGrid: $15/month for 40k emails
    - AWS SES: $0.10 per 1,000 emails
    - Better deliverability rates (SPF/DKIM/DMARC support)

  - **Scale (10k+ emails/day)**: AWS SES with dedicated IP
    - Reputation management
    - Advanced analytics

- **Integration Library**: `aiosmtplib` (async SMTP client)
  - Reasoning: Native async/await support, integrates with APScheduler

- **Retry Strategy**: `tenacity` library
  - Max 3 attempts per email
  - Exponential backoff: 1s, 2s, 4s
  - Retry on transient SMTP errors only (4xx codes)

### Integration Pattern
```python
# AI Generation
async def generate_email(task: Task) -> EmailContent:
    try:
        response = await client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
            timeout=10
        )
        return EmailContent(subject=..., body=response.content)
    except Exception as e:
        logger.error(f"Gemini API failed: {e}")
        return generate_fallback_template(task)

# Email Delivery
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
async def send_email(to: str, subject: str, body: str):
    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=587,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True
    )
```

## Consequences

### Positive

**AI Integration**:
- **Cost Efficiency**: Gemini Flash is 10x cheaper than GPT-4 ($0.075 vs $0.75 per 1M tokens)
- **Fast Inference**: Avg response time <500ms vs 1-2s for GPT-4
- **OpenAI SDK Compatibility**: Easy migration to OpenAI, Anthropic, or other providers
- **No Vendor Lock-In**: Standard OpenAI-compatible API allows provider swapping
- **Sufficient Quality**: Gemini Flash quality adequate for 2-3 sentence reminders

**Email Delivery**:
- **Tiered Scaling**: Start free (Gmail), pay as you grow (SendGrid/SES)
- **Standard Protocol**: SMTP is universal, any provider can replace another
- **Async Performance**: `aiosmtplib` integrates seamlessly with async scheduler
- **Built-in Retry**: `tenacity` handles transient failures automatically
- **Email Authentication**: All providers support SPF/DKIM/DMARC for deliverability

**Combined Stack**:
- **Python Native**: All libraries are first-class Python packages
- **Observable**: Easy to add logging, metrics, and tracing
- **Testable**: Can mock both AI and SMTP for unit tests
- **Low Operational Complexity**: No custom infrastructure, all managed services

### Negative

**AI Integration**:
- **Gemini Dependency**: Google could change pricing, deprecate API, or impose limits
- **Quality Variance**: Gemini Flash may produce lower-quality output than GPT-4 in some cases
- **Limited Control**: Cannot fine-tune Gemini models for specific reminder styles
- **API Outages**: Google API downtime affects email personalization (mitigated by fallback)

**Email Delivery**:
- **Gmail Limits**: 500 emails/day ceiling requires quick migration at scale
- **Reputation Management**: Must warm up IPs and monitor bounce rates
- **Deliverability Complexity**: SPF/DKIM/DMARC configuration non-trivial
- **Cost Growth**: Email costs scale linearly with user base
- **Provider Migration**: Changing providers requires DNS updates, IP warming

**Combined Stack**:
- **Dual Dependency**: Failures in either Gemini or SMTP affect user experience
- **Cost Uncertainty**: API pricing changes could significantly impact unit economics
- **No Multi-Cloud Redundancy**: Single provider for each service (no failover)

## Alternatives Considered

### Alternative 1: OpenAI GPT-4 for AI Generation
**Why Considered**: Best-in-class quality, well-documented, widely adopted

**Why Rejected**:
- **10x Cost**: $0.75/1M input tokens vs $0.075 for Gemini Flash
- **At Scale**: 10k reminders/day = ~$220/month (GPT-4) vs $22/month (Gemini)
- **Overkill**: Reminder emails don't require GPT-4's advanced reasoning
- **Latency**: Slower inference (1-2s vs 500ms)

**When to Reconsider**: If user feedback shows Gemini quality insufficient for engagement

### Alternative 2: Anthropic Claude for AI Generation
**Why Considered**: Excellent instruction-following, safety-focused

**Why Rejected**:
- **No OpenAI-Compatible API**: Requires custom SDK integration
- **Higher Cost**: $3/1M input tokens (Claude Haiku) vs $0.075 (Gemini Flash)
- **Migration Complexity**: Cannot use OpenAI SDK, harder to swap later

### Alternative 3: SendGrid/Twilio SendGrid from Day 1
**Why Considered**: Better deliverability, higher limits, professional features

**Why Rejected**:
- **Unnecessary for MVP**: 500 emails/day Gmail limit sufficient for initial validation
- **Cost**: $15/month vs $0 for Gmail during validation phase
- **Setup Overhead**: Requires account setup, API key management, DNS configuration
- **YAGNI**: Add when actually needed (>500 emails/day)

**Migration Plan**: When Gmail limits hit, switch to SendGrid (1-day setup)

### Alternative 4: AWS SES from Day 1
**Why Considered**: Lowest cost at scale, AWS ecosystem integration

**Why Rejected**:
- **Sandbox Mode**: New accounts start in sandbox (must request production access)
- **Reputation Building**: Requires IP warming period (weeks)
- **Complexity**: More configuration than Gmail/SendGrid
- **Not Needed Yet**: Gmail sufficient for MVP

**Migration Plan**: When >10k emails/day, migrate to SES with dedicated IP

### Alternative 5: Mailgun for Email Delivery
**Why Considered**: Developer-friendly API, good documentation

**Why Rejected**:
- **Cost**: $35/month for 50k emails vs $5/month for SES (same volume)
- **Less Popular**: Smaller community than SendGrid/SES
- **Feature Parity**: No significant advantages over SendGrid for our use case

### Alternative 6: Self-Hosted Email Server (Postfix/Exim)
**Why Considered**: Zero per-email cost, full control

**Why Rejected**:
- **Deliverability Nightmare**: High probability of landing in spam
- **Operational Burden**: Requires managing servers, security, uptime
- **Reputation Management**: IP reputation takes months to build
- **Blacklist Risk**: Shared IPs often blacklisted
- **Not Core Competency**: Focus on product, not email infrastructure

## References

- Feature Spec: `specs/ai-reminder-agent/spec.md` (Section 2 "Technology Stack", Section 5 "AI Email Generation")
- Implementation Plan: `specs/ai-reminder-agent/plan.md` (Phase 2 "Core Agent Logic", Phase 4 "Email System")
- Related ADRs: ADR-002 (AI Email Generation Strategy - complementary decision on fallback)
- Evaluator Evidence: Cost analysis in tasks.md estimates $22/month for 10k emails with Gemini vs $220/month with GPT-4

## Cost Projection

### AI Costs (10,000 reminders/day)
- Prompt: ~150 tokens/email (task context)
- Completion: ~50 tokens/email (2-3 sentences)
- Total: 200 tokens × 10k emails = 2M tokens/day
- Monthly: 60M tokens × $0.075/1M = $4.50/month

### Email Costs (10,000 reminders/day)
- Gmail: Cannot support this volume (500/day limit)
- SendGrid: 300k emails/month = $19/month
- AWS SES: 300k emails × $0.10/1k = $30/month

**Total Monthly Cost at 10k emails/day**: $23.50 (SendGrid) or $34.50 (SES)

**Unit Economics**: $0.00078 per reminder (fully loaded)

## Migration Triggers

**Trigger for Email Provider Upgrade**:
- Gmail → SendGrid: When daily volume exceeds 400 emails (80% of limit)
- SendGrid → AWS SES: When monthly cost exceeds $50 OR deliverability falls below 95%

**Trigger for LLM Provider Switch**:
- Gemini → OpenAI GPT-4: If user engagement metrics show <3/5 avg rating for AI emails
- Gemini → Claude: If Google imposes restrictive rate limits or policy changes
