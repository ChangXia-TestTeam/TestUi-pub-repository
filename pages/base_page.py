"""
POM 基类 - Page Object Model 设计模式
路径: pages/base_page.py
封装 Playwright 通用操作（导航/点击/输入/断言/截图/等待），所有 Page 类继承本类。
内置 AI 自愈钩子：定位失败时自动调用 ai/self_healing 寻找替代定位并回填。
内置步骤截图：每个操作自动截图并附加到 Allure，生成详细可视化报告。
"""
from __future__ import annotations

import time
from typing import Any, Optional

import allure
from playwright.sync_api import Page, Locator

from utils import config, screenshot as ss_mod

# 自愈开关（读 config.ai.self_healing）
_SELF_HEAL_ENABLED = None
# 步骤截图开关（读 config.screenshot.on_step）
_STEP_SHOT_ENABLED = None


def _self_heal_enabled() -> bool:
    global _SELF_HEAL_ENABLED
    if _SELF_HEAL_ENABLED is None:
        _SELF_HEAL_ENABLED = bool(config.get("ai.self_healing", True))
    return _SELF_HEAL_ENABLED


def _step_shot_enabled() -> bool:
    global _STEP_SHOT_ENABLED
    if _STEP_SHOT_ENABLED is None:
        _STEP_SHOT_ENABLED = bool(config.screenshot_config().get("on_step", True))
    return _STEP_SHOT_ENABLED


def _auto_shot(page, label: str):
    """自动步骤截图：每个操作后截图附加到 Allure。"""
    if not _step_shot_enabled():
        return
    try:
        ss_mod.take_screenshot(page, f"step: {label}", full_page=False)
    except Exception:
        pass


class BasePage:
    """所有页面对象的基类。"""

    # 子类覆盖：页面相对路径（不含 base_url），如 "/data-integration/source"
    path: str = ""

    def __init__(self, page: Page):
        self.page = page

    # ---- 导航 ----
    def open(self, base_url: Optional[str] = None, **qs):
        """打开本页：拼接 base_url + path + query。"""
        base = (base_url or config.base_url()).rstrip("/")
        url = base + self.path
        if qs:
            from urllib.parse import urlencode
            url += "?" + urlencode(qs)
        self.page.goto(url)
        _auto_shot(self.page, f"goto({url})")
        return self

    # ---- 元素查找 ----
    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def by_role(self, role: str, **kwargs) -> Locator:
        return self.page.get_by_role(role, **kwargs)

    def by_text(self, text: str, exact: bool = False) -> Locator:
        return self.page.get_by_text(text, exact=exact)

    def by_placeholder(self, text: str) -> Locator:
        return self.page.get_by_placeholder(text)

    def by_label(self, text: str) -> Locator:
        return self.page.get_by_label(text)

    def by_test_id(self, test_id: str) -> Locator:
        return self.page.get_by_test_id(test_id)

    # ---- 操作 ----
    @allure.step("点击 {selector}")
    def click(self, selector: str, timeout: Optional[int] = None):
        to = (timeout or config.timeout_config().get("element", 10)) * 1000
        try:
            self.locator(selector).first.click(timeout=to)
        except Exception as e:
            if not _self_heal_enabled():
                raise
            healed = self._try_heal(selector, "click")
            if healed:
                allure.attach(healed, name=f"self-healed: {selector} → {healed}",
                              attachment_type=allure.attachment_type.TEXT)
                self.locator(healed).first.click(timeout=to)
            else:
                raise
        _auto_shot(self.page, f"click({selector})")
        return self

    @allure.step("输入 '{text}' 到 {selector}")
    def fill(self, selector: str, text: str, clear: bool = True):
        try:
            loc = self.locator(selector).first
            if clear:
                loc.fill("")
            loc.fill(text)
        except Exception as e:
            if not _self_heal_enabled():
                raise
            healed = self._try_heal(selector, "fill")
            if healed:
                loc = self.locator(healed).first
                if clear:
                    loc.fill("")
                loc.fill(text)
            else:
                raise
        _auto_shot(self.page, f"fill({selector})")
        return self

    # ---- AI 自愈钩子 ----
    def _try_heal(self, selector: str, action: str):
        """定位失败时调用 ai/self_healing 寻找替代定位。"""
        try:
            from ai.self_healing import heal_locator
            cls_name = type(self).__name__
            return heal_locator(self.page, cls_name, selector, action)
        except Exception as he:
            print(f"[base_page] self-healing 异常: {he}")
            return None

    @allure.step("选择 {selector} = {value}")
    def select(self, selector: str, value: str):
        self.locator(selector).first.select_option(value)
        return self

    @allure.step("勾选 {selector}")
    def check(self, selector: str):
        self.locator(selector).first.check()
        return self

    @allure.step("悬停 {selector}")
    def hover(self, selector: str):
        self.locator(selector).first.hover()
        return self

    # ---- 等待 ----
    def wait_for(self, selector: Optional[str] = None, state: str = "visible", timeout: int = 10):
        if selector:
            self.locator(selector).first.wait_for(state=state, timeout=timeout * 1000)
        else:
            self.page.wait_for_load_state(state="networkidle", timeout=timeout * 1000)
        return self

    def wait(self, seconds: float):
        self.page.wait_for_timeout(int(seconds * 1000))
        return self

    # ---- 断言 ----
    def expect_visible(self, selector: str, msg: str = ""):
        from utils.assertions import assert_visible
        assert_visible(self.page, selector, msg=msg)
        return self

    def expect_text(self, selector: str, expected: str, msg: str = ""):
        from utils.assertions import assert_text
        assert_text(self.page, selector, expected, msg=msg)
        return self

    def expect_url_contains(self, fragment: str, msg: str = ""):
        from utils.assertions import assert_url_contains
        assert_url_contains(self.page, fragment, msg=msg)
        return self

    # ---- 截图 ----
    def screenshot(self, name: str, full_page: bool = True):
        ss_mod.take_screenshot(self.page, name, full_page=full_page)
        return self

    # ---- 通用流程：列表 + 搜索 + 详情 ----
    @allure.step("查询 '{keyword}'")
    def search(self, search_selector: str, keyword: str, submit: bool = True):
        self.fill(search_selector, keyword)
        if submit:
            self.page.keyboard.press("Enter")
        self.wait_for(state="networkidle")
        return self

    @allure.step("打开第 {index} 行详情")
    def open_row_detail(self, row_selector: str = "table tr", index: int = 1, action_selector: str = "a:has-text('详情')"):
        rows = self.locator(row_selector)
        rows.nth(index).locator(action_selector).first.click()
        self.wait_for(state="networkidle")
        return self

    # ---- 通用对话框 ----
    def dialog_ok(self, dialog_selector: str = ".el-dialog__footer .el-button--primary"):
        self.click(dialog_selector)
        self.wait_for(state="networkidle")
        return self

    def dialog_cancel(self, dialog_selector: str = ".el-dialog__footer .el-button--default"):
        self.click(dialog_selector)
        return self
