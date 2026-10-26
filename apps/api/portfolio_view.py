from __future__ import annotations

from html import escape
from pathlib import Path

from apps.api.blog_view import list_post_files, post_slug_from_path, read_post_summary
from apps.api.codex_guide import render_codex_guide
from apps.api.journal_view import render_journal_cards
from apps.api.site_view import SITE_NAME, render_about_nav, render_site_page


def _tag_row(tags: tuple[str, ...]) -> str:
    return "<div class='tag-row'>" + "".join(f"<span class='tag'>{escape(tag)}</span>" for tag in tags) + "</div>"


def _latest_posts(publish_dir: Path, limit: int = 3) -> str:
    cards: list[str] = []
    for post in list_post_files(publish_dir)[:limit]:
        slug = post_slug_from_path(post)
        title, preview, date = read_post_summary(post)
        cards.append(
            "<article class='card'>"
            f"<p class='card-kicker'>{escape(date)}</p>"
            f"<h3><a href='/blog/{escape(slug)}'>{escape(title)}</a></h3>"
            f"<p>{escape(preview)}</p>"
            "</article>"
        )
    return "".join(cards) or "<p>暂时还没有简报。</p>"


def render_home_page(publish_dir: Path, journal_dir: Path | None = None) -> str:
    journal_dir = journal_dir if journal_dir is not None else publish_dir.parent / "journal"
    body = (
        "<section class='hero'>"
        "<div class='hero-copy'>"
        "<p class='eyebrow'>Learn · Explore · Build</p>"
        "<h1 class='hero-title'>先把 AI 用起来，<br />再做出自己的作品。</h1>"
        "<p class='lead'>从安装、账号、Key 和环境变量开始，把第一次配置走通。这里也分享 AI 新变化，记录我的尝试、踩坑和想法。</p>"
        "<div class='hero-actions'><a class='button-link' href='/tutorials#codex-start'>先把 AI 用起来</a><a class='button-link secondary' href='/blog'>发现 AI 新资讯</a></div>"
        "<p class='hero-note'>想了解我的 AI 应用开发实践？<a href='/projects'>看看项目案例 →</a></p></div>"
        "<aside class='workflow-visual' aria-label='第一次配置 AI 工具的路线'>"
        "<p class='eyebrow'>Windows 默认 · Mac 可切换</p><h2>从不会配置，到收到第一条回复</h2>"
        "<div class='workflow-step'><b>01</b><span><strong>选好系统，安装工具</strong><br />打开哪个窗口、输入什么，逐步说明</span></div>"
        "<div class='workflow-step'><b>02</b><span><strong>把账号和 Key 配置好</strong><br />分清两种登录方式，检查环境变量</span></div>"
        "<div class='workflow-step'><b>03</b><span><strong>收到回复，确认能用</strong><br />先完成一次调用，再开始实际练习</span></div>"
        "</aside></section>"
        "<section class='section'><div class='section-heading'><p class='eyebrow'>第一课</p><h2>先解决卡住你的那一步</h2><p>这次用 Codex 命令行版走通安装与配置。Windows 和 Mac 分开讲，每一步都说明成功的标志；已经能用，再去做网页练习。</p></div>"
        "<div class='grid-3'>"
        "<article class='card'><p class='card-kicker'>01 · 从头开始</p><h3><a href='/tutorials#setup-terminal'>软件怎么装，命令在哪输？</a></h3><p>从打开 PowerShell 或 Mac 终端开始，安装基础环境和 Codex，检查版本。</p></article>"
        "<article class='card'><p class='card-kicker'>02 · 配置卡点</p><h3><a href='/tutorials#setup-key'>Key 填哪，环境变量怎么设？</a></h3><p>从创建自己的 Key，到让工具读到它，解释每一步的作用与费用边界。</p></article>"
        "<article class='card'><p class='card-kicker'>03 · 找到原因</p><h3><a href='/tutorials#codex-help'>照着做了，为什么还是报错？</a></h3><p>按找不到命令、读不到 Key、认证失败、额度和网络问题逐项排查。</p></article>"
        "</div></section>"
        "<section class='section'><div class='section-heading'><p class='eyebrow'>Briefing</p><h2>最新知行简报</h2><p>发现 AI 新工具、产品更新与研究进展，保留原始来源，方便继续追踪。</p></div>"
        f"<div class='grid-3'>{_latest_posts(publish_dir)}</div><p style='margin-top:20px'><a href='/blog'>查看全部简报 →</a></p></section>"
        "<section class='section'><div class='section-heading'><p class='eyebrow'>Learning in public</p><h2>最近的实践与思考</h2><p>亲自试过的方法、项目里的卡点，以及仍在琢磨的想法。</p></div>"
        f"<div class='reading-grid'>{render_journal_cards(journal_dir, limit=3)}</div>"
        "<p style='margin-top:20px'><a href='/about/journal'>查看全部成长记录 →</a></p></section>"
        "<section class='section'><div class='section-heading'><p class='eyebrow'>Selected work</p><h2>从模型调用走到业务执行</h2><p>项目不仅展示结果，也说明流程、技术取舍、失败处理和效果衡量。</p></div>"
        "<div class='grid-3'>"
        "<article class='card'><p class='card-kicker'>AGENT · E-COMMERCE</p><h3>商品自动化上架 Agent</h3><p>串联市场调研、竞品分析、Listing 生成、规则校验与 Shopify 页面执行。</p>" + _tag_row(("LangGraph", "Tool Calling", "Playwright")) + "</article>"
        "<article class='card'><p class='card-kicker'>RAG · CUSTOMER SERVICE</p><h3>TikTok 智能客服</h3><p>基于企业知识库回答商品、物流与售后问题，用检索筛选和业务边界降低幻觉。</p>" + _tag_row(("RAG", "FastAPI", "结构化输出")) + "</article>"
        "<article class='card'><p class='card-kicker'>AUTOMATION · CONTENT</p><h3>AI 资讯自动发布系统</h3><p>完成采集、聚类排序、长文生成、QA、GitHub Actions 与 Pages 发布闭环。</p>" + _tag_row(("Python", "QA", "GitHub Actions")) + "</article>"
        "</div><p style='margin-top:20px'><a href='/projects'>查看完整项目与技术细节 →</a></p></section>"
    )
    return render_site_page(SITE_NAME, body, "/")


