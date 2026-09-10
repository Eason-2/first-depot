from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

from core.config import Settings
from core.models import NormalizedEvent, TopicCluster
from workers.generation.draft_builder import DraftBuilder

_REFERENCE_PATTERN = re.compile(r"^- \[(\d+)\] (.+) - (https?://\S+)\s*$", re.MULTILINE)
_FACT_PATTERN = re.compile(
    r"^- (.+?)（([^，]+)，([^）]+)）。(.*?) 相关度 ([0-9.]+)，可信度 ([0-9.]+)。\s*$",
    re.MULTILINE,
)
_STOPWORDS = {
    "about",
    "after",
    "agent",
    "agents",
    "and",
    "are",
    "but",
    "can",
    "for",
    "from",
    "has",
    "how",
    "into",
    "its",
    "llm",
    "model",
    "models",
    "new",
    "not",
    "open",
    "our",
    "source",
    "that",
    "the",
    "their",
    "this",
    "using",
    "via",
    "was",
    "why",
    "will",
    "with",
    "your",
}


@dataclass(frozen=True)
class SourceReference:
    title: str
    url: str


@dataclass(frozen=True)
class PublishedMetadata:
    draft_id: str
    cluster_id: str
    confidence: float
    tags: list[str]
    published_date: str
    score: float
    source: str
    source_date: str
    summary: str
    relevance: float
    credibility: float
    upvotes: float
    comments: float
    references: list[SourceReference]


def _extract_quoted_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{key}:\s*'([^']*)'\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _extract_number(text: str, pattern: str, default: float) -> float:
    match = re.search(pattern, text, re.MULTILINE)
    try:
        return float(match.group(1)) if match else default
    except (TypeError, ValueError):
        return default


def _extract_tags(text: str) -> list[str]:
    match = re.search(r"^tags:\s*\[([^]]*)\]\s*$", text, re.MULTILINE)
    if not match:
        return ["ai-news", "automation", "longform", "zh"]
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


def _title_tokens(text: str) -> set[str]:
    tokens = set(re.findall(r"[A-Za-z0-9]+", text.lower()))
    return {token for token in tokens if len(token) >= 3 and token not in _STOPWORDS}


def _select_relevant_references(references: list[SourceReference]) -> list[SourceReference]:
    if not references:
        return []
    primary = references[0]
    primary_tokens = _title_tokens(primary.title)
    selected = [primary]
    seen_urls = {primary.url}
    for reference in references[1:]:
        if reference.url in seen_urls:
            continue
        overlap = len(primary_tokens.intersection(_title_tokens(reference.title)))
        if primary_tokens and overlap >= min(2, len(primary_tokens)):
            selected.append(reference)
            seen_urls.add(reference.url)
    return selected[:4]


def _parse_published(path: Path) -> PublishedMetadata:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    references = [SourceReference(title=title.strip(), url=url) for _, title, url in _REFERENCE_PATTERN.findall(raw)]
    if not references:
        raise ValueError("missing reference list")

    fact_match = _FACT_PATTERN.search(raw)
    primary = references[0]
    source = fact_match.group(2).strip() if fact_match else (urlparse(primary.url).hostname or "web")
    source_date = fact_match.group(3).strip() if fact_match else path.name[:10]
    summary = fact_match.group(4).strip() if fact_match else ""
    relevance = float(fact_match.group(5)) if fact_match else 0.6
    credibility = float(fact_match.group(6)) if fact_match else 0.7

    draft_id = _extract_quoted_value(raw, "draft_id")
    cluster_id = _extract_quoted_value(raw, "cluster_id")
    if not draft_id or not cluster_id:
        raise ValueError("missing draft_id or cluster_id")

    return PublishedMetadata(
        draft_id=draft_id,
        cluster_id=cluster_id,
        confidence=_extract_number(raw, r"^confidence:\s*([0-9.]+)", 0.7),
        tags=_extract_tags(raw),
        published_date=path.name[:10],
        score=_extract_number(raw, r"(?:在本轮评分\s*|聚类评分为\s*)([0-9.]+)/100", 50.0),
        source=source,
        source_date=source_date,
        summary=summary,
        relevance=relevance,
        credibility=credibility,
        upvotes=_extract_number(raw, r"(?:累计约\s*|合计约\s*)([0-9.]+)(?:\s*点赞|\s*个赞)", 0.0),
        comments=_extract_number(raw, r"(?:和\s*|、)([0-9.]+)(?:\s*评论|\s*条评论)", 0.0),
        references=_select_relevant_references(references),
    )


def _content_type(reference: SourceReference) -> str:
    lowered = f"{reference.title} {reference.url}".lower()
    if "arxiv.org" in lowered or any(word in lowered for word in ("evaluation", "training", "reasoning", "framework")):
        return "research"
    if "news.ycombinator.com" in lowered or reference.title.lower().startswith(("show hn:", "tell hn:")):
        return "discussion"
    if any(word in lowered for word in ("introducing", "launch hn:", "release", "gpt", "gemini", "qwen", "deepseek")):
        return "release"
    return "news"


