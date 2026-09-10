from __future__ import annotations

import re

from core.models import ArticleDraft

_BANNED_TERMS = {"guaranteed", "100%", "unstoppable", "secret trick", "稳赚", "闭眼入", "必赚"}
_MIN_VISIBLE_CHARS = 1200
_MIN_H2_HEADINGS = 6
_WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")
_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")
_H2_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
_GENERIC_TITLES = {
    "这条 AI 话题为什么值得你认真看一眼",
    "这波 AI 热点里，真正有价值的信息是什么",
    "我怎么判断这条 AI 信息值不值得跟进",
    "别急着下结论，先把这条 AI 话题看透",
}
_TOPIC_TITLE_SUFFIXES = (
    "：核心变化与验证重点",
    "：证据、边界与影响",
    " 值得关注什么？从来源到落地",
    " 看落地机会与限制",
    "：从原始资料到可执行判断",
    "，现有证据能说明什么",
    " 实测前先看这几项边界",
    "：事实、限制与下一步",
)


def _visible_chars(text: str) -> int:
    ascii_words = len(_WORD_PATTERN.findall(text))
    cjk_chars = len(_CJK_PATTERN.findall(text))
    return cjk_chars + ascii_words


def _duplicate_long_lines(content: str) -> list[str]:
    body = content.split("## 参考资料", 1)[0]
    seen: set[str] = set()
    duplicates: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        normalized = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "", line).lower()
        if len(normalized) < 32:
            continue
        if normalized in seen and line not in duplicates:
            duplicates.append(line)
        seen.add(normalized)
    return duplicates


def _topic_phrase_from_title(title: str) -> str:
    phrase = re.sub(r"（\d{4}-\d{2}-\d{2} [^）]+）$", "", title.strip())
    if phrase.startswith("解读 "):
        phrase = phrase[3:]
    elif phrase.startswith("从 "):
        phrase = phrase[2:]
    elif phrase.startswith("围绕 "):
        phrase = phrase[3:]
    elif phrase.startswith("重新审视 "):
        phrase = phrase[5:]
    for suffix in _TOPIC_TITLE_SUFFIXES:
        if phrase.endswith(suffix):
            phrase = phrase[: -len(suffix)]
            break
    return phrase.rstrip(".。… ")


def _normalize_topic_match(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "", text.replace("’", "'")).lower()


def check_style_and_structure(draft: ArticleDraft) -> tuple[bool, dict[str, object]]:
    lower = draft.content_markdown.lower()
    banned_hits = [term for term in _BANNED_TERMS if term in lower]
    visible_chars = _visible_chars(draft.content_markdown)
    noisy_markers = [marker for marker in ("**", "__") if marker in draft.content_markdown]
    h2_headings = _H2_PATTERN.findall(draft.content_markdown)
    unique_h2 = len({heading.strip() for heading in h2_headings})
    heading_count_ok = len(h2_headings) >= _MIN_H2_HEADINGS
    heading_diversity_ok = unique_h2 >= max(4, _MIN_H2_HEADINGS - 2)
    generic_title = draft.title.strip() in _GENERIC_TITLES
    duplicate_long_lines = _duplicate_long_lines(draft.content_markdown)
    body_without_h1 = re.sub(r"^#\s+.*$", "", draft.content_markdown, count=1, flags=re.MULTILINE)
    topic_phrase = _topic_phrase_from_title(draft.title)
    normalized_topic = _normalize_topic_match(topic_phrase)
    topic_phrase_present = len(normalized_topic) >= 3 and normalized_topic in _normalize_topic_match(body_without_h1)

    passed = (
        not banned_hits
        and visible_chars >= _MIN_VISIBLE_CHARS
        and not noisy_markers
        and heading_count_ok
        and heading_diversity_ok
        and not generic_title
        and not duplicate_long_lines
        and topic_phrase_present
    )
    return passed, {
        "banned_hits": banned_hits,
        "visible_chars": visible_chars,
        "min_visible_chars": _MIN_VISIBLE_CHARS,
        "noisy_markers": noisy_markers,
        "h2_heading_count": len(h2_headings),
        "h2_heading_unique_count": unique_h2,
        "min_h2_heading_count": _MIN_H2_HEADINGS,
        "generic_title": generic_title,
        "duplicate_long_lines": duplicate_long_lines,
        "topic_phrase": topic_phrase,
        "topic_phrase_present": topic_phrase_present,
    }
