from __future__ import annotations

import os

from scripts.daemon import main


if __name__ == "__main__":
    os.environ.setdefault("BLOG_HOST", "127.0.0.1")
    os.environ.setdefault("BLOG_PORT", "8088")
    os.environ.setdefault("AUTO_PUBLISH_MODE", "auto")
    os.environ.setdefault("ENABLE_CLOUDFLARE_TUNNEL", "1")
    main()
