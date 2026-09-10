from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from core.config import Settings
from core.models import ArticleDraft, NormalizedEvent, TopicCluster
from workers.generation.draft_builder import DraftBuilder
from workers.qa.checks.style import check_style_and_structure
from workers.qa.pipeline import QAPipeline

_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")


class GenerationQATests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = Settings.from_env(project_root=Path(__file__).resolve().parents[1])
        self.rotation_state_path = self.settings.runtime_dir / "generation_rotation_state.json"
        if self.rotation_state_path.exists():
            self.rotation_state_path.unlink()
        self.builder = DraftBuilder(self.settings)

    def tearDown(self) -> None:
        if self.rotation_state_path.exists():
            self.rotation_state_path.unlink()

    def test_generate_and_qa_pass(self) -> None:
        cluster = TopicCluster(
            cluster_id="cluster_1",
            title="AI product release",
            representative_url="https://example.com/a",
            event_ids=["e1", "e2"],
            sources=["newsapi", "hackernews"],
            size=2,
            score=88.0,
            explainability={},
        )
        events = [
            NormalizedEvent(
                event_id="e1",
                source="newsapi",
                source_item_id="1",
                title="AI product release details",
                summary="A major release introduces new model routing, better observability, and integration hooks for enterprise teams.",
                url="https://example.com/a",
                domain="example.com",
                author="",
                published_at="2026-03-06T00:00:00Z",
                fetched_at="2026-03-06T01:00:00Z",
                language="en",
                content_type="news",
                tags=[],
                engagement={"upvotes": 20.0, "comments": 10.0, "views": 0.0, "shares": 0.0},
                ai_relevance=0.9,
                credibility=0.8,
                dedup={"canonical_url": "https://example.com/a", "title_fingerprint": "x", "url_fingerprint": "y", "embedding_fingerprint": ""},
                raw_payload_ref="",
            ),
            NormalizedEvent(
                event_id="e2",
                source="hackernews",
                source_item_id="2",
                title="Developer response to the AI release",
                summary="Community discussion highlights migration strategy, safety constraints, and inference cost optimization.",
                url="https://example.com/b",
                domain="example.com",
                author="",
                published_at="2026-03-06T00:00:00Z",
                fetched_at="2026-03-06T01:00:00Z",
                language="en",
                content_type="discussion",
                tags=[],
                engagement={"upvotes": 50.0, "comments": 20.0, "views": 0.0, "shares": 0.0},
                ai_relevance=0.85,
                credibility=0.75,
                dedup={"canonical_url": "https://example.com/b", "title_fingerprint": "x2", "url_fingerprint": "y2", "embedding_fingerprint": ""},
                raw_payload_ref="",
            ),
        ]

        draft = self.builder.generate(cluster, events, context_events=events)
        qa = QAPipeline().evaluate(draft)

        self.assertTrue(qa.passed)
        self.assertEqual(draft.status, "generated")
        self.assertTrue(bool(_CJK_PATTERN.search(draft.title)))
        self.assertIn("AI product release", draft.title)
        self.assertNotIn("**", draft.content_markdown)
        self.assertNotIn("补充观察（第", draft.content_markdown)
        self.assertGreaterEqual(qa.details["style"]["visible_chars"], 1200)
        self.assertEqual(qa.details["style"]["duplicate_long_lines"], [])

    def test_titles_stay_specific_to_each_topic(self) -> None:
        titles = [
            self.builder._build_chinese_title("GPT-6 coding model preview", 0),
            self.builder._build_chinese_title("Open-source voice agent toolkit", 0),
        ]

        self.assertIn("GPT-6 coding model preview", titles[0])
        self.assertIn("Open-source voice agent toolkit", titles[1])
        self.assertNotEqual(titles[0], titles[1])
        self.assertNotIn("GPT-5.4", titles[0])

    def test_action_plan_changes_with_evidence_type(self) -> None:
        cluster = TopicCluster(
            cluster_id="cluster_action",
            title="Efficient agent evaluation",
            representative_url="https://example.com/action",
            event_ids=["action"],
            sources=["example"],
            size=1,
            score=80.0,
            explainability={},
        )
        event_fields = {
            "event_id": "action",
            "source": "example",
            "source_item_id": "action",
            "title": "Efficient agent evaluation details",
            "summary": "",
            "url": "https://example.com/action",
            "domain": "example.com",
            "author": "",
            "published_at": "2026-03-06T00:00:00Z",
            "fetched_at": "2026-03-06T01:00:00Z",
            "language": "en",
            "tags": [],
            "engagement": {},
            "ai_relevance": 0.9,
            "credibility": 0.8,
            "dedup": {},
            "raw_payload_ref": "",
        }
        news_plan = self.builder._build_action_plan(cluster, [NormalizedEvent(content_type="news", **event_fields)], 0)
        research_plan = self.builder._build_action_plan(cluster, [NormalizedEvent(content_type="research", **event_fields)], 0)

        self.assertIn("核对发布边界", news_plan)
        self.assertIn("复现材料中的核心实验", research_plan)
        self.assertNotEqual(news_plan, research_plan)

    def test_style_rejects_generic_title_and_duplicate_long_lines(self) -> None:
        repeated = "这是一段被重复使用的长句，用来确认质量检查能够拦住明显的模板化内容。"
        content = "\n\n".join(
            [
                "# 这条 AI 话题为什么值得你认真看一眼",
                "## 结论",
                repeated,
                "## 事实",
                repeated,
                "## 证据",
                "主题证据与具体来源需要逐项核对。" * 20,
                "## 行动",
                "记录输入、配置、输出和失败案例。" * 20,
                "## 风险",
                "来源集中时不能把转述数量当作独立证据。" * 20,
                "## 复盘",
                "使用实测结果决定是否扩大投入。" * 20,
            ]
        )
        draft = ArticleDraft(
            draft_id="draft_style",
            cluster_id="cluster_style",
            title="这条 AI 话题为什么值得你认真看一眼",
            content_markdown=content,
            citations=[],
            tags=[],
            confidence=0.8,
            status="generated",
        )

        passed, details = check_style_and_structure(draft)

        self.assertFalse(passed)
        self.assertTrue(details["generic_title"])
        self.assertEqual(details["duplicate_long_lines"], [repeated])

    def test_structure_templates_rotate_in_order(self) -> None:
        events = [
            NormalizedEvent(
                event_id="e1",
                source="newsapi",
                source_item_id="1",
                title="AI product release details",
                summary="A major release introduces new model routing, better observability, and integration hooks for enterprise teams.",
                url="https://example.com/a",
                domain="example.com",
                author="",
                published_at="2026-03-06T00:00:00Z",
                fetched_at="2026-03-06T01:00:00Z",
                language="en",
                content_type="news",
                tags=[],
                engagement={"upvotes": 20.0, "comments": 10.0, "views": 0.0, "shares": 0.0},
                ai_relevance=0.9,
                credibility=0.8,
                dedup={"canonical_url": "https://example.com/a", "title_fingerprint": "x", "url_fingerprint": "y", "embedding_fingerprint": ""},
                raw_payload_ref="",
            ),
            NormalizedEvent(
                event_id="e2",
                source="hackernews",
                source_item_id="2",
                title="Developer response to the AI release",
                summary="Community discussion highlights migration strategy, safety constraints, and inference cost optimization.",
                url="https://example.com/b",
                domain="example.com",
                author="",
                published_at="2026-03-06T00:00:00Z",
                fetched_at="2026-03-06T01:00:00Z",
                language="en",
                content_type="discussion",
                tags=[],
                engagement={"upvotes": 50.0, "comments": 20.0, "views": 0.0, "shares": 0.0},
                ai_relevance=0.85,
                credibility=0.75,
                dedup={"canonical_url": "https://example.com/b", "title_fingerprint": "x2", "url_fingerprint": "y2", "embedding_fingerprint": ""},
                raw_payload_ref="",
            ),
        ]
        expected_h2 = [
            "先说我的判断",
            "先给忙人版结论",
            "先把话挑明",
            "别急着站队，先看证据",
            "这次只回答一个核心问题",
            "先界定这篇文章讨论什么",
            "用决策备忘录的方式看这件事",
            "先拆开热度、证据与可用性",
        ]

        got_h2: list[str] = []
        for idx in range(8):
            cluster = TopicCluster(
                cluster_id=f"cluster_rotate_{idx}",
                title="AI product release",
                representative_url="https://example.com/a",
                event_ids=["e1", "e2"],
                sources=["newsapi", "hackernews"],
                size=2,
                score=88.0,
                explainability={},
            )
            draft = self.builder.generate(cluster, events, context_events=events)
            first_h2 = next((line[3:].strip() for line in draft.content_markdown.splitlines() if line.startswith("## ")), "")
            got_h2.append(first_h2)

        self.assertEqual(got_h2, expected_h2)
        state = json.loads(self.rotation_state_path.read_text(encoding="utf-8"))
        self.assertEqual(state.get("next_outline_variant"), 0)


if __name__ == "__main__":
    unittest.main()
