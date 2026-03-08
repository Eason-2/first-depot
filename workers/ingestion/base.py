from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class BaseConnector(ABC):
    source_name: str

    @abstractmethod
    def fetch_items(self, limit: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    def _request_json(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        query = f"?{urlencode(params)}" if params else ""
        req = Request(url + query, headers=headers or {})
        with urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8")
        return json.loads(body)

    def _request_text(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> str:
        query = f"?{urlencode(params)}" if params else ""
        req = Request(url + query, headers=headers or {})
        with urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8")
