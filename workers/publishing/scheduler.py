from __future__ import annotations

import json
import time
import traceback

from core.config import Settings
from core.storage import Storage
from core.utils import build_deterministic_id, utc_now_iso
from workers.generation.draft_builder import DraftBuilder
from workers.ingestion.pipeline import IngestionPipeline
from workers.publishing.cms_adapter.local_markdown import LocalMarkdownAdapter
from workers.qa.pipeline import QAPipeline
from workers.ranking.pipeline import RankingPipeline


class AutopublishScheduler:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.storage = Storage(settings.db_path)
        self.ingestion = IngestionPipeline(settings, self.storage)
        self.ranking = RankingPipeline(settings, self.storage)
        self.generator = DraftBuilder(settings)
        self.qa = QAPipeline()
        self.publisher = LocalMarkdownAdapter(settings.publish_dir)

    def run_cycle(self, max_items_per_source: int = 15) -> dict[str, object]:
        cycle_time = utc_now_iso()
        events = self.ingestion.run_once(max_items_per_source=max_items_per_source)
        if not events:
            result = {
                "cycle_time": cycle_time,
                "status": "no_events",
                "message": "No events fetched from sources.",
            }
            self._write_last_run(result)
            return result

        clusters = self.ranking.run(events)
        if not clusters:
            result = {
                "cycle_time": cycle_time,
                "status": "no_clusters",
                "message": "No topic clusters produced.",
                "events_count": len(events),
            }
            self._write_last_run(result)
            return result

        top_cluster = clusters[0]
        events_by_id = {event.event_id: event for event in events}
        cluster_events = [events_by_id[eid] for eid in top_cluster.event_ids if eid in events_by_id]

        draft = self.generator.generate(top_cluster, cluster_events, context_events=events)
        self.storage.save_draft(draft)

        qa_result = self.qa.evaluate(draft)
        self.storage.save_qa_result(qa_result)

        job_id = build_deterministic_id("job", f"{draft.draft_id}:{cycle_time}")
        now = utc_now_iso()

        if not qa_result.passed:
            self.storage.save_publish_job(
                job_id=job_id,
                draft_id=draft.draft_id,
                status="blocked_by_qa",
                target=self.publisher.target_name,
                output_ref="",
                error_message=",".join(qa_result.reason_codes),
                created_at=now,
                updated_at=now,
            )
            result = {
                "cycle_time": cycle_time,
                "status": "blocked_by_qa",
                "events_count": len(events),
                "cluster_id": top_cluster.cluster_id,
                "draft_id": draft.draft_id,
                "qa_reason_codes": qa_result.reason_codes,
            }
            self._write_last_run(result)
            return result

        if self.settings.auto_publish_mode == "manual":
            self.storage.save_publish_job(
                job_id=job_id,
                draft_id=draft.draft_id,
                status="pending_manual_approval",
                target=self.publisher.target_name,
                output_ref="",
                error_message="",
                created_at=now,
                updated_at=now,
            )
            result = {
                "cycle_time": cycle_time,
                "status": "pending_manual_approval",
                "events_count": len(events),
                "cluster_id": top_cluster.cluster_id,
                "draft_id": draft.draft_id,
            }
            self._write_last_run(result)
            return result

        try:
            output_ref = self.publisher.publish(draft)
            status = "published"
            error_message = ""
        except Exception as exc:
            output_ref = ""
            status = "publish_failed"
            error_message = str(exc)

        self.storage.save_publish_job(
            job_id=job_id,
            draft_id=draft.draft_id,
            status=status,
            target=self.publisher.target_name,
            output_ref=output_ref,
            error_message=error_message,
            created_at=now,
            updated_at=now,
        )

        result = {
            "cycle_time": cycle_time,
            "status": status,
            "events_count": len(events),
            "cluster_id": top_cluster.cluster_id,
            "draft_id": draft.draft_id,
            "output_ref": output_ref,
            "error_message": error_message,
        }
        self._write_last_run(result)
        return result

    def run_forever(self, max_items_per_source: int = 15) -> None:
        while True:
            try:
                self.run_cycle(max_items_per_source=max_items_per_source)
            except Exception as exc:
                result = {
                    "cycle_time": utc_now_iso(),
                    "status": "cycle_error",
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(limit=8),
                }
                self._write_last_run(result)
            time.sleep(self.settings.schedule_interval_minutes * 60)

    def _write_last_run(self, result: dict[str, object]) -> None:
        path = self.settings.runtime_dir / "last_run.json"
        path.write_text(json.dumps(result, indent=2), encoding="utf-8")
