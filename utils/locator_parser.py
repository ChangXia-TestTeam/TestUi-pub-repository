"""
元素定位解析器 - 从输入端(蓝湖标注/截图识别/AI 生成)产出可用的 Playwright 定位
路径: utils/locator_parser.py
约定：元素字典中 locator_hint → 真正的 Playwright locator 字符串。
本模块负责把 hint 规范化（CSS / role / text），失败时回退到 placeholder/text。
"""
from __future__ import annotations

from typing import Optional


def to_locator(elem: dict) -> str:
    """从元素字典提取/构造 Playwright 定位字符串。"""
    if not isinstance(elem, dict):
        return ""
    # 1) 已有精确定位直接用
    for key in ("locator", "selector", "css", "xpath"):
        v = elem.get(key)
        if v:
            if key == "xpath":
                return f"xpath={v}"
            return v
    # 2) role + name
    role = elem.get("role")
    name = elem.get("name") or elem.get("text")
    if role and name:
        return f"role={role}[name='{name}']"
    # 3) placeholder
    ph = elem.get("placeholder")
    if ph:
        return f"input[placeholder='{ph}']"
    # 4) text 匹配（兜底）
    if name:
        return f"text='{name}'"
    return ""


def guess_locator_by_type(name: str, type_: str) -> str:
    """按元素类型猜测定位（仅用于用例脚手架，实际运行前需替换为真实定位）。"""
    if type_ == "button":
        return f"button:has-text('{name}')"
    if type_ == "input":
        return f"input[placeholder*='{name}']"
    if type_ == "select":
        return f"select"
    if type_ == "dialog":
        return f".el-dialog:has-text('{name}')"
    if type_ == "menu":
        return f"nav >> text='{name}'"
    return f"text='{name}'"
