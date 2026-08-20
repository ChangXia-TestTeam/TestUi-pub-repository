"""
输入端解析总入口 - 4 种方式统一调度
路径: parsers/__init__.py
对外暴露 parse()，按 config.input.mode 选择：prd | lanhu | screenshot | mixed
"""
from __future__ import annotations

from typing import Optional

from utils import config
from utils.pipeline_logger import progress, counter, error, timer_start, timer_elapsed
from parsers.requirement_model import UIRequirement, UIPage
from parsers.prd_parser import parse_prd
from parsers.lanhu_parser import parse_lanhu
from parsers.screenshot_parser import parse_screenshots


def parse(mode: Optional[str] = None) -> UIRequirement:
    """根据 config.input.mode 或显式 mode 选择解析方式。"""
    mode = mode or config.input_config().get("mode", "mixed")
    t0 = timer_start()
    print(f"   mode={mode}")
    try:
        if mode == "prd":
            req = parse_prd()
        elif mode == "lanhu":
            req = parse_lanhu()
        elif mode == "screenshot":
            req = parse_screenshots()
        else:
            req = parse_mixed()
        counter("解析页面", len(req.pages))
        for i, pg in enumerate(req.pages):
            progress(i + 1, max(len(req.pages), 1), f"页面[{pg.name}]",
                     f"elements={len(pg.elements)} vps={len(pg.validation_points)} source={pg.source[:60] if pg.source else '-'}")
        print(f"   ⏱ 解析耗时 {timer_elapsed(t0):.1f}s")
        return req
    except Exception as e:
        error("parsers.parse", f"解析异常: {e}", "检查 UI_input_files/ 下文件格式是否正确")
        raise


def parse_mixed() -> UIRequirement:
    """混合输入：PRD + 蓝湖 + 截图，按页面名交叉印证合并。"""
    req = UIRequirement(project=config.project_name(), input_mode="mixed")
    subs = [
        ("PRD", parse_prd),
        ("蓝湖", parse_lanhu),
        ("原型截图", parse_screenshots),
    ]
    total = len(subs)
    for i, (label, fn) in enumerate(subs, 1):
        progress(i, total, f"解析子源 [{label}]")
        try:
            sub = fn()
            counter(f"  [{label}] 页面", len(sub.pages))
            for p in sub.pages:
                _merge_page(req, p)
        except Exception as e:
            error(f"parsers.mixed/{label}", str(e))
    counter("合并后页面", len(req.pages))
    return req


def _merge_page(req: UIRequirement, p: UIPage):
    """按页面名合并同名页面（PRD 描述 + 蓝湖元素 + 截图证据）。"""
    for existing in req.pages:
        if existing.name == p.name:
            if p.description and not existing.description:
                existing.description = p.description
            existing.elements.extend(p.elements)
            existing.flows.extend(p.flows)
            existing.validation_points.extend(p.validation_points)
            if not existing.source:
                existing.source = p.source
            else:
                existing.source += f" | {p.source}"
            return
    req.pages.append(p)


__all__ = [
    "parse", "parse_prd", "parse_lanhu", "parse_screenshots", "parse_mixed",
    "UIRequirement", "UIPage",
]
