from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from core.models import ArticleDraft, NormalizedEvent, QAResult, TopicCluster


class Storage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS raw_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    source_item_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    source_item_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    published_at TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    ai_relevance REAL NOT NULL,
                    credibility REAL NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS topic_clusters (
                    cluster_id TEXT PRIMARY KEY,
                    score REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS article_drafts (
                    draft_id TEXT PRIMARY KEY,
                    cluster_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS quality_reports (
                    report_id TEXT PRIMARY KEY,
                    draft_id TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS publish_jobs (
                    job_id TEXT PRIMARY KEY,
                    draft_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    target TEXT NOT NULL,
                    output_ref TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def save_raw_item(self, source: str, source_item_id: str, payload: dict[str, Any], fetched_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO raw_items (source, source_item_id, payload_json, fetched_at)
                VALUES (?, ?, ?, ?)
                """,
                (source, source_item_id, json.dumps(payload), fetched_at),
            )

    def save_events(self, events: list[NormalizedEvent]) -> int:
        inserted = 0
        with self._connect() as conn:
            for event in events:
                cursor = conn.execute(
                    """
                    INSERT OR IGNORE INTO events (
                        event_id, source, source_item_id, title, url,
                        published_at, fetched_at, ai_relevance, credibility, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_id,
                        event.source,
                        event.source_item_id,
                        event.title,
                        event.url,
                        event.published_at,
                        event.fetched_at,
                        event.ai_relevance,
                        event.credibility,
                        json.dumps(event.to_dict()),
                    ),
                )
                if cursor.rowcount > 0:
                    inserted += 1
        return inserted

    def save_clusters(self, clusters: list[TopicCluster]) -> None:
        with self._connect() as conn:
            for cluster in clusters:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO topic_clusters (cluster_id, score, created_at, payload_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (cluster.cluster_id, cluster.score, cluster.created_at, json.dumps(cluster.to_dict())),
                )

    def save_draft(self, draft: ArticleDraft) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO article_drafts (
                    draft_id, cluster_id, title, confidence, status, created_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    draft.draft_id,
                    draft.cluster_id,
                    draft.title,
                    draft.confidence,
                    draft.status,
                    draft.created_at,
                    json.dumps(draft.to_dict()),
                ),
            )

    def save_qa_result(self, result: QAResult) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO quality_reports (
                    report_id, draft_id, passed, created_at, payload_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (result.report_id, result.draft_id, 1 if result.passed else 0, result.created_at, json.dumps(result.to_dict())),
            )

    def save_publish_job(
        self,
        job_id: str,
        draft_id: str,
        status: str,
        target: str,
        output_ref: str,
        error_message: str,
        created_at: str,
        updated_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO publish_jobs (
                    job_id, draft_id, status, target, output_ref, error_message, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (job_id, draft_id, status, target, output_ref, error_message, created_at, updated_at),
            )

    def fetch_latest_clusters(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT payload_json FROM topic_clusters
                ORDER BY score DESC, created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def fetch_latest_draft(self) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT payload_json FROM article_drafts
                ORDER BY created_at DESC
                LIMIT 1
                """
            ).fetchone()
        return json.loads(row["payload_json"]) if row else None
