from __future__ import annotations

from html import escape


SITE_NAME = "AI 应用实践"
SITE_DESCRIPTION = "面向真实业务的 Agent、RAG、自动化与 AI 工具实践。"

_NAV_ITEMS = (
    ("首页", "/"),
    ("项目案例", "/projects"),
    ("实战教程", "/tutorials"),
    ("AI 工具箱", "/ai-toolbox"),
    ("知行简报", "/blog"),
    ("关于我", "/about"),
)


def render_site_nav(active_path: str) -> str:
    links: list[str] = []
    for label, path in _NAV_ITEMS:
        is_active = active_path == path or (path == "/blog" and active_path.startswith("/blog/"))
        if path == "/ai-toolbox" and active_path == "/ai-writer":
            is_active = True
        active_class = " is-active" if is_active else ""
        current = " aria-current='page'" if is_active else ""
        links.append(f"<a class='site-nav-link{active_class}' href='{path}'{current}>{label}</a>")

    return (
        "<header class='site-header'>"
        "<a class='site-brand' href='/' aria-label='返回首页'>"
        "<span class='site-brand-mark' aria-hidden='true'>AI</span>"
        "<span><strong>AI 应用实践</strong><small>Agent · RAG · 自动化</small></span>"
        "</a>"
        f"<nav class='site-nav' aria-label='一级导航'>{''.join(links)}</nav>"
        "</header>"
    )


def render_site_footer() -> str:
    return (
        "<footer class='site-footer'>"
        "<div><strong>AI 应用实践</strong><p>把大模型接入真实业务，让流程可执行、可验证、可上线。</p></div>"
        "<div class='footer-links'>"
        "<a href='https://github.com/Eason-2' target='_blank' rel='noopener noreferrer'>GitHub</a>"
        "<a href='/about'>关于我</a>"
        "</div>"
        "</footer>"
    )


def site_nav_css() -> str:
    return (
        ".site-header{position:sticky;top:0;z-index:40;max-width:1120px;margin:0 auto;min-height:84px;display:flex;align-items:center;justify-content:space-between;gap:24px;background:rgba(245,247,248,.96);backdrop-filter:blur(10px);}"
        ".site-brand{display:flex;align-items:center;gap:10px;color:#17202a;text-decoration:none;font-weight:700;white-space:nowrap;}"
        ".site-brand:hover{text-decoration:none;}"
        ".site-brand-mark{width:36px;height:36px;display:grid;place-items:center;background:#17202a;color:#fff;border-radius:6px;font-size:12px;}"
        ".site-brand span:last-child{display:flex;flex-direction:column;line-height:1.15;}"
        ".site-brand small{margin-top:4px;color:#64748b;font-size:11px;font-weight:600;}"
        ".site-nav{display:flex;align-items:center;justify-content:flex-end;gap:2px;flex-wrap:wrap;padding:5px;background:#fff;border:1px solid #d3dde3;border-radius:8px;box-shadow:0 3px 12px rgba(23,32,42,.08);}"
        ".site-nav-link{position:relative;min-height:42px;display:inline-flex;align-items:center;justify-content:center;padding:8px 13px;border-radius:5px;color:#273646;text-decoration:none;font-size:15px;font-weight:700;border-bottom:3px solid transparent;}"
        ".site-nav-link:hover{color:#0f766e;background:#eef6f5;text-decoration:none;}"
        ".site-nav-link:focus-visible{outline:2px solid #f97316;outline-offset:2px;}"
        ".site-nav-link.is-active{color:#0b625c;background:#e3f2f0;border-bottom-color:#f97316;}"
        ".site-footer{max-width:1120px;margin:64px auto 0;padding:28px 0;border-top:1px solid #dce3e8;display:flex;justify-content:space-between;gap:24px;color:#475569;}"
        ".site-footer p{margin:6px 0 0;}"
        ".footer-links{display:flex;align-items:flex-start;gap:18px;}"
        "@media(max-width:820px){.site-header{position:static;align-items:flex-start;flex-direction:column;padding:14px 0;gap:12px;}.site-nav{justify-content:flex-start;width:100%;}.site-nav-link{padding:7px 10px}.site-footer{flex-direction:column;margin-top:44px;}}"
        "@media(max-width:620px){.site-nav{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3px;padding:4px;}.site-nav-link{width:100%;text-align:center;padding:7px 3px;font-size:13px;}}"
    )