def render_projects_page() -> str:
    body = (
        "<header class='page-intro'><p class='eyebrow'>Project cases</p><h1>项目案例</h1><p>围绕真实业务问题，展示我如何完成流程拆解、模型接入、工具执行、质量控制和部署迭代。</p></header>"
        "<section class='case-study'><div><p class='card-kicker'>01 · AGENT</p><h2>商品自动化上架 Agent</h2>" + _tag_row(("LangGraph", "Function Calling", "Playwright", "Shopify")) + "</div>"
        "<div class='case-body'><div><h3>业务问题</h3><p>商品资料分散，市场调研、竞品分析、Listing 编写和页面录入依赖人工串联，耗时且容易遗漏规则。</p></div><div><h3>我的工作</h3><p>将流程拆为可复用节点，定义输入输出、状态流转、失败回退和人工确认；封装数据处理与浏览器自动化工具。</p></div><div><h3>工程处理</h3><p>使用结构化输出约束标题、卖点、描述与标签，在写入前完成必填项、格式和业务规则校验，并加入超时重试与异常捕获。</p></div><div><h3>结果</h3><p>形成从调研到 Shopify 上架的完整闭环，市场调研耗时减少约 90%，商品上架耗时减少约 70%。</p></div></div></section>"
        "<section class='case-study'><div><p class='card-kicker'>02 · RAG</p><h2>TikTok 智能客服机器人</h2>" + _tag_row(("RAG", "知识库", "Prompt 约束", "FastAPI")) + "</div>"
        "<div class='case-body'><div><h3>业务问题</h3><p>商品、物流与售后规则散落在不同资料中，人工客服重复回答高频问题，且模型容易产生无依据内容。</p></div><div><h3>我的工作</h3><p>清洗并分类企业资料，搭建问题解析、知识检索、上下文组装、Prompt 约束与 LLM 生成链路。</p></div><div><h3>工程处理</h3><p>按问题类型优化召回筛选与回答策略，明确业务边界；无法找到依据时转人工处理，而不是强行生成。</p></div><div><h3>结果</h3><p>约 90% 的常见咨询可由机器人自动处理，人工客服处理量降低约 80%，资源转向复杂售后场景。</p></div></div></section>"
        "<section class='case-study'><div><p class='card-kicker'>03 · AUTOMATION</p><h2>AI 资讯博客自动化发布系统</h2>" + _tag_row(("Python", "Hacker News", "arXiv", "GitHub Pages")) + "</div>"
        "<div class='case-body'><div><h3>业务问题</h3><p>资讯采集、筛选、写作与发布步骤分散，难以保持固定更新节奏，也缺少统一质量门槛。</p></div><div><h3>我的工作</h3><p>独立搭建采集、标准化、聚类排序、长文生成、QA 和发布链路，并提供本地 HTTP API。</p></div><div><h3>工程处理</h3><p>加入引用覆盖、结构风格和安全词检查，通过 GitHub Actions 定时运行并部署到 GitHub Pages。</p></div><div><h3>下一轮优化</h3><p>正在提高选题相关性、标题区分度和重复检测，把稳定发布进一步升级为稳定产出有价值的内容。</p></div></div></section>"
    )
    return render_site_page("项目案例", body, "/projects", "AI Agent、RAG、业务自动化与内容发布项目案例。")


