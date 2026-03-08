# Wireframe Spec (Phase 0)

## Scope
This low-fidelity prototype covers the solo-creator daily workflow from trend discovery to scheduled publish.

## Screen map
1. Source Config
2. Trend Board
3. Draft Studio
4. Publish Queue
5. Insights Dashboard

## Screen details

### 1) Source Config
- Purpose: manage open API sources and filtering policy.
- Primary KPI: ingestion freshness and source health.
- Components:
  - Source list with status badge (healthy/degraded/down)
  - API key vault reference (no plain text display)
  - Topic include/exclude rules
  - Save and test connection action
- States:
  - Success: latest sync timestamp visible
  - Failure: error code + retry action

### 2) Trend Board
- Purpose: show ranked topic candidates.
- Primary KPI: top-topic relevance and diversity.
- Components:
  - Ranked cards (score, confidence, source count)
  - Explainability panel (recency, engagement, credibility)
  - Action buttons (Generate Draft / Ignore / Pin)
- States:
  - Empty: no candidates found for interval
  - Warning: low-confidence cluster

### 3) Draft Studio
- Purpose: generate and edit article drafts.
- Primary KPI: draft acceptance rate.
- Components:
  - Structured article sections template
  - Source citation side panel
  - AI rewrite controls (tone, depth, length)
  - QA precheck button
- States:
  - Ready: citation coverage >= target
  - Blocked: missing citation on factual claim

### 4) Publish Queue
- Purpose: schedule release and control approvals.
- Primary KPI: publish success rate and latency.
- Components:
  - Job table (status, schedule time, retry count)
  - Mode selector (manual approval / auto publish)
  - Rollback button
- States:
  - Queued / Running / Published / Failed / RolledBack

### 5) Insights Dashboard
- Purpose: measure business and content quality outcomes.
- Primary KPI: traffic growth and correction rate.
- Components:
  - Views, CTR, avg read time
  - Time-to-publish and QA fail reasons
  - Cost per generated article

## Cross-screen interactions
- From Trend Board -> Draft Studio passes selected topic cluster ID.
- From Draft Studio -> Publish Queue passes draft ID + QA report.
- From Publish Queue -> Insights Dashboard writes publish outcome metrics.

## Acceptance criteria
- User can complete one end-to-end draft and schedule flow in <= 5 clicks from Trend Board.
- Every screen has clear success and failure feedback.
- Every factual paragraph in Draft Studio can open citation reference.
