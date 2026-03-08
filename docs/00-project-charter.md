# Project Charter

## Problem statement
AI news moves quickly. Manual tracking and writing causes delays and content inconsistency.

## Product goal
Create an automated blog engine that discovers trending AI news from open APIs, produces structured drafts, and publishes on a schedule with quality controls.

## Success metrics (MVP)
- Freshness: at least 3 top stories ingested every 4 hours.
- Throughput: at least 1 publish-ready article per day.
- Quality: less than 5% factual corrections after publish.
- Reliability: scheduler success rate >= 99% per week.
- Growth: +20% month-over-month organic traffic after launch.

## In scope
- Multi-source API ingestion.
- Story scoring and deduplication.
- AI-assisted article generation (summary + opinion + references).
- Scheduled publish workflow with review gate.
- Basic admin dashboard and observability.

## Out of scope (MVP)
- Multi-language localization.
- Full social media automation.
- Advanced personalization by user segment.

## Constraints
- Use open or low-cost APIs.
- Support manual override before publish.
- Keep architecture modular so provider swaps are low-cost.

## Risks and mitigations
- Hallucination risk -> citation enforcement + fact-check stage.
- API instability -> source redundancy + retry + cached fallback.
- Duplicate/low-quality output -> similarity threshold + editorial rubric.
- SEO underperformance -> template standardization + internal linking.
