from __future__ import annotations

import json

from core.config import Settings
from core.models import NormalizedEvent, TopicCluster
from core.storage import Storage
from workers.ranking.clustering import cluster_events
from workers.ranking.scoring import score_cluster


class RankingPipeline:
    def __init__(self, settings: Settings, storage: Storage) -> None:
        self.settings = settings
        self.storage = storage

    def run(self, events: list[NormalizedEvent]) -> list[TopicCluster]:
        if not events:
            return []

        clusters = cluster_events(events)
        events_by_id = {event.event_id: event for event in events}
        scored = [score_cluster(cluster, events_by_id) for cluster in clusters]
        ranked = sorted(scored, key=lambda c: (c.score, c.size), reverse=True)

        self.storage.save_clusters(ranked)
        self._save_runtime_snapshot(ranked)
        return ranked

    def _save_runtime_snapshot(self, clusters: list[TopicCluster]) -> None:
        snapshot_path = self.settings.runtime_dir / "latest_topics.json"
        payload = [cluster.to_dict() for cluster in clusters]
        snapshot_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
