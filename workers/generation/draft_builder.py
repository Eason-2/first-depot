from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter
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
    "agents",
    "against",
    "and",
    "among",
    "are",
    "being",
    "between",
    "but",
    "can",
    "could",
    "every",
    "first",
    "for",
    "from",
    "has",
    "how",
    "its",
    "llm",
    "new",
    "not",
    "our",
    "their",
    "the",
    "there",
    "these",
    "those",
    "under",
    "via",
    "was",
    "while",
    "why",
    "will",
    "with",
    "without",
    "your",
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
    {
        "hook": "这次只回答一个核心问题",
        "facts": "先核对原始信息与出处",
        "insight": "从事实走到判断，中间还缺什么",
        "action": "把判断变成一轮可复现实验",
        "risk": "哪些条件一变，结论就可能失效",
        "close": "下一次更新重点看这些信号",
        "sources": "参考资料",
        "order": ["hook", "facts", "insight", "close", "risk", "action"],
    },
    {
        "hook": "先界定这篇文章讨论什么",
        "facts": "资料里可以确认的内容",
        "insight": "证据强度与实际价值要分开看",
        "action": "研究、试用与复盘怎么安排",
        "risk": "当前结论的适用边界",
        "close": "暂时结论与观察清单",
        "sources": "参考资料",
        "order": ["hook", "facts", "risk", "insight", "action", "close"],
    },
    {
        "hook": "用决策备忘录的方式看这件事",
        "facts": "已知事实：来源、时间与主要说法",
        "insight": "这些信息会影响哪些判断",
        "action": "低成本验证路径",
        "risk": "决定投入前必须排除的误差",
        "close": "后续跟踪指标",
        "sources": "参考资料",
        "order": ["hook", "insight", "risk", "facts", "action", "close"],
    },
    {
        "hook": "先拆开热度、证据与可用性",
        "facts": "来源分别提供了什么信息",
        "insight": "把主张放回具体场景",
        "action": "从阅读资料到动手验证",
        "risk": "反例可能藏在哪里",
        "close": "目前可以保留的判断",
        "sources": "参考资料",
        "order": ["hook", "facts", "action", "insight", "risk", "close"],
    },
]

