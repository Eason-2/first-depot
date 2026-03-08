from __future__ import annotations

from collections.abc import Iterable

from core.config import Settings
from core.models import NormalizedEvent
from core.storage import Storage
from core.utils import utc_now_iso
from workers.ingestion.connectors.arxiv_connector import ArxivConnector
from workers.ingestion.connectors.hackernews_connector import HackerNewsConnector
from workers.ingestion.connectors.newsapi_connector import NewsAPIConnector
from workers.ingestion.normalize import normalize_item


class IngestionPipeline:
    def __init__(
        self,
        settings: Settings,
        storage: Storage,
        connectors: Iterable[object] | None = None,
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.connectors = list(connectors or self._default_connectors())

    def _default_connectors(self) -> list[object]:
        return [
            NewsAPIConnector(api_key=self.settings.newsapi_key),
            HackerNewsConnector(),
            ArxivConnector(),
        ]

    def run_once(self, max_items_per_source: int = 15) -> list[NormalizedEvent]:
        fetched_at = utc_now_iso()
        normalized_events: list[NormalizedEvent] = []

        for connector in self.connectors:
            source = getattr(connector, "source_name")
            try:
                items = connector.fetch_items(limit=max_items_per_source)
            except Exception:
                items = []

            for item in items:
                source_item_id = str(item.get("id") or item.get("url") or item.get("link") or "unknown")
                self.storage.save_raw_item(source, source_item_id, item, fetched_at)
                event = normalize_item(source, item, fetched_at)
                if event:
                    normalized_events.append(event)

        self.storage.save_events(normalized_events)
        return normalized_events
