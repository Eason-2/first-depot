from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_provider(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"ollama", "local"}:
        return "ollama"
    if raw in {"openai", "openai-compatible", "remote"}:
        return "openai"
    return "mock"


@dataclass
class AiWriterConfig:
    provider: str
    api_key: str
    base_url: str = ""
    model: str = "mock"
    timeout_seconds: int = 60
    max_retries: int = 1

    @classmethod
    def from_env(cls) -> "AiWriterConfig":
        provider = _normalize_provider(os.getenv("AI_WRITER_PROVIDER", "mock"))
        if _env_flag("AI_WRITER_USE_MOCK", False):
            provider = "mock"

        api_key = os.getenv("AI_WRITER_API_KEY", "").strip()
        base_url = os.getenv("AI_WRITER_BASE_URL", "").strip()
        model = os.getenv("AI_WRITER_MODEL", "").strip()

        if provider == "ollama":
            api_key = api_key or os.getenv("OPENAI_API_KEY", "").strip() or "local"
            base_url = base_url or os.getenv("OLLAMA_BASE_URL", "").strip() or "http://127.0.0.1:11434"
            model = model or os.getenv("OLLAMA_MODEL", "").strip() or "qwen2.5:3b-instruct"
        elif provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
            base_url = base_url or os.getenv("OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1"
            model = model or os.getenv("OPENAI_MODEL", "").strip() or "gpt-4o-mini"
            if not api_key:
                provider = "mock"
                base_url = ""
                model = "mock"
        else:
            api_key = ""
            base_url = ""
            model = "mock"

        return cls(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout_seconds=_env_int("AI_WRITER_TIMEOUT_SECONDS", 60),
            max_retries=_env_int("AI_WRITER_MAX_RETRIES", 1),
        )


class AiWriterService:
    def __init__(self, config: AiWriterConfig) -> None:
        self.config = config

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "provider": self.config.provider,
            "model": self.config.model,
            "base_url": self.config.base_url,
            "mock_mode": self.config.provider == "mock",
        }

    def runtime_settings(self) -> dict[str, Any]:
        return {
            "provider": self.config.provider,
            "base_url": self.config.base_url,
            "model": self.config.model,
            "api_key_present": bool(self.config.api_key),
        }

    def update_runtime(self, payload: dict[str, Any]) -> dict[str, Any]:
        provider = _normalize_provider(payload.get("provider", self.config.provider))
        timeout_seconds = self.config.timeout_seconds
        max_retries = self.config.max_retries

        if provider == "mock":
            self.config = AiWriterConfig(
                provider="mock",
                api_key="",
                base_url="",
                model="mock",
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
            )
            return self.runtime_settings()

        base_url = str(payload.get("base_url", "")).strip()
        model = str(payload.get("model", "")).strip()
        api_key = str(payload.get("api_key", "")).strip()

        if provider == "ollama":
            self.config = AiWriterConfig(
                provider="ollama",
                api_key=api_key or "local",
                base_url=base_url or "http://127.0.0.1:11434",
                model=model or "qwen2.5:3b-instruct",
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
            )
            return self.runtime_settings()

        if not api_key and self.config.provider == "openai":
            api_key = self.config.api_key
        if not api_key:
            raise ValueError("api_key is required for openai mode")

        self.config = AiWriterConfig(
            provider="openai",
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1",
            model=model or "gpt-4o-mini",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        return self.runtime_settings()

    def generate_outline(self, payload: dict[str, Any]) -> dict[str, Any]:
        topic = str(payload.get("topic", "")).strip()
        if not topic:
            raise ValueError("topic is required")

        scene = str(payload.get("scene", "general")).strip() or "general"
        tone = str(payload.get("tone", "natural")).strip() or "natural"
        length = str(payload.get("length", "standard")).strip() or "standard"
        language = _normalize_language(payload.get("language", "zh"))
        output_language = "English" if language == "en" else "Chinese (Simplified)"

        user_prompt = (
            "Create a writing outline.\\n"
            f"topic: {topic}\\n"
            f"scene: {scene}\\n"
            f"tone: {tone}\\n"
            f"length: {length}\\n"
            f"output language: {output_language}\\n"
            "Return JSON only with keys: title, sections.\\n"
            "sections is an array of objects with keys heading and bullets."
        )
        content = self._chat(
            system_prompt="You are a structured writing assistant. Return strict JSON only.",
            user_prompt=user_prompt,
            temperature=0.4,
            max_tokens=900,
            fallback=self._mock_outline(topic, scene, tone, length, language),
        )
        data = _parse_json_object(content)
        if not data:
            data = self._mock_outline(topic, scene, tone, length, language)
        data["scene"] = scene
        data["tone"] = tone
        data["length"] = length
        data["language"] = language
        return data

    def generate_draft(self, payload: dict[str, Any]) -> dict[str, Any]:
        topic = str(payload.get("topic", "")).strip()
        if not topic:
            raise ValueError("topic is required")

        scene = str(payload.get("scene", "general")).strip() or "general"
        tone = str(payload.get("tone", "natural")).strip() or "natural"
        word_count = _requested_word_count(payload.get("word_count", 120))
        language = _normalize_language(payload.get("language", "zh"))
        system_prompt, user_prompt, max_tokens = _draft_prompt(topic, scene, tone, word_count, language)
        content = self._chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.6,
            max_tokens=max_tokens,
            fallback=self._mock_draft(topic, scene, tone, language),
        )
        if self.config.provider != "mock" and _is_too_short(content, word_count, language):
            content = self._expand_short_draft(topic, scene, tone, word_count, language, content)
        return {"markdown": _mask_sensitive(content)}

    def rewrite_paragraph(self, payload: dict[str, Any]) -> dict[str, Any]:
        paragraph = str(payload.get("paragraph", "")).strip()
        instruction = str(payload.get("instruction", "Improve clarity and flow.")).strip()
        tone = str(payload.get("tone", "natural")).strip() or "natural"
        language = _normalize_language(payload.get("language", "zh"))
        output_language = "English" if language == "en" else "Chinese (Simplified)"
        if not paragraph:
            raise ValueError("paragraph is required")

        user_prompt = (
            "Rewrite the paragraph with the instruction below.\\n"
            f"instruction: {instruction}\\n"
            f"tone: {tone}\\n"
            f"output language: {output_language}\\n"
            f"paragraph:\\n{paragraph}"
        )
        content = self._chat(
            system_prompt="Rewrite the text directly. Keep facts, make it cleaner.",
            user_prompt=user_prompt,
            temperature=0.4,
            max_tokens=_rewrite_max_tokens(paragraph),
            fallback=f"{paragraph}\\n\\n[rewritten with instruction: {instruction}]",
        )
        return {"text": _mask_sensitive(content)}

    def polish_full_text(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = str(payload.get("text", "")).strip()
        tone = str(payload.get("tone", "professional")).strip() or "professional"
        language = _normalize_language(payload.get("language", "zh"))
        output_language = "English" if language == "en" else "Chinese (Simplified)"
        if not text:
            raise ValueError("text is required")

        user_prompt = (
            "Polish the full text while keeping meaning unchanged.\\n"
            f"tone: {tone}\\n"
            f"output language: {output_language}\\n"
            "Fix grammar, improve transitions, remove repetition.\\n"
            f"text:\\n{text}"
        )
        content = self._chat(
            system_prompt="Polish the text directly. Keep meaning unchanged.",
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=_polish_max_tokens(text),
            fallback=text,
        )
        return {"text": _mask_sensitive(content)}

    def translate_text(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = str(payload.get("text", "")).strip()
        if not text:
            raise ValueError("text is required")

        source = _normalize_source_language(payload.get("source_language", "auto"))
        target = _normalize_language(payload.get("target_language", "en"))
        source_label = {"auto": "Auto", "zh": "Chinese", "en": "English"}[source]
        target_label = "English" if target == "en" else "Chinese (Simplified)"

        user_prompt = (
            "Translate the text accurately, preserving meaning and key terms.\\n"
            f"source language: {source_label}\\n"
            f"target language: {target_label}\\n"
            "Keep output plain text only.\\n"
            f"text:\\n{text}"
        )
        fallback = f"[mock translation -> {target_label}]\\n{text}"
        content = self._chat(
            system_prompt="Translate directly and keep wording natural.",
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=_translate_max_tokens(text),
            fallback=fallback,
        )
        return {"text": _mask_sensitive(content), "target_language": target}

    def _chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        fallback: Any,
    ) -> str:
        if self.config.provider == "mock":
            return json.dumps(fallback, ensure_ascii=False, indent=2) if isinstance(fallback, dict) else str(fallback)

        endpoint, body, headers = self._build_request(system_prompt, user_prompt, temperature, max_tokens)

        last_error = ""
        for attempt in range(self.config.max_retries + 1):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(body).encode("utf-8"),
                    method="POST",
                    headers=headers,
                )
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                return self._extract_response_text(payload).strip()
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                socket.timeout,
                TimeoutError,
                KeyError,
                IndexError,
                json.JSONDecodeError,
            ) as ex:
                last_error = str(ex)
                if attempt < self.config.max_retries:
                    time.sleep(1 + attempt)
                continue

        if isinstance(fallback, dict):
            return json.dumps(fallback, ensure_ascii=False, indent=2)
        if fallback:
            return str(fallback)
        raise RuntimeError(f"model request failed: {last_error}")

    def _build_request(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, dict[str, Any], dict[str, str]]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        if self.config.provider == "ollama":
            base_url = self.config.base_url.rstrip("/")
            if base_url.endswith("/v1"):
                base_url = base_url[:-3]
            if base_url.endswith("/api/chat"):
                endpoint = base_url
            else:
                endpoint = base_url + "/api/chat"
            body = {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "think": False,
                "keep_alive": "15m",
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": 1024,
                },
            }
            return endpoint, body, {"Content-Type": "application/json"}

        endpoint = self.config.base_url.rstrip("/") + "/chat/completions"
        body = {
            "model": self.config.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }
        return endpoint, body, headers

    def _expand_short_draft(
        self,
        topic: str,
        scene: str,
        tone: str,
        word_count: int,
        language: str,
        short_text: str,
    ) -> str:
        min_length = _minimum_length(word_count, language)
        current = short_text
        for _ in range(3):
            if language == "en":
                current_units = _text_units(current, language)
                missing = max(0, min_length - current_units)
                user_prompt = (
                    f"Topic: {topic}\n"
                    f"Tone: {tone}\n"
                    f"Target length: about {word_count} words, at least {min_length} words\n"
                    f"Current draft:\n{current}\n"
                    f"It is still too short. Add at least {missing} more words without repeating the existing text. "
                    "Continue directly from the current draft and output only the full final text."
                )
                system_prompt = "You expand short drafts into complete final writing and must satisfy the minimum length."
            else:
                current_units = _text_units(current, language)
                missing = max(0, min_length - current_units)
                user_prompt = (
                    f"主题：{topic}\n"
                    f"语气：{_tone_label(tone, language)}\n"
                    f"目标字数：约{word_count}字，至少{min_length}字\n"
                    f"当前内容：\n{current}\n"
                    f"当前内容还差至少{missing}字。请在现有内容基础上继续补充，补足内容，不要重复前文。"
                    "必须直接输出完整成稿，字数达到要求，不要解释，不要写说明。"
                )
                system_prompt = "你负责把过短的中文草稿扩展成完整成稿，并且必须达到最低字数要求。"
            current = self._chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.45,
                max_tokens=_draft_max_tokens(scene, max(word_count, int(word_count * 1.8)), language),
                fallback=current,
            )
            if not _is_too_short(current, word_count, language):
                return current
        return current

    def _extract_response_text(self, payload: dict[str, Any]) -> str:
        if self.config.provider == "ollama":
            message = payload.get("message", {})
            if isinstance(message, dict):
                return str(message.get("content", ""))
            return ""

        choices = payload.get("choices", [])
        if not choices:
            raise KeyError("choices")
        message = choices[0].get("message", {})
        if not isinstance(message, dict):
            raise KeyError("message")
        content = str(message.get("content", "")).strip()
        if content:
            return content
        return str(message.get("reasoning", "")).strip()

    @staticmethod
    def _mock_outline(topic: str, scene: str, tone: str, length: str, language: str) -> dict[str, Any]:
        scene_label = _scene_label(scene, language)
        if language == "en":
            return {
                "title": f"{topic} ({scene_label})",
                "sections": [
                    {
                        "heading": "Background and objective",
                        "bullets": [
                            f"Explain why {topic} matters now",
                            "Define the audience and intended outcome",
                        ],
                    },
                    {
                        "heading": "Key points",
                        "bullets": [
                            "Point 1 with a concrete example",
                            "Point 2 with practical action steps",
                            "Point 3 with risk and mitigation",
                        ],
                    },
                    {
                        "heading": "Conclusion",
                        "bullets": [
                            "Summarize value",
                            f"Close in {tone} tone and {length} detail",
                        ],
                    },
                ],
            }

        return {
            "title": f"{topic}（{scene_label}）",
            "sections": [
                {
                    "heading": "背景与目标",
                    "bullets": [
                        f"说明 {topic} 在当前阶段的重要性",
                        "明确目标读者和预期结果",
                    ],
                },
                {
                    "heading": "核心要点",
                    "bullets": [
                        "要点一：给出具体案例",
                        "要点二：给出可执行步骤",
                        "要点三：说明风险与应对",
                    ],
                },
                {
                    "heading": "结论",
                    "bullets": [
                        "总结主要价值",
                        f"用{tone}语气、{length}篇幅收尾",
                    ],
                },
            ],
        }

    @staticmethod
    def _mock_draft(topic: str, scene: str, tone: str, language: str) -> str:
        if language == "en":
            if scene == "copy":
                return (
                    f"# {topic}\n\n"
                    f"{topic} is more than a style. It is a calm, expressive mood that blends elegance with freedom.\n\n"
                    "Use it in your brand copy, post caption, or campaign headline when you want a soft but memorable voice.\n\n"
                    "Suggested direction:\n"
                    "- Keep the wording concise and visual\n"
                    "- Use poetic but readable phrases\n"
                    "- End with a clear emotional hook\n"
                )
            return (
                f"# {topic}\n\n"
                f"This is a starter draft in {tone} tone.\n\n"
                "Write directly to the requested outcome instead of listing an outline first.\n\n"
                "Use concrete details, smooth transitions, and complete the full response in one pass.\n"
            )
        if scene == "copy":
            return (
                f"# {topic}\n\n"
                f"{topic}，不是刻意堆砌辞藻，而是在克制里保留气韵，在安静里写出力量。\n\n"
                "适合用于海报文案、短视频标题、账号简介或品牌短句，整体风格可以轻、稳、雅，但不要空。\n\n"
                "可直接参考的表达方向：\n"
                "- 语言简洁，但要有画面感\n"
                "- 情绪自然，不要故作玄虚\n"
                "- 结尾最好留一句能让人记住的话\n"
            )
        return (
            f"# {topic}\n\n"
            f"这是一份{tone}语气的中文草稿示例。\n\n"
            "正文会根据场景直接生成，不再额外输出提纲。\n"
        )


