
from __future__ import annotations

import json
import math
import os
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Any
from uuid import uuid4


SUPPORTED_TOOLS = {
    "study_planner",
    "doc_qa",
    "resume_optimizer",
    "interview_generator",
    "code_explainer",
}

TOOL_UI_CONFIG = {
    "study_planner": {
        "label": "学习计划",
        "description": "按目标、天数和每天投入时间，生成循序渐进的学习安排。",
        "tip": "最适合先验证三挡位和整体流程。",
        "task": "生成学习计划",
        "fields": [
            {"name": "goal", "label": "学习目标", "type": "textarea", "rows": 3, "value": "学 Python 自动化，并能自己写小工具。"},
            {"name": "days", "label": "学习天数", "type": "number", "min": 3, "max": 120, "step": 1, "value": 14},
            {"name": "hours_per_day", "label": "每天学习时长（小时）", "type": "number", "min": 0.5, "max": 12, "step": 0.5, "value": 2},
            {
                "name": "level",
                "label": "当前水平（可选）",
                "type": "select",
                "value": "",
                "options": [
                    {"value": "", "label": "不指定（默认按初学者）"},
                    {"value": "初学者", "label": "初学者"},
                    {"value": "中级", "label": "中级"},
                    {"value": "高级", "label": "高级"},
                ],
            },
        ],
    },
    "doc_qa": {
        "label": "文档问答",
        "description": "输入文档内容和问题，返回摘要、回答和证据。",
        "tip": "适合快速整理资料重点。",
        "task": "文档问答",
        "fields": [
            {"name": "content", "label": "文档内容", "type": "textarea", "rows": 8, "value": "我们把缓存层换成 Redis，平均延迟从 420ms 降到 150ms，项目分两阶段上线，总共用了三周。"},
            {"name": "question", "label": "你的问题", "type": "text", "value": "做了什么优化，效果是什么？"},
        ],
    },
    "resume_optimizer": {
        "label": "简历优化",
        "description": "对照目标岗位，找出关键词缺口并给出修改建议。",
        "tip": "适合投递前快速体检。",
        "task": "简历优化",
        "fields": [
            {"name": "resume_text", "label": "简历内容", "type": "textarea", "rows": 8, "value": "技能：Python、Flask、SQL。\n经历：搭建内部 API 服务，将延迟降低 35%。"},
            {"name": "target_job", "label": "目标岗位", "type": "text", "value": "后端工程师"},
            {"name": "job_description", "label": "岗位描述", "type": "textarea", "rows": 5, "value": "需要 Python、Flask、SQL、testing、architecture、communication 能力。"},
        ],
    },
    "interview_generator": {
        "label": "面试题生成",
        "description": "按岗位、级别和技能生成结构化面试题。",
        "tip": "适合自测或出题。",
        "task": "生成面试题",
        "fields": [
            {"name": "role", "label": "岗位名称", "type": "text", "value": "后端工程师"},
            {"name": "level", "label": "岗位级别", "type": "select", "value": "中级", "options": [{"value": "初级", "label": "初级"}, {"value": "中级", "label": "中级"}, {"value": "高级", "label": "高级"}]},
            {"name": "skills", "label": "技能列表", "type": "text", "value": "Python, 系统设计, SQL"},
            {"name": "question_count", "label": "题目数量", "type": "number", "min": 3, "max": 20, "step": 1, "value": 5},
        ],
    },
    "code_explainer": {
        "label": "代码解释",
        "description": "解释代码、指出风险和优化建议；切到 ollama / openai 后会调用对应模型。",
        "tip": "mock 挡位只用于演示流程。",
        "task": "解释代码",
        "fields": [
            {"name": "code", "label": "代码内容", "type": "textarea", "rows": 8, "value": "def add(a, b):\n    return a + b"},
            {"name": "focus", "label": "分析重点", "type": "text", "value": "关注 bug 和优化建议"},
            {"name": "language", "label": "代码语言", "type": "text", "value": "Python"},
        ],
    },
}

STOPWORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of", "on", "or", "that", "the", "to", "with", "了", "和", "是", "在", "的", "把", "被", "并", "及", "与", "我们"}
ASSET_DIR = Path(__file__).with_name("toolbox_assets")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except ValueError:
        return default