class DraftBuilder:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.minimum_visible_chars = 1200
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
        insight = self._build_insight(cluster, primary_events, avg_relevance, avg_credibility, variant)
        action_plan = self._build_action_plan(cluster, primary_events, variant)
        risks = self._build_risk_block(
            cluster,
            citation_events,
            avg_relevance,
            avg_credibility,
            total_upvotes,
            total_comments,
            variant,
        )
        closing = self._build_closing_block(cluster, primary_events, variant)
        intro = self._build_intro(
            cluster=cluster,
            events=citation_events,
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

        if self._visible_chars(body_content) < self.minimum_visible_chars:
            body_content += "\n\n" + self._build_evidence_gaps(cluster, citation_events, variant)

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
        topic = cleaned or "本轮 AI 主题"
        if len(topic) > 52:
            topic = topic[:49].rstrip(" -:：，,") + "..."
        candidates = [
            f"{topic}：核心变化与验证重点",
            f"解读 {topic}：证据、边界与影响",
            f"{topic} 值得关注什么？从来源到落地",
            f"从 {topic} 看落地机会与限制",
            f"{topic}：从原始资料到可执行判断",
            f"围绕 {topic}，现有证据能说明什么",
            f"{topic} 实测前先看这几项边界",
            f"重新审视 {topic}：事实、限制与下一步",
        ]
        return candidates[variant % len(candidates)]

    def _build_intro(
        self,
        cluster: TopicCluster,
        events: list[NormalizedEvent],
        avg_relevance: float,
        avg_credibility: float,
        source_count: int,
        total_upvotes: float,
        total_comments: float,
        variant: int,
    ) -> str:
        source_counts = Counter(event.source for event in events)
        type_counts = Counter(self._content_type_label(event.content_type) for event in events)
        source_profile = "、".join(f"{source} {count} 条" for source, count in source_counts.most_common())
        evidence_profile = "、".join(f"{kind} {count} 条" for kind, count in type_counts.most_common())
        engagement_note = (
            f"公开互动数据合计约 {total_upvotes:.0f} 个赞、{total_comments:.0f} 条评论，可用于观察讨论强度，"
            "但不能替代产品效果或研究结论。"
            if total_upvotes or total_comments
            else "当前来源没有可用的点赞、评论数据，因此本文不会用“热度高”代替证据强。"
        )
        openings = [
            "这篇不从泛泛的行业趋势谈起，而是先检查本轮资料能支持哪些结论。",
            "判断这个主题，第一步是把发布信息、研究证据和社区反馈分开看。",
            "这里先做证据盘点，再讨论它对产品和工程决策可能产生的影响。",
            "与其复述热搜，不如先回答来源是否独立、结论是否能验证。",
            "先限定讨论范围：本文只处理现有来源明确披露的内容，不为缺失信息补故事。",
            "这次按来源、主张和验证条件三层阅读，避免把不同强度的证据混在一起。",
            "下面把这条信息整理成一份决策备忘录，重点保留可核对项与未知项。",
            "热度、证据和可用性是三件事；这篇文章会分别检查，不用一个分数代替全部判断。",
        ]
        opening = openings[variant % len(openings)]
        return (
            f"{opening}本轮聚焦“{self._clean_text(cluster.title)}”，聚类评分为 {cluster.score:.1f}/100。"
            f"资料来自 {source_count} 个来源渠道，构成为 {source_profile or '来源未标注'}；"
            f"证据形态包括 {evidence_profile or '类型未标注'}。\n\n"
            f"对“{self._clean_text(cluster.title)}”而言，这些材料的平均 AI 相关度为 {avg_relevance:.2f}，"
            f"平均可信度为 {avg_credibility:.2f}。"
            f"{engagement_note}因此，下面的判断会把已知事实、推断和待验证项明确分开。"
        )

    def _build_facts(self, primary_events: list[NormalizedEvent]) -> str:
        lines: list[str] = []

        for event in primary_events:
            lines.append(
                f"- {self._clean_text(event.title)}（{event.source}，{self._date_only(event.published_at)}）。"
                f"{self._event_takeaway(event)} 相关度 {event.ai_relevance:.2f}，可信度 {event.credibility:.2f}。"
            )
        return "\n".join(lines)

    def _build_insight(
        self,
        cluster: TopicCluster,
        events: list[NormalizedEvent],
        avg_relevance: float,
        avg_credibility: float,
        variant: int,
    ) -> str:
        first = events[0]
        second = events[1] if len(events) > 1 else None
        first_title = self._clean_text(first.title)
        dominant_type = Counter(event.content_type or "unknown" for event in events).most_common(1)[0][0]
        comparison = (
            f"第一条材料“{first_title}”偏向{self._content_type_label(first.content_type)}，"
            f"第二条“{self._clean_text(second.title)}”偏向{self._content_type_label(second.content_type)}。"
            "两者回答的问题并不相同：前者更适合确认发生了什么，后者更适合发现迁移、成本或使用体验上的争议。"
            if second
            else f"目前只有“{first_title}”这一条核心材料，缺少第二来源对它的关键结论进行交叉验证。"
        )
        credibility_gap = max(event.credibility for event in events) - min(event.credibility for event in events)
        lens = self._variant_lens(variant)
        perspective = [
            f"这一版先用“{lens}”检查主题，不急着扩展到所有业务场景。",
            f"这里把“{lens}”放在首位，避免被单一亮点带偏整体判断。",
            f"本次复盘从“{lens}”切入，因为它最容易暴露宣传口径与实际表现的差距。",
            f"阅读这些资料时，我会持续追问“{lens}”是否有独立证据支持。",
            f"这组材料最适合先回答“{lens}”问题，再谈更大的行业影响。",
            f"与其汇总更多观点，这一版选择沿着“{lens}”追踪证据链。",
            f"如果把文章当成决策备忘录，“{lens}”是这一轮的主判断轴。",
            f"以下判断把“{lens}”与主题热度分开，分别给出证据和限制。",
        ][variant % len(_OUTLINES)]
        evidence_focus = {
            "research": "研究材料还要检查数据集覆盖范围、基线设置和复现实验，论文指标不能直接替代线上效果。",
            "paper": "研究材料还要检查数据集覆盖范围、基线设置和复现实验，论文指标不能直接替代线上效果。",
            "discussion": "社区讨论适合暴露问题，却容易受样本选择和情绪影响，关键说法仍需回到一手资料确认。",
            "news": "新闻材料可以确认发布时间与公开能力，但商业表述需要用实际账户、价格和限制条件复核。",
            "release": "发布说明可以确认功能边界，却通常不会完整呈现失败率、维护成本和迁移阻力。",
        }.get(dominant_type, "公开材料可以提供线索，但仍需区分原始证据、二手转述和作者判断。")
        return (
            f"{perspective}围绕“{self._clean_text(cluster.title)}”，需要保留来源之间的证据差异。"
            f"{comparison}\n\n"
            f"以“{lens}”为观察轴，整体相关度均值为 {avg_relevance:.2f}，说明这些材料与主题的贴合度较高；"
            f"可信度均值为 {avg_credibility:.2f}，来源间差值为 {credibility_gap:.2f}。"
            f"{evidence_focus}现阶段对“{self._clean_text(cluster.title)}”更稳妥的结论是：它值得进入验证队列，"
            "但价值大小仍要由具体场景、基线数据和失败样本决定。"
        )

    def _build_action_plan(self, cluster: TopicCluster, events: list[NormalizedEvent], variant: int) -> str:
        topic = self._clean_text(cluster.title)
        lens = self._variant_lens(variant)
        dominant_type = Counter(event.content_type or "unknown" for event in events).most_common(1)[0][0]
        first_title = self._clean_text(events[0].title)
        if dominant_type == "research":
            specific_steps = [
                f"- 复现材料中的核心实验：以“{first_title}”给出的任务、样本和评价指标为起点，先确认结果能否重复。",
                "- 对照基线与消融实验：记录模型、数据规模、硬件和随机种子，避免把配置差异误认为方法收益。",
                "- 增加业务外样本：至少加入一组论文未覆盖的数据，检查结论在真实输入分布下是否仍成立。",
            ]
        elif dominant_type == "discussion":
            specific_steps = [
                f"- 回到一手资料：从“{first_title}”提到的功能、版本或项目名称反查官方发布和变更记录。",
                "- 给社区反馈分类：把可复现问题、个人偏好和未经证实的猜测分开统计，不直接用点赞数投票。",
                "- 复测高频争议：选两个出现次数最多的问题，在固定环境中记录输入、输出、耗时和失败条件。",
            ]
        else:
            specific_steps = [
                f"- 核对发布边界：以“{first_title}”为入口，确认版本、开放范围、价格、地区和发布日期。",
                "- 选一个现有流程做对照：记录接入前后的质量、延迟、人工复核时间和单次运行成本。",
                "- 检查迁移代价：列出接口变化、数据权限、监控、回滚和供应商依赖，避免只计算演示成本。",
            ]
        qualified_steps = [
            f"{step} 验收时单独记录“{lens}”是否改善。" if index == 0 else
            f"{step} 对照组也必须使用同一套“{lens}”口径。" if index == 1 else
            f"{step} 一旦“{lens}”恶化，就回到上一步定位变量。"
            for index, step in enumerate(specific_steps)
        ]
        return "\n".join(
            qualified_steps
            + [
                f"- 为“{topic}”写清与“{lens}”对应的停止条件：若核心指标连续两轮没有改善，暂停扩展并回看假设。",
                f"- 保存“{topic}”每次验证的输入、配置、结果和反例，并在复盘中解释“{lens}”为何变化。",
            ]
        )

    def _build_risk_block(
        self,
        cluster: TopicCluster,
        events: list[NormalizedEvent],
        avg_relevance: float,
        avg_credibility: float,
        total_upvotes: float,
        total_comments: float,
        variant: int,
    ) -> str:
        source_counts = Counter(event.source for event in events)
        repeated_source = source_counts.most_common(1)[0]
        topic = self._clean_text(cluster.title)
        lens = self._variant_lens(variant)
        dominant_type = Counter(event.content_type or "unknown" for event in events).most_common(1)[0][0]
        interaction_risk = (
            f"- 热度误读：“{topic}”现有 {total_upvotes:.0f} 个赞和 {total_comments:.0f} 条评论只能反映关注度，"
            "不能证明效果、成本或稳定性。"
            if total_upvotes or total_comments
            else f"- 热度缺口：“{topic}”的现有资料没有可用互动数据，无法判断讨论扩散范围，更不能据此推断市场接受度。"
        )
        type_risks = {
            "research": [
                f"- 外部有效性：关于“{topic}”的实验结果可能依赖特定数据集与硬件，换到业务数据后需要重新测量。",
                f"- 复现风险：若“{topic}”没有公开代码、随机种子或完整参数，单次高分不足以支持工程选型。",
            ],
            "paper": [
                f"- 外部有效性：关于“{topic}”的实验结果可能依赖特定数据集与硬件，换到业务数据后需要重新测量。",
                f"- 复现风险：若“{topic}”没有公开代码、随机种子或完整参数，单次高分不足以支持工程选型。",
            ],
            "discussion": [
                f"- 样本偏差：“{topic}”的发言者不代表全部用户，活跃讨论也可能由少数高频账号贡献。",
                f"- 转述风险：社区对“{topic}”的截图和二手描述可能遗漏版本、配置与触发条件，应追溯原始链接。",
            ],
            "news": [
                f"- 可用性风险：“{topic}”即使已经宣布，也可能受灰度范围、地区、套餐或候补名单限制。",
                f"- 迁移风险：围绕“{topic}”评估接口变化、历史兼容性和回滚成本，不能只验证一次演示流程。",
            ],
            "release": [
                f"- 可用性风险：“{topic}”即使已经发布，也可能受灰度范围、地区、套餐或调用限额约束。",
                f"- 运维风险：接入“{topic}”前要确认监控、故障降级与版本锁定能力，避免上游变化直接影响业务。",
            ],
        }.get(
            dominant_type,
            [
                f"- 时效风险：“{topic}”的版本、价格和能力边界可能变化，引用旧结论前应重新核对当前文档。",
                f"- 落地风险：验证“{topic}”时要保留失败样本、人工兜底和回滚指标，不能从演示直接外推生产效果。",
            ],
        )
        return "\n".join(
            [
                f"- 来源集中：{repeated_source[0]} 占 {repeated_source[1]}/{len(events)} 条；从“{lens}”看，转述同一公告不能算独立旁证。",
                f"- 证据强度：平均相关度 {avg_relevance:.2f} 与平均可信度 {avg_credibility:.2f} 只是筛选信号，无法单独证明“{topic}”在“{lens}”上有效。",
                interaction_risk,
            ]
            + type_risks
        )

    def _build_closing_block(self, cluster: TopicCluster, events: list[NormalizedEvent], variant: int) -> str:
        topic = self._clean_text(cluster.title)
        lens = self._variant_lens(variant)
        first_title = self._clean_text(events[0].title)
        last_title = self._clean_text(events[-1].title)
        return (
            f"对“{topic}”的下一轮复盘，将“{lens}”设为首要观察项。先看“{first_title}”中的具体能力是否有正式文档或可运行样例，"
            "再看一次小规模对照能否同时改善质量、耗时和成本。只改善其中一项时，要明确另外两项付出了什么代价。\n\n"
            f"同时跟踪“{last_title}”涉及的限制是否被后续版本修正，并为“{lens}”补充至少一个独立来源。"
            "当一手说明、实测数据和外部反馈能够互相解释时，再决定扩大投入；如果三者冲突，就把冲突本身记录为下一轮要验证的问题。"
        )

    def _build_evidence_gaps(self, cluster: TopicCluster, events: list[NormalizedEvent], variant: int) -> str:
        topic = self._clean_text(cluster.title)
        lens = self._variant_lens(variant)
        lines = ["## 仍待确认的证据"]
        for event in events[:4]:
            lines.append(
                f"- “{self._clean_text(event.title)}”目前提供的是{self._content_type_label(event.content_type)}线索；"
                f"下一步需要核对其原始数据、适用版本和发布日期（{self._date_only(event.published_at)}）。"
            )
        lines.append(
            f"- 对“{topic}”的“{lens}”判断，应至少补齐一项可重复实验、一个失败案例和一个独立来源。"
        )
        lines.extend(
            [
                f"- 主动寻找“{topic}”在“{lens}”上的反证：检查效果下降、成本上升或无法复现的记录，并说明环境差异。",
                f"- 核对“{topic}”的时间边界，确认版本变化是否会让当前“{lens}”结论失效。",
                f"- 建立“{topic}”的“{lens}”决策记录：分别写下已确认事实、基于事实的推断和仍未知的信息；"
                "未知项没有补齐前，不把试验结论扩展到生产环境。",
                f"- 给“{topic}”设置“{lens}”复核日期：到期后重新检查原始链接、版本说明与反例，过期判断不直接沿用。",
            ]
        )
        return "\n".join(lines)

    def _variant_lens(self, variant: int) -> str:
        return (
            "基线对照",
            "成本变化",
            "失败样本",
            "版本边界",
            "数据质量",
            "可复现性",
            "维护负担",
            "用户反馈",
        )[variant % len(_OUTLINES)]

    def _content_type_label(self, content_type: str) -> str:
        return {
            "research": "研究",
            "paper": "研究",
            "discussion": "社区讨论",
            "news": "新闻报道",
            "release": "产品发布",
        }.get((content_type or "").lower(), "公开资料")

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
            required_overlap = min(2, len(title_tokens))
            if required_overlap == 0 or overlap < required_overlap:
                continue
            source_diversity_bonus = 0.5 if event.source not in cluster.sources else 0.0
            ai_hint_overlap = len(_AI_TOPIC_HINTS.intersection(haystack_tokens))
            score = overlap * 6.0 + ai_hint_overlap * 2.0 + event.ai_relevance * 2.0 + event.credibility + source_diversity_bonus
            scored.append((score, event))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [event for _, event in scored[:limit]]

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
