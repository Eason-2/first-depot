from __future__ import annotations

import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import urlopen

from apps.api.server import ApiHandler


class JournalRouteTests(unittest.TestCase):
    def test_journal_routes_and_missing_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            journal = root / "deliverables" / "journal"
            published = root / "deliverables" / "published"
            journal.mkdir(parents=True)
            published.mkdir()
            (journal / "2026-10-06-note.md").write_text(
                "---\ntitle: '一个学习问题'\n---\n\n# 一个学习问题\n\n记录正文。", encoding="utf-8"
            )
            (published / "2026-10-06-news.md").write_text(
                "---\ntitle: '资讯标题'\n---\n\n简报内容。", encoding="utf-8"
            )
            (root / "deliverables" / "outside.md").write_text("不应公开的材料", encoding="utf-8")

            class Handler(ApiHandler):
                context = SimpleNamespace(settings=SimpleNamespace(project_root=root, publish_dir=published))

                def log_message(self, *args: object) -> None:
                    pass

            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def get(path: str) -> str:
                with urlopen(base + path, timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    return response.read().decode()

            try:
                for path in ("/about/journal", "/about/journal/"):
                    page = get(path)
                    self.assertIn("一个学习问题", page)
                    self.assertNotIn("资讯标题", page)
                for path in ("/about/journal/2026-10-06-note", "/about/journal/2026-10-06-note/"):
                    page = get(path)
                    self.assertIn("记录正文。", page)
                    self.assertIn("href='/about' aria-current='page'", page)
                self.assertIn("资讯标题", get("/blog/"))
                self.assertNotIn("一个学习问题", get("/blog/"))
                home = get("/")
                self.assertIn("一个学习问题", home)
                self.assertIn("资讯标题", home)
                self.assertIn("href='/about/journal'", get("/about/"))
                self.assertIn("id='start-here'", get("/tutorials/"))
                for path in ("/about/journal/missing", "/about/journal/2026-10-06-news", "/about/journal/%2e%2e%2foutside"):
                    with self.assertRaises(HTTPError) as error:
                        get(path)
                    self.assertEqual(error.exception.code, 404)
                    error.exception.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
