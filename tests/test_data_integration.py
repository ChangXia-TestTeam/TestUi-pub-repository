"""
数据集成模块 UI 测试示例 - POM + Pytest + Allure
路径: tests/test_data_integration.py
对应 API 框架 test_integration.py，展示「列表→搜索→详情→新增」UI 全流程。
"""
import pytest
import allure

from pages.data_integration.source_page import SourcePage


@allure.feature("数据集成")
class TestDataIntegration:
    """数据集成 - 数据源管理 UI 测试。"""

    @allure.story("数据源列表")
    @pytest.mark.P0
    def test_source_list_visible(self, page):
        sp = SourcePage(page).goto_source()
        page.wait_for("table")
        rows = page.locator(SourcePage.SEL_TABLE_ROW).count()
        assert rows >= 1, "数据源列表为空"
        sp.screenshot("source_list")

    @allure.story("数据源搜索")
    @pytest.mark.P1
    def test_source_search(self, page):
        sp = SourcePage(page).goto_source()
        sp.search_source("test")
        page.wait_for_load_state("networkidle")
        sp.screenshot("source_search")

    @allure.story("数据源详情")
    @pytest.mark.P1
    def test_source_detail(self, page):
        sp = SourcePage(page).goto_source()
        sp.view_detail(index=1)
        page.wait_for_load_state("networkidle")
        sp.screenshot("source_detail")

    @allure.story("新增数据源")
    @pytest.mark.P0
    def test_source_create_open(self, page):
        sp = SourcePage(page).goto_source()
        sp.open_create()
        assert page.locator(SourcePage.SEL_CREATE_DIALOG).is_visible()
        sp.screenshot("source_create_open")
