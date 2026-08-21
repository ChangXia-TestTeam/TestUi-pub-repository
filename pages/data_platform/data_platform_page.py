"""
数据管理平台首页 - POM (Apache DolphinScheduler)
路径: pages/data_platform/data_platform_page.py
从首页点击"数据平台"卡片进入的 DolphinScheduler 数据管理平台。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class DataPlatformPage(BasePage):
    """DolphinScheduler 数据管理平台首页。"""

    # ---- 左侧导航菜单 ----
    SEL_METADATA_MGMT = "text=元数据管理"
    SEL_DATA_INTEGRATION = "text=数据集成"
    SEL_DATA_DEVELOPMENT = "text=数据开发"
    SEL_DATA_MANAGEMENT = "text=数据管理"
    SEL_DATA_SERVICE = "text=数据服务"
    SEL_DATA_GOVERNANCE = "text=数据治理"
    SEL_DATA_QUALITY = "text=数据质量"
    SEL_MONITOR_CENTER = "text=监控中心"
    SEL_OVERVIEW = "text=概览"
    SEL_SERVICE_MGMT = "text=服务管理"
    SEL_MASTER = "text=Master"
    SEL_WORKER = "text=Worker"
    SEL_DB = "text=DB"
    SEL_STATS_MGMT = "text=统计管理"
    SEL_SECURITY_CENTER = "text=安全中心"

    # ---- 主内容区 ----
    SEL_PAGE_TITLE = "text=数据管理平台"
    SEL_OVERVIEW_TITLE = "text=平台运行总览"
    SEL_TASK_INSTANCE_TOTAL = "text=任务实例总量"
    SEL_WORKFLOW_INSTANCE_TOTAL = "text=工作流实例总量"
    SEL_TASK_STATUS_CHART = "text=任务实例状态统计"
    SEL_WORKFLOW_STATUS_CHART = "text=工作流实例状态统计"

    def __init__(self, page: Page):
        super().__init__(page)

    # ---- 校验 ----
    @allure.step("校验数据管理平台首页加载完成")
    def is_page_loaded(self) -> bool:
        """校验 DolphinScheduler 首页关键元素存在。"""
        try:
            self.page.locator(self.SEL_PAGE_TITLE).first.wait_for(state="visible", timeout=10000)
            self.page.locator(self.SEL_OVERVIEW_TITLE).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    @allure.step("校验元数据管理菜单可见")
    def is_metadata_visible(self) -> bool:
        try:
            self.page.locator(self.SEL_METADATA_MGMT).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("校验监控中心菜单可见")
    def is_monitor_center_visible(self) -> bool:
        try:
            self.page.locator(self.SEL_MONITOR_CENTER).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    # ---- 操作：侧边栏导航 ----
    @allure.step("点击 元数据管理")
    def goto_metadata(self):
        self.click(self.SEL_METADATA_MGMT)
        return self

    @allure.step("点击 数据集成")
    def goto_data_integration(self):
        self.click(self.SEL_DATA_INTEGRATION)
        return self

    @allure.step("点击 数据开发")
    def goto_data_development(self):
        self.click(self.SEL_DATA_DEVELOPMENT)
        return self

    @allure.step("点击 监控中心 > 概览")
    def goto_overview(self):
        self.click(self.SEL_MONITOR_CENTER)
        self.page.wait_for_timeout(300)
        self.click(self.SEL_OVERVIEW)
        return self

    @allure.step("点击 监控中心 > 服务管理")
    def goto_service_management(self):
        self.click(self.SEL_MONITOR_CENTER)
        # 等待子菜单展开
        self.page.locator(self.SEL_SERVICE_MGMT).first.wait_for(state="visible", timeout=3000)
        self.click(self.SEL_SERVICE_MGMT)
        return self

    @allure.step("点击 统计管理")
    def goto_statistics(self):
        self.click(self.SEL_STATS_MGMT)
        # 等待子菜单展开
        self.page.locator("text=Statistics").first.wait_for(state="visible", timeout=3000)
        self.click("text=Statistics")
        return self
