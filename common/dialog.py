"""
通用对话框/弹窗组件 - 公共组件（与 pages/ 同级，不放在 pages 下）
路径: common/dialog.py
负责确认弹窗、Toast、Message 提示的统一处理。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class Dialog(BasePage):
    """通用 Element/Antd 对话框与提示。"""

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("确认对话框")
    def confirm(self):
        self.click(".el-dialog__footer .el-button--primary, .ant-modal-footer .ant-btn-primary")
        self.wait_for(state="networkidle")
        return self

    @allure.step("取消对话框")
    def cancel(self):
        self.click(".el-dialog__footer .el-button--default, .ant-modal-footer .ant-btn-default")
        return self

    @allure.step("关闭对话框")
    def close(self):
        self.click(".el-dialog__headerbtn, .ant-modal-close")
        return self

    @allure.step("读取 Toast/Message 提示")
    def get_message(self) -> str:
        loc = self.page.locator(".el-message__content, .ant-message-notice-content")
        loc.first.wait_for(state="visible", timeout=5000)
        return loc.first.inner_text()
