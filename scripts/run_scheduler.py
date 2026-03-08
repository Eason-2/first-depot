from __future__ import annotations

from core.config import Settings
from workers.publishing.scheduler import AutopublishScheduler


def main() -> None:
    settings = Settings.from_env()
    scheduler = AutopublishScheduler(settings)
    scheduler.run_forever(max_items_per_source=10)


if __name__ == "__main__":
    main()
