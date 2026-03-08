from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha1_hex(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def build_deterministic_id(source: str, source_item_id: str) -> str:
    digest = sha1_hex(f"{source}:{source_item_id}")[:12]
    return f"{source}_{digest}"


def clean_title(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r"[^a-z0-9\\s]", " ", lowered)
    return re.sub(r"\\s+", " ", lowered).strip()


def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path, "", "", ""))


def slugify(text: str, max_len: int = 80) -> str:
    slug = clean_title(text).replace(" ", "-")
    slug = re.sub(r"-+", "-", slug).strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    return slug or "untitled"
