from __future__ import annotations

from html import escape
from pathlib import Path

from apps.api.blog_view import list_post_files, post_slug_from_path, read_post_summary, render_article_page
from apps.api.site_view import render_about_nav, render_site_page


def render_journal_cards(journal_dir: Path, limit: int | None = None) -> str:
    posts = list_post_files(journal_dir)
    if limit is not None:
        posts = posts[:limit]
    cards: list[str] = []
    for post in posts:
        title, preview, date = read_post_summary(post)
        href = "/about/journal/" + post_slug_from_path(post)
        cards.append(
            "<article class='card'>"
            f"<p class='card-kicker'>{escape(date)} · 成长记录</p>"
            f"<h3><a href='{escape(href, quote=True)}'>{escape(title)}</a></h3>"
            f"<p>{escape(preview)}</p>"
            f"<a href='{escape(href, quote=True)}'>继续阅读 →</a>"
            "</article>"
        )
    return "".join(cards) or "<p>第一篇记录还在整理中。可以先看看项目案例和实战教程。</p>"


def render_journal_index(journal_dir: Path) -> str:
    body = (
        "<header class='page-intro'><p class='eyebrow'>Learning in public</p>"
        "<h1>成长记录</h1><p>记下尝试过的方法、卡住的问题，以及还没想明白的事。</p>"
        "<p>工具试用、项目进展和个人想法，都可以从一个具体问题写起。</p></header>"
        + render_about_nav("/about/journal")
        + "<section class='section' aria-label='记录列表'><div class='reading-grid'>"
        + render_journal_cards(journal_dir)
        + "</div></section>"
    )
    return render_site_page("成长记录", body, "/about/journal", "AI 学习、项目实践、踩坑与个人想法。")


def render_journal_post(title: str, content: str) -> str:
    return render_article_page(title, content, "/about/journal", "成长记录")
