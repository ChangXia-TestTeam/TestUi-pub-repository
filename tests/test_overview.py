"""
监控中心 > 概览页面测试
路径: tests/test_overview.py
登录 → 进入数据平台 → 概览页面 → 依次点击不同元素并断言不同内容。
覆盖：页面加载、统计卡片、标签筛选、日期选择器、状态表格、图表可视化、主题切换。
"""
import pytest
import allure

from pages.home.home_page import HomePage
from pages.data_platform.data_platform_page import DataPlatformPage
from pages.monitor.overview_page import OverviewPage


@allure.feature("监控中心-概览")
@pytest.mark.overview
class TestOverview:
    """概览页面交互测试。"""

    @allure.story("页面加载与统计卡片")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_overview_page_load(self, page):
        """登录后进入概览页，验证页面加载完成且统计卡片可见。"""
        home = HomePage(page)

        with allure.step("步骤1：登录并进入数据平台"):
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()
            overview = OverviewPage(data_page)
            assert overview.is_page_loaded(), "概览页面未加载完成"

        with allure.step("步骤2：验证统计卡片可见"):
            assert overview.are_stat_cards_visible(), "统计卡片不可见"
            data_platform = DataPlatformPage(data_page)
            data_platform.screenshot("overview_stat_cards")

        with allure.step("步骤3：验证三张统计卡片可见"):
            assert overview.are_all_cards_visible(), "部分统计卡片不可见"
            overview.screenshot("overview_all_cards")

        with allure.step("步骤4：验证日期选择器可见"):
            assert overview.are_date_pickers_visible(), "日期选择器不可见"

        data_page.close()

    @allure.story("标签筛选交互")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_click_status_tag(self, page):
        """点击状态分布/定义负责人分布标签，验证可交互。"""
        home = HomePage(page)

        with allure.step("步骤1：进入概览页"):
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()
            overview = OverviewPage(data_page)
            assert overview.is_page_loaded(), "概览页面未加载"

        with allure.step("步骤2：验证状态分布标签可见并点击"):
            assert overview.is_status_tag_visible(), "状态分布标签不可见"
            overview.click_status_distribution_tag()
            overview.screenshot("after_click_status_tag")

        with allure.step("步骤3：点击定义负责人分布标签"):
            overview.click_owner_distribution_tag()
            overview.screenshot("after_click_owner_tag")

        data_page.close()

    @allure.story("日期选择器交互")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_click_date_picker(self, page):
        """点击任务实例/工作流实例的日期选择器，验证可打开面板。"""
        home = HomePage(page)

        with allure.step("步骤1：进入概览页"):
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()
            overview = OverviewPage(data_page)
            assert overview.is_page_loaded(), "概览页面未加载"

        with allure.step("步骤2：点击任务实例开始日期选择器"):
            overview.click_task_date_picker(0)
            overview.wait(0.5)
            overview.screenshot("task_date_picker_opened")

        with allure.step("步骤3：点击任务实例结束日期选择器"):
            overview.click_task_date_picker(1)
            overview.wait(0.5)
            overview.screenshot("task_date_picker_2_opened")

        with allure.step("步骤4：点击工作流实例日期选择器"):
            overview.click_workflow_date_picker(0)
            overview.wait(0.5)
            overview.screenshot("workflow_date_picker_opened")

        data_page.close()

    @allure.story("任务实例状态表格断言")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_task_status_table(self, page):
        """验证任务实例状态表格结构正确、状态数据完整。"""
        home = HomePage(page)

        with allure.step("步骤1：进入概览页"):
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()
            overview = OverviewPage(data_page)
            assert overview.is_page_loaded(), "概览页面未加载"

        with allure.step("步骤2：验证任务实例表格可见"):
            assert overview.is_task_table_visible(), "任务实例状态表格不可见"

        with allure.step("步骤3：验证表格列头正确"):
            overview.assert_table_headers()

        with allure.step("步骤4：验证表格行数"):
            row_count = overview.get_task_table_row_count()
            assert row_count >= 1, f"任务实例状态表格至少应有1行，实际{row_count}行"
            overview.screenshot("task_status_table")

        with allure.step("步骤5：验证关键状态存在"):
            overview.assert_status_in_table("提交成功")
            overview.assert_status_in_table("正在运行")
            overview.assert_status_in_table("成功")

        with allure.step("步骤6：验证所有状态列表"):
            statuses = overview.get_all_status_texts()
            allure.attach(
                "\n".join(f"  {i+1}. {s}" for i, s in enumerate(statuses)),
                name="状态列表",
                attachment_type=allure.attachment_type.TEXT
            )
            assert len(statuses) >= 5, f"状态列表应至少包含5种状态，实际{len(statuses)}种"

        data_page.close()

    @allure.story("图表可视化验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_charts_visible(self, page):
        """验证概览页面图表（ECharts Canvas）正确渲染。"""
        home = HomePage(page)

        with allure.step("步骤1：进入概览页"):
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()
            overview = OverviewPage(data_page)
            assert overview.is_page_loaded(), "概览页面未加载"

        with allure.step("步骤2：验证图表可见"):
            assert overview.are_charts_visible(), "ECharts 图表不可见"
            overview.screenshot("overview_charts")

        data_page.close()

    @allure.story("主题切换")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_theme_switch(self, page):
        """点击主题切换按钮，验证主题可切换。"""
        home = HomePage(page)

        with allure.step("步骤1：进入概览页"):
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()
            overview = OverviewPage(data_page)
            assert overview.is_page_loaded(), "概览页面未加载"

        with allure.step("步骤2：点击主题切换按钮"):
            overview.click_theme_button()
            overview.wait(0.5)
            overview.screenshot("after_theme_switch")

        data_page.close()

    @allure.story("工作流状态表格断言")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_workflow_status_table(self, page):
        """验证工作流实例状态统计卡片和表格。"""
        home = HomePage(page)

        with allure.step("步骤1：进入概览页"):
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()
            overview = OverviewPage(data_page)
            assert overview.is_page_loaded(), "概览页面未加载"

        with allure.step("步骤2：验证工作流状态卡片可见"):
            assert overview.is_workflow_status_card_visible(), "工作流状态统计卡片不可见"

        with allure.step("步骤3：验证统计卡片有数值"):
            overview.assert_stat_cards_have_numbers()

        with allure.step("步骤4：整体截图"):
            overview.screenshot("workflow_status_overview")

        data_page.close()