def _event_id(url: str, index: int) -> str:
    digest = hashlib.sha1(f"{index}:{url}".encode("utf-8")).hexdigest()[:12]
    return f"historical_{digest}"


def _restore_events(metadata: PublishedMetadata) -> list[NormalizedEvent]:
    events: list[NormalizedEvent] = []
    for index, reference in enumerate(metadata.references):
        event_id = _event_id(reference.url, index)
        events.append(
            NormalizedEvent(
                event_id=event_id,
                source=metadata.source if index == 0 else (urlparse(reference.url).hostname or "web"),
                source_item_id=event_id,
                title=reference.title,
                summary=metadata.summary if index == 0 else "",
                url=reference.url,
                domain=urlparse(reference.url).hostname or "",
                author="",
                published_at=f"{metadata.source_date}T00:00:00Z",
                fetched_at=f"{metadata.published_date}T00:00:00Z",
                language="en",
                content_type=_content_type(reference),
                tags=[],
                engagement={
                    "upvotes": metadata.upvotes if index == 0 else 0.0,
                    "comments": metadata.comments if index == 0 else 0.0,
                    "views": 0.0,
                    "shares": 0.0,
                },
                ai_relevance=metadata.relevance if index == 0 else 0.6,
                credibility=metadata.credibility if index == 0 else 0.7,
                dedup={"canonical_url": reference.url},
                raw_payload_ref="",
            )
        )
    return events


def _replace_h1(content: str, title: str) -> str:
    return re.sub(r"^#\s+.*$", f"# {title}", content, count=1, flags=re.MULTILINE)


def _make_unique_title(title: str, published_date: str, used_titles: set[str]) -> str:
    if title not in used_titles:
        return title
    for angle in ("证据复盘", "工程复盘", "应用复盘", "边界复盘"):
        candidate = f"{title}（{published_date} {angle}）"
        if candidate not in used_titles:
            return candidate
    suffix = 2
    while f"{title}（{published_date} 复盘 {suffix}）" in used_titles:
        suffix += 1
    return f"{title}（{published_date} 复盘 {suffix}）"


def _write_published_file(path: Path, metadata: PublishedMetadata, title: str, content: str, urls: list[str]) -> None:
    safe_title = title.replace("'", "")
    lines = [
        "---",
        f"title: '{safe_title}'",
        f"draft_id: '{metadata.draft_id}'",
        f"cluster_id: '{metadata.cluster_id}'",
        f"confidence: {metadata.confidence}",
        f"tags: [{', '.join(metadata.tags)}]",
        "sources:",
    ]
    lines.extend(f"  - '{url}'" for url in urls)
    lines.extend(["---", "", content, ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def rewrite_articles(publish_dir: Path, builder: DraftBuilder, write: bool) -> dict[str, object]:
    used_titles: set[str] = set()
    updated: list[str] = []
    skipped: list[tuple[str, str]] = []
    source_counts: list[int] = []

    for path in sorted(publish_dir.glob("*.md")):
        try:
            metadata = _parse_published(path)
            events = _restore_events(metadata)
            if not events:
                raise ValueError("no relevant source remains")
            primary = events[0]
            cluster = TopicCluster(
                cluster_id=metadata.cluster_id,
                title=primary.title,
                representative_url=primary.url,
                event_ids=[event.event_id for event in events],
                sources=sorted({event.source for event in events}),
                size=len(events),
                score=metadata.score,
                explainability={},
            )
            draft = builder.generate(cluster, events, context_events=events)
            title = _make_unique_title(draft.title, metadata.published_date, used_titles)
            title = title.replace("'", "’")
            used_titles.add(title)
            content = _replace_h1(draft.content_markdown, title)
            if write:
                _write_published_file(path, metadata, title, content, [event.url for event in events])
            updated.append(path.name)
            source_counts.append(len(events))
        except (OSError, ValueError) as exc:
            skipped.append((path.name, str(exc)))

    return {
        "updated": updated,
        "skipped": skipped,
        "unique_titles": len(used_titles),
        "source_counts": source_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Rewrite legacy posts with topic-specific titles and evidence-driven copy.")
    parser.add_argument("--publish-dir", default="deliverables/published")
    parser.add_argument("--write", action="store_true", help="Write changes. Without this flag, perform a dry run.")
    args = parser.parse_args()

    with TemporaryDirectory() as temporary_root:
        settings = Settings.from_env(project_root=Path(temporary_root))
        builder = DraftBuilder(settings)
        result = rewrite_articles(Path(args.publish_dir), builder, write=args.write)
    mode = "write" if args.write else "dry-run"
    source_counts = result["source_counts"]
    print(f"mode={mode} updated={len(result['updated'])} skipped={len(result['skipped'])} unique_titles={result['unique_titles']}")
    if source_counts:
        print(f"sources_per_post=min:{min(source_counts)} max:{max(source_counts)}")
    for name, reason in result["skipped"]:
        print(f"skipped {name}: {reason}")


if __name__ == "__main__":
    main()
