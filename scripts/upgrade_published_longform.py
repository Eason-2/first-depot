from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from core.config import Settings
from core.models import NormalizedEvent, TopicCluster
from core.storage import Storage
from workers.generation.draft_builder import DraftBuilder

_WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")


def _extract_quoted_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{key}:\s*'([^']*)'\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _load_all_events(conn: sqlite3.Connection) -> list[NormalizedEvent]:
    rows = conn.execute("SELECT payload_json FROM events").fetchall()
    return [NormalizedEvent(**json.loads(row[0])) for row in rows]


def _load_cluster(conn: sqlite3.Connection, cluster_id: str) -> TopicCluster | None:
    row = conn.execute("SELECT payload_json FROM topic_clusters WHERE cluster_id = ?", (cluster_id,)).fetchone()
    if not row:
        return None
    return TopicCluster(**json.loads(row[0]))


def _write_published_file(
    path: Path,
    draft_id: str,
    draft_content: str,
    cluster_id: str,
    title: str,
    confidence: float,
    tags: list[str],
    citation_urls: list[str],
) -> None:
    safe_title = title.replace("'", "")
    lines = [
        "---",
        f"title: '{safe_title}'",
        f"draft_id: '{draft_id}'",
        f"cluster_id: '{cluster_id}'",
        f"confidence: {confidence}",
        f"tags: [{', '.join(tags)}]",
        "sources:",
    ]
    for url in citation_urls:
        lines.append(f"  - '{url}'")
    lines.extend(["---", "", draft_content, ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    settings = Settings.from_env()
    storage = Storage(settings.db_path)
    builder = DraftBuilder(settings)

    publish_dir = settings.publish_dir
    with sqlite3.connect(settings.db_path) as db:
        all_events = _load_all_events(db)
        events_by_id = {event.event_id: event for event in all_events}

        updated: list[tuple[str, int, int]] = []
        skipped: list[tuple[str, str]] = []

        for path in sorted(publish_dir.glob("*.md")):
            raw = path.read_text(encoding="utf-8", errors="replace")
            draft_id = _extract_quoted_value(raw, "draft_id")
            cluster_id = _extract_quoted_value(raw, "cluster_id")
            if not draft_id or not cluster_id:
                skipped.append((path.name, "missing draft_id or cluster_id"))
                continue

            cluster = _load_cluster(db, cluster_id)
            if not cluster:
                skipped.append((path.name, f"cluster not found: {cluster_id}"))
                continue

            cluster_events = [events_by_id[event_id] for event_id in cluster.event_ids if event_id in events_by_id]
            if not cluster_events:
                skipped.append((path.name, f"cluster events missing for {cluster_id}"))
                continue

            regenerated = builder.generate(cluster, cluster_events, context_events=all_events)
            regenerated.draft_id = draft_id

            storage.save_draft(regenerated)
            _write_published_file(
                path=path,
                draft_id=draft_id,
                draft_content=regenerated.content_markdown,
                cluster_id=regenerated.cluster_id,
                title=regenerated.title,
                confidence=regenerated.confidence,
                tags=regenerated.tags,
                citation_urls=[citation["url"] for citation in regenerated.citations],
            )

            word_count = len(_WORD_PATTERN.findall(regenerated.content_markdown))
            updated.append((path.name, word_count, len(regenerated.citations)))

    print("Updated published files:")
    for name, words, citations in updated:
        print(f"- {name}: words={words}, citations={citations}")

    if skipped:
        print("Skipped:")
        for name, reason in skipped:
            print(f"- {name}: {reason}")


if __name__ == "__main__":
    main()
