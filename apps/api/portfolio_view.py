from __future__ import annotations

from html import escape
from pathlib import Path

from apps.api.blog_view import list_post_files, post_slug_from_path, read_post_summary
from apps.api.codex_guide import render_codex_guide
from apps.api.site_view import SITE_NAME, render_about_nav, render_site_page


def _tag_row(tags: tuple[str, ...]) -> str:
    return "<div class='tag-row'>" + "".join(f"<span class='tag'>{escape(tag)}</span>" for tag in tags) + "</div>"


def _latest_posts(publish_dir: Path, limit: int = 3) -> str:
    cards: list[str] = []
    for post in list_post_files(publish_dir)[:limit]:
        slug = post_slug_from_path(post)
        title, _, date = read_post_summary(post)
        # The home index uses the topic; the article retains its full title.
        title = title.removesuffix("：核心变化与验证重点")
        cards.append(
            "<article class='dispatch-row'>"
            f"<time datetime='{escape(date)}'>{escape(date)}</time>"
            f"<h3><a href='/blog/{escape(slug)}'>{escape(title)}</a></h3>"
            "<span aria-hidden='true'>↗</span>"
            "</article>"
        )
    return "".join(cards) or "<p>暂时还没有简报。</p>"


def _recent_notes(journal_dir: Path) -> str:
    notes: list[str] = []
    for post in list_post_files(journal_dir)[:3]:
        title, _, date = read_post_summary(post)
        href = "/about/journal/" + post_slug_from_path(post)
        notes.append(
            "<article class='card'>"
            f"<p class='card-kicker'>{escape(date)} · 成长记录</p>"
            f"<h3><a href='{escape(href, quote=True)}'>{escape(title)}</a></h3>"
            f"<a href='{escape(href, quote=True)}'>继续阅读 →</a>"
            "</article>"
        )
    return "".join(notes) or "<p>第一篇记录还在整理中。</p>"


def _publishing_diagram() -> str:
    return (
        "<figure class='publishing-sheet'>"
        "<figcaption><span>知行简报</span><span>发布流程 / 示意</span></figcaption>"
        "<div class='source-line'><span>Hacker News</span><span>arXiv</span><span>NewsAPI</span></div>"
        "<ol class='publishing-flow'>"
        "<li><span>01</span><div><strong>收集与筛选</strong><small>归一化 · 聚类 · 排序</small></div></li>"
        "<li><span>02</span><div><strong>生成文章</strong><small>整理内容，附上来源</small></div></li>"
        "<li><span>03</span><div><strong>检查后发布</strong><small>引用与结构检查 → GitHub Pages</small></div></li>"
        "</ol><p class='sheet-footnote'><span aria-hidden='true'>↳</span> 检查未通过的文章，不进入发布步骤。</p>"
        "</figure>"
    )