def render_site_page(title: str, body: str, active_path: str, description: str = SITE_DESCRIPTION) -> str:
    full_title = SITE_NAME if title == SITE_NAME else f"{title} | {SITE_NAME}"
    return (
        "<!doctype html><html lang='zh-CN'><head>"
        "<meta charset='utf-8' />"
        "<meta name='viewport' content='width=device-width, initial-scale=1' />"
        f"<title>{escape(full_title)}</title>"
        f"<meta name='description' content='{escape(description, quote=True)}' />"
        "<style>"
        ":root{color-scheme:light;font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;--ink:#17202a;--muted:#586675;--teal:#0f766e;--orange:#f97316;--line:#dce3e8;--paper:#fff;--canvas:#f5f7f8;}"
        "*{box-sizing:border-box;}body{margin:0;color:var(--ink);background:var(--canvas);line-height:1.75;}"
        "a{color:var(--teal);font-weight:650;text-decoration:none;}a:hover{text-decoration:underline;}"
        ".site-shell{padding:0 24px 48px;}main{max-width:1120px;margin:0 auto;}"
        "h1,h2,h3{line-height:1.3;letter-spacing:0;color:var(--ink);}h1{font-size:62px;margin:0;}h2{font-size:28px;margin:0 0 16px;}h3{font-size:19px;margin:0 0 8px;}"
        "p{margin:0 0 14px;color:var(--muted);}ul{margin:0;padding-left:20px;}li{margin:6px 0;}"
        ".eyebrow{margin:0 0 12px;color:var(--teal);font-size:13px;font-weight:800;text-transform:uppercase;}"
        ".hero{min-height:500px;display:grid;grid-template-columns:minmax(0,1.15fr) minmax(320px,.85fr);align-items:center;gap:54px;padding:56px 0 64px;border-bottom:1px solid var(--line);}"
        ".hero-copy{max-width:690px;}.hero-copy .lead{font-size:21px;max-width:640px;margin:20px 0 26px;color:#334155;}"
        ".hero-actions,.tag-row,.metric-row{display:flex;flex-wrap:wrap;gap:10px;}"
        ".button-link{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:9px 16px;border:1px solid var(--ink);border-radius:6px;background:var(--ink);color:#fff;}"
        ".button-link.secondary{background:transparent;color:var(--ink);}.button-link:hover{text-decoration:none;background:var(--teal);border-color:var(--teal);color:#fff;}"
        ".workflow-visual{background:#17202a;color:#fff;border-radius:8px;padding:24px;box-shadow:12px 12px 0 #f97316;}"
        ".workflow-visual h2{font-size:18px;color:#fff;margin-bottom:18px;}.workflow-step{display:grid;grid-template-columns:30px 1fr;gap:12px;align-items:start;padding:12px 0;border-top:1px solid #334155;}"
        ".workflow-step b{width:28px;height:28px;display:grid;place-items:center;border-radius:50%;background:#0f766e;font-size:12px;}.workflow-step span{color:#dbe4ea;font-size:14px;}"
        ".section{padding:64px 0 0;}.section-heading{max-width:720px;margin-bottom:26px;}.section-heading p{font-size:17px;}"
        ".grid-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;}.grid-2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;}"
        ".card{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:22px;}.card p:last-child{margin-bottom:0;}.card-kicker{color:var(--orange);font-size:12px;font-weight:800;margin-bottom:9px;}"
        ".tag{display:inline-flex;padding:4px 8px;border-radius:4px;background:#e7f3f1;color:#0f766e;font-size:12px;font-weight:700;}"
        ".metric-row{margin-top:28px;}.metric{min-width:140px;padding:14px 16px;border-left:3px solid var(--orange);background:#fff;}.metric strong{display:block;font-size:27px;line-height:1.1;}.metric span{font-size:12px;color:var(--muted);}"
        ".page-intro{padding:56px 0 30px;border-bottom:1px solid var(--line);}.page-intro h1{font-size:46px;}.page-intro p{max-width:720px;font-size:18px;margin-top:14px;}"
        ".case-study{padding:32px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:250px 1fr;gap:36px;}.case-study h2{font-size:24px;}.case-body{display:grid;grid-template-columns:1fr 1fr;gap:24px;}.case-body .wide{grid-column:1/-1;}"
        ".tutorial-block{background:#fff;border:1px solid var(--line);border-radius:8px;padding:26px;margin-top:18px;}.tutorial-steps{counter-reset:step;list-style:none;padding:0;}.tutorial-steps li{counter-increment:step;position:relative;padding:0 0 22px 48px;}.tutorial-steps li:before{content:counter(step);position:absolute;left:0;top:0;width:30px;height:30px;display:grid;place-items:center;border-radius:50%;background:#0f766e;color:#fff;font-weight:800;}"
        "pre{overflow:auto;background:#17202a;color:#e2e8f0;padding:16px;border-radius:6px;line-height:1.55;}code{font-family:'SFMono-Regular',Consolas,monospace;}"
        ".post-card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:20px;margin:14px 0;}.post-card h2{font-size:22px;margin-bottom:7px;}.post-meta{font-size:12px;color:#718096;}.read-more{display:inline-block;margin-top:4px;}"
        ".article-header{max-width:800px;padding:46px 0 24px;}.article-header h1{font-size:44px;}.article-content{max-width:860px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:34px;margin-top:14px;}.article-content h1:first-child{display:none;}.article-content h2{font-size:24px;margin-top:30px;}.article-content h3{margin-top:24px;}"
        ".about-grid{display:grid;grid-template-columns:.75fr 1.25fr;gap:30px;align-items:start;}.skill-list{display:flex;flex-wrap:wrap;gap:8px;}.timeline-item{padding:0 0 24px 22px;border-left:2px solid #cbd5e1;position:relative;}.timeline-item:before{content:'';position:absolute;left:-7px;top:7px;width:12px;height:12px;background:var(--orange);border-radius:50%;}"
        + site_nav_css() +
        "@media(max-width:900px){.hero{grid-template-columns:1fr;min-height:auto;padding:42px 0 52px;}.grid-3{grid-template-columns:1fr 1fr;}.case-study{grid-template-columns:1fr;gap:12px;}.about-grid{grid-template-columns:1fr;}}"
        "@media(max-width:620px){.site-shell{padding:0 16px 36px;}.grid-3,.grid-2,.case-body{grid-template-columns:1fr;}.case-body .wide{grid-column:auto;}.hero{gap:32px;}.hero h1{font-size:44px;}.hero-copy .lead{font-size:18px;}.workflow-visual{box-shadow:7px 7px 0 #f97316;}.page-intro h1,.article-header h1{font-size:34px;}.section{padding-top:48px;}.article-content{padding:22px;}.metric{flex:1 1 130px;}}"
        "</style></head><body><div class='site-shell'>"
        f"{render_site_nav(active_path)}<main>{body}</main>{render_site_footer()}"
        "</div></body></html>"
    )