def _normalize_provider(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"ollama", "local"}:
        return "ollama"
    if raw in {"openai", "openai-compatible", "remote"}:
        return "openai"
    return "mock"


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(str(value).strip())
    except Exception:
        return default


def _normalize_level(value: Any, default: str = "初学者") -> str:
    raw = str(value or "").strip()
    if raw in {"高级", "资深", "advanced", "senior"}:
        return "高级"
    if raw in {"中级", "intermediate", "mid"}:
        return "中级"
    if raw in {"初级", "初学者", "beginner", "junior"}:
        return "初学者"
    return default


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[A-Za-z][A-Za-z0-9_+#.-]*|[\u4e00-\u9fff]{1,4}", text or "")]


def _extract_keywords(text: str, top_n: int = 20) -> list[str]:
    scores: dict[str, int] = {}
    for token in _tokenize(text):
        if len(token) <= 1 or token in STOPWORDS:
            continue
        scores[token] = scores.get(token, 0) + 1
    return [item[0] for item in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:top_n]]


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[。！？.!?])\s+|\n+", text.strip()) if part.strip()]


def _chunk_text(content: str, max_chars: int = 520) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", content) if part.strip()] or _split_sentences(content)
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = paragraph[:max_chars]
    if current:
        chunks.append(current)
    return chunks or [content[:max_chars]]


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = str(text or "").strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    if cleaned.startswith("{") and cleaned.endswith("}"):
        try:
            payload = json.loads(cleaned)
            return payload if isinstance(payload, dict) else {}
        except json.JSONDecodeError:
            pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        payload = json.loads(cleaned[start : end + 1])
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


