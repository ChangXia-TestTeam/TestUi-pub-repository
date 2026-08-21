"""
监控中心 - 概览页面 POM
路径: pages/monitor/overview_page.py
DolphinScheduler 数据管理平台概览页 (/monitor/home)。
包含统计卡片、日期筛选器、数据图表、状态表格等交互元素。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class OverviewPage(BasePage):
    """监控中心 > 概览页面。"""

    path = "/monitor/home"

    # ---- 页面标识 ----
    SEL_PAGE_TITLE = "text=平台运行总览"
    SEL_PAGE_TITLE_EN = "text=Data Platform Overview"

    # ---- 标签筛选 ----
    SEL_TAG_STATUS_DIST = "text=状态分布"
    SEL_TAG_OWNER_DIST = "text=定义负责人分布"

    # ---- 统计卡片（首屏大数字）----
    SEL_STAT_TASK_TOTAL = "text=任务实例总量"
    SEL_STAT_WORKFLOW_TOTAL = "text=工作流实例总量"
    SEL_STAT_TIME_WINDOW = "text=统计时间窗"

    # ---- 主题切换按钮 ----
    SEL_THEME_BUTTON = "button"

    # ---- 卡片 1：任务实例状态统计 ----
    SEL_CARD_TASK_STATUS = "text=任务实例状态统计"
    SEL_DATE_PICKER_TASK = ".n-card:has-text('任务实例状态统计') .n-date-picker"
    SEL_TASK_TABLE = ".n-card:has-text('任务实例状态统计') .n-data-table"
    SEL_TASK_TABLE_ROWS = ".n-card:has-text('任务实例状态统计') .n-data-table-tbody tr"
    SEL_TASK_TABLE_HEADER = ".n-card:has-text('任务实例状态统计') .n-data-table-th__title"
    SEL_TASK_CHART = ".n-card:has-text('任务实例状态统计') canvas"

    # ---- 卡片 2：工作流实例状态统计 ----
    SEL_CARD_WORKFLOW_STATUS = "text=工作流实例状态统计"
    SEL_DATE_PICKER_WORKFLOW = ".n-card:has-text('工作流实例状态统计') .n-date-picker"
    SEL_WORKFLOW_TABLE = ".n-card:has-text('工作流实例状态统计') .n-data-table"
    SEL_WORKFLOW_TABLE_ROWS = ".n-card:has-text('工作流实例状态统计') .n-data-table-tbody tr"
    SEL_WORKFLOW_CHART = ".n-card:has-text('工作流实例状态统计') canvas"

    # ---- 卡片 3：工作流定义统计 ----
    SEL_CARD_WORKFLOW_DEF = "text=工作流定义统计"

    # ---- 状态表格行内文本 ----
    SEL_STATUS_SUBMIT_SUCCESS = "text=提交成功"
    SEL_STATUS_RUNNING = "text=正在运行"
    SEL_STATUS_PAUSE = "text=暂停"
    SEL_STATUS_STOP = "text=停止"
    SEL_STATUS_FAILURE = "text=失败"
    SEL_STATUS_SUCCESS = "text=成功"
    SEL_STATUS_NEED_KILL = "text=需要容错"

    def __init__(self, page: Page):
        super().__init__(page)

    # ---- 页面加载校验 ----
    @allure.step("校验概览页面加载完成")
    def is_page_loaded(self) -> bool:
        try:
            self.locator(self.SEL_PAGE_TITLE).first.wait_for(state="visible", timeout=10000)
            self.locator(self.SEL_STAT_TASK_TOTAL).first.wait_for(state="visible", timeout=5000)
            self.locator(self.SEL_CARD_TASK_STATUS).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("校验统计卡片可见")
    def are_stat_cards_visible(self) -> bool:
        try:
            self.locator(self.SEL_STAT_TASK_TOTAL).first.wait_for(state="visible", timeout=5000)
            self.locator(self.SEL_STAT_WORKFLOW_TOTAL).first.wait_for(state="visible", timeout=5000)
            self.locator(self.SEL_STAT_TIME_WINDOW).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("校验状态分布标签可见")
    def is_status_tag_visible(self) -> bool:
        try:
            self.locator(self.SEL_TAG_STATUS_DIST).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("校验任务实例状态统计卡片可见")
    def is_task_status_card_visible(self) -> bool:
        try:
            self.locator(self.SEL_CARD_TASK_STATUS).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("校验任务实例表格可见")
    def is_task_table_visible(self) -> bool:
        try:
            self.locator(self.SEL_TASK_TABLE).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("校验工作流状态统计卡片可见")
    def is_workflow_status_card_visible(self) -> bool:
        try:
            self.locator(self.SEL_CARD_WORKFLOW_STATUS).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("校验所有三张统计卡片可见")
    def are_all_cards_visible(self) -> bool:
        try:
            self.locator(self.SEL_CARD_TASK_STATUS).first.wait_for(state="visible", timeout=5000)
            self.locator(self.SEL_CARD_WORKFLOW_STATUS).first.wait_for(state="visible", timeout=5000)
            self.locator(self.SEL_CARD_WORKFLOW_DEF).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("校验日期选择器可见")
    def are_date_pickers_visible(self) -> bool:
        try:
            card = self.locator(".n-card").filter(has_text="任务实例状态统计").first
            pickers = card.locator(".n-date-picker")
            if pickers.count() < 1:
                return False
            pickers.first.wait_for(state="visible", timeout=3000)
            return True
        except Exception:
            return False

    @allure.step("校验图表可见")
    def are_charts_visible(self) -> bool:
        try:
            task_card = self.locator(".n-card").filter(has_text="任务实例状态统计").first
            wf_card = self.locator(".n-card").filter(has_text="工作流实例状态统计").first
            task_card.locator("canvas").first.wait_for(state="visible", timeout=5000)
            wf_card.locator("canvas").first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    # ---- 交互：点击标签筛选 ----
    @allure.step("点击 状态分布 标签")
    def click_status_distribution_tag(self):
        self.click(self.SEL_TAG_STATUS_DIST)
        return self

    @allure.step("点击 定义负责人分布 标签")
    def click_owner_distribution_tag(self):
        self.click(self.SEL_TAG_OWNER_DIST)
        return self

    # ---- 交互：点击日期选择器 ----
    @allure.step("点击任务实例日期选择器")
    def click_task_date_picker(self, index: int = 0):
        card = self.locator(".n-card").filter(has_text="任务实例状态统计").first
        picker = card.locator(".n-date-picker").first
        # index=0 点击开始日期输入框, index=1 点击结束日期输入框
        inputs = picker.locator("input.n-input__input-el")
        if inputs.count() > index:
            inputs.nth(index).click()
        return self

    @allure.step("点击工作流实例日期选择器")
    def click_workflow_date_picker(self, index: int = 0):
        card = self.locator(".n-card").filter(has_text="工作流实例状态统计").first
        picker = card.locator(".n-date-picker").first
        inputs = picker.locator("input.n-input__input-el")
        if inputs.count() > index:
            inputs.nth(index).click()
        return self

    # ---- 交互：点击主题切换 ----
    @allure.step("点击主题切换按钮")
    def click_theme_button(self):
        self.locator("button").first.click()
        self.wait(0.5)
        return self

    # ---- 交互：点击表格行 ----
    @allure.step("点击状态表格第 {index} 行")
    def click_task_table_row(self, index: int):
        rows = self.locator(self.SEL_TASK_TABLE_ROWS)
        if rows.count() > index:
            rows.nth(index).click()
        return self

    # ---- 数据提取 ----
    def _get_task_card(self):
        return self.locator(".n-card").filter(has_text="任务实例状态统计").first

    @allure.step("获取任务实例表格行数")
    def get_task_table_row_count(self) -> int:
        card = self._get_task_card()
        return card.locator(".n-data-table-tbody tr").count()

    @allure.step("获取任务实例表格某行文本")
    def get_task_table_row_text(self, index: int) -> str:
        card = self._get_task_card()
        rows = card.locator(".n-data-table-tbody tr")
        if rows.count() > index:
            return rows.nth(index).inner_text()
        return ""

    @allure.step("获取状态列所有文本")
    def get_all_status_texts(self) -> list[str]:
        card = self._get_task_card()
        rows = card.locator(".n-data-table-tbody tr")
        texts = []
        for i in range(rows.count()):
            try:
                cells = rows.nth(i).locator(".n-data-table-td")
                last_cell = cells.last
                texts.append(last_cell.inner_text().strip())
            except Exception:
                pass
        return texts

    # ---- 状态断言 ----
    @allure.step("断言表格包含状态 '{status}'")
    def assert_status_in_table(self, status: str):
        texts = self.get_all_status_texts()
        assert status in texts, f"表格中未找到状态: {status}，实际状态列表: {texts}"

    @allure.step("断言统计卡片有数值")
    def assert_stat_cards_have_numbers(self):
        stat_labels = [
            "任务实例总量", "工作流实例总量", "统计时间窗"
        ]
        for label in stat_labels:
            el = self.locator(f"text={label}").first
            number_el = el.locator("..").locator("div").last
            text = number_el.inner_text().strip()
            assert text, f"统计卡片 '{label}' 数值为空"

    @allure.step("断言表格列头正确")
    def assert_table_headers(self):
        card = self._get_task_card()
        headers = card.locator(".n-data-table-th__title")
        expected = ["#", "数量", "状态"]
        for i, exp in enumerate(expected):
            if headers.count() > i:
                actual = headers.nth(i).inner_text().strip()
                assert actual == exp, f"第{i}列表头应为'{exp}'，实际为'{actual}'"
