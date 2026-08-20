"""
Pipeline 日志工具 - 结构化日志，方便排查流程卡住
路径: utils/pipeline_logger.py

设计原则（参考经验沉淀）：
    1) 用阶段编号（1/N、2/N）替代大段内容打印
    2) 用计数型指标（文件数/页面数/元素数）替代原文输出
    3) LLM 调用记录 prompt 长度、输出字符数、耗时，不打印模型名
    4) 错误时打印「当前阶段 + 已处理进度 + 耗时」便于定位卡点
"""
from __future__ import annotations

import time
from typing import Optional


def stage_start(stage: int, total: int, name: str):
    print(f"[{stage}/{total}] ▶ {name}")


def stage_done(stage: int, total: int, name: str, elapsed: float):
    print(f"[{stage}/{total}] ✅ {name} 完成 ({elapsed:.1f}s)")


def progress(idx: int, total: int, label: str, detail: str = ""):
    """进度行：2/5  PRD文档   file=xxx.docx pages=3"""
    tail = f"  {detail}" if detail else ""
    print(f"   [{idx}/{total}] {label}{tail}")


def counter(label: str, value, extra: str = ""):
    print(f"   📊 {label}: {value}{('  (' + extra + ')') if extra else ''}")


def llm_call(stage: str, prompt_len: int, output_len: int, elapsed: float, extra: str = ""):
    """LLM 调用摘要（不打印模型名、不打印 prompt 原文）。"""
    tail = f"  ({extra})" if extra else ""
    print(f"   🤖 [{stage}] prompt={prompt_len}chars → output={output_len}chars  ⏱{elapsed:.1f}s{tail}")


def error(stage: str, msg: str, hint: str = ""):
    print(f"   ❌ [{stage}] {msg}")
    if hint:
        print(f"      💡 {hint}")


def warn(stage: str, msg: str, hint: str = ""):
    print(f"   ⚠️  [{stage}] {msg}")
    if hint:
        print(f"      💡 {hint}")


def timer_start() -> float:
    return time.time()


def timer_elapsed(t0: float) -> float:
    return time.time() - t0
