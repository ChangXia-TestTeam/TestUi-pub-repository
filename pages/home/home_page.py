"""
首页 - POM
路径: pages/home/home_page.py
登录成功后进入的系统首页，包含各平台入口卡片。
注意：点击卡片可能会在新标签页中打开。
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class HomePage(BasePage):
    """系统首页 - 可再生能源一体化调控软件。"""

    # ---- 元素定位 ----
    # 使能平台卡片
    SEL_DATA_PLATFORM = "text=数据平台"
    SEL_MODEL_PLATFORM = "text=模型平台"
    SEL_SCENE_BUILDER = "text=场景构建"
    SEL_APP_BUILDER = "text=应用构建"

    # 应用平台卡片
    SEL_WEATHER_FORECAST = "text=气象预报"
    SEL_POWER_PREDICTION = "text=功率预测"
    SEL_HYDRO_FORECAST = "text=水文预报"
    SEL_STATION_DISPATCH = "text=站群调度"

    # 首页通用
    SEL_ENABLE_PLATFORM = "text=使能平台"
    SEL_APP_PLATFORM = "text=应用平台"

    def __init__(self, page: Page):
        super().__init__(page)

    # ---- 操作 ----
    @allure.step("点击 数据平台（新标签页打开）")
    def click_data_platform(self) -> Page:
        """点击首页'使能平台'下的'数据平台'卡片。
        返回：新打开的标签页 Page 对象（因为点击会在新窗口打开）。
        """
        # 先确保使能平台区域可见
        self.page.locator(self.SEL_ENABLE_PLATFORM).scroll_into_view_if_needed()

        # 记录点击前的页面列表
        context = self.page.context
        before_pages = list(context.pages)
        print(f"[HomePage] 点击前页面数: {len(before_pages)}")

        # 点击卡片
        self.page.locator(self.SEL_DATA_PLATFORM).first.click()
        print(f"[HomePage] 已点击数据平台卡片")

        # 等待新标签页出现（最多 10s）
        new_page = None
        for i in range(20):
            import time as _t
            _t.sleep(0.5)
            current_pages = list(context.pages)
            for p in current_pages:
                if p not in before_pages:
                    new_page = p
                    print(f"[HomePage] 发现新页面: url={p.url}")
                    break
            if new_page:
                break
            print(f"[HomePage] 等待新页面... ({i+1}/20), 当前页面数: {len(current_pages)}")

        if new_page is None:
            # 兜底：检查是否只有一个页面（可能在同标签页跳转）
            if len(context.pages) == 1:
                new_page = context.pages[0]
                print(f"[HomePage] 未检测到新标签页，使用当前页面: {new_page.url}")
            else:
                raise RuntimeError("点击数据平台后未检测到新标签页打开")

        new_page.wait_for_load_state("networkidle")
        new_page.wait_for_timeout(1500)
        print(f"[HomePage] 新页面加载完成: url={new_page.url}, title={new_page.title()}")
        return new_page

    @allure.step("点击 模型平台")
    def click_model_platform(self) -> Page:
        return self._click_platform_card(self.SEL_MODEL_PLATFORM)

    @allure.step("点击 场景构建")
    def click_scene_builder(self) -> Page:
        return self._click_platform_card(self.SEL_SCENE_BUILDER)

    @allure.step("点击 应用构建")
    def click_app_builder(self) -> Page:
        return self._click_platform_card(self.SEL_APP_BUILDER)

    def _click_platform_card(self, selector: str) -> Page:
        """通用：点击使能平台卡片，返回新标签页 Page。"""
        self.page.locator(self.SEL_ENABLE_PLATFORM).scroll_into_view_if_needed()
        context = self.page.context
        before_pages = list(context.pages)
        self.page.locator(selector).first.click()

        new_page = None
        for _ in range(20):
            import time as _t
            _t.sleep(0.5)
            for p in context.pages:
                if p not in before_pages:
                    new_page = p
                    break
            if new_page:
                break
        if new_page is None:
            raise RuntimeError(f"点击 {selector} 后未检测到新标签页打开")
        new_page.wait_for_load_state("networkidle")
        new_page.wait_for_timeout(1500)
        return new_page

    # ---- 校验 ----
    @allure.step("校验首页加载完成")
    def is_home_loaded(self) -> bool:
        """校验首页关键元素存在。"""
        try:
            self.page.locator(self.SEL_ENABLE_PLATFORM).wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    @allure.step("校验数据平台入口可见")
    def is_data_platform_visible(self) -> bool:
        try:
            el = self.page.locator(self.SEL_DATA_PLATFORM).first
            el.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False
