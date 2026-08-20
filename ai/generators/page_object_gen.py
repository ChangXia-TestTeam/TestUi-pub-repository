"""
Page Object 生成器 - AI 驱动：需求(UIRequirement) → Page Object 代码
路径: ai/generators/page_object_gen.py

市面 AI UI 自动化（Midscene/zeroStep/AutoPlaywright）核心思路：
    输入（PRD/截图/蓝湖）→ 结构化需求 → LLM 产出可执行 Page Object 代码
本模块编排该流程：组装 prompt → 调 LLM → 落盘到 pages/<module>/。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from ai import llm_client
from utils import config
from utils.pipeline_logger import progress, counter, warn, timer_start, timer_elapsed


def generate(req) -> list[Path]:
    """
    入参 req: parsers.requirement_model.UIRequirement
    输出：生成的 Page 文件路径列表。
    """
    written = []
    prompt_tmpl = llm_client.load_prompt("page_object")
    total = len(req.pages)
    if total == 0:
        warn("page_object_gen", "无页面可生成")
        return written

    print(f"   待生成 {total} 个 Page Object")
    t_all = timer_start()
    for i, page in enumerate(req.pages, 1):
        progress(i, total, f"Page Object", f"{page.name}  elements={len(page.elements)} vps={len(page.validation_points)}")
        module = _slug(page.name)
        prompt = _build_prompt(prompt_tmpl, page, req.project)
        out = llm_client.call(prompt, system="你是 Playwright Page Object 专家，只输出 Python 代码", stage=f"PageObject[{page.name}]")
        code = _extract_code(out)
        if not code:
            warn("page_object_gen", f"{page.name} LLM 未产出代码，跳过")
            continue
        path = _write_page(module, page.name, code)
        if path:
            written.append(path)
        counter("  文件", len(written))
    print(f"   ⏱ 总耗时 {timer_elapsed(t_all):.1f}s")
    return written


def _build_prompt(tmpl: str, page, project: str) -> str:
    elements = "\n".join(
        f"- {e.get('name', '')} (type={e.get('type', 'element')}, hint={e.get('locator_hint', '')})"
        for e in page.elements
    ) or "(无明确元素，按页面描述生成)"
    return (tmpl or "").replace("{{PROJECT}}", project).replace("{{PAGE_NAME}}", page.name) \
        .replace("{{PAGE_DESC}}", page.description).replace("{{ELEMENTS}}", elements) \
        .replace("{{VALIDATION}}", "\n".join(page.validation_points))


def _extract_code(out: str) -> str:
    """从 LLM 输出中提取 ```python ... ``` 代码块；若无则整段返回。"""
    m = re.search(r"```python\s*(.*?)```", out, re.S)
    return (m.group(1) if m else out).strip()


def _slug(name: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fa5]+", "_", name).strip("_").lower()
    return s or "page"


def _write_page(module: str, name: str, code: str) -> Optional[Path]:
    pages_dir = config.ROOT_DIR / "pages" / module
    pages_dir.mkdir(parents=True, exist_ok=True)
    # 类名：PascalCase
    cls = "".join(w.capitalize() for w in re.split(r"[_\s]+", _slug(name))) or "Page"
    fname = f"{_slug(name)}_page.py"
    path = pages_dir / fname
    # 写入（若已存在则追加备份注释，便于人工 review）
    header = f'"""\nPage Object (AI 生成) - {name}\n路径: pages/{module}/{fname}\n生成时间: {__import__("time").strftime("%Y-%m-%d %H:%M:%S")}\n⚠️ AI 生成，运行前请人工核对元素定位。\n"""\n'
    path.write_text(header + code, encoding="utf-8")
    print(f"[page_object_gen] 生成: {path}")
    return path
