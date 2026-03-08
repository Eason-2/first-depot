from __future__ import annotations

import os

from scripts.daemon import main


if __name__ == "__main__":
    os.environ.setdefault("BLOG_HOST", "0.0.0.0")
    os.environ.setdefault("BLOG_PORT", "8088")
    os.environ.setdefault("AUTO_PUBLISH_MODE", "auto")
    main()
