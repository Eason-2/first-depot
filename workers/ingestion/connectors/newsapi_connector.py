from __future__ import annotations

from workers.ingestion.base import BaseConnector


class NewsAPIConnector(BaseConnector):
    source_name = "newsapi"

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    def fetch_items(self, limit: int) -> list[dict]:
        if not self.api_key:
            return []

        params = {
            "q": "artificial intelligence OR LLM OR generative AI",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": max(1, min(limit, 100)),
        }
        headers = {"X-Api-Key": self.api_key}
        payload = self._request_json("https://newsapi.org/v2/everything", params=params, headers=headers)
        return payload.get("articles", [])
