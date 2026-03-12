from __future__ import annotations

import re
from html import escape
from pathlib import Path

_URL_PATTERN = re.compile(r"(https?://[^\s<]+)")
_BG_IMAGE_URL = "https://pic1.zhimg.com/v2-407d96bc59e33e239c838aedb04013b2_r.jpg?source=1940ef5c"
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


def render_blog_index(publish_dir: Path) -> str:
    posts = list_post_files(publish_dir)
    if not posts:
        body = "<p>还没有发布文章，稍后再来看看。</p>"
    else:
        cards = []
        for post in posts:
            slug = post_slug_from_path(post)
            raw = post.read_text(encoding="utf-8")
            meta, content = _parse_front_matter(raw)
            title = meta.get("title") or _extract_title(raw) or slug
            preview = _build_preview(content or raw)
            cards.append(
                "<article class='post-card'>"
                f"<h2><a href='/blog/{escape(slug)}'>{escape(title)}</a></h2>"
                f"<p class='post-meta'>{escape(slug)}</p>"
                f"<p>{escape(preview)}</p>"
                f"<a class='read-more' href='/blog/{escape(slug)}'>阅读全文</a>"
                "</article>"
            )
        body = "".join(cards)

    header = (
        "<header class='page-header'>"
        "<div class='page-title'>"
        f"<h1>{_SITE_NAME}</h1>"
        f"<p>{_SITE_TAGLINE}</p>"
        "</div>"
        "<div class='page-actions'>"
        "<a class='action-link' href='/ai-writer'>写作助手</a>"
        "</div>"
        "</header>"
    )
    return _layout(_SITE_NAME, f"{header}{body}")


def render_blog_post(title: str, markdown_content: str) -> str:
    article = markdown_to_html(markdown_content)
    return _layout(
        title,
        "<p><a href='/blog'>返回文章列表</a></p>"
        + f"<h1>{escape(title)}</h1>"
        + f"<article>{article}</article>",
    )


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
    return (
        "<!doctype html>"
        "<html lang='zh-CN'>"
        "<head>"
        "<meta charset='utf-8' />"
        "<meta name='viewport' content='width=device-width, initial-scale=1' />"
        f"<title>{escape(title)}</title>"
        "<style>"
        "body{font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;max-width:980px;margin:0 auto;padding:28px 18px 42px;"
        "line-height:1.9;color:#0f172a;"
        f"background:linear-gradient(rgba(246,251,255,.88),rgba(251,241,249,.90)),url('{_BG_IMAGE_URL}') center top/cover no-repeat;"
        "background-attachment:scroll;}"
        "a{color:#1d4ed8;text-decoration:none;font-weight:600;}"
        "a:hover{text-decoration:underline;}"
        "article{margin-top:14px;background:rgba(255,255,255,.96);border:1px solid rgba(59,130,246,.16);border-radius:14px;padding:20px;}"
        "h1,h2,h3{line-height:1.45;color:#0b3a75;}"
        "p{margin:0 0 14px;}"
        "ul{margin:0 0 16px 0;padding-left:22px;}"
        "li{margin:0 0 8px;}"
        "code{background:#e7f2ff;padding:2px 6px;border-radius:6px;}"
        ".page-header{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:18px;}"
        ".page-title{min-width:0;}"
        ".page-title h1{margin:0 0 6px;}"
        ".page-actions{flex:0 0 auto;display:flex;justify-content:flex-end;}"
        ".action-link{display:inline-flex;align-items:center;justify-content:center;padding:8px 14px;border-radius:999px;border:1px solid rgba(29,78,216,.22);background:rgba(255,255,255,.92);box-shadow:0 8px 24px rgba(15,23,42,.06);white-space:nowrap;}"
        ".post-card{background:rgba(255,255,255,.95);border:1px solid rgba(59,130,246,.16);border-radius:14px;padding:16px 18px;margin:14px 0;}"
        ".post-meta{font-size:12px;color:#64748b;margin-bottom:6px;}"
        ".read-more{display:inline-block;margin-top:4px;}"
        "@media (max-width:640px){.page-header{flex-direction:column;}.page-actions{justify-content:flex-start;}}"
        "</style>"
        "</head>"
        "<body>"
        f"{body}"
        "</body>"
        "</html>"
    )
