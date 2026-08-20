"""
UI 需求统一数据模型 - AI 驱动 UI 自动化的「输入端产物」
路径: parsers/requirement_model.py
所有输入端（PRD/蓝湖/截图）解析后都产出本结构，供 AI 生成器消费。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class UIPage:
    """一个原型页面/一个 PRD 页面段落。"""
    name: str
    source: str = ""
    description: str = ""
    elements: list[dict] = field(default_factory=list)
    flows: list[dict] = field(default_factory=list)
    validation_points: list[str] = field(default_factory=list)


@dataclass
class UIRequirement:
    """一次输入解析后的完整 UI 需求。"""
    project: str = ""
    input_mode: str = ""               # prd | lanhu | screenshot | mixed
    pages: list[UIPage] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


def guess_type(name: str) -> str:
    """根据名称猜测元素类型。"""
    n = name.lower()
    if any(k in n for k in ("按钮", "btn", "button", "提交", "保存", "删除", "查询")):
        return "button"
    if any(k in n for k in ("输入", "框", "input", "搜索", "名称")):
        return "input"
    if any(k in n for k in ("下拉", "select", "选择", "选择器")):
        return "select"
    if any(k in n for k in ("表格", "table", "列表")):
        return "table"
    if any(k in n for k in ("弹窗", "dialog", "modal")):
        return "dialog"
    if any(k in n for k in ("菜单", "nav", "导航", "tab", "标签")):
        return "menu"
    return "element"