def render_home_page(publish_dir: Path, journal_dir: Path | None = None) -> str:
    journal_dir = journal_dir if journal_dir is not None else publish_dir.parent / "journal"
    body = (
        "<div class='portfolio-page home-notebook'>"
        "<section class='notebook-opening' aria-labelledby='home-title'>"
        "<div class='opening-copy'><p class='folio-label'>个人博客 <span>/</span> AI 应用开发</p>"
        "<h1 id='home-title'>边用，<br /><em>边记。</em></h1>"
        "<p class='opening-intro'>我把用 AI 的过程放在这里。<br />从第一次安装，到做项目时的尝试和想法。</p>"
        "<a class='ink-button' href='/tutorials#codex-start'>先把 AI 用起来 <span aria-hidden='true'>↗</span></a>"
        "<a class='quiet-link opening-secondary' href='/about/journal'>读读我的近况 <span aria-hidden='true'>→</span></a></div>"
        "<aside class='starter-cover' aria-labelledby='starter-title'>"
        "<div class='cover-top'><span>入门手册</span><span>01</span></div>"
        "<p class='cover-margin'>给还没用过 Codex 的你</p>"
        "<h2 id='starter-title'>装在哪？<br />Key 填哪？<br /><span>从这里开始。</span></h2>"
        "<p class='cover-caption'>打开哪个窗口、输入哪条命令，<br />按步骤来，直到收到第一条回复。</p>"
        "<a class='cover-link' href='/tutorials#codex-start'>打开安装教程 <span aria-hidden='true'>↗</span></a>"
        "<div class='cover-bottom'><span>Windows 默认</span><span>可切换 macOS</span></div>"
        "</aside></section>"
        "<nav class='quick-index' aria-label='常见配置问题'>"
        "<span>已经卡在某一步？</span>"
        "<a href='/tutorials#setup-terminal'>打开终端 <span aria-hidden='true'>↗</span></a>"
        "<a href='/tutorials#setup-key'>配置 Key <span aria-hidden='true'>↗</span></a>"
        "<a href='/tutorials#codex-help'>查找报错 <span aria-hidden='true'>↗</span></a></nav>"
        "<section class='notebook-section' aria-labelledby='work-title'>"
        "<div class='editorial-heading'><div><p class='folio-label'>01 / 项目选录</p><h2 id='work-title'>做过的项目</h2></div>"
        "<a class='quiet-link' href='/projects'>全部项目 <span aria-hidden='true'>↗</span></a></div>"
        "<div class='home-feature'>" + _publishing_diagram() +
        "<div class='feature-copy'><p class='folio-label'>个人项目 · 源码公开</p>"
        "<h3><a href='/projects#news-publisher'>这个博客，<br />也是一个项目。</a></h3>"
        "<p>知行简报背后有一套自动发布程序：收集 AI 资讯、筛选选题、生成文章，再发布到网站。</p>"
        "<p>程序能按时运行之后，标题重复、文章读起来太像，又成了要继续改的问题。</p>"
        "<a class='text-link' href='/projects#news-publisher'>看看它是怎么做的 <span aria-hidden='true'>→</span></a>"
        "</div></div>"
        "<div class='other-work'>"
        "<a href='/projects#listing-agent'><span class='work-index'>02</span><span><strong>商品自动化上架 Agent</strong><small>从整理商品资料，到填写 Shopify 页面</small></span><span aria-hidden='true'>↗</span></a>"
        "<a href='/projects#support-assistant'><span class='work-index'>03</span><span><strong>TikTok 智能客服</strong><small>查商品与售后资料，再回答用户的问题</small></span><span aria-hidden='true'>↗</span></a>"
        "</div></section>"
        "<div class='reading-desk'>"
        "<section aria-labelledby='briefing-title'><div class='editorial-heading'><div>"
        "<p class='folio-label'>02 / 关注外面的变化</p><h2 id='briefing-title'>知行简报</h2></div>"
        "<a class='quiet-link' href='/blog'>全部简报 ↗</a></div>"
        "<p class='section-caption'>AI 产品、工具和研究的新消息，文章里附有来源。</p>"
        f"<div class='dispatch-list'>{_latest_posts(publish_dir)}</div></section>"
        "<section class='journal-column' aria-labelledby='journal-title'><div class='editorial-heading'><div>"
        "<p class='folio-label'>03 / 留一点自己的记录</p><h2 id='journal-title'>最近在想</h2></div></div>"
        f"<div class='journal-notes'>{_recent_notes(journal_dir)}</div>"
        "<a class='quiet-link' href='/about/journal'>全部成长记录 ↗</a></section></div>"
        "<aside class='closing-note'><p>刚开始时，我也卡在安装、Key 和环境变量上。</p>"
        "<a class='text-link' href='/tutorials#codex-start'>所以，教程从这些地方讲起 <span aria-hidden='true'>→</span></a></aside></div>"
    )
    return render_site_page(SITE_NAME, body, "/")


