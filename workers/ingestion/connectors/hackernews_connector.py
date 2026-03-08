from __future__ import annotations

from workers.ingestion.base import BaseConnector


class HackerNewsConnector(BaseConnector):
    source_name = "hackernews"

    def fetch_items(self, limit: int) -> list[dict]:
        top_ids = self._request_json("https://hacker-news.firebaseio.com/v0/topstories.json")
        items: list[dict] = []
        for item_id in top_ids[:limit]:
            item = self._request_json(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json")
            if isinstance(item, dict):
                items.append(item)
        return items
