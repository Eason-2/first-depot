from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone

from core.config import Settings
from core.models import ArticleDraft, NormalizedEvent, TopicCluster
from core.utils import build_deterministic_id

_WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")
_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")
_STOPWORDS = {
    "about",
    "after",
    "again",
    "agent",
    "against",
    "among",
    "being",
    "between",
    "could",
    "every",
    "first",
    "from",
    "their",
    "there",
    "these",
    "those",
    "under",
    "while",
    "with",
    "without",
}
_AI_TOPIC_HINTS = {
    "ai",
    "agent",
    "agents",
    "anthropic",
    "arxiv",
    "automation",
    "benchmark",
    "evaluation",
    "gpt",
    "inference",
    "learning",
    "llm",
    "model",
    "models",
    "neural",
    "openai",
    "reasoning",
    "training",
}

_OUTLINES = [
    {
        "hook": "先说我的判断",
        "facts": "我先把关键事实摆出来",
        "insight": "为什么这件事不只是热度问题",
        "action": "如果你真要做，可以先从这几步开始",
        "risk": "最容易踩的坑",
        "close": "最后给你一个可直接落地的复盘框架",
        "sources": "参考资料",
        "order": ["hook", "facts", "insight", "action", "risk", "close"],
    },
    {
        "hook": "先给忙人版结论",
        "facts": "核心信息复盘：发生了什么、没发生什么",
        "insight": "看完资料后，我真正重视的信号",
        "action": "从今天到 90 天，怎么推进更稳",
        "risk": "别被热度带节奏：风险清单",
        "close": "给团队同步时可以直接照着讲",
        "sources": "参考资料",
        "order": ["hook", "insight", "facts", "risk", "action", "close"],
    },
    {
        "hook": "先把话挑明",
        "facts": "事实层：哪些信息最值得信",
        "insight": "这件事对产品、工程、运营分别意味着什么",
        "action": "一条可执行路线：先小步验证，再逐步放大",
        "risk": "成本、稳定性、协同这三类风险最常见",
        "close": "怎么判断该继续加码还是及时止损",
        "sources": "参考资料",
        "order": ["hook", "facts", "risk", "insight", "close", "action"],
    },
    {
        "hook": "别急着站队，先看证据",
        "facts": "证据链梳理：主线与旁证",
        "insight": "我认为最有价值的三个观察",
        "action": "落地节奏建议：7 天、30 天、90 天",
        "risk": "会拖垮项目的隐性问题",
        "close": "你明天就能启动的动作清单",
        "sources": "参考资料",
        "order": ["hook", "facts", "insight", "risk", "close", "action"],
    },
]

