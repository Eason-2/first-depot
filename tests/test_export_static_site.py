from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.export_static_site import _apply_base_path, _normalize_base_path, export_static_site


class ExportStaticSiteTests(unittest.TestCase):
    def test_normalize_base_path(self) -> None:
        self.assertEqual(_normalize_base_path(""), "")
        self.assertEqual(_normalize_base_path("/"), "")
        self.assertEqual(_normalize_base_path("first-depot"), "/first-depot")
        self.assertEqual(_normalize_base_path("/first-depot/"), "/first-depot")
        self.assertEqual(_normalize_base_path("https://user.github.io/first-depot/"), "/first-depot")

    def test_apply_base_path(self) -> None:
        html = (
            "<a href='/'>Home</a>"
            "<a href='/projects'>Projects</a>"
            "<a href='/tutorials'>Tutorials</a>"
            "<a href='/blog'>Blog</a>"
            "<a href='/blog/post-a'>Post A</a>"
            '<a href="/blog/post-b">Post B</a>'
            "<a href='/about'>About</a>"
        )
        updated = _apply_base_path(html, "/first-depot")
        self.assertIn("href='/first-depot/'", updated)
        self.assertIn("href='/first-depot/projects'", updated)
        self.assertIn("href='/first-depot/tutorials'", updated)
        self.assertIn("href='/first-depot/blog'", updated)
        self.assertIn("href='/first-depot/blog/post-a'", updated)
        self.assertIn('href="/first-depot/blog/post-b"', updated)
        self.assertIn("href='/first-depot/about'", updated)

    def test_export_static_site_with_base_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            publish_dir = root / "deliverables" / "published"
            output_dir = root / "site"
            publish_dir.mkdir(parents=True, exist_ok=True)
            (publish_dir / "2026-03-10-sample.md").write_text(
                "---\n"
                "title: Sample Post\n"
                "---\n"
                "\n"
                "Hello world.\n",
                encoding="utf-8",
            )

            result = export_static_site(
                project_root=root,
                output_dir=output_dir,
                publish_dir=publish_dir,
                base_path="/first-depot",
            )

            self.assertEqual(result["base_path"], "/first-depot")
            self.assertTrue((output_dir / ".nojekyll").exists())
            self.assertTrue((output_dir / "projects" / "index.html").exists())
            self.assertTrue((output_dir / "tutorials" / "index.html").exists())
            self.assertTrue((output_dir / "about" / "index.html").exists())
            self.assertTrue((output_dir / "about" / "journal" / "index.html").exists())
            self.assertEqual(result["journal_count"], 0)
            self.assertIn("href='/first-depot/blog/2026-03-10-sample'", (output_dir / "index.html").read_text(encoding="utf-8"))
            self.assertIn("href='/first-depot/blog'", (output_dir / "blog" / "2026-03-10-sample" / "index.html").read_text(encoding="utf-8"))
            self.assertIn("href='/first-depot/blog'", (output_dir / "404.html").read_text(encoding="utf-8"))

    def test_journal_exports_separately_with_project_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            published = root / "deliverables" / "published"
            journal = root / "deliverables" / "journal"
            published.mkdir(parents=True)
            journal.mkdir()
            (published / "2026-10-06-news.md").write_text(
                "---\ntitle: '资讯样本'\n---\n\n# 资讯样本\n\n资讯内容。", encoding="utf-8"
            )
            for day in range(1, 5):
                (journal / f"2026-10-0{day}-note.md").write_text(
                    f"---\ntitle: '成长记录 {day}'\n---\n\n# 成长记录 {day}\n\n记录正文。", encoding="utf-8"
                )
            output = root / "site"
            result = export_static_site(root, output, published, base_path="/first-depot")
            home = (output / "index.html").read_text()
            index = (output / "about/journal/index.html").read_text()
            post = (output / "about/journal/2026-10-04-note/index.html").read_text()
            news = (output / "blog/index.html").read_text()

            self.assertEqual((result["post_count"], result["journal_count"]), (1, 4))
            self.assertIn("资讯样本", home)
            self.assertIn("href='/first-depot/tutorials#start-here'", home)
            self.assertIn("href='/first-depot/about/journal/2026-10-04-note'", home)
            self.assertNotIn("2026-10-01-note", home)
            self.assertLess(home.index("2026-10-04-note"), home.index("2026-10-03-note"))
            self.assertIn("2026-10-01-note", index)
            self.assertNotIn("资讯样本", index)
            self.assertNotIn("2026-10-04-note", news)
            self.assertIn("href='/first-depot/about/journal'", post)
            self.assertIn("href='/first-depot/about' aria-current='page'", post)
            self.assertEqual(post.count("<h1>成长记录 4</h1>"), 1)


if __name__ == "__main__":
    unittest.main()