SERVICE = AiWriterService(AiWriterConfig.from_env())


def handle_ai_writer_get(path: str, handler: Any) -> bool:
    if path in {"/ai-writer", "/writer"}:
        handler._html_response(HTTPStatus.OK, render_ai_writer_page())
        return True
    if path == "/api/ai-writer/health":
        handler._json_response(HTTPStatus.OK, SERVICE.health())
        return True
    if path == "/api/ai-writer/runtime":
        handler._json_response(HTTPStatus.OK, {"ok": True, "data": SERVICE.runtime_settings()})
        return True
    return False


def handle_ai_writer_post(path: str, body_raw: bytes, handler: Any) -> bool:
    if path not in {
        "/api/ai-writer/outline",
        "/api/ai-writer/draft",
        "/api/ai-writer/rewrite",
        "/api/ai-writer/polish",
        "/api/ai-writer/translate",
        "/api/ai-writer/runtime",
    }:
        return False

    try:
        payload = json.loads(body_raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        handler._json_response(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_json"})
        return True

    try:
        if path.endswith("/runtime"):
            data = SERVICE.update_runtime(payload)
        elif path.endswith("/outline"):
            data = SERVICE.generate_outline(payload)
        elif path.endswith("/draft"):
            data = SERVICE.generate_draft(payload)
        elif path.endswith("/rewrite"):
            data = SERVICE.rewrite_paragraph(payload)
        elif path.endswith("/translate"):
            data = SERVICE.translate_text(payload)
        else:
            data = SERVICE.polish_full_text(payload)
    except ValueError as ex:
        handler._json_response(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(ex)})
        return True
    except RuntimeError as ex:
        handler._json_response(HTTPStatus.BAD_GATEWAY, {"ok": False, "error": str(ex)})
        return True

    handler._json_response(HTTPStatus.OK, {"ok": True, "data": data})
    return True


def render_ai_writer_page() -> str:
    return (
        "<!doctype html>"
        "<html lang='zh-CN'>"
        "<head>"
        "<meta charset='utf-8' />"
        "<meta name='viewport' content='width=device-width, initial-scale=1' />"
        "<title>AI 写作助手</title>"
        "<style>"
        "body{font-family:Segoe UI,Arial,sans-serif;max-width:1240px;margin:0 auto;padding:24px;line-height:1.6;background:#f8fafc;color:#0f172a;position:relative;}"
        "h1{margin:0 0 8px;}"
        "section{background:#fff;border:1px solid #cbd5e1;border-radius:10px;padding:14px 16px;margin:14px 0;}"
        "label{display:block;font-weight:600;margin-top:8px;}"
        "input,select,textarea{width:100%;padding:8px;margin-top:6px;border:1px solid #94a3b8;border-radius:8px;box-sizing:border-box;}"
        "textarea{min-height:110px;}"
        "button{margin-top:10px;margin-right:8px;padding:8px 14px;border-radius:8px;border:1px solid #2563eb;background:#2563eb;color:#fff;cursor:pointer;}"
        "button:hover{opacity:0.92;}"
        ".grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}"
        ".result{white-space:pre-wrap;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:8px;padding:10px;margin-top:10px;}"
        ".hint{color:#475569;font-size:14px;}"
        ".topbar{position:relative;display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin:14px 0 10px;}"
        ".intro{flex:1 1 auto;min-width:0;max-width:none;padding-right:72px;}"
        ".main-shell{max-width:none;}"
        ".runtime-wrap{position:absolute;top:0;right:0;display:flex;flex-direction:column;align-items:flex-end;gap:8px;}"
        ".runtime-toggle{margin-top:0;margin-right:0;padding:6px 10px;font-size:12px;line-height:1;min-width:44px;}"
        ".runtime-panel{position:absolute;top:38px;right:0;width:280px;background:#fff;border:1px solid #cbd5e1;border-radius:12px;padding:12px 14px;box-sizing:border-box;box-shadow:0 12px 28px rgba(15,23,42,0.18);z-index:20;}"
        ".runtime-panel.hidden{display:none;}"
        ".runtime-head{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px;}"
        ".runtime-panel h2{margin:0;font-size:17px;}"
        ".runtime-close{margin:0;padding:2px 8px;font-size:16px;line-height:1;border-color:#cbd5e1;background:#fff;color:#334155;}"
        ".runtime-panel .hint{margin:0 0 8px;line-height:1.4;font-size:13px;}"
        ".runtime-panel label{font-size:13px;margin-top:6px;}"
        ".runtime-panel input,.runtime-panel select{padding:6px;font-size:14px;}"
        ".runtime-panel button{padding:6px 10px;font-size:13px;}"
        ".runtime-panel .result{font-size:13px;padding:8px;margin-top:8px;}"
        "@media (max-width: 900px){.grid{grid-template-columns:1fr;}.intro{padding-right:0;}.runtime-wrap{position:static;}.runtime-panel{position:fixed;top:56px;right:12px;left:12px;width:auto;}}"
        "</style>"
        "</head>"
        "<body>"
        "<p><a href='/blog'>返回博客</a></p>"
        "<div class='topbar'>"
        "<div class='intro'>"
        "<h1>AI 写作助手</h1>"
        "<p>输入主题后直接生成结果，再按需改写、润色或翻译。支持 mock / Ollama / OpenAI 兼容接口。</p>"
        "</div>"
        "<div class='runtime-wrap'>"
        "<button class='runtime-toggle' onclick='toggleRuntimePanel()'>设置</button>"
        "<aside id='runtime_panel' class='runtime-panel hidden'>"
        "<div class='runtime-head'><h2>运行挡位</h2><button class='runtime-close' onclick='closeRuntimePanel()'>×</button></div>"
        "<p class='hint'>只影响当前服务，重启后恢复默认配置。</p>"
        "<div><label>模式</label><select id='provider' onchange='onProviderChange()'><option value='mock'>mock（演示）</option><option value='ollama'>ollama（本地）</option><option value='openai'>openai（远程/兼容）</option></select></div>"
        "<div><label>服务地址</label><input id='base_url' placeholder='例如：http://127.0.0.1:11434' /></div>"
        "<div><label>模型</label><input id='model_name' placeholder='例如：qwen2.5:3b-instruct' /></div>"
        "<div><label>API Key</label><input id='api_key' type='password' placeholder='mock 可留空，ollama 可填 local' /></div>"
        "<button onclick='fillRecommended()'>推荐值</button>"
        "<button onclick='applyRuntime()'>应用</button>"
        "<div id='runtime' class='result'>运行模式检测中...</div>"
        "<div id='runtime_apply' class='hint'></div>"
        "</aside>"
        "</div>"
        "</div>"
        "<div class='main-shell'>"
        "<section>"
        "<div class='grid'>"
        "<div><label>主题</label><input id='topic' placeholder='例如：AI 如何帮助学生写课程报告' /></div>"
        "<div><label>场景</label><select id='scene'><option value='copy'>文案</option><option value='report'>报告</option><option value='email'>邮件</option><option value='translate'>翻译稿</option></select></div>"
        "<div><label>语气</label><select id='tone'><option value='natural'>自然</option><option value='formal'>正式</option><option value='professional'>专业</option></select></div>"
        "<div><label>字数</label><input id='word_count' type='number' min='50' max='1200' step='10' value='150' placeholder='例如：80 / 150 / 300' /></div>"
        "<div><label>写作语言</label><select id='language'><option value='zh' selected>中文</option><option value='en'>English</option></select></div>"
        "</div>"
        "<button onclick='genDraft()'>生成结果</button>"
        "<div id='draft' class='result'></div>"
        "</section>"
        "<section>"
        "<label>待改写段落</label><textarea id='paragraph'></textarea>"
        "<label>改写要求</label><input id='instruction' value='请改得更简洁清晰。' />"
        "<button onclick='rewritePara()'>段落改写</button>"
        "<div id='rewrite' class='result'></div>"
        "</section>"
        "<section>"
        "<label>待润色全文</label><textarea id='fulltext'></textarea>"
        "<button onclick='polishText()'>全文润色</button>"
        "<div id='polish' class='result'></div>"
        "</section>"
        "<section>"
        "<label>翻译文本</label><textarea id='translate_input'></textarea>"
        "<div class='grid'>"
        "<div><label>源语言</label><select id='source_language'><option value='auto' selected>自动识别</option><option value='zh'>中文</option><option value='en'>English</option></select></div>"
        "<div><label>目标语言</label><select id='target_language'><option value='en' selected>English</option><option value='zh'>中文</option></select></div>"
        "</div>"
        "<button onclick='translateText()'>开始翻译</button>"
        "<div id='translate' class='result'></div>"
        "</section>"
        "</div>"
        "<script>"
        "const REQUEST_TIMEOUT_MS = 180000;"
        "function val(id){return document.getElementById(id).value.trim()}"
        "function setValue(id, value){document.getElementById(id).value = value || '';}"
        "function show(id, obj){document.getElementById(id).textContent = typeof obj==='string' ? obj : JSON.stringify(obj,null,2)}"
        "function renderOutline(data){ if(!data || typeof data!=='object'){ return '暂无结果'; } const lines=[]; if(data.title){ lines.push(data.title); lines.push(''); } const sections=Array.isArray(data.sections)?data.sections:[]; for(const sec of sections){ if(sec && sec.heading){ lines.push(sec.heading); } const bullets=Array.isArray(sec && sec.bullets)?sec.bullets:[]; for(const item of bullets){ lines.push(`- ${item}`); } lines.push(''); } return lines.join('\\n').trim(); }"
        "function errMsg(e){return e && e.name==='AbortError' ? '请求超时，请重试。' : (e && e.message ? e.message : '请求失败');}"
        "function recommendedRuntime(provider){ if(provider==='ollama'){ return {provider:'ollama', base_url:'http://127.0.0.1:11434', model:'qwen2.5:3b-instruct', api_key:'local'}; } if(provider==='openai'){ return {provider:'openai', base_url:'https://api.openai.com/v1', model:'gpt-4o-mini', api_key:''}; } return {provider:'mock', base_url:'', model:'mock', api_key:''}; }"
        "function renderRuntimeStatus(data){ const parts=[`当前模式：${data.provider||'unknown'}`,`模型：${data.model||'-'}`]; if(data.base_url){ parts.push(`地址：${data.base_url}`); } if(data.api_key_present){ parts.push('API Key：已设置'); } document.getElementById('runtime').textContent=parts.join(' | '); }"
        "function onProviderChange(){ const provider = val('provider') || 'mock'; const disabled = provider === 'mock'; document.getElementById('base_url').disabled = disabled; document.getElementById('model_name').disabled = disabled; document.getElementById('api_key').disabled = disabled; }"
        "function toggleRuntimePanel(){ document.getElementById('runtime_panel').classList.toggle('hidden'); }"
        "function closeRuntimePanel(){ document.getElementById('runtime_panel').classList.add('hidden'); }"
        "function fillRuntimeForm(data){ setValue('provider', data.provider); setValue('base_url', data.base_url); setValue('model_name', data.model); setValue('api_key', ''); onProviderChange(); }"
        "function fillRecommended(){ const runtime = recommendedRuntime(val('provider') || 'mock'); fillRuntimeForm(runtime); show('runtime_apply', '已填入推荐值，点击“应用挡位”后生效。'); }"
        "async function loadRuntime(){ try{ const r = await fetch('/api/ai-writer/runtime'); const payload = await r.json(); if(!payload.ok){ throw new Error(payload.error || '加载失败'); } fillRuntimeForm(payload.data); renderRuntimeStatus(payload.data); show('runtime_apply', '当前挡位已加载。'); } catch(e){ show('runtime_apply', errMsg(e)); document.getElementById('runtime').textContent='运行模式检测失败'; } }"
        "async function applyRuntime(){ show('runtime_apply', '应用中...'); try{ const payload = { provider: val('provider'), base_url: val('base_url'), model: val('model_name'), api_key: val('api_key') }; const res = await req('/api/ai-writer/runtime', payload); if(!res.ok){ show('runtime_apply', res.error || '应用失败'); return; } renderRuntimeStatus(res.data); setValue('api_key', ''); show('runtime_apply', '挡位已应用，后续生成将使用新配置。'); closeRuntimePanel(); } catch(e){ show('runtime_apply', errMsg(e)); } }"
        "async function req(path, payload){"
        " const controller = new AbortController();"
        " const timer = setTimeout(()=>controller.abort(), REQUEST_TIMEOUT_MS);"
        " try {"
        "  const r = await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal});"
        "  return await r.json();"
        " } finally { clearTimeout(timer); }"
        "}"
        "function basePayload(){return {topic:val('topic'),scene:val('scene'),tone:val('tone'),word_count:val('word_count'),language:val('language')}}"
        "async function genDraft(){show('draft','生成中...'); try{const payload=basePayload(); const res=await req('/api/ai-writer/draft',payload); if(!res.ok){show('draft',res.error||'请求失败');return;} show('draft',res.data.markdown); document.getElementById('fulltext').value=res.data.markdown;}catch(e){show('draft',errMsg(e));}}"
        "async function rewritePara(){show('rewrite','改写中...'); try{const payload={paragraph:val('paragraph'),instruction:val('instruction'),tone:val('tone'),language:val('language')}; const res=await req('/api/ai-writer/rewrite',payload); if(!res.ok){show('rewrite',res.error||'请求失败');return;} show('rewrite',res.data.text);}catch(e){show('rewrite',errMsg(e));}}"
        "async function polishText(){show('polish','润色中...'); try{const payload={text:val('fulltext'),tone:val('tone'),language:val('language')}; const res=await req('/api/ai-writer/polish',payload); if(!res.ok){show('polish',res.error||'请求失败');return;} show('polish',res.data.text);}catch(e){show('polish',errMsg(e));}}"
        "async function translateText(){show('translate','翻译中...'); try{const payload={text:val('translate_input'),source_language:val('source_language'),target_language:val('target_language')}; const res=await req('/api/ai-writer/translate',payload); if(!res.ok){show('translate',res.error||'请求失败');return;} show('translate',res.data.text);}catch(e){show('translate',errMsg(e));}}"
        "loadRuntime();"
        "</script>"
        "</body>"
        "</html>"
    )


def _normalize_language(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"en", "english"}:
        return "en"
    return "zh"


def _normalize_source_language(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"zh", "chinese", "cn"}:
        return "zh"
    if raw in {"en", "english"}:
        return "en"
    return "auto"


def _scene_label(scene: str, language: str) -> str:
    labels = {
        "copy": {"zh": "文案", "en": "copy"},
        "report": {"zh": "报告", "en": "report"},
        "email": {"zh": "邮件", "en": "email"},
        "translate": {"zh": "翻译", "en": "translation"},
        "general": {"zh": "通用", "en": "general"},
    }
    selected = labels.get(scene, labels["general"])
    return selected["en"] if language == "en" else selected["zh"]


def _tone_label(tone: str, language: str) -> str:
    labels = {
        "natural": {"zh": "自然", "en": "natural"},
        "formal": {"zh": "正式", "en": "formal"},
        "professional": {"zh": "专业", "en": "professional"},
    }
    selected = labels.get(tone, labels["natural"])
    return selected["en"] if language == "en" else selected["zh"]


def _requested_word_count(value: Any) -> int:
    try:
        count = int(str(value).strip())
    except ValueError:
        return 150
    return max(50, min(1200, count))


def _draft_prompt(topic: str, scene: str, tone: str, word_count: int, language: str) -> tuple[str, str, int]:
    max_tokens = _draft_max_tokens(scene, word_count, language)
    if language == "en":
        if scene == "copy":
            user_prompt = (
                f"Topic: {topic}\n"
                f"Tone: {tone}\n"
                f"Target length: about {word_count} words\n"
                "Write one polished final copy. No explanations, no bullet list, no meta commentary."
            )
            return "You write polished marketing copy that is directly usable.", user_prompt, max_tokens
        if scene == "email":
            user_prompt = (
                f"Topic: {topic}\n"
                f"Tone: {tone}\n"
                f"Target length: about {word_count} words\n"
                "Write one complete email with subject and body. Keep it natural and useful."
            )
            return "You write clean business emails.", user_prompt, max_tokens
        if scene == "report":
            user_prompt = (
                f"Topic: {topic}\n"
                f"Tone: {tone}\n"
                f"Target length: about {word_count} words\n"
                "Write a compact report with a title and short sections. Output only the final text."
            )
            return "You write concise reports with good structure.", user_prompt, max_tokens
        if scene == "translate":
            user_prompt = (
                f"Text to translate:\n{topic}\n"
                f"Target language: English\n"
                "Translate accurately and naturally. Output only the translated text."
            )
            return "You are a precise translator.", user_prompt, max_tokens
        user_prompt = (
            f"Topic: {topic}\n"
            f"Tone: {tone}\n"
            f"Target length: about {word_count} words\n"
            "Write one final piece that is clear and directly usable. Output only the final text."
        )
        return "You are a concise writing assistant.", user_prompt, max_tokens

    if scene == "copy":
        user_prompt = (
            f"主题：{topic}\n"
            f"语气：{_tone_label(tone, language)}\n"
            f"目标字数：约{word_count}字，至少{_minimum_length(word_count, language)}字\n"
            "请直接写一版可直接使用的成品文案。不要解释思路，不要写说明，不要列创作步骤。"
            "语言要自然、有画面感、有记忆点，且字数必须达标，不能只写一句话。"
        )
        return "你是资深中文文案写手，只输出成品。", user_prompt, max_tokens
    if scene == "email":
        user_prompt = (
            f"主题：{topic}\n"
            f"语气：{_tone_label(tone, language)}\n"
            f"目标字数：约{word_count}字，至少{_minimum_length(word_count, language)}字\n"
            "请直接写一封完整邮件，包含邮件标题和正文。表达自然、清楚、能直接发送，且字数必须达标。"
        )
        return "你擅长写简洁自然的中文邮件，只输出最终邮件。", user_prompt, max_tokens
    if scene == "report":
        user_prompt = (
            f"主题：{topic}\n"
            f"语气：{_tone_label(tone, language)}\n"
            f"目标字数：约{word_count}字，至少{_minimum_length(word_count, language)}字\n"
            "请直接写一篇简明报告，带标题和清晰的小节。内容务实，不空泛，不要写提纲，且字数必须达标。"
        )
        return "你擅长写结构清晰、信息密度高的中文报告。", user_prompt, max_tokens
    if scene == "translate":
        user_prompt = (
            f"待翻译文本：\n{topic}\n"
            "请直接翻译成中文，表达自然、准确、通顺。只输出翻译结果，不要解释。"
        )
        return "你是专业翻译，只输出最终译文。", user_prompt, max_tokens
    user_prompt = (
        f"主题：{topic}\n"
        f"语气：{_tone_label(tone, language)}\n"
        f"目标字数：约{word_count}字，至少{_minimum_length(word_count, language)}字\n"
        "请直接写出最终成稿。表达自然、具体、可直接使用，不要写说明或额外注释，且字数必须达标。"
    )
    return "你是高质量中文写作助手，只输出最终成稿。", user_prompt, max_tokens


def _draft_max_tokens(scene: str, word_count: int, language: str) -> int:
    scene_base = {
        "copy": 1.3,
        "email": 1.5,
        "translate": 1.5,
        "report": 1.8,
        "general": 1.6,
    }.get(scene, 1.6)
    multiplier = scene_base if language == "en" else max(scene_base, 1.8)
    return max(120, min(900, int(word_count * multiplier)))


def _minimum_length(word_count: int, language: str) -> int:
    return max(40, int(word_count * 0.9))


def _text_units(text: str, language: str) -> int:
    text = text.strip()
    if not text:
        return 0
    if language == "en":
        return len([part for part in text.split() if part.strip()])
    return len([ch for ch in text if not ch.isspace()])


def _is_too_short(text: str, word_count: int, language: str) -> bool:
    return _text_units(text, language) < _minimum_length(word_count, language)


def _rewrite_max_tokens(paragraph: str) -> int:
    return max(96, min(220, len(paragraph) // 3))


def _polish_max_tokens(text: str) -> int:
    return max(140, min(320, len(text) // 3))


def _translate_max_tokens(text: str) -> int:
    return max(140, min(320, len(text) // 3))


def _outline_to_text(outline: Any) -> str:
    if isinstance(outline, str):
        return outline
    if not isinstance(outline, dict):
        return ""
    lines: list[str] = []
    title = outline.get("title")
    if title:
        lines.append(f"Title: {title}")
    for sec in outline.get("sections", []):
        heading = sec.get("heading", "") if isinstance(sec, dict) else ""
        if heading:
            lines.append(f"- {heading}")
        bullets = sec.get("bullets", []) if isinstance(sec, dict) else []
        if isinstance(bullets, list):
            for item in bullets:
                lines.append(f"  - {item}")
    return "\n".join(lines)


def _parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    if text.startswith("{") and text.endswith("}"):
        try:
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else {}
        except json.JSONDecodeError:
            return {}

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        obj = json.loads(text[start : end + 1])
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


def _mask_sensitive(text: str) -> str:
    blocked = ("terror", "bomb", "hack bank")
    sanitized = text
    for token in blocked:
        sanitized = sanitized.replace(token, "***")
        sanitized = sanitized.replace(token.title(), "***")
    return sanitized
