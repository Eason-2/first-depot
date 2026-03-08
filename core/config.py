from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    project_root: Path
    runtime_dir: Path
    publish_dir: Path
    db_path: Path
    auto_publish_mode: str
    schedule_interval_minutes: int
    target_cms: str
    newsapi_key: str | None
    api_host: str
    api_port: int
    admin_token: str | None

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> "Settings":
        root = project_root or Path(__file__).resolve().parents[1]
        runtime_dir = root / "runtime"
        publish_dir = root / "deliverables" / "published"
        db_path = runtime_dir / "autopublisher.db"

        mode = os.getenv("AUTO_PUBLISH_MODE", "manual").strip().lower()
        if mode not in {"manual", "auto"}:
            mode = "manual"

        interval_raw = os.getenv("SCHEDULE_INTERVAL_MINUTES", "60")
        try:
            interval = max(5, int(interval_raw))
        except ValueError:
            interval = 60

        target_cms = os.getenv("TARGET_CMS", "local_markdown").strip().lower()
        newsapi_key = os.getenv("NEWSAPI_KEY")
        api_host = os.getenv("BLOG_HOST", "127.0.0.1").strip() or "127.0.0.1"
        port_raw = os.getenv("BLOG_PORT", "8088").strip()
        try:
            api_port = int(port_raw)
        except ValueError:
            api_port = 8088
        if api_port < 1 or api_port > 65535:
            api_port = 8088

        admin_token = os.getenv("ADMIN_TOKEN")
        if admin_token:
            admin_token = admin_token.strip()
        if not admin_token:
            admin_token = None

        settings = cls(
            project_root=root,
            runtime_dir=runtime_dir,
            publish_dir=publish_dir,
            db_path=db_path,
            auto_publish_mode=mode,
            schedule_interval_minutes=interval,
            target_cms=target_cms,
            newsapi_key=newsapi_key,
            api_host=api_host,
            api_port=api_port,
            admin_token=admin_token,
        )
        settings.ensure_directories()
        return settings

    def ensure_directories(self) -> None:
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.publish_dir.mkdir(parents=True, exist_ok=True)
