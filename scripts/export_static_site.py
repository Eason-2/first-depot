from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

from apps.api.ai_writer import render_ai_writer_page
from apps.api.blog_view import load_post_by_slug, post_slug_from_path, render_blog_index, render_blog_post


def _normalize_cname(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""
    if "://" in value:
        parsed = urlparse(value)
        value = parsed.netloc or parsed.path
    value = value.strip().strip("/")
    if "/" in value:
        value = value.split("/", 1)[0]
    return value


def _normalize_base_path(raw: str) -> str:
    value = (raw or "").strip()
    if not value or value == "/":
        return ""
    if "://" in value:
        parsed = urlparse(value)
        value = parsed.path or ""
    if not value.startswith("/"):
        value = "/" + value
    value = value.rstrip("/")
    return value


def _apply_base_path(html: str, base_path: str) -> str:
    if not base_path:
        return html
    return (
        html.replace("href='/blog/", f"href='{base_path}/blog/")
        .replace('href="/blog/', f'href="{base_path}/blog/')
        .replace("href='/blog'", f"href='{base_path}/blog'")
        .replace('href="/blog"', f'href="{base_path}/blog"')
        .replace("href='/ai-writer'", f"href='{base_path}/ai-writer'")
        .replace('href="/ai-writer"', f'href="{base_path}/ai-writer"')
    )


def export_static_site(
    project_root: Path,
    output_dir: Path,
    publish_dir: Path,
    cname: str = "",
    base_path: str = "",
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    blog_dir = output_dir / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)
    ai_writer_dir = output_dir / "ai-writer"
    ai_writer_dir.mkdir(parents=True, exist_ok=True)

    normalized_base_path = _normalize_base_path(base_path)
    index_html = _apply_base_path(render_blog_index(publish_dir), normalized_base_path)
    ai_writer_html = _apply_base_path(render_ai_writer_page(), normalized_base_path)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")
    (blog_dir / "index.html").write_text(index_html, encoding="utf-8")
    (ai_writer_dir / "index.html").write_text(ai_writer_html, encoding="utf-8")

    post_count = 0
    for post_path in sorted(publish_dir.glob("*.md"), reverse=True):
        if not post_path.is_file():
            continue
        slug = post_slug_from_path(post_path)
        loaded = load_post_by_slug(publish_dir, slug)
        if not loaded:
            continue
        title, content = loaded
        post_dir = blog_dir / slug
        post_dir.mkdir(parents=True, exist_ok=True)
        post_html = _apply_base_path(render_blog_post(title, content), normalized_base_path)
        (post_dir / "index.html").write_text(post_html, encoding="utf-8")
        post_count += 1

    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    back_to_blog = f"{normalized_base_path}/blog" if normalized_base_path else "/blog"
    (output_dir / "404.html").write_text(
        (
            "<!doctype html><html><head><meta charset='utf-8' />"
            "<meta name='viewport' content='width=device-width, initial-scale=1' />"
            "<title>404 Not Found</title></head>"
            f"<body><h1>404</h1><p>Page not found.</p><p><a href='{back_to_blog}'>Back to blog</a></p></body></html>"
        ),
        encoding="utf-8",
    )

    cname_value = _normalize_cname(cname)
    if cname_value:
        (output_dir / "CNAME").write_text(cname_value + "\n", encoding="utf-8")

    return {
        "output_dir": str(output_dir),
        "publish_dir": str(publish_dir),
        "post_count": post_count,
        "cname": cname_value,
        "base_path": normalized_base_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export local markdown blog to static HTML files.")
    parser.add_argument("--output-dir", default="site", help="Output directory for static site files.")
    parser.add_argument(
        "--publish-dir",
        default="deliverables/published",
        help="Directory containing markdown posts.",
    )
    parser.add_argument("--cname", default="", help="Optional custom domain (example: blog.example.com).")
    parser.add_argument(
        "--base-path",
        default="",
        help="Optional URL base path for project pages (example: /first-depot).",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / args.output_dir
    publish_dir = project_root / args.publish_dir
    result = export_static_site(
        project_root=project_root,
        output_dir=output_dir,
        publish_dir=publish_dir,
        cname=args.cname,
        base_path=args.base_path,
    )

    print("Static export complete:")
    print(f"- output_dir: {result['output_dir']}")
    print(f"- publish_dir: {result['publish_dir']}")
    print(f"- post_count: {result['post_count']}")
    if result["cname"]:
        print(f"- cname: {result['cname']}")
    if result["base_path"]:
        print(f"- base_path: {result['base_path']}")


if __name__ == "__main__":
    main()
