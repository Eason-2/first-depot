# MVP Task Board

## P0 - must have
- [ ] Define source API contract and normalized event schema.
- [ ] Implement 3 connectors (NewsAPI, Hacker News, arXiv).
- [ ] Build dedup clustering by URL + semantic similarity.
- [ ] Implement topic scoring function and explainability fields.
- [ ] Create draft generation pipeline with citation insertion.
- [ ] Add quality gate: factual and plagiarism checks.
- [ ] Build publish queue with review and auto modes.
- [ ] Integrate at least one CMS adapter.
- [ ] Add scheduler retry logic and alerting.

## P1 - should have
- [ ] SEO metadata auto generation (slug, meta description, OG tags).
- [ ] Internal link recommender for older posts.
- [ ] Topic diversity guardrail to prevent repeated themes.
- [ ] Cost dashboard per generated article.

## P2 - nice to have
- [ ] Newsletter auto-compilation.
- [ ] Social post snippets after publish.
- [ ] Multi-language translation pipeline.

## Suggested repo structure
- `apps/web` - blog and admin UI.
- `apps/api` - backend service.
- `workers/ingestion` - fetch + normalize.
- `workers/generation` - draft + QA.
- `infra/` - deployment, monitoring, IaC.
- `docs/` - specs, runbooks, prompts.
