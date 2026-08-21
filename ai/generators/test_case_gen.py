"""
测试用例生成器 - AI 驱动：需求(UIRequirement) → Pytest 用例代码
路径: ai/generators/test_case_gen.py

设计模式：对标 AutoPlaywright / QA Wolf 的「需求/场景 → pytest 用例」自动生成。
输入端（PRD/蓝湖/截图）解析出的 UIRequirement + 校验点 → LLM 产出 pytest 用例，
按 P0/P1 优先级与 Allure feature/story 标注组织。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from ai import llm_client
from utils import config
from utils.pipeline_logger import progress, counter, warn, timer_start, timer_elapsed


def generate(req, page_files: list[Path] | None = None) -> list[Path]:
    """
    入参 req: parsers.requirement_model.UIRequirement
    page_files: 上一步生成的 Page 文件路径（用于 import 提示）
    输出：生成的 test_*.py 路径列表。
    """
    written = []
    prompt_tmpl = llm_client.load_prompt("test_case")
    page_import_hints = "\n".join(
        f"from pages.{p.parent.name}.{p.stem} import {_class_name(p.stem)}"
        for p in (page_files or [])
    ) or "(无已生成 Page，请用 page.base_page.BasePage)"

    total = len(req.pages)
    if total == 0:
        warn("test_case_gen", "无页面可生成")
        return written

    print(f"   待生成 {total} 个测试用例文件")
    t_all = timer_start()
    for i, page in enumerate(req.pages, 1):
        progress(i, total, "测试用例", f"{page.name}  vps={len(page.validation_points)}")
        prompt = _build_prompt(prompt_tmpl, page, page_import_hints, req.project)
        out = llm_client.call(prompt, system="你是 pytest + Playwright 测试专家，只输出 Python 代码", stage=f"TestCase[{page.name}]")

        # trae 模式下 llm_client.call 返回的是提示文本（非 Python 代码），跳过写入
        if _is_trae_placeholder(out):
            warn("test_case_gen", f"{page.name} 当前 trae 模式，跳过代码生成；请在 ai/.pending/ 中处理 prompt")
            continue

        code = _extract_code(out)
        if not code or not _looks_like_python(code):
            warn("test_case_gen", f"{page.name} LLM 未产出有效 Python 代码，跳过")
            continue
        path = _write_test(page.name, code)
        if path:
            written.append(path)
        counter("  文件", len(written))
    print(f"   ⏱ 总耗时 {timer_elapsed(t_all):.1f}s")
    return written


def _build_prompt(tmpl: str, page, page_imports: str, project: str) -> str:
    vps = "\n".join(f"- {v}" for v in page.validation_points) or "(按页面描述提炼校验点)"
    return (tmpl or "").replace("{{PROJECT}}", project).replace("{{PAGE_NAME}}", page.name) \
        .replace("{{PAGE_DESC}}", page.description).replace("{{VALIDATION}}", vps) \
        .replace("{{PAGE_IMPORTS}}", page_imports)


def _extract_code(out: str) -> str:
    m = re.search(r"```python\s*(.*?)```", out, re.S)
    return (m.group(1) if m else out).strip()


def _is_trae_placeholder(text: str) -> bool:
    """检测 trae 模式下的提示文本（非 LLM 产出的代码）。"""
    return text.startswith("[llm_client/trae]")


def _looks_like_python(code: str) -> bool:
    """粗略检查输出是否像 Python 代码。"""
    if not code:
        return False
    keywords = ("import ", "from ", "class ", "def ", "@")
    hits = sum(1 for k in keywords if k in code)
    return hits >= 2


def _class_name(stem: str) -> str:
    return "".join(w.capitalize() for w in re.split(r"[_\s]+", stem)) or "Page"


def _write_test(name: str, code: str) -> Optional[Path]:
    tests_dir = config.ROOT_DIR / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    fname = f"test_{re.sub(r'[^\\w]+', '_', name).strip('_').lower()}.py"
    path = tests_dir / fname
    header = f'"""\n测试用例 (AI 生成) - {name}\n路径: tests/{fname}\n生成时间: {__import__("time").strftime("%Y-%m-%d %H:%M:%S")}\n⚠️ AI 生成，运行前请人工核对。\n"""\n'
    path.write_text(header + code, encoding="utf-8")
    print(f"[test_case_gen] 生成: {path}")
    return path
