# Operations Runbook (MVP)

## Daily checks
- Verify `runtime/last_run.json` timestamp freshness.
- Verify publish queue status in sqlite `publish_jobs` table.
- Verify latest draft has QA pass before publish.

## Incident: source API outage
1. Confirm failing connector from logs/raw data count.
2. Keep pipeline running with available connectors.
3. Mark source as degraded and review topic diversity.

## Incident: QA failures spike
1. Inspect latest quality reports for reason code trends.
2. Tune generation template and citation policy.
3. Keep mode in `manual` until pass rate recovers.

## Incident: publish failure
1. Check `publish_jobs.error_message`.
2. Retry after adapter/config validation.
3. If repeated, switch adapter to `local_markdown` fallback.
