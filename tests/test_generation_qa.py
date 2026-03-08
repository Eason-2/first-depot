from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from core.config import Settings
from core.models import NormalizedEvent, TopicCluster
from workers.generation.draft_builder import DraftBuilder
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
        self.assertNotIn("**", draft.content_markdown)
        self.assertGreaterEqual(len(_CJK_PATTERN.findall(draft.content_markdown)), 1000)

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
        ]

        got_h2: list[str] = []
        for idx in range(4):
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
