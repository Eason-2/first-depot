from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from apps.api.blog_view import render_blog_post, render_news_metadata
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
        self.assertIn("先把 AI 用起来", home)
        self.assertIn("商品自动化上架 Agent", render_projects_page())
        tutorials = render_tutorials_page()
        self.assertIn("从零开始使用 Codex", tutorials)
        self.assertIn("先不要修改任何文件", tutorials)
        self.assertIn("不要自动执行删除、上传、发布或修改系统设置的命令", tutorials)
        self.assertIn("python -m scripts.start_api", render_tutorials_page())
        self.assertIn("能力结构", render_about_page())

    def test_blog_post_does_not_repeat_markdown_title(self) -> None:
        html = render_blog_post("示例标题", "# 示例标题\n\n正文。")
        self.assertEqual(html.count(">示例标题</h1>"), 1)

    def test_news_sources_use_unique_domains_from_declared_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            post = Path(tmp) / "news.md"
            post.write_text(
                "---\ntitle: 'Example'\nsources:\n"
                "  - 'https://www.example.com/first'\n"
                "  - 'https://example.com/second'\n"
                "  - 'https://arxiv.org/abs/1234'\n"
                "  - 'https://[invalid'\n"
                "  - 'javascript:alert(1)'\n"
                "---\n\nAn unrelated URL: https://unrelated.example/\n",
                encoding="utf-8",
            )
            metadata = render_news_metadata(post, "2026-10-27")
        self.assertIn("来源 · example.com / arxiv.org", metadata)
        self.assertEqual(metadata.count("example.com"), 1)
        self.assertNotIn("unrelated.example", metadata)
        self.assertNotIn("javascript:", metadata)
        self.assertIn("datetime='2026-10-27'", metadata)

    def test_news_without_declared_sources_does_not_invent_attribution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            post = Path(tmp) / "news.md"
            post.write_text("# Article\n\nsources:\n  - https://unrelated.example/", encoding="utf-8")
            metadata = render_news_metadata(post, "")
        self.assertIn("来源见正文", metadata)
        self.assertNotIn("<time", metadata)
        self.assertNotIn("unrelated.example", metadata)


if __name__ == "__main__":
    unittest.main()
