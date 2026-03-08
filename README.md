# AI News Blog Autopublisher

Automated personal blog pipeline that scans open APIs, ranks trending AI topics, generates drafts with citations, runs QA guardrails, and publishes on schedule.

## Workspace
- Fixed root: `C:/Users/32025/projects/ai-blog-autopublisher`
- All docs and outputs stay inside this directory.

## Current MVP status
- [x] Phase 0 prototype and docs
- [x] Phase 1 connector skeletons (NewsAPI + Hacker News + arXiv)
- [x] End-to-end pipeline (ingestion -> ranking -> generation -> QA -> publishing)
- [x] Local API endpoints and test suite

## Project structure
- `apps/api`: lightweight HTTP API server.
- `core`: config, models, storage, shared utilities.
- `workers/ingestion`: connectors + normalization.
- `workers/ranking`: clustering + scoring.
- `workers/generation`: markdown draft builder.
- `workers/qa`: quality gates.
- `workers/publishing`: scheduler + CMS adapters.
- `deliverables`: prototype docs and published markdown files.
- `runtime`: sqlite db and runtime snapshots.

## Quick start
```bash
python -m scripts.run_once
```

### Start scheduler loop
```bash
python -m scripts.run_scheduler
```

### Start local API
```bash
python -m scripts.start_api
```

### Start public API (listen on all interfaces)
```bash
python -m scripts.start_public_api
```

### Start public daemon (API + auto publish)
```bash
python -m scripts.start_public_daemon
```

### Start public daemon with Cloudflare quick tunnel
```bash
python -m scripts.start_public_tunnel
```

### Offline full demo (with mock data, auto-publish)
```bash
python -m scripts.demo_with_mock
```

Blog URL:
- `http://127.0.0.1:8088/blog`

API endpoints:
- `GET /health`
- `GET /latest-topics`
- `GET /latest-draft`
- `GET /last-run`
- `POST /run-once`

## Environment variables
- `AUTO_PUBLISH_MODE`: `manual` (default) or `auto`
- `SCHEDULE_INTERVAL_MINUTES`: scheduler cycle interval, default `60`
- `NEWSAPI_KEY`: enables NewsAPI connector
- `BLOG_HOST`: bind host, default `127.0.0.1` (public mode uses `0.0.0.0`)
- `BLOG_PORT`: bind port, default `8088`
- `ADMIN_TOKEN`: required for remote `POST /run-once` when exposed publicly
- `ENABLE_CLOUDFLARE_TUNNEL`: set `1` to start quick tunnel in daemon

## Outputs
- Runtime state: `runtime/`
- Published markdown: `deliverables/published/`
- Contracts: `apps/api/contracts/event-schema.json`

## Testing
```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Windows Auto Start + Timed Publishing
Install user-level startup autostart (API + scheduler daemon):
```bash
python -m scripts.windows.install_autostart --interval 30 --run-now
```

Install startup autostart with Cloudflare quick tunnel:
```bash
python -m scripts.windows.install_autostart --interval 30 --enable-tunnel --run-now
```

Install `cloudflared` binary into project runtime tools (for tunnel mode):
```bash
python -m scripts.windows.install_cloudflared
```

Remove startup autostart:
```bash
python -m scripts.windows.uninstall_autostart
```

Open Windows firewall port 8088 (run as admin PowerShell):
```bash
python -m scripts.windows.firewall_port open --port 8088
```

Show access info (local/LAN/tunnel):
```bash
python -m scripts.public_access_info
```

Optional (if your Windows account allows Task Scheduler creation):
```bash
python -m scripts.windows.install_tasks --interval 30 --run-now
```

## Public Internet Access Notes
- Quickest internet access: run with Cloudflare tunnel and share `runtime/public_tunnel_url.txt`.
- Direct internet access without tunnel requires router port-forwarding TCP `8088` to this machine and firewall allow rule.
- If exposed publicly, use `ADMIN_TOKEN` for `POST /run-once` (set header `X-Admin-Token: <token>`).
- Auto-start installation writes token to `runtime/admin_token.txt`.

Example remote trigger:
```bash
curl -X POST http://<your-public-host>:8088/run-once -H "X-Admin-Token: <token>"
```

## Multi-agent docs
- Coordination protocol: `docs/04-agent-collaboration-protocol.md`
- Agent prompts: `docs/agent-prompts/`
