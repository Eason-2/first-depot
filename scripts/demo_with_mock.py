from __future__ import annotations

import json
import os
from pathlib import Path

from core.config import Settings
from workers.ingestion.pipeline import IngestionPipeline
from workers.publishing.scheduler import AutopublishScheduler


class MockNewsConnector:
    source_name = "newsapi"

    def fetch_items(self, limit: int) -> list[dict]:
        return [
            {
                "title": "Open model provider announces faster reasoning release",
                "url": "https://example.com/ai/reasoning-release",
                "description": "New release with better latency and cost profile for AI teams.",
                "author": "Example Reporter",
                "publishedAt": "2026-03-06T08:00:00Z",
            },
            {
                "title": "Enterprise AI stack adopts unified agent runtime",
                "url": "https://example.com/ai/agent-runtime",
                "description": "Vendors converge on shared tooling for agent orchestration.",
                "author": "Example Reporter",
                "publishedAt": "2026-03-06T07:00:00Z",
            },
        ]


class MockHNConnector:
    source_name = "hackernews"

    def fetch_items(self, limit: int) -> list[dict]:
        return [
            {
                "id": 991,
                "title": "Discussion: practical impact of the new reasoning model",
                "url": "https://example.com/ai/reasoning-release",
                "by": "dev_user",
                "score": 210,
                "descendants": 88,
                "time": 1770000000,
            }
        ]


class MockArxivConnector:
    source_name = "arxiv"

    def fetch_items(self, limit: int) -> list[dict]:
        return [
            {
                "id": "http://arxiv.org/abs/2603.12345",
                "title": "Efficient inference scheduling for large AI systems",
                "summary": "A framework for reducing inference latency and cost.",
                "published": "2026-03-05T11:00:00Z",
                "link": "http://arxiv.org/abs/2603.12345",
            }
        ]


def main() -> None:
    os.environ["AUTO_PUBLISH_MODE"] = "auto"
    settings = Settings.from_env(project_root=Path(__file__).resolve().parents[1])
    scheduler = AutopublishScheduler(settings)
    scheduler.ingestion = IngestionPipeline(
        settings,
        scheduler.storage,
        connectors=[MockNewsConnector(), MockHNConnector(), MockArxivConnector()],
    )

    result = scheduler.run_cycle(max_items_per_source=10)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
