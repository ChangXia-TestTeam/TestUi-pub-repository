"""
PRD 文档解析 - 输入端 A
路径: parsers/prd_parser.py
支持 docx / pdf / markdown，按标题层级切分页面段落，提取元素清单与校验点。
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from utils import config
from utils.pipeline_logger import progress, counter, warn, timer_start, timer_elapsed
from parsers.requirement_model import UIRequirement, UIPage, guess_type


def parse_prd(path: Optional[str] = None) -> UIRequirement:
    """解析 PRD 目录下所有文档。"""
    inp = config.input_config()
    prd_dir = config.ROOT_DIR / (path or inp.get("prd_dir", "UI_input_files/prd"))
    req = UIRequirement(project=config.project_name(), input_mode="prd")

    if not prd_dir.exists():
        print(f"   ⚠️  PRD 目录不存在: {prd_dir}")
        return req

    files = [f for f in sorted(prd_dir.iterdir()) if f.suffix.lower() in (".docx", ".pdf", ".md", ".markdown")]
    if not files:
        print(f"   ⚠️  PRD 目录为空: {prd_dir}")
        return req

    print(f"   发现 {len(files)} 个 PRD 文件")
    total = len(files)
    for i, f in enumerate(files, 1):
        progress(i, total, f"解析文件", f"{f.name} ({f.suffix})")
        t0 = timer_start()
        if f.suffix.lower() == ".docx":
            pages = _parse_docx(f)
        elif f.suffix.lower() == ".pdf":
            pages = _parse_pdf(f)
        else:
            pages = _parse_markdown(f)
        for p in pages:
            p.source = str(f)
        req.pages.extend(pages)
        counter("  页面", len(pages), f"耗时 {timer_elapsed(t0):.1f}s")

    counter("文件", len(files))
    counter("页面", len(req.pages))
    counter("元素", sum(len(p.elements) for p in req.pages))
    counter("校验点", sum(len(p.validation_points) for p in req.pages))
    return req


def _parse_docx(path: Path) -> list[UIPage]:
    try:
        import docx
    except ImportError:
        warn("prd_parser", "缺少 python-docx，跳过 docx 解析", "pip install python-docx")
        return []
    doc = docx.Document(str(path))
    pages: list[UIPage] = []
    cur: Optional[UIPage] = None
    total_elements = 0
    total_vps = 0
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            continue
        if p.style and (p.style.name.startswith("Heading 1") or p.style.name.startswith("标题 1")):
            cur = UIPage(name=txt)
            pages.append(cur)
        elif p.style and (p.style.name.startswith("Heading 2") or p.style.name.startswith("标题 2")):
            if cur:
                cur.validation_points.append(txt)
                total_vps += 1
        else:
            if cur is None:
                cur = UIPage(name="未命名")
                pages.append(cur)
            if "：" in txt or ":" in txt:
                name, _, desc = txt.partition("：") if "：" in txt else txt.partition(":")
                cur.elements.append({"name": name.strip(), "type": guess_type(name), "locator_hint": desc.strip()})
                total_elements += 1
            else:
                cur.description += txt + "\n"
    counter("  元素", total_elements)
    counter("  校验点", total_vps)
    return pages


def _parse_pdf(path: Path) -> list[UIPage]:
    try:
        import pdfplumber
    except ImportError:
        warn("prd_parser", "缺少 pdfplumber，跳过 pdf 解析", "pip install pdfplumber")
        return []
    pages: list[UIPage] = []
    with pdfplumber.open(str(path)) as pdf:
        for i, pg in enumerate(pdf.pages, 1):
            text = pg.extract_text() or ""
            if text.strip():
                pages.append(UIPage(name=f"第{i}页", description=text))
    return pages


def _parse_markdown(path: Path) -> list[UIPage]:
    pages: list[UIPage] = []
    cur: Optional[UIPage] = None
    total_elements = 0
    total_vps = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            cur = UIPage(name=line.lstrip("# ").strip())
            pages.append(cur)
        elif line.startswith("## "):
            if cur:
                cur.validation_points.append(line.lstrip("# ").strip())
                total_vps += 1
        elif line.startswith("- "):
            if cur:
                item = line.lstrip("- ").strip()
                cur.elements.append({"name": item, "type": guess_type(item)})
                total_elements += 1
        else:
            if cur is None:
                cur = UIPage(name="未命名")
                pages.append(cur)
            cur.description += line + "\n"
    counter("  元素", total_elements)
    counter("  校验点", total_vps)
    return pages
