from __future__ import annotations

import unittest

from workers.ingestion.normalize import normalize_arxiv, normalize_hackernews, normalize_newsapi


class NormalizeTests(unittest.TestCase):
    def test_normalize_newsapi(self) -> None:
        event = normalize_newsapi(
            {
                "title": "OpenAI introduces new agent model",
                "url": "https://example.com/news/openai-agent",
                "description": "AI agent update",
                "author": "Reporter",
                "publishedAt": "2026-03-06T00:00:00Z",
            },
            fetched_at="2026-03-06T01:00:00Z",
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.source, "newsapi")
        self.assertGreater(event.ai_relevance, 0.2)

    def test_normalize_hackernews(self) -> None:
        event = normalize_hackernews(
            {
                "id": 123,
                "title": "LLM benchmarking in production",
                "url": "https://example.com/llm-bench",
                "by": "alice",
                "score": 120,
                "descendants": 30,
                "time": 1770000000,
            },
            fetched_at="2026-03-06T01:00:00Z",
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.source_item_id, "123")
        self.assertGreater(event.engagement.get("upvotes", 0.0), 0.0)

    def test_normalize_arxiv(self) -> None:
        event = normalize_arxiv(
            {
                "id": "http://arxiv.org/abs/1234.5678",
                "title": "Transformer efficiency for AI systems",
                "summary": "A study on efficient inference.",
                "published": "2026-03-05T12:00:00Z",
                "link": "http://arxiv.org/abs/1234.5678",
            },
            fetched_at="2026-03-06T01:00:00Z",
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.content_type, "research")
        self.assertEqual(event.source, "arxiv")


if __name__ == "__main__":
    unittest.main()