def render_projects_page() -> str:
    body = (
        "<div class='portfolio-page project-notebook'>"
        "<header class='projects-opening'><p class='folio-label'>项目案例 <span>/</span> 过程与记录</p>"
        "<div><h1>做过的<br /><em>几个项目。</em></h1>"
        "<p>一个自己维护的博客，<br />两段工作中的 AI 应用实践。<br />这里写具体做法，也写还没解决好的问题。</p></div></header>"
        "<nav class='project-index' aria-label='项目目录'>"
        "<a href='#news-publisher'><span>01</span> 资讯发布 <span aria-hidden='true'>↓</span></a>"
        "<a href='#listing-agent'><span>02</span> 商品上架 <span aria-hidden='true'>↓</span></a>"
        "<a href='#support-assistant'><span>03</span> 智能客服 <span aria-hidden='true'>↓</span></a></nav>"
        "<article class='project-story' id='news-publisher' aria-labelledby='publisher-title'>"
        "<header class='story-heading'><span class='story-number'>01</span><div><p class='folio-label'>个人项目 · 源码公开</p>"
        "<h2 id='publisher-title'>让知行简报自己更新</h2><p>AI 资讯博客自动化发布系统</p></div></header>"
        "<div class='publisher-layout'><div class='story-prose'>"
        "<p class='story-lead'>你正在看的这个网站，<br />就是它的发布结果。</p>"
        "<p>我想持续关注 AI 资讯，又不想每次都重复找来源、整理文章、上传网页。这套程序把这些步骤接了起来。</p>"
        "<p>我负责从采集到发布的代码。内容先做标准化、聚类和排序，生成文章后检查引用与结构，再交给 GitHub Actions 导出静态页面。</p>"
        "<div class='project-actions'><a class='ink-button' href='/blog'>看知行简报 <span aria-hidden='true'>↗</span></a>"
        "<a class='text-link' href='https://github.com/Eason-2/first-depot' target='_blank' rel='noopener noreferrer'>看源码 ↗</a></div>"
        + _tag_row(("Python", "SQLite", "GitHub Actions", "GitHub Pages")) +
        "</div>" + _publishing_diagram() + "</div>"
        "<aside class='project-afterword'><span>还在改的地方</span><p>能定时发出来，只解决了一半。前面的文章出现过标题相近、段落像套模板的问题。标题和结构已经调整过，后续仍要逐篇看内容，不能把“发布成功”当成写得好。</p></aside></article>"
        "<article class='project-story' id='listing-agent' aria-labelledby='listing-title'>"
        "<header class='story-heading'><span class='story-number'>02</span><div><p class='folio-label'>工作实践 · 商品运营</p>"
        "<h2 id='listing-title'>把商品资料填进上架页面</h2><p>商品自动化上架 Agent</p></div></header>"
        "<div class='listing-layout'><div class='listing-sheet'>"
        "<p class='folio-label'>处理流程 / 示意</p>"
        "<div class='listing-input'><span>输入</span><strong>商品资料 · 市场与竞品信息</strong></div>"
        "<div class='listing-fields'><span>标题</span><span>卖点</span><span>描述</span><span>标签</span></div>"
        "<div class='listing-check'><span aria-hidden='true'>↳</span><p><strong>写入前检查</strong><br />必填项、格式、业务规则与人工确认</p></div>"
        "<div class='listing-output'><span>输出</span><strong>Shopify 商品页面</strong></div>"
        "</div><div class='story-prose'><h3>重复的不只是写文案。</h3>"
        "<p>整理商品资料、看竞品、写标题和卖点，最后还要一项项填进后台。中间任何一步漏了信息，后面都要回头补。</p>"
        "<p>我负责把这些步骤拆成工作流节点，约定每一步传什么数据，再用 Playwright 处理页面填写。LangGraph 管理步骤之间的状态，工具调用负责执行具体操作。</p>"
        "<h3>生成完，还不能直接上架。</h3>"
        "<p>标题、描述和标签先按约定格式输出；写入页面前，再检查字段和业务规则。遇到失败要有回退和人工确认的位置。</p>"
        + _tag_row(("LangGraph", "Function Calling", "Playwright", "Shopify")) + "</div></div></article>"
        "<article class='project-story' id='support-assistant' aria-labelledby='support-title'>"
        "<header class='story-heading'><span class='story-number'>03</span><div><p class='folio-label'>工作实践 · 客服知识库</p>"
        "<h2 id='support-title'>先查资料，再回答</h2><p>TikTok 智能客服机器人</p></div></header>"
        "<div class='support-layout'><div class='story-prose'><p class='story-lead'>商品、物流、售后，<br />答案要有出处。</p>"
        "<p>这类咨询的问题经常重复，依据却分散在不同资料里。我负责清洗、分类企业资料，再串起问题解析、知识检索和回答生成。</p>"
        "<p>检索结果会按问题类型筛选，和回答规则一起交给模型。找不到依据的问题，转给人工处理。</p>"
        + _tag_row(("RAG", "知识库", "Prompt 约束", "FastAPI")) + "</div>"
        "<aside class='answer-sheet' aria-label='客服回答流程示意'><p class='folio-label'>回答之前</p>"
        "<h3>资料里，<br />有这个答案吗？</h3>"
        "<div class='answer-route'><span>有依据</span><p>用检索到的资料组织回答</p><span aria-hidden='true'>↗</span></div>"
        "<div class='answer-route'><span>没找到</span><p>交给人工继续处理</p><span aria-hidden='true'>→</span></div>"
        "<p class='answer-note'>流程示意，不展示真实客户对话。</p></aside></div></article>"
        "<aside class='closing-note'><p>项目之外，也写一些学习中的事。</p>"
        "<a class='text-link' href='/about/journal'>去看成长记录 <span aria-hidden='true'>→</span></a></aside></div>"
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
