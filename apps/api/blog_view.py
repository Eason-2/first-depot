from __future__ import annotations

import re
from html import escape
from pathlib import Path

from apps.api.site_view import render_site_page

_URL_PATTERN = re.compile(r"(https?://[^\s<]+)")
_SITE_NAME = "知行简报"
_SITE_TAGLINE = "追踪热点，也尊重常识。"


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


def render_blog_index(publish_dir: Path) -> str:
    posts = list_post_files(publish_dir)
    if not posts:
        body = "<p>还没有发布文章，稍后再来看看。</p>"
    else:
        cards = []
        for post in posts:
            slug = post_slug_from_path(post)
            title, preview, date = read_post_summary(post)
            cards.append(
                "<article class='post-card'>"
                f"<h2><a href='/blog/{escape(slug)}'>{escape(title)}</a></h2>"
                f"<p class='post-meta'>{escape(date)}</p>"
                f"<p>{escape(preview)}</p>"
                f"<a class='read-more' href='/blog/{escape(slug)}'>阅读全文</a>"
                "</article>"
            )
        body = "".join(cards)

    header = (
        "<header class='page-intro'>"
        "<p class='eyebrow'>AI briefing</p>"
        f"<h1>{_SITE_NAME}</h1>"
        f"<p>{_SITE_TAGLINE}这里保留自动采集与发布的资讯实验，项目案例和教程请从一级导航进入。</p>"
        "</header>"
    )
    return render_site_page(_SITE_NAME, f"{header}<section class='section'>{body}</section>", "/blog")


def render_blog_post(title: str, markdown_content: str) -> str:
    article = markdown_to_html(_remove_leading_title(markdown_content, title))
    return render_site_page(
        title,
        "<header class='article-header'><p><a href='/blog'>← 返回知行简报</a></p>"
        + f"<h1>{escape(title)}</h1></header>"
        + f"<article class='article-content'>{article}</article>",
        "/blog/post",
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
