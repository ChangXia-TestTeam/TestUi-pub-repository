"""
pytest fixtures - 仿 API 框架 conftest.py（自动注入 page、登录态、失败截图）
路径: tests/conftest.py
本文件提供：
    - browser_mgr: 浏览器资源（自动 start/close）
    - page: 当前页面对象（POM 入口）
    - logged_in: 自动登录 fixture（storage_state 优先 / 环境变量 / UI 登录）
    - allure 截图钩子（失败自动截图）
POM 注入：各业务 Page 类直接 import pages.xxx，new 时传入 page。
"""
from __future__ import annotations

import os
import pytest
import allure

from utils import config
from utils.browser import BrowserManager
from utils import auth


# ---- 浏览器生命周期 ----
@pytest.fixture(scope="session")
def browser_mgr_session():
    """session 级浏览器管理（多测试共用一个 context 池）。"""
    mgr = BrowserManager().start()
    yield mgr
    mgr.close()


@pytest.fixture(scope="function")
def browser_mgr(browser_mgr_session):
    """每个测试函数一个独立 context（隔离数据），复用 session 浏览器。"""
    bm = browser_mgr_session
    # 新建独立 context + page（避免测试间 cookie/localStorage 串扰）
    new_ctx = bm._browser.new_context(
        viewport=bm.cfg.get("viewport", {"width": 1920, "height": 1080}),
        locale=bm.cfg.get("locale", "zh-CN"),
        timezone_id=bm.cfg.get("timezone", "Asia/Shanghai"),
    )
    page = new_ctx.new_page()
    to = config.timeout_config()
    page.set_default_timeout(to.get("element", 10) * 1000)
    page.set_default_navigation_timeout(to.get("navigation", 30) * 1000)
    # 临时替换 mgr.page 供后续 fixture 使用
    bm._page = page
    bm._context = new_ctx
    yield bm
    try:
        page.close()
    except Exception:
        pass
    try:
        new_ctx.close()
    except Exception:
        pass


@pytest.fixture(scope="function")
def page(browser_mgr):
    """直接暴露 Playwright Page。"""
    return browser_mgr.page


@pytest.fixture(scope="function", autouse=True)
def logged_in(browser_mgr):
    """自动登录：storage_state > 环境变量 > UI 登录。"""
    info = auth.get_or_login(browser_mgr)
    print(f"[conftest] 登录态来源: {info.get('source')}")


@pytest.fixture(scope="function", autouse=True)
def _attach_screenshot_on_failure(browser_mgr):
    """失败自动截图（pytest_runtest_makereport 钩子方式更稳，这里用 yield 兜底）。"""
    yield
    # 具体失败截图由 hook 负责，这里仅占位保证顺序


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """失败时自动截图并附加到 Allure。"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        bm = item.funcargs.get("browser_mgr")
        if bm and bm.page:
            try:
                from utils.screenshot import take_screenshot
                take_screenshot(bm.page, f"FAIL - {item.name}")
            except Exception as e:
                print(f"[conftest] 失败截图异常: {e}")


# ---- 可选：在 Allure 里标记环境信息 ----
def pytest_sessionstart(session):
    try:
        allure.attach(
            config.base_url(),
            name="base_url",
            attachment_type=allure.attachment_type.TEXT,
        )
    except Exception:
        pass
