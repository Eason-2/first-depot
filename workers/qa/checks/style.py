from __future__ import annotations

import re

from core.models import ArticleDraft

_BANNED_TERMS = {"guaranteed", "100%", "unstoppable", "secret trick", "稳赚", "闭眼入", "必赚"}
_MIN_VISIBLE_CHARS = 1200
_MIN_H2_HEADINGS = 6
_WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")
_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")
_H2_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def _visible_chars(text: str) -> int:
    ascii_words = len(_WORD_PATTERN.findall(text))
    cjk_chars = len(_CJK_PATTERN.findall(text))
    return cjk_chars + ascii_words


def check_style_and_structure(draft: ArticleDraft) -> tuple[bool, dict[str, object]]:
    lower = draft.content_markdown.lower()
    banned_hits = [term for term in _BANNED_TERMS if term in lower]
    visible_chars = _visible_chars(draft.content_markdown)
    noisy_markers = [marker for marker in ("**", "__") if marker in draft.content_markdown]
    h2_headings = _H2_PATTERN.findall(draft.content_markdown)
    unique_h2 = len({heading.strip() for heading in h2_headings})
    heading_count_ok = len(h2_headings) >= _MIN_H2_HEADINGS
    heading_diversity_ok = unique_h2 >= max(4, _MIN_H2_HEADINGS - 2)

    passed = (
        not banned_hits
        and visible_chars >= _MIN_VISIBLE_CHARS
        and not noisy_markers
        and heading_count_ok
        and heading_diversity_ok
    )
    return passed, {
        "banned_hits": banned_hits,
        "visible_chars": visible_chars,
        "min_visible_chars": _MIN_VISIBLE_CHARS,
        "noisy_markers": noisy_markers,
        "h2_heading_count": len(h2_headings),
        "h2_heading_unique_count": unique_h2,
        "min_h2_heading_count": _MIN_H2_HEADINGS,
    }
