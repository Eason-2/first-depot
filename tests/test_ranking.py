from __future__ import annotations

import unittest

from core.models import NormalizedEvent
from workers.ranking.clustering import cluster_events
from workers.ranking.scoring import score_cluster


class RankingTests(unittest.TestCase):
    def _event(self, event_id: str, title: str, url: str, source: str) -> NormalizedEvent:
        return NormalizedEvent(
            event_id=event_id,
            source=source,
            source_item_id=event_id,
            title=title,
            summary="summary",
            url=url,
            domain="example.com",
            author="",
            published_at="2026-03-06T00:00:00Z",
            fetched_at="2026-03-06T01:00:00Z",
            language="en",
            content_type="news",
            tags=[],
            engagement={"upvotes": 100.0, "comments": 20.0, "views": 0.0, "shares": 0.0},
            ai_relevance=0.9,
            credibility=0.8,
            dedup={
                "canonical_url": url,
                "title_fingerprint": "abc",
                "url_fingerprint": "def",
                "embedding_fingerprint": "",
            },
            raw_payload_ref="",
        )

    def test_cluster_by_url(self) -> None:
        events = [
            self._event("e1", "AI launch", "https://example.com/a", "newsapi"),
            self._event("e2", "AI launch coverage", "https://example.com/a", "hackernews"),
            self._event("e3", "Different topic", "https://example.com/b", "arxiv"),
        ]
        clusters = cluster_events(events)
        self.assertEqual(len(clusters), 2)

    def test_score_cluster(self) -> None:
        events = [self._event("e1", "AI launch", "https://example.com/a", "newsapi")]
        cluster = cluster_events(events)[0]
        scored = score_cluster(cluster, {event.event_id: event for event in events})
        self.assertGreater(scored.score, 0)
        self.assertIn("recency", scored.explainability)


if __name__ == "__main__":
    unittest.main()