_INTRO_OPENERS = [
    "先不喊口号，先看证据。",
    "这次不玩悬念，先把关键点摊开。",
    "先说结论：值得跟，但不值得盲冲。",
    "热闹归热闹，先把账算清再说。",
]
_INTRO_FRAMES = [
    "把它当成一次体检，不是热搜接力赛。",
    "先别急着上头，咖啡可以续杯，决策别续命。",
    "这类议题最怕一眼定终身，所以先拆分看。",
    "与其猜“会不会爆”，不如看“能不能复盘”。",
]
_INTRO_CLOSES = [
    "这些信号还不构成保证，但足够进入认真评估阶段。",
    "它不是稳赢牌，不过已经是该上桌讨论的议题。",
    "结论不是“马上冲”，而是“可以算账并试跑”。",
    "别把它当神话，也别当噪声，按证据推进最稳。",
]
_INSIGHT_LEADS = [
    "真正贵的不是试错，而是试了半天却没留下可复用方法。",
    "很多团队输的不是方向，而是把“讨论热度”当“执行进度”。",
    "看起来像技术问题，最后常常卡在协同和节奏。",
    "如果把项目比作长跑，前 5 公里冲刺通常不叫领先，叫透支。",
]
_ACTION_PLANS = [
    [
        "- 第一步（7 天）：把目标写成可量化指标，同时定义失败阈值和回滚条件。",
        "- 第二步（30 天）：跑一个小规模试点，重点看效果、成本、稳定性三组数据。",
        "- 第三步（90 天）：根据试点结果决定扩容或收缩，不要在证据不足时重投入。",
        "- 每周固定复盘：记录假设、证据、结果和下周动作，减少靠感觉决策。",
        "- 对外沟通时：能证实的才承诺，暂时不能证实的明确写清边界。",
    ],
    [
        "- 如果资源紧，先盯住 2~3 个关键指标，其余先放观察席。",
        "- 先做“低风险版”上线：保留人工兜底，别一开始就全自动。",
        "- 每周只回答三个问题：效果有没有变好、成本有没有失控、团队有没有更顺手。",
        "- 先把失败样本收集齐，再谈扩大范围；没有反例的成功通常不稳。",
        "- 推进节奏建议是“短试验 + 快复盘 + 小迭代”，别搞一锤子工程。",
    ],
    [
        "- 不急着做也没关系，先把可观察信号列成清单，避免“错过焦虑”。",
        "- 可以先做一版影子流程：不影响正式业务，只验证判断是否靠谱。",
        "- 先约定好停止条件，比约定“什么时候成功”更能省钱。",
        "- 若跨团队协作复杂，先挑一个单点场景打样，降低沟通成本。",
        "- 复盘时把“我们为什么猜错”写清楚，这比“我们猜对了”更值钱。",
    ],
    [
        "- 把“拍脑袋会议”改成“看证据会议”：所有观点都要挂到数据或案例上。",
        "- 先排一个两周冲刺，不求漂亮，只求能稳定复现。",
        "- 保留一条保守路线，给业务侧一个随时可回退的安全门。",
        "- 每次迭代只改一个关键变量，不然很难判断到底哪步有效。",
        "- 节奏上宁可慢半拍，也别因为赶热点把后续维护成本埋雷。",
    ],
]
_RISK_NOTES = [
    [
        "- 叙事风险：热度上来后最容易出现过度承诺，最后变成高投入返工。",
        "- 成本风险：调用、日志、人工复核会形成长期成本，前期不算清后面会被动。",
        "- 稳定性风险：上游接口波动、数据漂移、提示词衰减都可能让效果回落。",
        "- 组织风险：目标不一致时，项目常见结果是“大家都很忙，但沉淀很少”。",
    ],
    [
        "- 指标风险：只盯单一指标会导致“看起来变好，实际体验变差”。",
        "- 节奏风险：为了追进度跳过验证，往往会在后期用更高成本补课。",
        "- 依赖风险：外部接口或模型策略变化，会让历史结论快速过期。",
        "- 沟通风险：同一词在不同团队里定义不同，误解会直接放大返工量。",
    ],
    [
        "- 认知风险：把阶段性结果当长期规律，容易在扩展时踩空。",
        "- 人力风险：关键流程过度依赖少数人，团队一忙就断档。",
        "- 合规风险：数据边界和审计记录若没前置，后续补齐成本很高。",
        "- 维护风险：功能先跑通但无人维护，最终会拖慢整个交付链条。",
    ],
    [
        "- 情绪风险：看到同行案例就临时改方向，项目会越做越碎片化。",
        "- 机会成本：把资源全压在热门点，可能错过更稳的增长面。",
        "- 工程风险：缺少监控与回滚通道时，小故障也会被放大成事故。",
        "- 可信风险：对外说得太满，一旦效果波动，团队信誉最先受损。",
    ],
]
_CLOSING_NOTES = [
    "如果只记一件事，我建议记这句：不要比谁更激动，要比谁更可验证。把判断和指标绑在一起，时间会帮你过滤噪声。",
    "这类话题不怕慢，就怕乱。先把证据、边界和动作对齐，后面的投入才不容易失真。",
    "真正拉开差距的通常不是第一天的判断，而是第十天还能不能持续修正。",
    "别急着争“站哪边”，先把“怎么验证”写下来；能复盘的方案，才有长期价值。",
]
_EXTENSION_QUESTIONS = [
    "更值得追问的是：这条信息会改变谁的决策、在多大范围内生效？",
    "建议顺手核对它的适用边界，避免把局部结论当成通用规律。",
    "如果要继续跟进，最好补一条反例，确认它不是幸存者偏差。",
    "把它放进时间轴看更稳：短期热度和长期价值常常不是一回事。",
    "把“证据强度”和“可执行性”分开打分，判断会更少情绪波动。",
]
_EXTENSION_FOLLOWUPS = [
    "如果答案偏模糊，就先别着急扩大范围。",
    "这一步看似慢，但通常能省下后面的返工时间。",
    "把结论写成可复核句子，团队协作会顺很多。",
    "先求可解释，再求可复制，节奏会更稳。",
    "能说清楚“为什么没做”也是有效决策的一部分。",
]
_EXTENSION_EXTRA_NOTES = [
    "- 高阅读量内容可以有节奏感，但真正能支持决策的文章，必须同时交代证据、边界和动作。",
    "- 别把“观点很多”误判成“信息充分”，可复核的数据永远比漂亮表述更有用。",
    "- 写作可以幽默，但结论要严谨；越是热议话题，越要留出回滚空间。",
]