@dataclass
class AiToolboxConfig:
    provider: str
    api_key: str
    base_url: str = ""
    model: str = "mock"
    timeout_seconds: int = 60
    max_retries: int = 1

    @classmethod
    def from_env(cls) -> "AiToolboxConfig":
        provider = _normalize_provider(os.getenv("AI_TOOLBOX_PROVIDER", "mock"))
        api_key = os.getenv("AI_TOOLBOX_API_KEY", "").strip()
        base_url = os.getenv("AI_TOOLBOX_BASE_URL", "").strip()
        model = os.getenv("AI_TOOLBOX_MODEL", "").strip()
        if provider == "ollama":
            return cls(provider="ollama", api_key=api_key or "local", base_url=base_url or os.getenv("OLLAMA_BASE_URL", "").strip() or "http://127.0.0.1:11434", model=model or os.getenv("OLLAMA_MODEL", "").strip() or "qwen2.5:3b-instruct", timeout_seconds=_env_int("AI_TOOLBOX_TIMEOUT_SECONDS", 60), max_retries=_env_int("AI_TOOLBOX_MAX_RETRIES", 1))
        if provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
            if api_key:
                return cls(provider="openai", api_key=api_key, base_url=base_url or os.getenv("OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1", model=model or os.getenv("OPENAI_MODEL", "").strip() or "gpt-4o-mini", timeout_seconds=_env_int("AI_TOOLBOX_TIMEOUT_SECONDS", 60), max_retries=_env_int("AI_TOOLBOX_MAX_RETRIES", 1))
        return cls(provider="mock", api_key="", base_url="", model="mock", timeout_seconds=_env_int("AI_TOOLBOX_TIMEOUT_SECONDS", 60), max_retries=_env_int("AI_TOOLBOX_MAX_RETRIES", 1))


class AiToolboxService:
    def __init__(self, config: AiToolboxConfig) -> None:
        self.config = config

    def health(self) -> dict[str, Any]:
        return {"service": "ai-toolbox", "provider": self.config.provider, "model": self.config.model, "base_url": self.config.base_url, "mock_mode": self.config.provider == "mock"}

    def runtime_settings(self) -> dict[str, Any]:
        return {"provider": self.config.provider, "base_url": self.config.base_url, "model": self.config.model, "api_key_present": bool(self.config.api_key)}

    def update_runtime(self, payload: dict[str, Any]) -> dict[str, Any]:
        provider = _normalize_provider(payload.get("provider", self.config.provider))
        timeout_seconds = self.config.timeout_seconds
        max_retries = self.config.max_retries
        if provider == "mock":
            self.config = AiToolboxConfig("mock", "", "", "mock", timeout_seconds, max_retries)
            return self.runtime_settings()
        base_url = str(payload.get("base_url", "")).strip()
        model = str(payload.get("model", "")).strip()
        api_key = str(payload.get("api_key", "")).strip()
        if provider == "ollama":
            self.config = AiToolboxConfig("ollama", api_key or "local", base_url or "http://127.0.0.1:11434", model or "qwen2.5:3b-instruct", timeout_seconds, max_retries)
            return self.runtime_settings()
        if not api_key and self.config.provider == "openai":
            api_key = self.config.api_key
        if not api_key:
            raise ValueError("openai 模式必须填写 API Key。")
        self.config = AiToolboxConfig("openai", api_key, base_url or "https://api.openai.com/v1", model or "gpt-4o-mini", timeout_seconds, max_retries)
        return self.runtime_settings()

    def run_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("请求体必须是 JSON 对象。")
        tool_name = str(payload.get("tool_name", "")).strip()
        task = str(payload.get("task", "")).strip() or tool_name
        input_data = payload.get("input")
        if tool_name not in SUPPORTED_TOOLS:
            raise ValueError(f"不支持的工具：{tool_name or '未指定'}")
        if not isinstance(input_data, dict):
            raise ValueError("字段 input 必须是对象。")
        result = getattr(self, f"_tool_{tool_name}")(task, input_data)
        return {"request_id": str(uuid4()), "status": "success", "tool_name": tool_name, "result": result, "error": None}

    def _tool_doc_qa(self, task: str, input_data: dict[str, Any]) -> dict[str, Any]:
        content = str(input_data.get("content", "")).strip()
        question = str(input_data.get("question", "")).strip()
        if not content:
            raise ValueError("请先填写文档内容。")
        chunks = _chunk_text(content)
        q_tokens = [token for token in _tokenize(question) if token not in STOPWORDS]
        scored = []
        for index, chunk in enumerate(chunks, start=1):
            overlap = len(set(q_tokens) & set(_tokenize(chunk)))
            scored.append((overlap, index, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        top_hits = [item for item in scored if item[0] > 0][:3] or scored[:1]
        answer_chunk = top_hits[0][2] if top_hits else content[:180]
        return {
            "summary": " ".join([_split_sentences(chunk)[0] for chunk in chunks[:3] if _split_sentences(chunk)]) or content[:180],
            "question": question,
            "answer": " ".join(_split_sentences(answer_chunk)[:2]) if question else "你还没有填写问题，这里先返回文档摘要。",
            "confidence": "较高" if top_hits and top_hits[0][0] >= 4 else ("中等" if top_hits and top_hits[0][0] >= 2 else "较低"),
            "evidence": [{"chunk_id": index, "relevance": score, "snippet": chunk[:220]} for score, index, chunk in top_hits],
        }

    def _tool_resume_optimizer(self, task: str, input_data: dict[str, Any]) -> dict[str, Any]:
        resume_text = str(input_data.get("resume_text", "")).strip()
        target_job = str(input_data.get("target_job", "")).strip() or "目标岗位"
        job_description = str(input_data.get("job_description", "")).strip()
        if not resume_text:
            raise ValueError("请先填写简历内容。")
        keywords = _extract_keywords(f"{target_job} {job_description}", 24) or ["python", "flask", "sql", "testing", "architecture", "communication"]
        resume_tokens = set(_tokenize(resume_text))
        matched = [item for item in keywords if item in resume_tokens]
        missing = [item for item in keywords if item not in resume_tokens]
        score = max(0, min(100, int(round(len(matched) / max(len(keywords), 1) * 100))))
        suggestions = [
            {"section": "skills", "suggestion": f"建议在前半部分补充或强化这些关键词：{'、'.join(missing[:4]) or '暂无'}。", "reason": "这些关键词在目标岗位里出现较多，但简历里体现不足。"},
            {"section": "experience", "suggestion": "把经历改成“做了什么 + 用了什么 + 带来什么结果”的写法，并尽量量化。", "reason": "量化结果比笼统描述更容易被招聘方和 ATS 捕捉。"},
            {"section": "projects", "suggestion": "每个项目建议补充技术栈、你的职责和至少一个可量化结果。", "reason": "这样更容易看出你的真实贡献和技术深度。"},
        ]
        return {"summary": "已完成简历匹配分析，并生成关键词缺口和改写建议。", "target_job": target_job, "match_score": score, "high_priority_gaps": missing[:5], "rewrite_suggestions": suggestions, "ats_tips": ["每条经历尽量以动作动词开头，并写出结果。", "把岗位关键词自然融入简介、技能和经历里。", "日期格式保持统一，避免大段密集文字。"]}

    def _tool_interview_generator(self, task: str, input_data: dict[str, Any]) -> dict[str, Any]:
        role = str(input_data.get("role", "")).strip() or "后端工程师"
        level = _normalize_level(input_data.get("level", "中级"), "中级")
        question_count = max(3, min(_safe_int(input_data.get("question_count", 5), 5), 20))
        raw_skills = input_data.get("skills", "")
        skills = [item.strip() for item in re.split(r"[，,、/]+", str(raw_skills)) if item.strip()] or ["Python", "系统设计", "SQL"]
        question_types = ["fundamental", "coding", "debugging", "scenario"]
        questions = []
        for index in range(question_count):
            skill = skills[index % len(skills)]
            qtype = question_types[index % len(question_types)]
            if qtype == "fundamental":
                text = f"请你系统讲一下“{skill}”的核心原理，以及它在真实项目里的常见取舍。"
            elif qtype == "coding":
                text = f"如果让你围绕“{skill}”现场写一个简化方案，你会怎么设计？时间复杂度和边界情况怎么考虑？"
            elif qtype == "debugging":
                text = f"如果一个和“{skill}”相关的功能线上异常，你会如何从定位到修复完整排查？"
            else:
                text = f"请分享一个“{skill}”真正影响结果的项目场景，你当时是如何处理的？"
            questions.append({"id": index + 1, "type": qtype, "difficulty": level, "skill": skill, "question": text})
        return {"summary": "已生成结构化面试题。", "role": role, "level": level, "question_count": question_count, "questions": questions}

    def _tool_code_explainer(self, task: str, input_data: dict[str, Any]) -> dict[str, Any]:
        code = str(input_data.get("code", "")).strip()
        focus = str(input_data.get("focus", "")).strip() or "整体质量"
        language = str(input_data.get("language", "")).strip() or "未指定"
        if not code:
            raise ValueError("请先填写代码内容。")
        if self.config.provider == "mock":
            return {"summary": "这是演示模式结果：当前没有调用真实模型，而是返回固定结构的说明样例。", "line_by_line": [{"line_range": f"1-{max(len(code.splitlines()), 1)}", "explanation": "mock 挡位主要用于展示页面流程和返回结构。"}], "risks": ["演示模式不会真正理解代码语义。", "如需真实解释，请切到 ollama 或 openai 挡位。"], "improvements": [f"任务：{task}", f"分析重点：{focus}", f"代码语言：{language}"], "complexity": {"time": "示意值", "space": "示意值"}, "mode": "mock", "provider": "mock"}
        fallback = {"summary": "模型暂时不可用，已切换为本地启发式分析结果。", "line_by_line": [{"line_range": f"1-{max(len(code.splitlines()), 1)}", "explanation": "本地回退模式只能根据代码形态给出有限说明。"}], "risks": ["当前结果未经过真实语义推理，深度有限。", "请确认模型地址、模型名和 API Key 是否正确。"], "improvements": [f"任务：{task}", f"分析重点：{focus}", f"代码语言：{language}"], "complexity": {"time": "未知", "space": "未知"}, "mode": "fallback", "provider": self.config.provider}
        content = self._chat(
            "你是中文代码解释助手。只返回 JSON。必须包含 summary, line_by_line, risks, improvements, complexity 这些键。",
            f"任务：{task}\n分析重点：{focus}\n代码语言：{language}\n请用简体中文分析以下代码，并只返回 JSON：\n{code}",
            0.2,
            900,
            fallback,
        )
        data = _parse_json_object(content)
        if not data:
            return fallback
        data.setdefault("mode", "llm")
        data.setdefault("provider", self.config.provider)
        return data

    def _tool_study_planner(self, task: str, input_data: dict[str, Any]) -> dict[str, Any]:
        goal = str(input_data.get("goal", "")).strip() or "学会一项能落地的小技能，并做出自己的作品。"
        days = max(3, min(_safe_int(input_data.get("days", 14), 14), 120))
        hours = max(0.5, min(_safe_float(input_data.get("hours_per_day", 2), 2), 12.0))
        level = _normalize_level(input_data.get("level", ""), "初学者")
        fallback = _build_study_plan(goal, days, hours, level)
        if self.config.provider == "mock":
            fallback["summary"] = "这是演示模式结果：当前展示的是一份示例学习计划，方便你先看流程和页面效果。"
            fallback["mode"] = "mock"
            fallback["provider"] = "mock"
            return fallback
        if days > 45:
            fallback["mode"] = "fallback"
            fallback["provider"] = self.config.provider
            return fallback
        content = self._chat(
            "你是中文学习规划助手。只返回 JSON。顶层必须包含 summary, focus_areas, phases, weekly_checkpoints。phase 只能是 foundation, practice, project, review。",
            f"学习目标：{goal}\n总天数：{days}\n每天学习时长：{hours} 小时\n当前水平：{level}\n请生成学习计划蓝图，只输出 JSON。",
            0.2,
            1200,
            {"summary": fallback["summary"], "focus_areas": fallback["focus_areas"], "phases": _fallback_phases(days, goal), "weekly_checkpoints": fallback["weekly_checkpoints"]},
        )
        data = _parse_json_object(content)
        if not data:
            fallback["mode"] = "fallback"
            fallback["provider"] = self.config.provider
            return fallback
        try:
            schedule = _expand_schedule(data, goal, days, hours, level)
        except Exception:
            fallback["mode"] = "fallback"
            fallback["provider"] = self.config.provider
            return fallback
        checkpoints = []
        for item in data.get("weekly_checkpoints", []):
            if isinstance(item, dict) and _safe_int(item.get("day", 0), 0) > 0 and str(item.get("goal_check", "")).strip():
                checkpoints.append({"day": _safe_int(item.get("day", 0), 0), "goal_check": str(item.get("goal_check", "")).strip()})
        return {"summary": str(data.get("summary", "")).strip() or fallback["summary"], "goal": goal, "duration_days": days, "level": level, "hours_per_day": hours, "focus_areas": [str(item).strip() for item in (data.get("focus_areas") or []) if str(item).strip()] or fallback["focus_areas"], "weekly_checkpoints": checkpoints or fallback["weekly_checkpoints"], "schedule": schedule[:days], "mode": "llm", "provider": self.config.provider}

    def _chat(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int, fallback: Any) -> str:
        if self.config.provider == "mock":
            return json.dumps(fallback, ensure_ascii=False, indent=2) if isinstance(fallback, dict) else str(fallback)
        endpoint, body, headers = self._build_request(system_prompt, user_prompt, temperature, max_tokens)
        last_error = ""
        for attempt in range(self.config.max_retries + 1):
            try:
                request = urllib.request.Request(endpoint, data=json.dumps(body).encode("utf-8"), method="POST", headers=headers)
                with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                return self._extract_response_text(payload).strip()
            except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as ex:
                last_error = str(ex)
                if attempt < self.config.max_retries:
                    time.sleep(1 + attempt)
        if isinstance(fallback, dict):
            fallback = dict(fallback)
            fallback.setdefault("meta", {})
            if isinstance(fallback["meta"], dict):
                fallback["meta"]["reason"] = last_error or "请求失败"
            return json.dumps(fallback, ensure_ascii=False, indent=2)
        return str(fallback)

    def _build_request(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> tuple[str, dict[str, Any], dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        if self.config.provider == "ollama":
            base_url = self.config.base_url.rstrip("/")
            if base_url.endswith("/v1"):
                base_url = base_url[:-3]
            endpoint = base_url if base_url.endswith("/api/chat") else base_url + "/api/chat"
            return endpoint, {"model": self.config.model, "messages": messages, "stream": False, "think": False, "keep_alive": "15m", "options": {"temperature": temperature, "num_predict": max_tokens, "num_ctx": 2048}}, {"Content-Type": "application/json"}
        return self.config.base_url.rstrip("/") + "/chat/completions", {"model": self.config.model, "temperature": temperature, "max_tokens": max_tokens, "messages": messages}, {"Content-Type": "application/json", "Authorization": f"Bearer {self.config.api_key}"}

    def _extract_response_text(self, payload: dict[str, Any]) -> str:
        if self.config.provider == "ollama":
            message = payload.get("message", {})
            return str(message.get("content", "")) if isinstance(message, dict) else str(payload.get("response", ""))
        choices = payload.get("choices", [])
        if not choices:
            raise KeyError("choices")
        message = choices[0].get("message", {})
        if not isinstance(message, dict):
            raise KeyError("message")
        return str(message.get("content", "") or message.get("reasoning", "")).strip()


def _build_study_plan(goal: str, days: int, hours: float, level: str) -> dict[str, Any]:
    phase_limits = {"foundation": math.ceil(days * 0.35), "practice": math.ceil(days * 0.7), "project": math.ceil(days * 0.9)}
    tasks = {
        "foundation": ["学习核心概念，并整理简明笔记。", "完成一次带练教程，并在本地复现结果。"],
        "practice": ["完成针对性练习，并尝试口头讲解思路。", "复盘一个旧方案，优化可读性和效果。"],
        "project": ["围绕学习目标做一个小项目。", "记录项目思路、问题和解决方案。"],
        "review": ["系统回顾笔记、错题和关键问题。", "整理下一阶段 30 天行动计划。"],
    }
    schedule = []
    for day in range(1, days + 1):
        phase = "foundation" if day <= phase_limits["foundation"] else ("practice" if day <= phase_limits["practice"] else ("project" if day <= phase_limits["project"] else "review"))
        schedule.append({"day": day, "phase": phase, "estimated_hours": hours, "tasks": tasks[phase], "milestone": tasks[phase][-1]})
    checkpoints = [{"day": day, "goal_check": "检查本周进度、识别卡点，并调整下周重点。"} for day in range(7, days + 1, 7)]
    return {"summary": "已生成分阶段学习计划，包含每日任务和每周检查点。", "goal": goal, "duration_days": days, "level": level, "hours_per_day": hours, "focus_areas": [goal], "weekly_checkpoints": checkpoints, "schedule": schedule}


def _fallback_phases(days: int, goal: str) -> list[dict[str, Any]]:
    foundation = max(1, math.ceil(days * 0.35))
    practice = max(1, math.ceil(days * 0.35))
    project = max(1, days - foundation - practice - 1)
    return [
        {"phase": "foundation", "days": foundation, "objective": f"建立与“{goal}”相关的基础理解。", "key_outputs": ["基础笔记", "一份最小示例"], "task_patterns": ["学习核心概念并整理笔记。", "跟做一份入门示例并复现结果。"], "milestone": "能够说清楚核心概念并完成第一版练习。"},
        {"phase": "practice", "days": practice, "objective": "通过练习提高熟练度。", "key_outputs": ["练习记录", "可复用代码片段"], "task_patterns": ["围绕重点概念完成针对性练习。", "复盘错误并整理改进方案。"], "milestone": "能够独立完成常见练习题。"},
        {"phase": "project", "days": project, "objective": "做一个小项目，把知识真正用起来。", "key_outputs": ["一个小项目", "README 说明"], "task_patterns": ["把学习内容落到项目里。", "记录项目思路和问题处理过程。"], "milestone": "完成一个可以展示的作品。"},
        {"phase": "review", "days": 1, "objective": "复盘成果，找出下一步方向。", "key_outputs": ["复盘清单"], "task_patterns": ["回顾重点笔记和项目问题。", "整理下一阶段计划。"], "milestone": "形成下一阶段可执行清单。"},
    ]


def _expand_schedule(blueprint: dict[str, Any], goal: str, days: int, hours: float, level: str) -> list[dict[str, Any]]:
    phases = []
    for item in blueprint.get("phases", []):
        if not isinstance(item, dict):
            continue
        phase_name = str(item.get("phase", "")).strip().lower()
        if phase_name not in {"foundation", "practice", "project", "review"}:
            phase_name = "practice"
        patterns = [str(value).strip() for value in item.get("task_patterns", []) if str(value).strip()]
        outputs = [str(value).strip() for value in item.get("key_outputs", []) if str(value).strip()]
        if not patterns and not outputs:
            continue
        phases.append({"phase": phase_name, "days": max(1, _safe_int(item.get("days", 1), 1)), "task_patterns": patterns or [str(item.get("objective", "")).strip() or f"围绕“{goal}”推进学习。"], "key_outputs": outputs or [str(item.get("milestone", "")).strip() or f"产出与“{goal}”相关的小成果。"], "milestone": str(item.get("milestone", "")).strip()})
    if not phases:
        raise ValueError("缺少 phases")
    base_sum = sum(phase["days"] for phase in phases)
    scaled = [max(1, int(round(phase["days"] * days / max(base_sum, 1)))) for phase in phases]
    while sum(scaled) < days:
        scaled[scaled.index(min(scaled))] += 1
    while sum(scaled) > days and any(item > 1 for item in scaled):
        idx = max(range(len(scaled)), key=lambda i: scaled[i])
        if scaled[idx] > 1:
            scaled[idx] -= 1
    focus_areas = [str(value).strip() for value in blueprint.get("focus_areas", []) if str(value).strip()] or [goal]
    schedule = []
    current_day = 1
    for phase, allocated in zip(phases, scaled):
        for phase_day in range(1, allocated + 1):
            task_patterns = phase["task_patterns"]
            tasks = [
                task_patterns[(phase_day - 1) % len(task_patterns)],
                f"围绕“{focus_areas[(current_day - 1) % len(focus_areas)]}”做一次针对性推进。" if level == "初学者" else task_patterns[phase_day % len(task_patterns)],
                f"完成或更新交付物：{phase['key_outputs'][(phase_day - 1) % len(phase['key_outputs'])]}",
            ]
            schedule.append({"day": current_day, "phase": phase["phase"], "estimated_hours": hours, "tasks": tasks, "milestone": phase["milestone"] or tasks[-1]})
            current_day += 1
            if current_day > days + 1:
                break
    return schedule[:days]


_SERVICE = AiToolboxService(AiToolboxConfig.from_env())


def _parse_body(body_raw: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(body_raw.decode("utf-8") if body_raw else "{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as ex:
        raise ValueError("请求体不是有效的 UTF-8 JSON。") from ex
    if not isinstance(payload, dict):
        raise ValueError("请求体必须是 JSON 对象。")
    return payload


def _read_asset(name: str) -> str:
    path = ASSET_DIR / name
    if not path.exists():
        raise FileNotFoundError(name)
    return path.read_text(encoding="utf-8")


def _serve_asset(name: str, content_type: str, handler: Any) -> bool:
    try:
        text = _read_asset(name)
    except FileNotFoundError:
        handler._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found"})
        return True
    data = text.encode("utf-8")
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", f"{content_type}; charset=utf-8")
    handler.send_header("Cache-Control", "no-store, max-age=0")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)
    return True


def handle_ai_toolbox_get(path: str, handler: Any) -> bool:
    if path == "/ai-toolbox":
        handler._html_response(HTTPStatus.OK, render_ai_toolbox_page())
        return True
    if path == "/api/ai-toolbox/health":
        handler._json_response(HTTPStatus.OK, {"ok": True, "data": _SERVICE.health()})
        return True
    if path == "/api/ai-toolbox/runtime":
        handler._json_response(HTTPStatus.OK, {"ok": True, "data": _SERVICE.runtime_settings()})
        return True
    if path == "/api/ai-toolbox/assets/app.css":
        return _serve_asset("app.css", "text/css", handler)
    if path == "/api/ai-toolbox/assets/app.js":
        return _serve_asset("app.js", "application/javascript", handler)
    return False


def handle_ai_toolbox_post(path: str, body_raw: bytes, handler: Any) -> bool:
    payload: dict[str, Any] | None = None
    if path == "/api/ai-toolbox/runtime":
        try:
            payload = _parse_body(body_raw)
            handler._json_response(HTTPStatus.OK, {"ok": True, "data": _SERVICE.update_runtime(payload)})
        except ValueError as ex:
            handler._json_response(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(ex)})
        return True
    if path == "/api/ai-toolbox/run":
        try:
            payload = _parse_body(body_raw)
            handler._json_response(HTTPStatus.OK, _SERVICE.run_tool(payload))
        except ValueError as ex:
            handler._json_response(HTTPStatus.BAD_REQUEST, {"request_id": str(uuid4()), "status": "error", "tool_name": payload.get("tool_name") if isinstance(payload, dict) else None, "result": None, "error": {"message": str(ex)}})
        except Exception as ex:
            handler._json_response(HTTPStatus.INTERNAL_SERVER_ERROR, {"request_id": str(uuid4()), "status": "error", "tool_name": payload.get("tool_name") if isinstance(payload, dict) else None, "result": None, "error": {"message": f"服务内部错误：{ex}"}})
        return True
    return False


def render_ai_toolbox_page() -> str:
    tool_json = json.dumps(TOOL_UI_CONFIG, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI 工具箱</title>
  <link rel="stylesheet" href="/api/ai-toolbox/assets/app.css" />
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="hero-topbar">
        <div>
          <p class="eyebrow">AI 工具箱</p>
          <h1>博客内置 AI 工具箱</h1>
          <p>按“写作助手”的接入方式，直接集成到博客服务里，支持三挡位：mock / ollama / openai。</p>
          <p><a href="/blog">返回知行简报</a></p>
        </div>
        <div class="hero-actions">
          <button id="runtime-button" type="button" class="secondary">设置挡位</button>
          <div id="runtime-summary" class="runtime-summary">当前模式：加载中</div>
        </div>
      </div>
    </section>
    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>开始使用</h2>
          <p>选择一个工具，填写内容后直接提交即可。</p>
        </div>
        <label class="field compact"><span>工具</span><select id="tool-select"></select></label>
      </div>
      <div class="tool-intro"><h3 id="tool-title"></h3><p id="tool-description"></p><div id="tool-tip"></div></div>
      <form id="tool-form" class="tool-form">
        <div id="fields-container" class="fields-grid"></div>
        <div class="actions"><button id="submit-button" type="submit">开始生成</button><button id="reset-button" type="button" class="secondary">恢复示例</button></div>
      </form>
    </section>
    <section class="panel">
      <div class="status-row"><span id="status-badge" class="status idle">准备就绪</span><span id="http-status" class="http-status">未提交</span></div>
      <p id="status-message" class="status-message">填写信息后点击“开始生成”。</p>
      <p id="error-message" class="error-message hidden"></p>
      <div id="rendered-result" class="rendered-result empty">生成完成后，这里会显示整理好的结果。</div>
    </section>
  </main>
  <div id="runtime-overlay" class="runtime-overlay hidden">
    <div class="runtime-modal">
      <div class="runtime-modal-header">
        <div>
          <h3>运行挡位</h3>
          <p>这里直接切换 mock / ollama / openai，不影响博客原有文章页。</p>
        </div>
        <button id="runtime-close" type="button" class="secondary">关闭</button>
      </div>
      <form id="runtime-form" class="runtime-form">
        <div class="fields-grid runtime-grid">
          <label class="field"><span>模式</span><select id="runtime-provider"><option value="mock">mock（演示）</option><option value="ollama">ollama（本地）</option><option value="openai">openai（远程/兼容）</option></select></label>
          <label class="field"><span>服务地址</span><input id="runtime-base-url" type="text" /></label>
          <label class="field"><span>模型名</span><input id="runtime-model" type="text" /></label>
          <label class="field"><span>API Key</span><input id="runtime-api-key" type="password" autocomplete="off" /></label>
        </div>
        <div class="runtime-current"><div id="runtime-current-status"></div></div>
        <p id="runtime-message" class="runtime-message hidden"></p>
        <div class="actions"><button id="runtime-recommend" type="button" class="secondary">推荐值</button><button id="runtime-apply" type="submit">应用挡位</button></div>
      </form>
    </div>
  </div>
  <script>window.__AI_TOOLBOX_CONFIG__ = {tool_json};</script>
  <script src="/api/ai-toolbox/assets/app.js"></script>
</body>
</html>'''