def render_tutorials_page() -> str:
    body = (
        "<div class='tutorials-page'>"
        + render_codex_guide() +
        "<details class='tutorial-supplement' id='local-toolbox'><summary><span><strong>另一个项目：本地 AI 工具箱</strong><span>需要 Python 和 Git · 有基础后再看</span></span></summary>"
        "<p>Mock 模式只演示流程；接入 Ollama 后才会调用本地模型。</p>"
        "<div class='tutorial-block'><ol class='tutorial-steps'>"
        "<li><h3>准备环境</h3><p>安装 Python 3.11 或更高版本和 Git。需要本地模型时，再安装 Ollama。</p></li>"
        "<li><h3>克隆并进入项目</h3><pre><code>git clone https://github.com/Eason-2/first-depot.git\ncd first-depot</code></pre></li>"
        "<li><h3>启动本地服务</h3><pre><code>python -m scripts.start_api</code></pre><p>服务默认监听 <code>http://127.0.0.1:8088</code>。</p></li>"
        "<li><h3>打开工具箱</h3><pre><code>http://127.0.0.1:8088/ai-toolbox</code></pre><p>先使用默认 Mock 模式验证界面和工作流。</p></li>"
        "<li><h3>切换到 Ollama</h3><pre><code>ollama pull qwen2.5:3b-instruct</code></pre><p>在“设置”中选择 <code>ollama</code>，地址填写 <code>http://127.0.0.1:11434</code>，模型填写对应名称。</p></li>"
        "<li><h3>验证与排错</h3><p>先检查本地 API 是否运行，再检查 Ollama 模型名称和地址。公网 GitHub Pages 仅展示界面，不会连接你电脑上的本地服务。</p></li>"
        "</ol><div class='hero-actions'><a class='button-link' href='/ai-toolbox'>打开 AI 工具箱</a><a class='button-link secondary' href='https://github.com/Eason-2/first-depot' target='_blank' rel='noopener noreferrer'>查看源码</a></div></div></details>"
        "<aside class='tutorial-planned' id='learning-path'><p>计划补充：工具调用、文档问答、LangGraph 工作流与服务部署。完整教程尚未发布。</p></aside></div>"
    )
    return render_site_page("实战教程", body, "/tutorials", "Windows 默认、macOS 可切换的 AI 配置教程：安装 Codex、登录账号、创建 API Key、设置环境变量、验证调用与排错。")


def render_about_page() -> str:
    body = (
        "<header class='page-intro'><p class='eyebrow'>About</p><h1>关于我</h1><p>计算机科学与技术专业，方向是 AI Agent、LLM 应用开发与大模型工程化落地。这里也记录学习过程，以及做项目时的思考。</p></header>"
        + render_about_nav("/about") +
        "<section class='section'><div class='card'><p class='card-kicker'>LEARNING IN PUBLIC</p><h2>成长记录</h2><p>工具试用、项目进展、踩坑和想法，写下过程里值得留下的部分。</p><a class='button-link secondary' href='/about/journal'>阅读我的实践与思考 →</a></div></section>"
        "<section class='section about-grid'><div class='card'><p class='card-kicker'>CURRENT FOCUS</p><h2>让 AI 真正进入业务流程</h2><p>我关注的不只是模型回答得好不好，也关注它能否调用工具、遵守规则、处理异常、留下日志并稳定部署。</p><p><a href='https://github.com/Eason-2' target='_blank' rel='noopener noreferrer'>查看我的 GitHub →</a></p></div>"
        "<div><div class='timeline-item'><h3>AI Agent 开发实习</h3><p>参与跨境电商商品智能运营、TikTok 智能客服和运营流程自动化，负责 Workflow、工具调用、RAG 与服务工程化。</p></div>"
        "<div class='timeline-item'><h3>AI 资讯博客自动化发布系统</h3><p>独立完成从数据源到静态站发布的端到端链路，并持续优化内容质量和用户体验。</p></div>"
        "<div class='timeline-item'><h3>Web 开发实践</h3><p>具备页面开发、接口联调、性能优化、回归测试和线上问题复盘经验。</p></div></div></section>"
        "<section class='section'><div class='section-heading'><p class='eyebrow'>Capabilities</p><h2>能力结构</h2></div><div class='grid-3'>"
        "<article class='card'><h3>AI 应用</h3><p>LLM、Prompt Engineering、Agent、RAG、Function Calling、MCP、LangChain、LangGraph。</p></article>"
        "<article class='card'><h3>后端与数据</h3><p>Python、FastAPI、Flask、MySQL、Redis、SQLite、Pandas、RESTful API、数据清洗。</p></article>"
        "<article class='card'><h3>自动化与工程化</h3><p>Playwright、Selenium、Docker、Git、Linux、pytest、超时重试、异常处理与日志排障。</p></article>"
        "</div></section>"
    )
    return render_site_page("关于我", body, "/about", "AI 应用开发经历、项目方向与技术能力。")
