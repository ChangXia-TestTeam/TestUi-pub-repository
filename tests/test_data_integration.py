"""
数据集成模块 UI 测试 - POM + Pytest + Allure
路径: tests/test_data_integration.py
登录 → 数据平台 → 数据集成 → 数据源字段映射页 → 列表/搜索/详情/新增
"""
import pytest
import allure

from pages.home.home_page import HomePage
from pages.data_integration.source_page import SourcePage


@allure.feature("数据集成")
@pytest.mark.P1
class TestDataIntegration:
    """数据集成 - 数据源字段映射 UI 测试。"""

    @allure.story("数据源列表")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_source_list_visible(self, page):
        """验证数据源字段映射表格可见且至少有 1 行数据。"""
        with allure.step("步骤1：登录并进入数据平台"):
            home = HomePage(page)
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()

        with allure.step("步骤2：进入数据源字段映射页"):
            sp = SourcePage(data_page).goto_source()

        with allure.step("步骤3：验证表格可见"):
            assert sp.is_table_visible(), "数据源表格不可见"

        with allure.step("步骤4：验证表格行数 ≥ 1"):
            row_count = sp.get_row_count()
            assert row_count >= 1, f"数据源列表为空，实际行数: {row_count}"

        with allure.step("步骤5：验证操作按钮可见"):
            assert sp.are_action_buttons_visible(), "新增/批量删除按钮不可见"

        with allure.step("步骤6：验证分页器可见"):
            assert sp.is_pagination_visible(), "分页器不可见"

        sp.screenshot("source_list")
        data_page.close()

    @allure.story("数据源搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_source_search(self, page):
        """验证搜索功能可用。"""
        with allure.step("步骤1：进入数据源字段映射页"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            sp = SourcePage(data_page).goto_source()

        with allure.step("步骤2：输入关键字搜索"):
            sp.search_source("test")
            sp.screenshot("source_search_result")

        with allure.step("步骤3：重置搜索"):
            sp.reset_search()
            sp.screenshot("source_after_reset")

        data_page.close()

    @allure.story("数据源详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_source_detail(self, page):
        """验证点击表格行能查看详情。"""
        with allure.step("步骤1：进入数据源字段映射页"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            sp = SourcePage(data_page).goto_source()

        with allure.step("步骤2：点击第 1 行查看详情"):
            sp.view_detail(index=0)
            sp.screenshot("source_detail")

        data_page.close()

    @allure.story("新增数据源弹窗")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_source_create_open(self, page):
        """验证点击新增按钮打开弹窗。"""
        with allure.step("步骤1：进入数据源字段映射页"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            sp = SourcePage(data_page).goto_source()

        with allure.step("步骤2：点击新增按钮"):
            sp.open_create()

        with allure.step("步骤3：验证弹窗已打开"):
            dialog_visible = data_page.locator(SourcePage.SEL_CREATE_DIALOG).is_visible()
            assert dialog_visible, "新增数据源弹窗未打开"
            sp.screenshot("source_create_open")
            sp.close_dialog()

        data_page.close()
