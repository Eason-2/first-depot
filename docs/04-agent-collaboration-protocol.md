# Agent Collaboration Protocol

## Execution order
1. Orchestrator Agent creates sprint plan and assigns tasks.
2. Product Prototype Agent validates UX and editorial workflow.
3. Ingestion Agent and Ranking Agent build data pipeline in parallel.
4. Content Generation Agent consumes ranked topics for draft creation.
5. QA Guardrail Agent approves or rejects drafts.
6. Publishing DevOps Agent publishes approved drafts and monitors health.

## Handoffs
- Each agent writes outputs to `deliverables/<domain>/`.
- Handoff must include assumptions, test evidence, and known gaps.
- Orchestrator blocks downstream work if upstream acceptance criteria fail.

## Cadence
- Daily: standup update from all agents.
- Every 2 days: integration checkpoint.
- Weekly: KPI review and backlog reprioritization.

## Escalation rules
- P0 blocker > 24h: escalate to Orchestrator.
- Repeated publish failure (>2 in 24h): pause auto mode.
- Source API outage > 12h: switch to fallback source set.
