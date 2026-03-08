from __future__ import annotations

import unittest
from pathlib import Path

from core.config import Settings
from core.storage import Storage
from workers.ingestion.pipeline import IngestionPipeline
from workers.publishing.scheduler import AutopublishScheduler


class _MockConnector:
    source_name = "newsapi"

    def fetch_items(self, limit: int) -> list[dict]:
        return [
            {
                "title": "AI launch update",
                "url": "https://example.com/launch",
                "description": "New AI launch",
                "author": "Reporter",
                "publishedAt": "2026-03-06T00:00:00Z",
            }
        ]


class EndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.settings = Settings.from_env(project_root=self.project_root)
        self.storage = Storage(self.settings.db_path)

    def test_ingestion_pipeline_with_mock(self) -> None:
        pipeline = IngestionPipeline(self.settings, self.storage, connectors=[_MockConnector()])
        events = pipeline.run_once(max_items_per_source=5)
        self.assertGreaterEqual(len(events), 1)

    def test_scheduler_cycle_manual(self) -> None:
        scheduler = AutopublishScheduler(self.settings)
        scheduler.ingestion = IngestionPipeline(self.settings, scheduler.storage, connectors=[_MockConnector()])
        result = scheduler.run_cycle(max_items_per_source=5)
        self.assertIn(result["status"], {"pending_manual_approval", "published", "blocked_by_qa"})


if __name__ == "__main__":
    unittest.main()
