"""
Playwright 浏览器管理 - 仿 API 框架 utils/http_client.py
路径: utils/browser.py
负责 Playwright / Browser / BrowserContext / Page 的生命周期管理。
"""
from __future__ import annotations

from typing import Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from utils import config


class BrowserManager:
    """
    统一管理 Playwright 资源：
        - 浏览器类型（chromium/firefox/webkit）
        - headless / slow_mo / viewport / locale / timezone
        - storage_state 复用登录态
        - trace / video 录制
    用法（在 conftest.py 中作为 fixture 注入）：
        mgr = BrowserManager()
        page = mgr.new_page()
        ... 测试 ...
        mgr.close()
    """

    def __init__(self, cfg: Optional[dict] = None):
        self.cfg = cfg or config.browser_config()
        self._pw = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    # ---- 资源初始化 ----
    def start(self) -> "BrowserManager":
        self._pw = sync_playwright().start()
        browser_type = self._pw[self.cfg.get("type", "chromium")]
        self._browser = browser_type.launch(
            headless=self.cfg.get("headless", True),
            slow_mo=self.cfg.get("slow_mo", 0),
        )
        self._context = self._new_context()
        self._page = self._context.new_page()
        # 默认超时
        to = config.timeout_config()
        self._page.set_default_timeout(to.get("element", 10) * 1000)
        self._page.set_default_navigation_timeout(to.get("navigation", 30) * 1000)
        return self

    def _new_context(self) -> BrowserContext:
        vp = self.cfg.get("viewport", {"width": 1920, "height": 1080})
        storage_state = config.auth_config().get("storage_state")
        ctx_kwargs = dict(
            viewport=vp,
            locale=self.cfg.get("locale", "zh-CN"),
            timezone_id=self.cfg.get("timezone", "Asia/Shanghai"),
            record_video_dir="reports/videos" if self.cfg.get("record_video") else None,
            record_video_size=vp,
        )
        # 复用登录态
        if storage_state:
            from pathlib import Path
            state_path = Path(storage_state)
            if not state_path.is_absolute():
                state_path = config.ROOT_DIR / storage_state
            if state_path.exists():
                ctx_kwargs["storage_state"] = str(state_path)
        # 移除 None 值
        ctx_kwargs = {k: v for k, v in ctx_kwargs.items() if v is not None}
        return self._browser.new_context(**ctx_kwargs)

    # ---- 页面访问 ----
    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("BrowserManager 未 start()，请先调用 start()")
        return self._page

    @property
    def context(self) -> BrowserContext:
        if self._context is None:
            raise RuntimeError("BrowserManager 未 start()")
        return self._context

    def new_page(self) -> Page:
        """新建一个 page（多标签场景）。"""
        return self._context.new_page()

    # ---- 登录态持久化 ----
    def save_auth_state(self, path: str | None = None):
        """保存当前 context 的 cookies + localStorage 到 storage_state 文件。"""
        path = path or config.auth_config().get("storage_state")
        if not path:
            return
        from pathlib import Path
        p = Path(path)
        if not p.is_absolute():
            p = config.ROOT_DIR / path
        p.parent.mkdir(parents=True, exist_ok=True)
        self._context.storage_state(path=str(p))

    # ---- 资源释放 ----
    def close(self):
        try:
            if self._page:
                self._page.close()
        except Exception:
            pass
        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._pw:
                self._pw.stop()
        except Exception:
            pass
        self._page = self._context = self._browser = self._pw = None
