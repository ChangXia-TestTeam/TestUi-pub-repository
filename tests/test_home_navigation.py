"""
首页导航测试 - 登录后点击数据平台
路径: tests/test_home_navigation.py
验证登录成功后，在首页点击"数据平台"卡片，成功进入 DolphinScheduler 数据管理平台。
侧边栏导航采用 URL 直接跳转方式，避免菜单展开/折叠状态管理问题。
"""
import pytest
import allure

from pages.home.home_page import HomePage
from pages.data_platform.data_platform_page import DataPlatformPage


@allure.feature("首页导航")
class TestHomeNavigation:
    """首页导航功能测试。"""

    @allure.story("进入数据平台")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_enter_data_platform(self, page):
        """登录后从首页点击'数据平台'卡片，验证成功进入 DolphinScheduler 数据管理平台。"""
        home = HomePage(page)

        with allure.step("步骤1：校验首页加载完成"):
            assert home.is_home_loaded(), "首页未加载完成"

        with allure.step("步骤2：校验数据平台入口可见"):
            assert home.is_data_platform_visible(), "数据平台入口不可见"
            home.screenshot("home_before_click")

        with allure.step("步骤3：点击'数据平台'卡片（新标签页打开）"):
            data_page = home.click_data_platform()

        with allure.step("步骤4：验证数据管理平台首页加载完成"):
            data_platform = DataPlatformPage(data_page)
            assert data_platform.is_page_loaded(), "数据管理平台首页未加载完成"
            data_platform.screenshot("dolphinscheduler_home")

        with allure.step("步骤5：验证元数据管理菜单可见"):
            assert data_platform.is_metadata_visible(), "元数据管理菜单不可见"

        with allure.step("步骤6：验证监控中心菜单可见"):
            assert data_platform.is_monitor_center_visible(), "监控中心菜单不可见"

        data_page.close()

    @allure.story("数据平台侧边栏导航")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_data_platform_sidebar_nav(self, page):
        """验证数据管理平台各页面可正常访问（URL 直接导航方式）。"""
        home = HomePage(page)

        with allure.step("步骤1：进入数据平台首页"):
            assert home.is_home_loaded(), "首页未加载完成"
            data_page = home.click_data_platform()
            data_platform = DataPlatformPage(data_page)
            base_ds = data_page.url.split("/ui/")[0] + "/ui"
            assert data_platform.is_page_loaded(), "数据管理平台首页未加载完成"

        with allure.step("步骤2：导航到数据集成页面"):
            data_page.goto(f"{base_ds}/integration/schedule")
            data_page.wait_for_load_state("networkidle")
            data_page.wait_for_timeout(1000)
            data_platform.screenshot("data_integration_page")

        with allure.step("步骤3：导航到监控中心 > 服务管理"):
            data_page.goto(f"{base_ds}/monitor/service")
            data_page.wait_for_load_state("networkidle")
            data_page.wait_for_timeout(1000)
            data_platform.screenshot("service_management_page")

        with allure.step("步骤4：导航到统计管理"):
            data_page.goto(f"{base_ds}/statistics/list")
            data_page.wait_for_load_state("networkidle")
            data_page.wait_for_timeout(1000)
            data_platform.screenshot("statistics_page")

        with allure.step("步骤5：返回首页"):
            data_page.goto(f"{base_ds}/monitor/home")
            data_page.wait_for_load_state("networkidle")
            data_page.wait_for_timeout(1000)
            assert data_platform.is_page_loaded(), "返回首页失败"

        data_page.close()
