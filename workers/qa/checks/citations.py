from __future__ import annotations

import re

from core.models import ArticleDraft

_SOURCE_LINE_ID_PATTERN = re.compile(r"^\s*-\s*\[(\d+)\]", re.MULTILINE)
_MIN_REQUIRED_SOURCES = 5


def _extract_sources_section(content: str) -> str:
    if "## 参考资料" in content:
        return content.split("## 参考资料", 1)[1]
    if "## Sources" in content:
        return content.split("## Sources", 1)[1]
    return ""


def check_citations(draft: ArticleDraft) -> tuple[bool, dict[str, int]]:
    available = len(draft.citations)
    required = min(_MIN_REQUIRED_SOURCES, available)
    sources_section = _extract_sources_section(draft.content_markdown)

    found_ids = set(_SOURCE_LINE_ID_PATTERN.findall(sources_section))
    url_hits = 0
    for citation in draft.citations:
        url = citation.get("url", "")
        if url and url in sources_section:
            url_hits += 1

    passed = len(found_ids) >= required and url_hits >= required
    return passed, {
        "required_sources": required,
        "found_source_lines": len(found_ids),
        "matched_source_urls": url_hits,
        "available_citations": available,
    }
