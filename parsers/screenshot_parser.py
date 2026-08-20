"""
原型截图解析 - 输入端 C
路径: parsers/screenshot_parser.py
每张截图视为一个页面，元素定位需 AI 视觉识别补充（见 ai/generators/locator_gen.py）。
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from utils import config
from utils.pipeline_logger import progress, counter, timer_start, timer_elapsed
from parsers.requirement_model import UIRequirement, UIPage


def parse_screenshots(path: Optional[str] = None) -> UIRequirement:
    inp = config.input_config()
    ss_dir = config.ROOT_DIR / (path or inp.get("screenshot_dir", "UI_input_files/screenshots"))
    req = UIRequirement(project=config.project_name(), input_mode="screenshot")
    if not ss_dir.exists():
        print(f"   ⚠️  截图目录不存在: {ss_dir}")
        return req
    files = [f for f in sorted(ss_dir.iterdir()) if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    if not files:
        print(f"   ⚠️  截图目录为空: {ss_dir}")
        return req

    print(f"   发现 {len(files)} 张截图")
    total = len(files)
    t0 = timer_start()
    for i, f in enumerate(files, 1):
        progress(i, total, "截图", f"{f.name} ({f.stat().st_size/1024:.1f}KB)")
        req.pages.append(UIPage(
            name=f.stem,
            source=str(f),
            description=f"原型截图：{f.name}（元素定位需 AI 识别截图后补充）",
        ))
    counter("截图", len(files), f"耗时 {timer_elapsed(t0):.1f}s")
    counter("页面", len(req.pages))
    return req
