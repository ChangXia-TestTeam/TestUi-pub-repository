"""
登录页 POM
路径: pages/login/login_page.py
⚠️ 元素定位为占位，需根据真实项目登录页替换。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils import config


class LoginPage(BasePage):
    path = "/login"   # 与 config.auth.login_url 对应

    # ---- 元素定位（占位，按真实页面替换）----
    SEL_USERNAME = "input[placeholder*='账号'], input[name='username']"
    SEL_PASSWORD = "input[placeholder*='密码'], input[type='password']"
    SEL_SUBMIT = "button:has-text('登录'), button[type='submit']"

    @allure.step("打开登录页")
    def open_login(self):
        base = config.base_url()
        self.page.goto(base.rstrip("/") + self.path)
        self.wait_for(self.SEL_USERNAME)
        return self

    @allure.step("登录 用户={username}")
    def login(self, username: str, password: str):
        self.open_login()
        self.fill(self.SEL_USERNAME, username)
        self.fill(self.SEL_PASSWORD, password)
        self.click(self.SEL_SUBMIT)
        # 等待登录成功（URL 跳转 / 首页元素出现）
        try:
            self.page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
        except Exception:
            # 兜底：等待首页通用元素
            self.page.wait_for_load_state("networkidle")
        return self

    def is_logged_in(self) -> bool:
        return "/login" not in self.page.url
