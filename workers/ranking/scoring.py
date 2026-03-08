from __future__ import annotations

from datetime import datetime, timezone

from core.models import NormalizedEvent, TopicCluster

_SOURCE_WEIGHT = {
    "arxiv": 0.95,
    "newsapi": 0.8,
    "hackernews": 0.75,
}


def _hours_since(published_at: str, now: datetime) -> float:
    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except ValueError:
        return 72.0
    return max(0.0, (now - dt.astimezone(timezone.utc)).total_seconds() / 3600)


def _recency_score(hours_old: float) -> float:
    if hours_old <= 6:
        return 1.0
    if hours_old <= 24:
        return 0.8
    if hours_old <= 72:
        return 0.5
    return 0.2


def score_cluster(cluster: TopicCluster, events_by_id: dict[str, NormalizedEvent]) -> TopicCluster:
    now = datetime.now(timezone.utc)
    events = [events_by_id[event_id] for event_id in cluster.event_ids if event_id in events_by_id]
    if not events:
        return cluster

    recency_values = []
    relevance_values = []
    credibility_values = []
    engagement_values = []
    source_values = []

    for event in events:
        recency_values.append(_recency_score(_hours_since(event.published_at, now)))
        relevance_values.append(event.ai_relevance)
        credibility_values.append(event.credibility)
        engagement = (event.engagement.get("upvotes", 0.0) * 1.0) + (event.engagement.get("comments", 0.0) * 0.4)
        engagement_values.append(min(1.0, engagement / 500.0))
        source_values.append(_SOURCE_WEIGHT.get(event.source, 0.7))

    recency = sum(recency_values) / len(recency_values)
    relevance = sum(relevance_values) / len(relevance_values)
    credibility = sum(credibility_values) / len(credibility_values)
    engagement = sum(engagement_values) / len(engagement_values)
    source_quality = sum(source_values) / len(source_values)
    diversity = min(1.0, len(cluster.sources) / 3.0)

    score_0_1 = (
        recency * 0.30
        + relevance * 0.25
        + credibility * 0.15
        + engagement * 0.15
        + diversity * 0.10
        + source_quality * 0.05
    )

    cluster.score = round(score_0_1 * 100, 2)
    cluster.explainability = {
        "recency": round(recency, 3),
        "relevance": round(relevance, 3),
        "credibility": round(credibility, 3),
        "engagement": round(engagement, 3),
        "diversity": round(diversity, 3),
        "source_quality": round(source_quality, 3),
    }
    return cluster
