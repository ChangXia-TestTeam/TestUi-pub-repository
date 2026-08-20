"""
登录模块 UI 测试示例 - POM + Pytest + Allure
路径: tests/test_login.py
仿 API 框架 test_*.py 风格：用例分组、优先级标记、Allure step/feature。
"""
import pytest
import allure

from pages.login.login_page import LoginPage


@allure.feature("登录")
class TestLogin:
    """登录页 UI 测试。"""

    @allure.story("正常登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_login_success(self, page):
        login = LoginPage(page)
        from utils import config
        auth = config.auth_config()
        login.login(auth.get("username", ""), auth.get("password", ""))
        assert login.is_logged_in(), "登录后未跳转离开 /login"
        login.screenshot("login_success")

    @allure.story("错误账号")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_login_wrong_password(self, page):
        from common.dialog import Dialog
        login = LoginPage(page)
        login.open_login()
        login.fill(login.SEL_USERNAME, "wrong_user")
        login.fill(login.SEL_PASSWORD, "wrong_pass")
        login.click(login.SEL_SUBMIT)
        # 校验错误提示
        msg = Dialog(page).get_message()
        assert msg, "错误登录未出现提示"
        login.screenshot("login_wrong_password")
