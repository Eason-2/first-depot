from __future__ import annotations

import re

from core.models import ArticleDraft

_WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")
_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")
_MIN_VISIBLE_CHARS = 1200


def _visible_chars(text: str) -> int:
    ascii_words = len(_WORD_PATTERN.findall(text))
    cjk_chars = len(_CJK_PATTERN.findall(text))
    return cjk_chars + ascii_words


def check_safety(draft: ArticleDraft) -> tuple[bool, dict[str, object]]:
    visible_chars = _visible_chars(draft.content_markdown)
    too_short = visible_chars < _MIN_VISIBLE_CHARS
    has_sources_section = ("## Sources" in draft.content_markdown) or ("## 参考资料" in draft.content_markdown)
    return (not too_short) and has_sources_section, {
        "too_short": too_short,
        "visible_chars": visible_chars,
        "min_visible_chars": _MIN_VISIBLE_CHARS,
        "has_sources_section": has_sources_section,
    }
