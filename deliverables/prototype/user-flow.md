# User Flow (Phase 0)

## Flow A: Manual review mode (default)
1. Scheduler triggers ingestion at set interval.
2. User opens Trend Board and selects one ranked topic.
3. User clicks Generate Draft.
4. Draft Studio displays article with citations.
5. QA precheck runs.
6. If pass, user schedules publish; if fail, user edits and reruns QA.
7. Publish Queue executes at scheduled time.
8. Insights updates after publish.

## Flow B: Auto publish mode (trusted)
1. Scheduler runs ingestion -> ranking -> generation.
2. QA gate must pass all required checks.
3. Publish job enters auto queue.
4. System publishes and notifies user with evidence packet.

## Failure paths
- Ingestion source outage: fallback source set + degraded mode warning.
- Low-confidence draft: force manual approval.
- Publish adapter failure: retry with exponential backoff and hold state.

## Click-path tests
- Test 1: Configure source and run connection test in <= 4 steps.
- Test 2: Generate draft from top topic and schedule in <= 6 steps.
- Test 3: Trigger failed QA and verify remediation guidance appears.
- Test 4: Rollback a published job and confirm status audit trail.
