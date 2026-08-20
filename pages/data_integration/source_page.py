"""
数据源管理页 POM（示例 - 对应 API 框架 test_integration 模块）
路径: pages/data_integration/source_page.py
⚠️ 元素定位为占位，需根据真实页面/输入端解析结果替换。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class SourcePage(BasePage):
    """数据集成 - 数据源管理页。"""

    path = "/data-integration/source"

    SEL_TABLE_ROW = "table tr"
    SEL_SEARCH = "input[placeholder*='搜索'], input[placeholder*='名称']"
    SEL_CREATE_BTN = "button:has-text('新增'), button:has-text('新建')"
    SEL_CREATE_DIALOG = ".el-dialog:has-text('数据源')"

    @allure.step("进入数据源管理页")
    def goto_source(self):
        self.open()
        self.wait_for(self.SEL_TABLE_ROW)
        return self

    @allure.step("搜索数据源 '{keyword}'")
    def search_source(self, keyword: str):
        return self.search(self.SEL_SEARCH, keyword)

    @allure.step("打开新增数据源弹窗")
    def open_create(self):
        self.click(self.SEL_CREATE_BTN)
        self.wait_for(self.SEL_CREATE_DIALOG)
        return self

    @allure.step("查看第 {index} 行数据源详情")
    def view_detail(self, index: int = 1):
        return self.open_row_detail(self.SEL_TABLE_ROW, index)
