from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from apps.api.blog_view import render_blog_post
from apps.api.portfolio_view import render_about_page, render_home_page, render_projects_page, render_tutorials_page
from apps.api.site_view import render_site_nav


class SiteViewTests(unittest.TestCase):
    def test_primary_navigation_contains_requested_sections(self) -> None:
        nav = render_site_nav("/projects")
        for label in ("首页", "项目案例", "实战教程", "AI 工具箱", "知行简报", "关于我"):
            self.assertIn(label, nav)
        self.assertIn("href='/projects' aria-current='page'", nav)

    def test_portfolio_pages_render_real_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            publish_dir = Path(tmp)
            (publish_dir / "2026-09-07-ai.md").write_text(
                "---\ntitle: 'AI 测试文章'\n---\n\n# AI 测试文章\n\n正文内容。\n",
                encoding="utf-8",
            )
            home = render_home_page(publish_dir)

        self.assertIn("AI 应用开发", home)
        self.assertNotIn("黄逸山", home)
        self.assertIn("AI 测试文章", home)
        self.assertIn("商品自动化上架 Agent", render_projects_page())
        self.assertIn("python -m scripts.start_api", render_tutorials_page())
        self.assertIn("能力结构", render_about_page())

    def test_blog_post_does_not_repeat_markdown_title(self) -> None:
        html = render_blog_post("示例标题", "# 示例标题\n\n正文。")
        self.assertEqual(html.count(">示例标题</h1>"), 1)


if __name__ == "__main__":
    unittest.main()
