"""
LLM 客户端封装 - AI 驱动 UI 自动化的统一模型调用入口
路径: ai/llm_client.py

设计模式：市面上 AI 驱动 UI 自动化（如 Midscene / zeroStep / QA Wolf / AutoPlaywright）
都把「自然语言 + 截图/标注 → 可执行代码/动作」交给 LLM。本模块封装统一调用接口，
使生成器（page_object_gen / test_case_gen / locator_gen）与自愈器（self_healing）
都通过同一入口取模型输出，便于切换底层模型。

两种执行模式：
    1) "trae"   —— 在 Trae 对话中，本模块生成 prompt 落盘到 ai/.pending/*.txt，
                   由对话 AI（本助手）读取并产出代码，再回填到 pages/ tests/。
                   适合「零额外配置」直接跑通。
    2) "api"    —— 配置 config.ai.provider/openai_base_url/api_key，直接 HTTP 调用。
                   适合无人值守的 CI 场景。
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from utils import config
from utils.pipeline_logger import llm_call, error

PENDING_DIR = config.ROOT_DIR / "ai" / ".pending"


def _ensure_pending():
    PENDING_DIR.mkdir(parents=True, exist_ok=True)


def call(prompt: str, system: str = "", expect_json: bool = False, stage: str = "") -> str:
    """
    统一调用入口，返回模型输出文本。
    根据 config.ai.mode 选择执行模式：
        - trae: 把 prompt 落盘，提示对话 AI 接管（返回提示文本）
        - api:  HTTP 调用配置的模型
    stage: 调用阶段名（用于日志，不打印模型名）
    """
    ai_cfg = config.get("ai", {}) or {}
    mode = ai_cfg.get("mode", "trae")
    t0 = time.time()
    try:
        if mode == "api":
            out = _call_api(prompt, system, ai_cfg, expect_json)
        else:
            out = _call_trae(prompt, system, ai_cfg)
        if stage:
            llm_call(stage, len(prompt), len(out), time.time() - t0)
        return out
    except Exception as e:
        if stage:
            error(f"llm_client/{stage}", str(e))
        raise


# ============================================================
# 模式 1：Trae 对话接管
# ============================================================
def _call_trae(prompt: str, system: str, ai_cfg: dict) -> str:
    """把 prompt 落盘到 ai/.pending/，供对话 AI（本助手）读取并产出代码。"""
    _ensure_pending()
    ts = time.strftime("%Y%m%d_%H%M%S")
    pending = PENDING_DIR / f"task_{ts}.txt"
    body = f"=== SYSTEM ===\n{system}\n\n=== USER ===\n{prompt}\n"
    pending.write_text(body, encoding="utf-8")
    return (
        f"[llm_client/trae] 已生成 prompt 任务：{pending}\n"
        f"请对话 AI 读取该任务并按 ai/prompts/ 中的模板产出代码到 pages/ 或 tests/，"
        f"产出后将 .pending 文件移至 ai/.done/"
    )


# ============================================================
# 模式 2：API 直调
# ============================================================
def _call_api(prompt: str, system: str, ai_cfg: dict, expect_json: bool) -> str:
    """直接 HTTP 调用 OpenAI 兼容接口。"""
    import requests

    base_url = ai_cfg.get("openai_base_url") or ai_cfg.get("base_url")
    api_key = ai_cfg.get("api_key") or ai_cfg.get("openai_api_key")
    model = ai_cfg.get("model", "gpt-4o")
    if not (base_url and api_key):
        return "[llm_client/api] 未配置 ai.openai_base_url / ai.api_key，回退到 trae 模式"

    url = base_url.rstrip("/") + "/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": ai_cfg.get("temperature", 0.2),
    }
    if expect_json:
        payload["response_format"] = {"type": "json_object"}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=ai_cfg.get("timeout", 120))
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[llm_client/api] 调用失败: {e}"


def load_prompt(name: str) -> str:
    """读取 ai/prompts/{name}.md 模板。"""
    p = config.ROOT_DIR / "ai" / "prompts" / f"{name}.md"
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")
