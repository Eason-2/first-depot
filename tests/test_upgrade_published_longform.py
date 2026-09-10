from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from core.config import Settings
from scripts.upgrade_published_longform import SourceReference, _select_relevant_references, rewrite_articles
from workers.generation.draft_builder import DraftBuilder


class UpgradePublishedLongformTests(unittest.TestCase):
    def test_select_relevant_references_drops_unrelated_ai_sources(self) -> None:
        references = [
            SourceReference("GPT-6 Astra", "https://example.com/gpt-6-astra"),
            SourceReference("GPT-6 Astra system card", "https://example.com/gpt-6-astra-card"),
            SourceReference("POET-X memory-efficient training", "https://arxiv.org/abs/example"),
        ]

        selected = _select_relevant_references(references)

        self.assertEqual([reference.title for reference in selected], ["GPT-6 Astra", "GPT-6 Astra system card"])

    def test_rewrite_uses_primary_source_and_removes_legacy_boilerplate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            publish_dir = root / "published"
            publish_dir.mkdir()
            post = publish_dir / "2026-09-03-ai.md"
            post.write_text(
                """---
title: '这条 AI 话题为什么值得你认真看一眼'
draft_id: 'draft_1'
cluster_id: 'cluster_1'
confidence: 0.8
tags: [ai-news, automation, longform, zh]
sources:
  - 'https://example.com/gpt-6-astra'
  - 'https://example.com/gpt-6-astra-card'
  - 'https://arxiv.org/abs/example'
---

# 这条 AI 话题为什么值得你认真看一眼

当前主题“Unrelated cluster title”在本轮评分 72.0/100。

- GPT-6 Astra（newsapi，2026-09-03）。A release note describes a new model preview and its availability. 相关度 0.90，可信度 0.85。

## 补充观察（第 1 轮）

如果这一轮看下来仍然意见分裂，先补证据再下结论，别把音量当成胜负。

## 参考资料

- [1] GPT-6 Astra - https://example.com/gpt-6-astra
- [2] GPT-6 Astra system card - https://example.com/gpt-6-astra-card
- [3] POET-X memory-efficient training - https://arxiv.org/abs/example
""",
                encoding="utf-8",
            )
            builder = DraftBuilder(Settings.from_env(project_root=root / "runtime-root"))

            result = rewrite_articles(publish_dir, builder, write=True)
            rewritten = post.read_text(encoding="utf-8")

        self.assertEqual(result["updated"], [post.name])
        self.assertEqual(result["skipped"], [])
        title = re.search(r"^title: '(.+)'$", rewritten, re.MULTILINE)
        self.assertIsNotNone(title)
        self.assertIn("GPT-6 Astra", title.group(1))
        self.assertNotIn("POET-X", rewritten)
        self.assertNotIn("补充观察（第", rewritten)
        self.assertNotIn("别把音量当成胜负", rewritten)


if __name__ == "__main__":
    unittest.main()
