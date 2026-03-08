from __future__ import annotations

from core.models import ArticleDraft


class GhostAdapter:
    target_name = "ghost"

    def publish(self, draft: ArticleDraft) -> str:
        raise NotImplementedError("Ghost adapter is a placeholder. Configure Ghost Admin API before enabling.")
