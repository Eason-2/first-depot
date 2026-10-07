from __future__ import annotations

from html import escape
from pathlib import Path

from apps.api.blog_view import list_post_files, post_slug_from_path, read_post_summary
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
        "<h1 class='hero-title'>从第一次提问，<br />到做出自己的作品。</h1>"
        "<p class='lead'>分享能跟着操作的 AI 教程，发现值得关注的新变化，也记录我的尝试、踩坑和想法。</p>"
        "<div class='hero-actions'><a class='button-link' href='/tutorials#codex-start'>第一次使用 Codex</a><a class='button-link secondary' href='/blog'>发现 AI 新资讯</a></div>"
        "<p class='hero-note'>想了解我的 AI 应用开发实践？<a href='/projects'>看看项目案例 →</a></p></div>"
        "<aside class='workflow-visual' aria-label='第一次使用 Codex 的练习路线'>"
        "<p class='eyebrow'>Your first Codex task</p><h2>让 Codex 带你做出一个小网页</h2>"
        "<div class='workflow-step'><b>01</b><span><strong>打开项目文件夹</strong><br />先让 Codex 只读了解文件，不急着修改</span></div>"
        "<div class='workflow-step'><b>02</b><span><strong>说清楚第一个任务</strong><br />从一个最小的个人介绍网页开始</span></div>"
        "<div class='workflow-step'><b>03</b><span><strong>查看、运行、再确认</strong><br />读懂修改内容，检查结果后再继续</span></div>"
        "</aside></section>"
        "<section class='section'><div class='section-heading'><p class='eyebrow'>Start with Codex</p><h2>零基础，从 Codex 的第一个任务开始</h2><p>不要求你先会编程。先让 Codex 读懂一个安全的小项目，再用计划、修改和检查完成一个小网页。</p></div>"
        "<div class='grid-3'>"
        "<article class='card'><p class='card-kicker'>01 · 认识入口</p><h3><a href='/tutorials#choose-tool'>打开 Codex</a></h3><p>先选择网页、桌面应用或进阶工具，知道它将访问哪个项目。</p></article>"
        "<article class='card'><p class='card-kicker'>02 · 第一个任务</p><h3><a href='/tutorials#first-task'>做一个个人介绍网页</a></h3><p>先让 Codex 给计划，再决定是否执行，边做边理解文件变化。</p></article>"
        "<article class='card'><p class='card-kicker'>03 · 检查结果</p><h3><a href='/tutorials#check-result'>看懂修改并运行</a></h3><p>查看差异、打开页面、运行检查，把安全边界放在每一步。</p></article>"
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
        "<header class='page-intro'><p class='eyebrow'>Practical tutorials</p><h1>实战教程</h1><p>从第一次使用 Codex 开始，带着一个小项目理解 AI 如何读文件、改代码和运行检查。</p>"
        "<div class='hero-actions'><a href='#codex-start'>从零开始使用 Codex ↓</a><a href='#local-toolbox'>本地工具箱 ↓</a><a href='#learning-path'>进阶路线 ↓</a></div></header>"
        "<section class='section' id='codex-start'><div class='section-heading'><p class='eyebrow'>Beginner Codex guide</p><h2>从零开始使用 Codex</h2><p>这是一条给纯小白的路线：先认识入口，再让 Codex 只读分析一个安全的小项目，最后完成一个可以在浏览器打开的个人介绍网页。</p></div>"
        "<article class='tutorial-block' id='choose-tool'><h3>1. 先认识 Codex，选择适合你的入口</h3>"
        "<p>Codex 是一个编程助手，可以阅读你选择的项目文件夹，协助编写或修改代码，并帮助你运行检查。它不是“按一下就全部完成”的按钮：你要看懂它准备做什么，检查修改结果，再决定下一步。</p>"
        "<p>第一次使用，最简单的是 <a href='https://chatgpt.com/codex' target='_blank' rel='noopener noreferrer'>网页 Codex</a>，不需要安装；如果你想处理电脑上的本地项目，可以安装 <a href='https://chatgpt.com/download' target='_blank' rel='noopener noreferrer'>ChatGPT 桌面应用</a>，登录后选择 Codex。CLI 和 IDE 扩展适合已经熟悉终端或编辑器的读者，可以留到后面。</p>"
        "<p>官方的 <a href='https://developers.openai.com/codex/quickstart' target='_blank' rel='noopener noreferrer'>Codex Quickstart</a> 会随着产品更新，登录方式和界面以官方页面当时的说明为准。</p></article>"
        "<article class='tutorial-block'><h3>2. 准备一个安全的小项目</h3>"
        "<p>在电脑上新建一个空文件夹，例如 <code>my-first-codex-project</code>。不要一开始选择整个磁盘，也不要把密码、API Key、Cookie、身份证号或客户资料放进去。重要项目先复制一份备份，或用 Git 保存一个可以回退的版本。</p>"
        "<p>打开 Codex 后，创建项目或选择这个文件夹。你会看到一个可以输入任务的对话区域；如果使用网页入口，则按页面提示进入 Codex 工作区。</p></article>"
        "<article class='tutorial-block' id='first-task'><h3>3. 发出第一条“只读”指令</h3><p>第一次先让 Codex 观察，不让它改文件。把下面这段话复制进去：</p>"
        "<pre class='prompt-example'><code>你是我的编程学习助手。\n先不要修改任何文件。\n请阅读当前项目结构，用普通中文告诉我：\n1. 当前有哪些文件；\n2. 每个文件可能负责什么；\n3. 如果我要做一个最简单的个人介绍网页，建议先从哪一步开始。\n不要运行删除、上传、发布或付费相关操作。</code></pre>"
        "<p>读完回答后，重点看它是否真的理解了当前文件夹。如果它误解了目录或提出了你不需要的操作，先追问或停止，不要急着执行。</p></article>"
        "<article class='tutorial-block'><h3>4. 做一个最小的个人介绍网页</h3><p>确认 Codex 的计划后，再把任务说小、说清楚：</p>"
        "<pre class='prompt-example'><code>请帮我创建一个最简单的个人介绍网页。\n先给我实现计划和准备修改的文件，暂时不要执行。\n网页包含：一句自我介绍、三个兴趣标签、一个联系方式占位符。\n使用最基础的 HTML 和 CSS，不要引入外部依赖。</code></pre>"
        "<p>先读计划，确认文件范围和实现方式都合理，再明确告诉它可以执行。第一次练习的目标是理解“提出需求 → 看计划 → 执行”，而不是一次完成很大的项目。</p></article>"
        "<article class='tutorial-block' id='check-result'><h3>5. 查看修改、打开网页、运行检查</h3>"
        "<p>执行后不要只看一句“已完成”。让 Codex 解释它做了什么：</p>"
        "<pre class='prompt-example'><code>请说明你刚才修改了哪些文件、每个文件为什么要改，\n并列出我应该重点检查的地方。</code></pre>"
        "<p>查看 diff 或文件内容，确认没有多余改动。然后继续询问如何验证：</p>"
        "<pre class='prompt-example'><code>请告诉我如何在本地打开这个网页。\n如果需要运行命令，请先解释每条命令的作用，\n不要自动执行删除、上传、发布或修改系统设置的命令。</code></pre>"
        "<p>按照说明在浏览器打开网页，检查文字、样式和链接是否符合预期。遇到报错时，把完整错误和相关文件交给 Codex，让它先分析原因，再提出最小修复方案。</p></article>"
        "<article class='tutorial-block'><h3>6. 记住这几条安全边界</h3>"
        "<ul><li>不要粘贴密码、API Key、Cookie、私密文件或客户信息。</li>"
        "<li>不要让 Codex 直接删除大量文件，也不要在不了解作用时运行命令。</li>"
        "<li>发布到 GitHub、推送代码、发送外部消息或产生付费操作前，先看清目标和变更。</li>"
        "<li>养成“先看计划，再看修改，最后运行检查”的习惯；重要项目先备份并使用 Git。</li></ul>"
        "<p>如果你不确定某一步是否安全，可以直接问：“这条命令会读取、修改或上传什么？如果失败会怎样？”让 Codex 先用普通话解释。</p>"
        "<a href='https://developers.openai.com/codex/developer-commands' target='_blank' rel='noopener noreferrer'>继续了解 Codex 的命令与工作方式 →</a></article>"
        "<article class='tutorial-block'><h3>完成第一次任务后，下一步学什么？</h3><p>你可以先修改网页文字和样式，再让 Codex 修复一个小 bug、写一个简单 Python 脚本，最后给项目增加测试。熟悉这条协作流程后，再进入 Agent、RAG 和工具调用。</p>"
        "<a href='/blog'>去知行简报发现 AI 新工具与产品变化 →</a></article></section>"
        "<section class='section' id='local-toolbox'><div class='section-heading'><p class='eyebrow'>Local tools</p><h2>在本地启动 AI 工具箱</h2><p>已经会用对话工具，并想尝试本地运行时，可以继续这一节。需要安装软件并使用终端；Mock 模式用于体验流程，Ollama 模式用于接入本地模型。</p></div>"
        "<div class='tutorial-block'><ol class='tutorial-steps'>"
        "<li><h3>准备环境</h3><p>安装 Python 3.11 或更高版本和 Git。需要本地模型时，再安装 Ollama。</p></li>"
        "<li><h3>克隆并进入项目</h3><pre><code>git clone https://github.com/Eason-2/first-depot.git\ncd first-depot</code></pre></li>"
        "<li><h3>启动本地服务</h3><pre><code>python -m scripts.start_api</code></pre><p>服务默认监听 <code>http://127.0.0.1:8088</code>。</p></li>"
        "<li><h3>打开工具箱</h3><pre><code>http://127.0.0.1:8088/ai-toolbox</code></pre><p>先使用默认 Mock 模式验证界面和工作流。</p></li>"
        "<li><h3>切换到 Ollama</h3><pre><code>ollama pull qwen2.5:3b-instruct</code></pre><p>在“设置”中选择 <code>ollama</code>，地址填写 <code>http://127.0.0.1:11434</code>，模型填写对应名称。</p></li>"
        "<li><h3>验证与排错</h3><p>先检查本地 API 是否运行，再检查 Ollama 模型名称和地址。公网 GitHub Pages 仅展示界面，不会连接你电脑上的本地服务。</p></li>"
        "</ol><div class='hero-actions'><a class='button-link' href='/ai-toolbox'>打开 AI 工具箱</a><a class='button-link secondary' href='https://github.com/Eason-2/first-depot' target='_blank' rel='noopener noreferrer'>查看源码</a></div></div></section>"
        "<section class='section' id='learning-path'><div class='section-heading'><p class='eyebrow'>Learning path</p><h2>后续教程路线</h2><p>以下是待补充的进阶主题，完整教程尚未发布。</p></div><div class='grid-2'>"
        "<article class='card'><p class='card-kicker'>01 · TOOL CALLING</p><h3>为 Agent 设计一个可靠工具</h3><p>输入 Schema、参数校验、返回格式、超时重试和人工确认。</p></article>"
        "<article class='card'><p class='card-kicker'>02 · RAG</p><h3>让文档问答给出引用依据</h3><p>文档清洗、切分、召回、重排、上下文组装与拒答策略。</p></article>"
        "<article class='card'><p class='card-kicker'>03 · WORKFLOW</p><h3>用 LangGraph 管理状态流转</h3><p>将多步骤任务拆成节点，并处理失败回退和断点恢复。</p></article>"
        "<article class='card'><p class='card-kicker'>04 · DELIVERY</p><h3>把 AI 服务部署成可维护应用</h3><p>FastAPI、Docker、日志、健康检查、密钥管理和持续部署。</p></article>"
        "</div></section>"
    )
    return render_site_page("实战教程", body, "/tutorials", "AI 工具、Agent、RAG 和自动化开发实战教程。")


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
