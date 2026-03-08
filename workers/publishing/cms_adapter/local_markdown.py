from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from core.models import ArticleDraft
from core.utils import slugify


class LocalMarkdownAdapter:
    target_name = "local_markdown"

    def __init__(self, publish_dir: Path) -> None:
        self.publish_dir = publish_dir
        self.publish_dir.mkdir(parents=True, exist_ok=True)

    def publish(self, draft: ArticleDraft) -> str:
        now = datetime.now(timezone.utc)
        date_prefix = now.strftime("%Y-%m-%d")
        slug = slugify(draft.title)
        if slug == "untitled":
            slug = f"post-{draft.cluster_id.split('_')[-1]}"

        path = self.publish_dir / f"{date_prefix}-{slug}.md"
        safe_title = draft.title.replace("'", "")

        lines = [
            "---",
            f"title: '{safe_title}'",
            f"draft_id: '{draft.draft_id}'",
            f"cluster_id: '{draft.cluster_id}'",
            f"confidence: {draft.confidence}",
            f"tags: [{', '.join(draft.tags)}]",
            "sources:",
        ]
        for citation in draft.citations:
            lines.append(f"  - '{citation['url']}'")
        lines.extend(["---", "", draft.content_markdown, ""])
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)
