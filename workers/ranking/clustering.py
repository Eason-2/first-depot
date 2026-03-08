from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from core.models import NormalizedEvent, TopicCluster
from core.utils import clean_title, sha1_hex


def _cluster_key(event: NormalizedEvent) -> str:
    canonical_url = (event.dedup or {}).get("canonical_url") or ""
    if canonical_url:
        return f"url:{canonical_url}"
    return f"title:{clean_title(event.title)}"


def cluster_events(events: Iterable[NormalizedEvent]) -> list[TopicCluster]:
    grouped: dict[str, list[NormalizedEvent]] = defaultdict(list)
    for event in events:
        grouped[_cluster_key(event)].append(event)

    clusters: list[TopicCluster] = []
    for key, group in grouped.items():
        representative = sorted(group, key=lambda e: e.ai_relevance, reverse=True)[0]
        cluster_id = "cluster_" + sha1_hex(key)[:12]
        clusters.append(
            TopicCluster(
                cluster_id=cluster_id,
                title=representative.title,
                representative_url=representative.url,
                event_ids=[e.event_id for e in group],
                sources=sorted({e.source for e in group}),
                size=len(group),
                score=0.0,
                explainability={},
            )
        )

    return clusters
