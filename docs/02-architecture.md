# Architecture

## High-level components
1. Source Connectors
   - Pull from open APIs (NewsAPI, GDELT, Reddit, Hacker News, arXiv, GitHub trends).
2. Ingestion Pipeline
   - Normalize schema, language detection, dedup fingerprints.
3. Ranking Engine
   - Score by recency, engagement, source credibility, AI relevance.
4. Content Generator
   - Build outline, draft, title variants, tags, and excerpt.
5. Quality Gate
   - Fact consistency checks, citation coverage, style linting.
6. Publisher
   - Push Markdown/HTML to target blog CMS.
7. Orchestrator
   - Scheduled workflows, retries, dead-letter queue.
8. Admin Console
   - Source config, queue management, human approval.

## Data flow
- Cron trigger -> fetch source feeds -> normalize records -> score topics -> pick candidates -> generate draft -> run QA -> publish -> log metrics.

## Core data entities
- `raw_items`: source payload snapshots.
- `topic_clusters`: merged events.
- `article_drafts`: generated versions with provenance.
- `publish_jobs`: schedule state machine.
- `quality_reports`: validation evidence and failures.

## Reliability design
- Retry with exponential backoff per source.
- Idempotent publish key per article.
- Alerting when ingestion or publish SLA breaches.
- Circuit breaker per unstable API provider.

## Security and compliance
- Store API keys in secret manager, never in plain text.
- Strip personal data from ingestion payloads where possible.
- Keep generation prompts and outputs auditable.
