# Prototype Design (Phase 0)

## Primary user
Solo creator who wants daily AI news posts with minimal manual effort and full control before publish.

## Core user journey
1. System ingests signals from selected APIs.
2. Dashboard shows ranked topic candidates.
3. User picks auto mode (publish) or review mode (approve first).
4. Agent drafts article with citations and metadata.
5. QA checks quality, style, and policy compliance.
6. Scheduler publishes and records metrics.

## Prototype screens
- Source Config: API keys, topic filters, blocked keywords.
- Trend Board: ranked topics with score rationale.
- Draft Studio: generated article + citations + edit controls.
- Publish Queue: schedule, state, retry, rollback.
- Insights: traffic, CTR, time-to-publish, correction rate.

## MVP content template
- Hook: why this matters now.
- News summary: what happened and who announced it.
- Practical impact: builders, businesses, users.
- Expert angle: interpreted insights and trade-offs.
- Sources: links and publish timestamps.

## Editorial guardrails
- Every factual claim maps to a source reference.
- Mark uncertainty when source confidence is low.
- Ban sensational language and unsupported predictions.
- Enforce plagiarism and similarity checks before publish.

## Prototype outputs
- Clickable low-fidelity dashboard wireframes.
- Example generated post from real API data.
- End-to-end flow demo with scheduler simulation.
