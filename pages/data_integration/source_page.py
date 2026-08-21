"""
数据集成 - 数据源字段映射页 POM
路径: pages/data_integration/source_page.py
对应 DolphinScheduler 路由: /integration/source_mapping
从首页 → 数据平台 → 数据集成 → 数据源字段映射 进入。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class SourcePage(BasePage):
    """数据集成 - 数据源字段映射页。"""

    path = "/integration/source_mapping"

    # ---- 菜单导航 ----
    SEL_MENU_DATA_INTEGRATION = ".n-menu-item-content:has-text('数据集成')"
    SEL_MENU_SOURCE_MAPPING = ".n-menu-item-content:has-text('数据源字段映射')"

    # ---- 表格 ----
    SEL_TABLE = ".n-data-table"
    SEL_TABLE_ROW = ".n-data-table-tbody tr"
    SEL_TABLE_HEADER = ".n-data-table-th__title"

    # ---- 搜索/筛选 ----
    SEL_SEARCH_INPUT = ".n-card input[placeholder='请输入']:first-of-type"
    SEL_SEARCH_BUTTON = "button:has-text('查询')"
    SEL_RESET_BUTTON = "button:has-text('重置')"

    # ---- 操作按钮 ----
    SEL_CREATE_BTN = "button:has-text('新增')"
    SEL_BATCH_DELETE_BTN = "button:has-text('批量删除')"
    SEL_EDIT_BTN = "button:has-text('编辑')"

    # ---- 弹窗 ----
    SEL_CREATE_DIALOG = ".n-modal:has-text('新增'), .n-modal:has-text('编辑')"
    SEL_PAGINATION = ".n-pagination"

    def __init__(self, page: Page):
        super().__init__(page)

    # ---- 导航 ----
    @allure.step("从数据平台首页进入数据源字段映射页")
    def goto_source(self):
        """点击 数据集成 → 数据源字段映射 子菜单。"""
        self.page.locator(self.SEL_MENU_DATA_INTEGRATION).first.click()
        self.page.wait_for_timeout(500)
        self.page.locator(self.SEL_MENU_SOURCE_MAPPING).first.click()
        self.page.wait_for_timeout(1000)
        self.page.wait_for_load_state("networkidle", timeout=15000)
        self.wait_for(self.SEL_TABLE_ROW)
        return self

    # ---- 校验 ----
    @allure.step("校验数据源表格可见")
    def is_table_visible(self) -> bool:
        try:
            self.page.locator(self.SEL_TABLE).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    @allure.step("校验操作按钮可见")
    def are_action_buttons_visible(self) -> bool:
        try:
            self.page.locator(self.SEL_CREATE_BTN).first.wait_for(state="visible", timeout=3000)
            self.page.locator(self.SEL_BATCH_DELETE_BTN).first.wait_for(state="visible", timeout=3000)
            return True
        except Exception:
            return False

    @allure.step("校验分页器可见")
    def is_pagination_visible(self) -> bool:
        try:
            self.page.locator(self.SEL_PAGINATION).first.wait_for(state="visible", timeout=3000)
            return True
        except Exception:
            return False

    # ---- 数据提取 ----
    @allure.step("获取表格行数")
    def get_row_count(self) -> int:
        return self.page.locator(self.SEL_TABLE_ROW).count()

    @allure.step("获取表格列头")
    def get_headers(self) -> list[str]:
        headers = self.page.locator(self.SEL_TABLE_HEADER)
        return [headers.nth(i).inner_text().strip() for i in range(headers.count())]

    @allure.step("获取第 {index} 行文本")
    def get_row_text(self, index: int = 0) -> str:
        rows = self.page.locator(self.SEL_TABLE_ROW)
        if rows.count() > index:
            return rows.nth(index).inner_text()
        return ""

    # ---- 交互 ----
    @allure.step("搜索数据源 '{keyword}'")
    def search_source(self, keyword: str):
        self.page.locator(self.SEL_SEARCH_INPUT).first.fill(keyword)
        self.page.locator(self.SEL_SEARCH_BUTTON).first.click()
        self.page.wait_for_load_state("networkidle", timeout=10000)
        return self

    @allure.step("重置搜索条件")
    def reset_search(self):
        self.page.locator(self.SEL_RESET_BUTTON).first.click()
        self.page.wait_for_load_state("networkidle", timeout=10000)
        return self

    @allure.step("打开新增数据源弹窗")
    def open_create(self):
        self.page.locator(self.SEL_CREATE_BTN).first.click()
        self.page.locator(self.SEL_CREATE_DIALOG).first.wait_for(state="visible", timeout=5000)
        return self

    @allure.step("查看第 {index} 行数据源详情")
    def view_detail(self, index: int = 0):
        rows = self.page.locator(self.SEL_TABLE_ROW)
        if rows.count() > index:
            rows.nth(index).click()
            self.page.wait_for_load_state("networkidle", timeout=10000)
        return self

    @allure.step("关闭弹窗")
    def close_dialog(self):
        try:
            self.page.locator(self.SEL_CREATE_DIALOG).first.locator("button:has-text('取消'), button:has-text('关闭')").first.click()
        except Exception:
            pass
        return self
