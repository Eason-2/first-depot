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
            "<a href='/blog'>Blog</a>"
            "<a href='/blog/post-a'>Post A</a>"
            '<a href="/blog/post-b">Post B</a>'
        )
        updated = _apply_base_path(html, "/first-depot")
        self.assertIn("href='/first-depot/blog'", updated)
        self.assertIn("href='/first-depot/blog/post-a'", updated)
        self.assertIn('href="/first-depot/blog/post-b"', updated)

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
            self.assertIn("href='/first-depot/blog/2026-03-10-sample'", (output_dir / "index.html").read_text(encoding="utf-8"))
            self.assertIn("href='/first-depot/blog'", (output_dir / "blog" / "2026-03-10-sample" / "index.html").read_text(encoding="utf-8"))
            self.assertIn("href='/first-depot/blog'", (output_dir / "404.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
