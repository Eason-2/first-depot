from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from core.models import NormalizedEvent
from core.utils import build_deterministic_id, canonicalize_url, clean_title, sha1_hex

_AI_KEYWORDS = {
    "ai",
    "artificial intelligence",
    "llm",
    "gpt",
    "agent",
    "machine learning",
    "deep learning",
    "inference",
    "model",
    "transformer",
}

_DOMAIN_CREDIBILITY = {
    "arxiv.org": 0.9,
    "openai.com": 0.9,
    "deepmind.google": 0.9,
    "news.ycombinator.com": 0.75,
}


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower()


def _estimate_ai_relevance(title: str, summary: str) -> float:
    text = f"{title} {summary}".lower()
    hits = sum(1 for keyword in _AI_KEYWORDS if keyword in text)
    return min(1.0, 0.2 + hits * 0.15)


def _credibility_for(url: str) -> float:
    domain = _domain(url)
    if domain in _DOMAIN_CREDIBILITY:
        return _DOMAIN_CREDIBILITY[domain]
    if domain.endswith(".edu"):
        return 0.8
    return 0.65


def _fallback_published(value: str | None) -> str:
    if value:
        return value
    return datetime.now(timezone.utc).isoformat()


def _fingerprints(url: str, title: str) -> dict[str, str]:
    canonical = canonicalize_url(url)
    return {
        "canonical_url": canonical,
        "url_fingerprint": sha1_hex(canonical)[:12] if canonical else "",
        "title_fingerprint": sha1_hex(clean_title(title))[:12],
        "embedding_fingerprint": "",
    }


def normalize_newsapi(item: dict[str, Any], fetched_at: str) -> NormalizedEvent | None:
    title = item.get("title") or ""
    url = item.get("url") or ""
    if not title or not url:
        return None

    source_item_id = url
    summary = item.get("description") or item.get("content") or ""

    return NormalizedEvent(
        event_id=build_deterministic_id("newsapi", source_item_id),
        source="newsapi",
        source_item_id=source_item_id,
        title=title.strip(),
        summary=summary.strip(),
        url=url,
        domain=_domain(url),
        author=(item.get("author") or "").strip(),
        published_at=_fallback_published(item.get("publishedAt")),
        fetched_at=fetched_at,
        language="en",
        content_type="news",
        tags=[],
        engagement={"views": 0.0, "upvotes": 0.0, "comments": 0.0, "shares": 0.0},
        ai_relevance=_estimate_ai_relevance(title, summary),
        credibility=_credibility_for(url),
        dedup=_fingerprints(url, title),
        raw_payload_ref=f"raw/newsapi/{source_item_id}",
    )


def normalize_hackernews(item: dict[str, Any], fetched_at: str) -> NormalizedEvent | None:
    title = item.get("title") or ""
    if not title:
        return None

    source_item_id = str(item.get("id") or "")
    if not source_item_id:
        return None

    url = item.get("url") or f"https://news.ycombinator.com/item?id={source_item_id}"
    published_unix = item.get("time")
    if isinstance(published_unix, int):
        published_at = datetime.fromtimestamp(published_unix, tz=timezone.utc).isoformat()
    else:
        published_at = _fallback_published(None)

    summary = item.get("text") or ""

    return NormalizedEvent(
        event_id=build_deterministic_id("hackernews", source_item_id),
        source="hackernews",
        source_item_id=source_item_id,
        title=title.strip(),
        summary=str(summary).strip(),
        url=url,
        domain=_domain(url),
        author=str(item.get("by") or "").strip(),
        published_at=published_at,
        fetched_at=fetched_at,
        language="en",
        content_type="discussion",
        tags=[],
        engagement={
            "views": 0.0,
            "upvotes": float(item.get("score") or 0),
            "comments": float(item.get("descendants") or 0),
            "shares": 0.0,
        },
        ai_relevance=_estimate_ai_relevance(title, str(summary)),
        credibility=_credibility_for(url),
        dedup=_fingerprints(url, title),
        raw_payload_ref=f"raw/hackernews/{source_item_id}",
    )


def normalize_arxiv(item: dict[str, Any], fetched_at: str) -> NormalizedEvent | None:
    title = item.get("title") or ""
    url = item.get("link") or item.get("id") or ""
    if not title or not url:
        return None

    source_item_id = item.get("id") or url
    summary = item.get("summary") or ""

    return NormalizedEvent(
        event_id=build_deterministic_id("arxiv", source_item_id),
        source="arxiv",
        source_item_id=source_item_id,
        title=title.strip(),
        summary=summary.strip(),
        url=url,
        domain=_domain(url),
        author="",
        published_at=_fallback_published(item.get("published")),
        fetched_at=fetched_at,
        language="en",
        content_type="research",
        tags=["research"],
        engagement={"views": 0.0, "upvotes": 0.0, "comments": 0.0, "shares": 0.0},
        ai_relevance=_estimate_ai_relevance(title, summary),
        credibility=_credibility_for(url),
        dedup=_fingerprints(url, title),
        raw_payload_ref=f"raw/arxiv/{sha1_hex(source_item_id)[:10]}",
    )


def normalize_item(source: str, item: dict[str, Any], fetched_at: str) -> NormalizedEvent | None:
    if source == "newsapi":
        return normalize_newsapi(item, fetched_at)
    if source == "hackernews":
        return normalize_hackernews(item, fetched_at)
    if source == "arxiv":
        return normalize_arxiv(item, fetched_at)
    return None
