from __future__ import annotations

import json

from core.config import Settings
from workers.publishing.scheduler import AutopublishScheduler


def main() -> None:
    settings = Settings.from_env()
    scheduler = AutopublishScheduler(settings)
    result = scheduler.run_cycle(max_items_per_source=10)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
