# AI News Blog Autopublisher

Automated personal blog pipeline that scans open APIs, ranks trending AI topics, generates drafts with citations, runs QA guardrails, and publishes on schedule.

## 给读者：AI 写作助手 / AI 工具箱怎么用（方案 3）

如果你是在博客里点进来的，请先注意：

- GitHub Pages 上的 `AI 写作助手` / `AI 工具箱` 页面主要是**展示入口**
- 真正可用的方式是：**把仓库拉到你自己电脑上，再本地启动**
- 如果你电脑里已经有 Ollama，这套方式最适合你

### 你会用到的本地地址

本地服务启动后，请在浏览器打开：

- 博客：`http://127.0.0.1:8088/blog`
- AI 工具箱：`http://127.0.0.1:8088/ai-toolbox`
- AI 写作助手：`http://127.0.0.1:8088/ai-writer`

> 不要直接把 GitHub Pages 页面当成在线 AI 服务来用；完整功能需要本地启动后才能使用。

### 第 1 步：准备环境

请先确认本机已经安装：

- Python 3.11+（本项目当前也可在 3.13 运行）
- Git
- Ollama（如果你想用本地模型）

如果你只想先体验流程，不装 Ollama 也可以，先用 `mock` 挡位。

### 第 2 步：克隆仓库

```bash
git clone https://github.com/Eason-2/first-depot.git
cd first-depot
```

如果你把仓库下载到了别的文件夹，只要后面命令都在**仓库根目录**运行即可。

### 第 3 步：启动本地 API

```bash
python -m scripts.start_api
```

看到下面这类输出就说明启动成功：

```text
API server listening on http://127.0.0.1:8088
```

此时浏览器打开：

```text
http://127.0.0.1:8088/blog
```

然后你就可以从本地博客页进入 `AI 工具箱` 或 `AI 写作助手`。

### 第 4 步：如果你要用 Ollama

先确认 Ollama 已经启动，并且本机有模型：

```bash
ollama list
```

如果还没有模型，可以先拉一个：

```bash
ollama pull qwen2.5:3b-instruct
```

然后在页面右上角点“设置”，填：

- 模式：`ollama`
- 服务地址：`http://127.0.0.1:11434`
- 模型：`qwen2.5:3b-instruct`
- API Key：`local`

再点击“应用”。

### 第 5 步：如果你不想折腾模型

直接使用默认的 `mock` 挡位即可。

这适合：

- 先看页面交互
- 先试整个流程
- 暂时没有安装 Ollama

### 常见问题

#### 1）为什么博客公网地址里点进去不能直接用？

因为 GitHub Pages 是静态站，那里主要是展示入口；真正执行 AI 请求的是你本地启动的 API 服务。

#### 2）为什么我填了 `127.0.0.1:11434` 还是不行？

因为你必须先启动本地 API：

```bash
python -m scripts.start_api
```

然后访问本地地址：

- `http://127.0.0.1:8088/ai-toolbox`
- `http://127.0.0.1:8088/ai-writer`

不是直接在 GitHub Pages 页面里操作。

#### 3）怎么停止服务？

回到运行 `python -m scripts.start_api` 的那个终端，按：

```text
Ctrl + C
```

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
- Extension guide: `docs/06-extension-guide.md`
- Agent prompts: `docs/agent-prompts/`

## 2026-03-16 AI 工具箱接入记录
- 已按“AI写作助手”的方式，把 `AI 工具箱` 直接接入博客服务，不再依赖单独本地网页或 iframe 外链。
- 博客首页在“知行简报”右侧保留独立入口：`/ai-toolbox`。
- 新增三挡位运行时：`mock` / `ollama` / `openai`。
- 运行时接口：
  - `GET /api/ai-toolbox/runtime`
  - `POST /api/ai-toolbox/runtime`
- 工具箱执行接口：
  - `POST /api/ai-toolbox/run`
- 健康检查：
  - `GET /api/ai-toolbox/health`
- 当前内置工具：学习计划、文档问答、简历优化、面试题生成、代码解释。
- 原博客文章列表、文章详情、`/run-once` 等原有能力保持不变。

### AI 工具箱可用环境变量
- `AI_TOOLBOX_PROVIDER`：默认挡位，支持 `mock` / `ollama` / `openai`
- `AI_TOOLBOX_BASE_URL`：工具箱模型服务地址
- `AI_TOOLBOX_MODEL`：工具箱默认模型名
- `AI_TOOLBOX_API_KEY`：OpenAI/兼容接口 Key
- `AI_TOOLBOX_TIMEOUT_SECONDS`：请求超时秒数
- `AI_TOOLBOX_MAX_RETRIES`：失败重试次数

### 2026-03-16 同日补充记录（公网 Pages / 清理）
- 已确认本地博客入口和公网 GitHub Pages 入口是两套链路：
  - 本地服务：`http://127.0.0.1:8088/blog`
  - 公网静态页：`https://eason-2.github.io/first-depot/blog/`
- 已补齐 GitHub Pages 静态导出逻辑，使 `AI 工具箱` 和 `AI 写作助手` 一样可被导出到静态站。
- 已更新静态导出脚本：
  - `scripts/export_static_site.py`
  - 新增导出目录：`/ai-toolbox/`
  - 新增导出资源：`ai-toolbox/app.css`、`ai-toolbox/app.js`
- 已验证公网访问可见：
  - 博客页可看到 `AI工具箱` 按钮
  - 工具箱静态入口：`https://eason-2.github.io/first-depot/ai-toolbox/`
- 本次操作中需要注意：
  - 机器上存在两份同名项目：`Desktop` 与 `projects`
  - 以后以 `C:\Users\32025\projects\ai-blog-autopublisher` 为当前实际使用项目
  - 为避免串项目，导出静态站时优先使用：
    - `python scripts\export_static_site.py --output-dir site --base-path /first-depot`
  - 不优先用：
    - `python -m scripts.export_static_site`
- 已完成仓库清理，避免误提交测试导出和历史备份：
  - 清理 `site_test/`
  - 清理 `知行简报版本1.0/`
  - `.gitignore` 已加入：
    - `site_test/`
    - `知行简报版本1.0/`
- 已完成清理提交并推送：
  - commit: `8d9ba2e`
  - message: `cleanup generated exports and backup files`