class DraftBuilder:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.minimum_visible_chars = 2200
        self.minimum_citation_events = 6
        self.rotation_state_path = self.settings.runtime_dir / "generation_rotation_state.json"

    def generate(
        self,
        cluster: TopicCluster,
        events: list[NormalizedEvent],
        context_events: list[NormalizedEvent] | None = None,
    ) -> ArticleDraft:
        all_events = self._dedupe_events((context_events or []) + events)
        ranked_cluster_events = sorted(self._dedupe_events(events), key=self._event_strength, reverse=True)
        if not ranked_cluster_events:
            ranked_cluster_events = sorted(all_events, key=self._event_strength, reverse=True)
        if not ranked_cluster_events:
            raise ValueError("DraftBuilder.generate requires at least one event")

        primary_events = ranked_cluster_events[:4]
        related_events = self._select_related_events(cluster, primary_events, all_events, limit=6)

        citation_events = self._dedupe_events(primary_events + related_events)
        if len(citation_events) < self.minimum_citation_events:
            ranked_all = sorted(all_events, key=self._event_strength, reverse=True)
            existing = {event.event_id for event in citation_events}
            for candidate in ranked_all:
                if candidate.event_id in existing:
                    continue
                citation_events.append(candidate)
                existing.add(candidate.event_id)
                if len(citation_events) >= self.minimum_citation_events:
                    break

        citation_events = citation_events[:10]
        citations = [
            {
                "id": f"[{index}]",
                "title": self._clean_text(event.title),
                "url": event.url,
                "source": event.source,
                "published_at": event.published_at,
            }
            for index, event in enumerate(citation_events, start=1)
        ]

        avg_relevance = sum(event.ai_relevance for event in citation_events) / max(1, len(citation_events))
        avg_credibility = sum(event.credibility for event in citation_events) / max(1, len(citation_events))
        total_upvotes = sum(float(event.engagement.get("upvotes", 0.0)) for event in citation_events)
        total_comments = sum(float(event.engagement.get("comments", 0.0)) for event in citation_events)
        source_count = len({event.source for event in citation_events})

        variant = self._next_variant(cluster.cluster_id)
        outline = _OUTLINES[variant]
        title = self._build_chinese_title(cluster.title, variant)

        facts = self._build_facts(primary_events)
        insight = self._build_insight(cluster, avg_relevance, avg_credibility, variant)
        action_plan = self._build_action_plan(variant)
        risks = self._build_risk_block(variant)
        closing = self._build_closing_block(cluster.cluster_id)
        intro = self._build_intro(
            cluster=cluster,
            avg_relevance=avg_relevance,
            avg_credibility=avg_credibility,
            source_count=source_count,
            total_upvotes=total_upvotes,
            total_comments=total_comments,
            variant=variant,
        )
        sources = "\n".join([f"- [{idx}] {item['title']} - {item['url']}" for idx, item in enumerate(citations, start=1)])

        section_contents = {
            "hook": intro,
            "facts": facts,
            "insight": insight,
            "action": action_plan,
            "risk": risks,
            "close": closing,
        }

        ordered_sections = [f"# {title}"]
        for section_key in outline.get("order", ["hook", "facts", "insight", "action", "risk", "close"]):
            ordered_sections.append(f"## {outline[section_key]}")
            ordered_sections.append(section_contents[section_key])
        body_content = "\n\n".join(ordered_sections)

        extension_index = 1
        while self._visible_chars(body_content) < self.minimum_visible_chars and extension_index <= 3:
            body_content += "\n\n" + self._build_extension_block(extension_index, citation_events)
            extension_index += 1

        content = "\n\n".join([body_content, f"## {outline['sources']}", sources])

        draft_id = build_deterministic_id("draft", f"{cluster.cluster_id}:{datetime.now(timezone.utc).isoformat()}")
        confidence = min(0.98, max(0.5, cluster.score / 100.0 + 0.2))

        return ArticleDraft(
            draft_id=draft_id,
            cluster_id=cluster.cluster_id,
            title=title,
            content_markdown=content,
            citations=citations,
            tags=["ai-news", "automation", "longform", "zh"],
            confidence=round(confidence, 2),
            status="generated",
        )

    def _pick_variant(self, cluster_id: str) -> int:
        digest = hashlib.sha1(cluster_id.encode("utf-8")).hexdigest()
        return int(digest[:2], 16) % len(_OUTLINES)

    def _next_variant(self, cluster_id: str) -> int:
        state = self._load_rotation_state()
        raw_next = state.get("next_outline_variant", 0)
        try:
            next_outline_variant = int(raw_next)
        except (TypeError, ValueError):
            next_outline_variant = self._pick_variant(cluster_id)

        variant = next_outline_variant % len(_OUTLINES)
        state["next_outline_variant"] = (variant + 1) % len(_OUTLINES)
        state["last_cluster_id"] = cluster_id
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_rotation_state(state)
        return variant

    def _load_rotation_state(self) -> dict[str, object]:
        path = self.rotation_state_path
        try:
            if not path.exists():
                return {}
            raw = path.read_text(encoding="utf-8").strip()
            if not raw:
                return {}
            payload = json.loads(raw)
            if isinstance(payload, dict):
                return payload
        except (OSError, ValueError, TypeError):
            return {}
        return {}

    def _save_rotation_state(self, state: dict[str, object]) -> None:
        path = self.rotation_state_path
        try:
            path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            # Keep generation resilient even when runtime state is temporarily unwritable.
            return

    def _build_chinese_title(self, original_title: str, variant: int) -> str:
        cleaned = self._clean_text(original_title)
        lowered = cleaned.lower()
        if "gpt" in lowered:
            candidates = [
                "GPT-5.4 真正值得看的，不只是参数和榜单",
                "聊聊 GPT-5.4：哪些变化对业务真的有用",
                "GPT-5.4 讨论很热，但落地要先看这几件事",
                "看完 GPT-5.4 资料后，我会先做这三步",
            ]
            return candidates[variant % len(candidates)]
        if "poet-x" in lowered:
            candidates = [
                "POET-X 这条路线值不值得跟：我的判断",
                "POET-X 不只是在省显存，它改的是训练节奏",
                "POET-X 观察：高效训练背后的取舍",
                "POET-X 怎么看才不跑偏：从论文到落地",
            ]
            return candidates[variant % len(candidates)]
        if "moongate" in lowered:
            candidates = [
                "Moongate 为什么火了：热度背后的硬问题",
                "从 Moongate 讨论里，我看到的三件实事",
                "Moongate 不只是情怀项目，难点在工程细节",
                "看 Moongate：社区热闹之外的执行账",
            ]
            return candidates[variant % len(candidates)]
        if "plasma" in lowered:
            candidates = [
                "Plasma Bigscreen 讨论升温，机会和限制都很明显",
                "Plasma Bigscreen 到底值不值得追",
                "聊聊 Plasma Bigscreen：热度之外看执行",
                "Plasma Bigscreen 的看点，不止是界面",
            ]
            return candidates[variant % len(candidates)]
        if "enterprise" in lowered and "agent" in lowered:
            candidates = [
                "企业 Agent Runtime 为什么被反复提起",
                "统一运行时是不是企业 AI 的必选项",
                "企业 Agent Runtime：我更关心这三点",
                "别只看概念，企业 Runtime 落地看这几步",
            ]
            return candidates[variant % len(candidates)]

        fallback = [
            "这条 AI 话题为什么值得你认真看一眼",
            "这波 AI 热点里，真正有价值的信息是什么",
            "我怎么判断这条 AI 信息值不值得跟进",
            "别急着下结论，先把这条 AI 话题看透",
        ]
        return fallback[variant % len(fallback)]

    def _build_intro(
        self,
        cluster: TopicCluster,
        avg_relevance: float,
        avg_credibility: float,
        source_count: int,
        total_upvotes: float,
        total_comments: float,
        variant: int,
    ) -> str:
        opener = _INTRO_OPENERS[variant]
        frame = _INTRO_FRAMES[self._pick_slot(cluster.cluster_id, "intro-frame", len(_INTRO_FRAMES))]
        close = _INTRO_CLOSES[self._pick_slot(cluster.cluster_id, "intro-close", len(_INTRO_CLOSES))]
        return (
            f"{opener}{frame}"
            f"当前主题“{self._clean_text(cluster.title)}”在本轮评分 {cluster.score:.1f}/100，"
            f"并且来自 {source_count} 个来源的信号能互相印证。\n\n"
            f"数据上看，平均相关度 {avg_relevance:.2f}、平均可信度 {avg_credibility:.2f}，"
            f"累计约 {total_upvotes:.0f} 点赞和 {total_comments:.0f} 评论。"
            f"{close}"
        )

    def _build_facts(self, primary_events: list[NormalizedEvent]) -> str:
        lines: list[str] = []

        for event in primary_events:
            lines.append(
                f"- {self._clean_text(event.title)}（{event.source}，{self._date_only(event.published_at)}）。"
                f"{self._event_takeaway(event)} 相关度 {event.ai_relevance:.2f}，可信度 {event.credibility:.2f}。"
            )
        return "\n".join(lines)

    def _build_insight(self, cluster: TopicCluster, avg_relevance: float, avg_credibility: float, variant: int) -> str:
        lead = _INSIGHT_LEADS[variant]
        return (
            f"{lead}"
            f"我最在意的不是“谁喊得更响”，而是“哪些判断可验证”。"
            f"像“{self._clean_text(cluster.title)}”这种议题，最常见问题不是方向错，而是验证机制弱，"
            "导致团队做了很多动作却没留下可复用能力。\n\n"
            f"如果把事情拆开看，相关度 {avg_relevance:.2f} 说明它确实贴近行业主线，"
            f"可信度 {avg_credibility:.2f} 说明信息质量也还不错。"
            "但落地时真正决定结果的，往往是执行节奏、跨团队协同和回滚机制。"
        )

    def _build_action_plan(self, variant: int) -> str:
        return "\n".join(_ACTION_PLANS[variant])

    def _build_risk_block(self, variant: int) -> str:
        return "\n".join(_RISK_NOTES[variant])

    def _build_closing_block(self, cluster_id: str) -> str:
        first = _CLOSING_NOTES[self._pick_slot(cluster_id, "closing-first", len(_CLOSING_NOTES))]
        second = _CLOSING_NOTES[self._pick_slot(cluster_id, "closing-second", len(_CLOSING_NOTES))]
        if first == second:
            second = _CLOSING_NOTES[(self._pick_slot(cluster_id, "closing-second-alt", len(_CLOSING_NOTES)) + 1) % len(_CLOSING_NOTES)]
        return first + "\n\n" + second

    def _build_extension_block(self, extension_index: int, events: list[NormalizedEvent]) -> str:
        lines = [f"## 补充观察（第 {extension_index} 轮）"]
        for event in events[:5]:
            question = _EXTENSION_QUESTIONS[self._pick_slot(event.event_id, "extension-question", len(_EXTENSION_QUESTIONS))]
            followup = _EXTENSION_FOLLOWUPS[self._pick_slot(event.event_id, "extension-followup", len(_EXTENSION_FOLLOWUPS))]
            lines.append(f"- 围绕“{self._clean_text(event.title)}”，{question}{followup}")
        lines.append(_EXTENSION_EXTRA_NOTES[(extension_index - 1) % len(_EXTENSION_EXTRA_NOTES)])
        lines.append("- 如果这一轮看下来仍然意见分裂，先补证据再下结论，别把音量当成胜负。")
        return "\n".join(lines)

    def _select_related_events(
        self,
        cluster: TopicCluster,
        primary_events: list[NormalizedEvent],
        all_events: list[NormalizedEvent],
        limit: int,
    ) -> list[NormalizedEvent]:
        primary_ids = {event.event_id for event in primary_events}
        title_tokens = self._title_tokens(cluster.title)

        scored: list[tuple[float, NormalizedEvent]] = []
        for event in all_events:
            if event.event_id in primary_ids:
                continue
            haystack_tokens = self._title_tokens(f"{event.title} {event.summary}")
            overlap = len(title_tokens.intersection(haystack_tokens))
            ai_hint_overlap = len(_AI_TOPIC_HINTS.intersection(haystack_tokens))
            if overlap == 0 and ai_hint_overlap == 0 and event.ai_relevance < 0.35:
                continue
            source_diversity_bonus = 0.5 if event.source not in cluster.sources else 0.0
            score = overlap * 6.0 + ai_hint_overlap * 2.0 + event.ai_relevance * 2.0 + event.credibility + source_diversity_bonus
            scored.append((score, event))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [event for _, event in scored[:limit]]

        if len(selected) < limit:
            existing = {event.event_id for event in selected}
            high_relevance = [
                event
                for event in sorted(all_events, key=self._event_strength, reverse=True)
                if event.event_id not in primary_ids and event.event_id not in existing and event.ai_relevance >= 0.35
            ]
            selected.extend(high_relevance[: max(0, limit - len(selected))])

        return selected[:limit]

    def _event_takeaway(self, event: NormalizedEvent) -> str:
        summary = self._clean_text(event.summary)
        if not summary:
            return "公开资料给出的细节并不完整，所以更需要在真实业务里做二次验证。"
        words = summary.split()
        if len(words) > 55:
            return " ".join(words[:55]) + "..."
        return summary

    def _pick_slot(self, seed: str, salt: str, size: int) -> int:
        digest = hashlib.sha1(f"{seed}:{salt}".encode("utf-8")).hexdigest()
        return int(digest[:8], 16) % max(1, size)

    def _event_strength(self, event: NormalizedEvent) -> float:
        engagement = event.engagement
        return (
            event.ai_relevance * 100.0
            + event.credibility * 60.0
            + float(engagement.get("upvotes", 0.0)) * 0.08
            + float(engagement.get("comments", 0.0)) * 0.16
            + float(engagement.get("shares", 0.0)) * 0.2
            + float(engagement.get("views", 0.0)) * 0.001
        )

    def _dedupe_events(self, events: list[NormalizedEvent]) -> list[NormalizedEvent]:
        deduped: list[NormalizedEvent] = []
        seen_ids: set[str] = set()
        for event in events:
            if event.event_id in seen_ids:
                continue
            seen_ids.add(event.event_id)
            deduped.append(event)
        return deduped

    def _title_tokens(self, text: str) -> set[str]:
        tokens = set(_WORD_PATTERN.findall(text.lower()))
        return {token for token in tokens if len(token) >= 3 and token not in _STOPWORDS}

    def _clean_text(self, text: str) -> str:
        cleaned = html.unescape(text or "")
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = cleaned.replace("\r", " ").replace("\n", " ")
        cleaned = cleaned.replace("**", "").replace("__", "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def _visible_chars(self, text: str) -> int:
        ascii_words = len(_WORD_PATTERN.findall(text))
        cjk_chars = len(_CJK_PATTERN.findall(text))
        return cjk_chars + ascii_words

    def _date_only(self, timestamp: str) -> str:
        return (timestamp or "").split("T", 1)[0] or "unknown-date"
