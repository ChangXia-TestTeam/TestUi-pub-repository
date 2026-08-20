"""
定位生成器 - AI 驱动：截图/蓝湖标注 → Playwright 定位
路径: ai/generators/locator_gen.py

对标 Midscene 的视觉理解思路：截图 → LLM 识别页面元素 → 生成稳定定位。
对于 PRD 解析得到的元素 hint，本模块将其规范化为可用定位。
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from ai import llm_client
from utils import config


def generate_from_screenshot(image_path: Path, page_name: str = "") -> list[dict]:
    """基于原型截图，调用 LLM（多模态）识别元素并产出定位候选。"""
    prompt_tmpl = llm_client.load_prompt("locator")
    prompt = (prompt_tmpl or "").replace("{{ORIGINAL}}", f"截图: {image_path.name}").replace("{{ACTION}}", "识别元素")
    prompt += f"\n\n=== 截图 ===\n{image_path}\n请输出 JSON 数组，元素含 name/type/role/locator/placeholder"
    out = llm_client.call(prompt, system="你是 Playwright 定位专家，输出 JSON 数组", expect_json=True)
    return _parse_elements(out)


def enrich_elements(page) -> list[dict]:
    """对 UIRequirement.UIPage 的元素补充可用定位。"""
    from utils.locator_parser import to_locator, guess_locator_by_type
    enriched = []
    for e in page.elements:
        loc = to_locator(e) or guess_locator_by_type(e.get("name", ""), e.get("type", "element"))
        enriched.append({**e, "locator": loc})
    return enriched


def _parse_elements(out: str) -> list[dict]:
    import json
    try:
        data = json.loads(out)
        return data if isinstance(data, list) else []
    except Exception:
        return []
