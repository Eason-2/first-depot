from __future__ import annotations

import os

from apps.api.server import run_api_server


if __name__ == "__main__":
    os.environ.setdefault("BLOG_HOST", "0.0.0.0")
    os.environ.setdefault("BLOG_PORT", "8088")
    run_api_server()
