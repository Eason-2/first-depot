from __future__ import annotations

from core.models import ArticleDraft


class WordPressAdapter:
    target_name = "wordpress"

    def publish(self, draft: ArticleDraft) -> str:
        raise NotImplementedError("WordPress adapter is a placeholder. Configure REST credentials before enabling.")
