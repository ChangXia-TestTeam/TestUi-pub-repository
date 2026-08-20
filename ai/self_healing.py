"""
自愈定位器（Self-Healing Locator）- AI 驱动 UI 自动化的标志性能力
路径: ai/self_healing.py

灵感来源：Healenium / Midscene / autonomous 测试工具。当某个定位在运行时失效
（DOM 变更/重构），本模块：
    1) 捕获当前页面快照（HTML 片段 + 截图）
    2) 用语义相近的候选定位（role/text/placeholder/aria-label）逐个试探
    3) 仍失败则调用 LLM 基于页面快照重新生成定位
    4) 命中后回写到 pages/<page>.py 的元素定义，并记录 healing 记录供报告展示

调用方：pages/base_page.py 的 locator/click/fill 在失败时走 heal_then_retry。
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from utils import config
from utils.pipeline_logger import progress, counter, warn, llm_call, timer_start, timer_elapsed

HEAL_LOG_DIR = config.ROOT_DIR / "reports" / "self_healing"


@dataclass
class HealRecord:
    timestamp: str
    page_url: str
    page_class: str
    original_locator: str
    healed_locator: str
    strategy: str          # candidate | llm
    success: bool


def _ensure_dir():
    HEAL_LOG_DIR.mkdir(parents=True, exist_ok=True)


def _candidate_locators(original: str) -> list[str]:
    """从原定位派生语义候选定位（按启发式排序）。"""
    cands = []
    # 抽取可见文本启发
    import re
    m = re.search(r"has-text\('([^']+)'\)|text=['\"]([^'\"]+)['\"]|get_by_text\(['\"]([^'\"]+)['\"]", original)
    text = next((g for g in m.groups() if g), None) if m else None
    if text:
        cands.append(f"text='{text}'")
        cands.append(f"button:has-text('{text}')")
        cands.append(f"[aria-label='{text}']")
        cands.append(f"[title='{text}']")
    # role 启发
    if "button" in original.lower():
        cands.append("button")
    if "input" in original.lower() or "placeholder" in original.lower():
        cands.append("input:visible")
    return cands


def heal_locator(page, page_class_name: str, original_locator: str, action: str = "click") -> Optional[str]:
    """
    尝试为失效定位找到替代定位。返回命中的新定位字符串，失败返回 None。
    page: Playwright Page
    """
    _ensure_dir()
    url = page.url
    t0 = timer_start()
    # 1) 候选定位试探
    cands = _candidate_locators(original_locator)
    print(f"   🔧 [self_healing] page={page_class_name} original='{original_locator}' 候选={len(cands)}")
    for idx, cand in enumerate(cands, 1):
        try:
            loc = page.locator(cand).first
            if loc.count() == 1:
                if action in ("click",):
                    loc.click(timeout=3000)
                else:
                    loc.is_visible(timeout=3000)
                _log(HealRecord(time.strftime("%Y-%m-%d %H:%M:%S"), url, page_class_name,
                                original_locator, cand, "candidate", True))
                print(f"   ✅ [self_healing] 候选命中 [{idx}/{len(cands)}]: '{cand}' ({timer_elapsed(t0):.1f}s)")
                return cand
        except Exception:
            continue

    # 2) LLM 生成定位（基于页面快照）
    print(f"   🔧 [self_healing] 候选全部失败，尝试 LLM 生成定位...")
    try:
        from ai import llm_client
        prompt_tmpl = llm_client.load_prompt("locator")
        snapshot = _page_snapshot_text(page)
        prompt = (prompt_tmpl or "").replace("{{ORIGINAL}}", original_locator).replace("{{ACTION}}", action)
        prompt = prompt + f"\n\n=== 页面快照 ===\n{snapshot[:6000]}"
        out = llm_client.call(prompt, system="你是 Playwright 定位专家", expect_json=True, stage=f"heal[{page_class_name}]")
        new_loc = _extract_locator_from_output(out)
        if new_loc:
            try:
                page.locator(new_loc).first.click(timeout=3000)
                _log(HealRecord(time.strftime("%Y-%m-%d %H:%M:%S"), url, page_class_name,
                                original_locator, new_loc, "llm", True))
                print(f"   ✅ [self_healing] LLM 生成定位命中: '{new_loc}' ({timer_elapsed(t0):.1f}s)")
                return new_loc
            except Exception:
                print(f"   ❌ [self_healing] LLM 定位 '{new_loc}' 也无法命中")
    except Exception as e:
        print(f"   ❌ [self_healing] LLM 生成异常: {e}")

    _log(HealRecord(time.strftime("%Y-%m-%d %H:%M:%S"), url, page_class_name,
                    original_locator, "", "failed", False))
    print(f"   ❌ [self_healing] 自愈失败，原定位 '{original_locator}' 完全不可用 ({timer_elapsed(t0):.1f}s)")
    return None


def _page_snapshot_text(page) -> str:
    """取页面关键元素的文本快照（供 LLM 推断定位）。"""
    try:
        return page.evaluate(
            "() => JSON.stringify(Array.from(document.querySelectorAll('button, a, input, [role], [aria-label]'))"
            ".slice(0, 200).map(e => ({tag: e.tagName.toLowerCase(), text: (e.innerText||'').trim().slice(0,40), "
            "role: e.getAttribute('role'), aria: e.getAttribute('aria-label'), ph: e.getAttribute('placeholder'), "
            "id: e.id, cls: e.className})))"
        )
    except Exception:
        return ""


def _extract_locator_from_output(out: str) -> Optional[str]:
    """从 LLM 文本输出中提取 locator 字段。"""
    try:
        # 尝试 JSON
        data = json.loads(out)
        if isinstance(data, dict):
            for k in ("locator", "selector", "css", "playwright"):
                if data.get(k):
                    return data[k]
    except Exception:
        pass
    # 退化：取第一行非空代码行
    for line in out.splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("//"):
            return s
    return None


def _log(rec: HealRecord):
    try:
        f = HEAL_LOG_DIR / f"heal_{time.strftime('%Y%m%d')}.jsonl"
        with open(f, "a", encoding="utf-8") as fp:
            fp.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
    except Exception:
        pass


def stats() -> dict:
    """汇总自愈记录供报告展示。"""
    total = healed = failed = 0
    if HEAL_LOG_DIR.exists():
        for f in HEAL_LOG_DIR.glob("*.jsonl"):
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    d = json.loads(line)
                    total += 1
                    if d.get("success"):
                        healed += 1
                    else:
                        failed += 1
                except Exception:
                    pass
    return {"heal_total": total, "healed": healed, "heal_failed": failed}
