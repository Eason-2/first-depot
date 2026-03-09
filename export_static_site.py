from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

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


def export_static_site(project_root: Path, output_dir: Path, publish_dir: Path, cname: str = "") -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    blog_dir = output_dir / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)

    index_html = render_blog_index(publish_dir)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")
    (blog_dir / "index.html").write_text(index_html, encoding="utf-8")

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
        (post_dir / "index.html").write_text(render_blog_post(title, content), encoding="utf-8")
        post_count += 1

    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    (output_dir / "404.html").write_text(
        (
            "<!doctype html><html><head><meta charset='utf-8' />"
            "<meta name='viewport' content='width=device-width, initial-scale=1' />"
            "<title>404 Not Found</title></head>"
            "<body><h1>404</h1><p>Page not found.</p><p><a href='/blog'>Back to blog</a></p></body></html>"
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
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / args.output_dir
    publish_dir = project_root / args.publish_dir
    result = export_static_site(
        project_root=project_root,
        output_dir=output_dir,
        publish_dir=publish_dir,
        cname=args.cname,
    )

    print("Static export complete:")
    print(f"- output_dir: {result['output_dir']}")
    print(f"- publish_dir: {result['publish_dir']}")
    print(f"- post_count: {result['post_count']}")
    if result["cname"]:
        print(f"- cname: {result['cname']}")


if __name__ == "__main__":
    main()
