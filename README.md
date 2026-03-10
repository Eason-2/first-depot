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

### Start public daemon with a fixed long-term URL (Cloudflare named tunnel)
```bash
set ENABLE_CLOUDFLARE_TUNNEL=1
set CLOUDFLARE_TUNNEL_TOKEN=<your_named_tunnel_token>
set PUBLIC_BASE_URL=https://blog.example.com
python -m scripts.daemon
```

Notes:
- `CLOUDFLARE_TUNNEL_TOKEN` uses your Cloudflare named tunnel (stable domain).
- `PUBLIC_BASE_URL` is used by local tooling/status files to show your fixed URL.
- This still depends on your PC staying online.

## Always-on fixed URL (recommended): GitHub Pages (free)
This mode keeps your blog online even when your computer is off.

1. Push this project to a GitHub repository.
2. In GitHub repo settings, enable **Pages** and select **GitHub Actions** as source.
3. The workflow `.github/workflows/deploy-pages.yml` will build and publish static pages from `deliverables/published/*.md`.
4. (Optional custom domain) set repo variable `BLOG_CNAME` to your domain, e.g. `blog.example.com`.
5. Point DNS `CNAME` record to `<your-github-username>.github.io`.
6. For project repos (not `<username>.github.io` repo), blog URL includes repo path: `https://<username>.github.io/<repo>/blog/`.

After that, every time you edit markdown files in `deliverables/published/` and push to GitHub, the public site updates automatically.

Build static site locally:
```bash
python -m scripts.export_static_site --output-dir site
```

### Fully automatic publishing (no manual push)
Use workflow `.github/workflows/auto-publish-pages.yml`.

- Runs every 30 minutes (`cron`), executes one publish cycle (`python -m scripts.run_once`).
- If a new post is published to `deliverables/published/`, it auto-commits and pushes to your repo.
- Then it rebuilds and deploys GitHub Pages automatically.
- Your readers can keep using the same fixed URL even when your PC is off.

Required GitHub settings:
- `Settings -> Pages`: source = `GitHub Actions`
- (Optional but recommended) `Settings -> Secrets and variables -> Actions -> Secrets`:
  - `NEWSAPI_KEY` (if you want NewsAPI source)
- (Optional custom domain) `Settings -> Secrets and variables -> Actions -> Variables`:
  - `BLOG_CNAME=blog.example.com`
  - `BLOG_BASE_PATH=/first-depot` (optional override for project pages path)

### Local auto-publish + local auto git push (PC must stay on)
If you want to keep generation on your local machine and still update GitHub Pages automatically, enable git auto sync in daemon:

```bash
set ENABLE_GIT_AUTO_SYNC=1
set GIT_SYNC_PATHS=deliverables/published
python -m scripts.daemon
```

- Daemon keeps publishing posts locally.
- A sync thread auto-runs `git add/commit/push` for paths in `GIT_SYNC_PATHS`.
- GitHub Pages workflow then updates your public site.
- Requires local git login/auth to GitHub (one-time setup).
- If you use this mode, keep only one publishing source (local or cloud workflow) to avoid duplicate post races.

One-time prerequisites:
- Install Git for Windows.
- Ensure this local folder is a git repo linked to your GitHub repo (`origin`).
- Ensure `git push` works locally without interactive prompt (credential manager/PAT/SSH).

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
- `ENABLE_GIT_AUTO_SYNC`: set `1` to auto commit/push selected local paths
- `GIT_SYNC_PATHS`: comma-separated paths for auto git sync (default `deliverables/published`)
- `GIT_SYNC_REMOTE`: git remote for auto push (default `origin`)
- `GIT_SYNC_BRANCH`: optional branch name for auto push
- `GIT_SYNC_INTERVAL_SECONDS`: sync loop interval in daemon (default `120`)
- `CLOUDFLARE_TUNNEL_TOKEN`: optional named-tunnel token for stable domain
- `PUBLIC_BASE_URL`: optional fixed URL used for status display (example `https://blog.example.com`)

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

This enables local git auto sync by default. Use `--disable-git-sync` if you want to turn it off.

Install startup autostart with Cloudflare quick tunnel:
```bash
python -m scripts.windows.install_autostart --interval 30 --enable-tunnel --run-now
```

Install startup autostart with Cloudflare named tunnel + fixed URL:
```bash
python -m scripts.windows.install_autostart --interval 30 --cloudflare-token <token> --public-base-url https://blog.example.com --run-now
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
- Long-term fixed URL: use a Cloudflare named tunnel token (`CLOUDFLARE_TUNNEL_TOKEN`) and set `PUBLIC_BASE_URL`.
- Direct internet access without tunnel requires router port-forwarding TCP `8088` to this machine and firewall allow rule.
- If exposed publicly, use `ADMIN_TOKEN` for `POST /run-once` (set header `X-Admin-Token: <token>`).
- Auto-start installation writes token to `runtime/admin_token.txt`.
- Blog content is rendered from markdown files on each request; editing files in `deliverables/published/` is reflected after page refresh.

Example remote trigger:
```bash
curl -X POST http://<your-public-host>:8088/run-once -H "X-Admin-Token: <token>"
```

## Multi-agent docs
- Coordination protocol: `docs/04-agent-collaboration-protocol.md`
- Agent prompts: `docs/agent-prompts/`
