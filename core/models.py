from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class NormalizedEvent:
    event_id: str
    source: str
    source_item_id: str
    title: str
    summary: str
    url: str
    domain: str
    author: str
    published_at: str
    fetched_at: str
    language: str
    content_type: str
    tags: list[str] = field(default_factory=list)
    engagement: dict[str, float] = field(default_factory=dict)
    ai_relevance: float = 0.0
    credibility: float = 0.5
    dedup: dict[str, str] = field(default_factory=dict)
    raw_payload_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TopicCluster:
    cluster_id: str
    title: str
    representative_url: str
    event_ids: list[str]
    sources: list[str]
    size: int
    score: float
    explainability: dict[str, float]
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArticleDraft:
    draft_id: str
    cluster_id: str
    title: str
    content_markdown: str
    citations: list[dict[str, str]]
    tags: list[str]
    confidence: float
    status: str
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QAResult:
    report_id: str
    draft_id: str
    passed: bool
    reason_codes: list[str]
    details: dict[str, Any]
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PublishResult:
    job_id: str
    draft_id: str
    status: str
    output_ref: str
    error_message: str
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
