"""
截图管理 - 失败自动截图 + Allure 附件
路径: utils/screenshot.py
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import allure
from playwright.sync_api import Page

from utils import config


def take_screenshot(page: Page, name: str, full_page: bool = True) -> str:
    """
    截图并保存到 reports/screenshots，同时附加到 Allure。
    返回保存路径。
    """
    ss_cfg = config.screenshot_config()
    ss_dir = config.ROOT_DIR / ss_cfg.get("dir", "reports/screenshots")
    ss_dir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d_%H%M%S")
    safe_name = name.replace(" ", "_").replace("/", "_")
    filename = f"{ts}_{safe_name}.png"
    filepath = ss_dir / filename

    try:
        page.screenshot(path=str(filepath), full_page=full_page or ss_cfg.get("full_page", True))
    except Exception as e:
        print(f"[screenshot] 截图失败: {name} | {e}")
        return ""

    # 附加到 Allure
    try:
        with open(filepath, "rb") as f:
            allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
    except Exception:
        pass

    return str(filepath)
