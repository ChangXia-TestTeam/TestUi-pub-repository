"""
UI 断言封装 - 仿 API 框架 utils/assertions.py
路径: utils/assertions.py
集中维护 UI 层断言，失败时自动截图并附带 Allure 附件。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page, expect


def _attach_screenshot(page: Page, name: str):
    try:
        png = page.screenshot(full_page=True)
        allure.attach(png, name=name, attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        print(f"[assertions] 截图失败: {e}")


def assert_visible(page: Page, locator, timeout: int = 10, msg: str = ""):
    """断言元素可见。"""
    loc = page.locator(locator) if isinstance(locator, str) else locator
    try:
        expect(loc).to_be_visible(timeout=timeout * 1000)
    except Exception as e:
        _attach_screenshot(page, f"FAIL - {msg or 'assert_visible'}")
        raise AssertionError(f"元素不可见: {locator} | {msg} | {e}")


def assert_text(page: Page, locator, expected: str, msg: str = ""):
    """断言元素文本包含期望值。"""
    loc = page.locator(locator) if isinstance(locator, str) else locator
    try:
        expect(loc).to_have_text(expected, timeout=10000)
    except Exception as e:
        _attach_screenshot(page, f"FAIL - {msg or 'assert_text'}")
        raise AssertionError(f"文本不匹配: 期望='{expected}' | {msg} | {e}")


def assert_url_contains(page: Page, fragment: str, msg: str = ""):
    try:
        expect(page).to_have_url(f"**{fragment}**", timeout=15000)
    except Exception as e:
        _attach_screenshot(page, f"FAIL - {msg or 'assert_url'}")
        raise AssertionError(f"URL 不包含 '{fragment}' | {msg} | {e}")


def assert_title(page: Page, expected: str, msg: str = ""):
    try:
        expect(page).to_have_title(expected)
    except Exception as e:
        _attach_screenshot(page, f"FAIL - {msg or 'assert_title'}")
        raise AssertionError(f"标题不匹配: 期望='{expected}' | {msg} | {e}")
