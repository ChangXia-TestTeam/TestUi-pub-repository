"""
通用导航/菜单 - 公共组件（与 pages/ 同级，不放在 pages 下）
路径: common/navigation.py
负责左侧菜单、面包屑、Tab 切换等跨页面通用行为。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class Navigation(BasePage):
    """侧边导航菜单（Element UI / Antd 通用形态）。"""

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("展开一级菜单 '{menu}'")
    def expand_menu(self, menu: str):
        # 通用：点击展开含该文本的菜单项
        self.page.locator(f".el-submenu__title:has-text('{menu}'), .ant-menu-submenu-title:has-text('{menu}')").first.click()
        return self

    @allure.step("跳转菜单 '{menu} > {submenu}'")
    def goto(self, menu: str, submenu: str):
        self.expand_menu(menu)
        self.page.locator(f"li:has-text('{submenu}')").first.click()
        self.wait_for(state="networkidle")
        return self

    @allure.step("切换 Tab '{tab}'")
    def switch_tab(self, tab: str):
        self.page.locator(f".el-tabs__item:has-text('{tab}'), .ant-tabs-tab:has-text('{tab}')").first.click()
        return self

    @allure.step("返回上一级")
    def go_back(self):
        self.page.go_back()
        self.wait_for(state="networkidle")
        return self
