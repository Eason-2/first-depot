from __future__ import annotations

import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from apps.api.site_view import render_site_page

_URL_PATTERN = re.compile(r"(https?://[^\s<]+)")
_SITE_NAME = "知行简报"


def list_post_files(publish_dir: Path) -> list[Path]:
    posts = sorted(publish_dir.glob("*.md"), reverse=True)
    return [post for post in posts if post.is_file()]


def post_slug_from_path(path: Path) -> str:
    return path.stem


def load_post_by_slug(publish_dir: Path, slug: str) -> tuple[str, str] | None:
    if "/" in slug or "\\" in slug or ".." in slug:
        return None
    post_path = publish_dir / f"{slug}.md"
    if not post_path.exists() or not post_path.is_file():
        return None

    raw = post_path.read_text(encoding="utf-8")
    meta, body = _parse_front_matter(raw)
    title = meta.get("title") or _extract_title(raw) or slug.replace("-", " ").title()
    return title, body or raw


def read_post_summary(post_path: Path) -> tuple[str, str, str]:
    raw = post_path.read_text(encoding="utf-8")
    meta, content = _parse_front_matter(raw)
    title = meta.get("title") or _extract_title(raw) or post_path.stem
    date = post_path.stem[:10] if re.match(r"\d{4}-\d{2}-\d{2}", post_path.stem) else ""
    return title, _build_preview(content or raw), date


def render_news_metadata(post_path: Path, date: str) -> str:
    raw = post_path.read_text(encoding="utf-8").lstrip("\ufeff")
    header = raw.split("\n---", 1)[0] if raw.startswith("---\n") else ""
    domains: list[str] = []
    in_sources = False
    for line in header.splitlines():
        if line.strip() == "sources:":
            in_sources = True
            continue
        if in_sources and line and not line[0].isspace():
            break
        if not in_sources or not line.strip().startswith("- "):
            continue
        url = line.strip()[2:].strip().strip("'\"")
        try:
            parsed = urlsplit(url)
            domain = (parsed.hostname or "").removeprefix("www.")
        except ValueError:
            continue
        if parsed.scheme in ("http", "https") and domain and domain not in domains:
            domains.append(domain)
    sources = "来源 · " + " / ".join(domains[:2]) if domains else "来源见正文"
    if len(domains) > 2:
        sources += f" 等 {len(domains)} 个来源"
    timestamp = f"<time datetime='{escape(date, quote=True)}'>{escape(date)}</time>" if date else ""
    return (
        "<div class='news-meta'><span class='news-type'>AI 资讯</span>"
        + timestamp
        + f"<span class='news-sources'>{escape(sources)}</span></div>"
    )


def render_blog_index(publish_dir: Path) -> str:
    posts = list_post_files(publish_dir)
    if not posts:
        body = "<p>还没有发布文章，稍后再来看看。</p>"
    else:
        cards = []
        for post in posts:
            slug = post_slug_from_path(post)
            title, _, date = read_post_summary(post)
            title = title.removesuffix("：核心变化与验证重点")
            cards.append(
                "<article class='news-item'>"
                + render_news_metadata(post, date) +
                f"<h2><a href='/blog/{escape(slug)}'>{escape(title)}</a></h2>"
                f"<a class='ui-link' href='/blog/{escape(slug)}' aria-label='阅读全文：{escape(title, quote=True)}'>阅读全文</a>"
                "</article>"
            )
        body = "".join(cards)

    latest_date = read_post_summary(posts[0])[2] if posts else ""
    updated = f"最近更新 {escape(latest_date)}" if latest_date else "AI 资讯索引"
    header = (
        "<header class='news-masthead'><div class='news-edition'>"
        f"<strong>{_SITE_NAME}</strong><span>{updated}</span></div>"
        "<h1>AI 新闻与产品动态</h1>"
        "<p>新模型发布、工具更新、研究进展。每篇附上消息来源，方便回到原文继续看。</p>"
        "<div class='news-topics' aria-label='关注范围'><span>模型与产品</span><span>工具与应用</span><span>研究与行业</span></div></header>"
        "<p class='news-disclosure'>本站通过自动化流程整理公开资讯；重要信息请核对原始来源。</p>"
    )
    return render_site_page(
        _SITE_NAME,
        f"<div class='news-room'>{header}<section class='news-archive' aria-labelledby='latest-news'>"
        f"<div class='news-archive-heading'><h2 id='latest-news'>最新资讯</h2><span>{len(posts)} 篇归档 · 按日期排序</span></div>{body}</section></div>",
        "/blog", "知行简报：AI 新闻、模型发布、工具更新与研究进展，附原始消息来源。",
    )


def render_blog_post(title: str, markdown_content: str) -> str:
    return render_article_page(title, markdown_content, "/blog", "知行简报")


def render_article_page(title: str, markdown_content: str, collection_path: str, collection_name: str) -> str:
    article = markdown_to_html(_remove_leading_title(markdown_content, title))
    return render_site_page(
        title,
        f"<header class='article-header'><p><a href='{escape(collection_path, quote=True)}'>← 返回{escape(collection_name)}</a></p>"
        + f"<h1>{escape(title)}</h1></header>"
        + f"<article class='article-content'>{article}</article>",
        collection_path + "/post",
    )


def _remove_leading_title(markdown_content: str, title: str) -> str:
    lines = markdown_content.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if line.strip() == f"# {title}":
            return "\n".join(lines[:index] + lines[index + 1 :])
        break
    return markdown_content


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    in_list = False

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            if in_list:
                output.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("# "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<h1>{_render_inline(stripped[2:])}</h1>")
            continue
        if stripped.startswith("## "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<h2>{_render_inline(stripped[3:])}</h2>")
            continue
        if stripped.startswith("### "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<h3>{_render_inline(stripped[4:])}</h3>")
            continue
        if stripped.startswith("- "):
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{_render_inline(stripped[2:])}</li>")
            continue

        if in_list:
            output.append("</ul>")
            in_list = False
        output.append(f"<p>{_render_inline(stripped)}</p>")

    if in_list:
        output.append("</ul>")

    return "".join(output)


def _render_inline(text: str) -> str:
    cleaned = text.replace("**", "").replace("__", "")
    if "http://" not in cleaned and "https://" not in cleaned:
        return escape(cleaned)
    pieces = _URL_PATTERN.split(cleaned)
    rendered: list[str] = []
    for idx, piece in enumerate(pieces):
        if idx % 2 == 1:
            href = escape(piece, quote=True)
            rendered.append(f"<a href='{href}' target='_blank' rel='noopener noreferrer'>{escape(piece)}</a>")
        else:
            rendered.append(escape(piece))
    return "".join(rendered)


def _parse_front_matter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n"):
        return {}, content

    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, content

    header = parts[0][4:]
    body = parts[1]
    meta: dict[str, str] = {}

    for line in header.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip().strip("'\"")

    return meta, body


def _extract_title(markdown_content: str) -> str | None:
    for line in markdown_content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("title:"):
            value = stripped.split(":", 1)[1].strip().strip("'").strip('"')
            if value:
                return value
    return None


def _build_preview(content: str) -> str:
    cleaned = re.sub(r"```.*?```", " ", content, flags=re.DOTALL)
    cleaned = cleaned.replace("#", " ").replace("-", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:150] + ("..." if len(cleaned) > 150 else "")


def _layout(title: str, body: str) -> str:
    return render_site_page(title, body, "/blog")
