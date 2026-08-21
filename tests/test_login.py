"""
登录模块 UI 测试示例 - POM + Pytest + Allure（含步骤截图）
路径: tests/test_login.py
每个操作步骤自动截图附加到 Allure 报告，生成详细可视化测试报告。
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
        """验证使用正确账号密码登录系统成功。"""
        login = LoginPage(page)
        from utils import config
        auth = config.auth_config()

        with allure.step("步骤1：打开登录页"):
            login.open_login()

        with allure.step("步骤2：输入用户名"):
            login.fill(login.SEL_USERNAME, auth.get("username", ""))

        with allure.step("步骤3：输入密码"):
            login.fill(login.SEL_PASSWORD, auth.get("password", ""))

        with allure.step("步骤4：点击登录按钮"):
            login.click(login.SEL_SUBMIT)

        with allure.step("步骤5：验证登录成功跳转"):
            assert login.is_logged_in(), "登录后未跳转离开 /login"
            login.screenshot("login_success_final")

    @allure.story("错误账号")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_login_wrong_password(self, page):
        """验证使用错误密码登录时显示错误提示。"""
        from common.dialog import Dialog
        login = LoginPage(page)

        with allure.step("步骤1：打开登录页"):
            login.open_login()

        with allure.step("步骤2：输入错误用户名"):
            login.fill(login.SEL_USERNAME, "wrong_user")

        with allure.step("步骤3：输入错误密码"):
            login.fill(login.SEL_PASSWORD, "wrong_pass")

        with allure.step("步骤4：点击登录按钮"):
            login.click(login.SEL_SUBMIT)

        with allure.step("步骤5：验证错误提示出现"):
            msg = Dialog(page).get_message()
            assert msg, "错误登录未出现提示"
            login.screenshot("login_wrong_password_final")
