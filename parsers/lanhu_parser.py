"""
蓝湖解析 - 输入端 B
路径: parsers/lanhu_parser.py
在线：配置 config.input.lanhu_base_url，在对话中用浏览器抓取导出。
本地：读取 UI_input_files/lanhu/ 下的导出 JSON/HTML。
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from utils import config
from utils.pipeline_logger import progress, counter, warn, timer_start, timer_elapsed
from parsers.requirement_model import UIRequirement, UIPage


def parse_lanhu(url: Optional[str] = None) -> UIRequirement:
    inp = config.input_config()
    lanhu_url = url or inp.get("lanhu_base_url", "")
    lanhu_dir = config.ROOT_DIR / inp.get("lanhu_dir", "UI_input_files/lanhu")
    req = UIRequirement(project=config.project_name(), input_mode="lanhu")

    if lanhu_url and not lanhu_url.startswith("http"):
        warn("lanhu_parser", f"蓝湖 URL 无效: {lanhu_url}")
    if lanhu_url:
        print(f"   蓝湖在线解析需在对话中调用浏览器抓取: {lanhu_url}")
        print(f"   提示语：'用浏览器打开蓝湖地址 xxx，抓取所有页面设计稿与标注，导出到 UI_input_files/lanhu'")

    if not lanhu_dir.exists():
        print(f"   ⚠️  蓝湖目录不存在: {lanhu_dir}")
        return req

    files = [f for f in sorted(lanhu_dir.iterdir()) if f.suffix.lower() in (".json", ".html", ".htm")]
    if not files:
        print(f"   ⚠️  蓝湖目录为空: {lanhu_dir}")
        return req

    print(f"   发现 {len(files)} 个蓝湖文件")
    total = len(files)
    for i, f in enumerate(files, 1):
        progress(i, total, "解析文件", f"{f.name}")
        t0 = timer_start()
        if f.suffix.lower() == ".json":
            _load_lanhu_json(f, req)
        else:
            _load_lanhu_html(f, req)
        counter("  页面", len(req.pages), f"耗时 {timer_elapsed(t0):.1f}s")

    counter("文件", len(files))
    counter("页面", len(req.pages))
    return req


def _load_lanhu_json(path: Path, req: UIRequirement):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        warn("lanhu_parser", f"JSON 解析失败 {path}: {e}")
        return
    pages = data.get("pages") if isinstance(data, dict) else data
    if not isinstance(pages, list):
        return
    for pg in pages:
        req.pages.append(UIPage(
            name=pg.get("name", "未命名"),
            source=str(path),
            description=pg.get("description", ""),
            elements=pg.get("elements", []),
            flows=pg.get("flows", []),
            validation_points=pg.get("validation_points", []),
        ))


def _load_lanhu_html(path: Path, req: UIRequirement):
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    m = re.search(r"<title>(.*?)</title>", html, re.S) or re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    name = (m.group(1).strip() if m else path.stem)
    req.pages.append(UIPage(name=name, source=str(path)))
