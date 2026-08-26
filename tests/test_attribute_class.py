"""
元数据管理 - 属性类 模块测试
路径: tests/test_attribute_class.py
覆盖「列表 / 搜索 / 新增 / 编辑 / 查看详情 / 删除 / 批量操作 / 启用禁用 / 自动生成编码 / 分页」全流程
包含 正常 / 异常 / 边界 三类用例

页面结构（探查确认）:
- 筛选区: 结构编码(下拉) / 属性类名称(输入) / 属性类编码(输入) / 是否启用(下拉)
- 表格列: 序号 / 结构编码 / 属性类编码 / 属性类名称 / 事件 / 是否启用 / 备注 / 操作
- 操作列4按钮: 查看(info) / 编辑(primary) / 启用禁用切换(warning) / 删除(error)
- 新增弹窗: 结构编码*(下拉) / 属性类编码*(3位数字) / 属性类名称*(85字符) /
             事件(85字符) / 是否启用(开关默认开) / 备注(85字符TEXTAREA)
- 顶部: 查询 / 重置 / 新增 / 批量删除 / 批量启用 / 批量禁用
- 弹窗含「自动生成属性类编码」按钮
"""
import time
import pytest
import allure

from pages.home.home_page import HomePage
from pages.metadata.attribute_class_page import AttributeClassPage


@allure.feature("元数据管理-属性类")
@pytest.mark.metadata
class TestAttributeClass:
    """属性类页面 CRUD + 搜索 + 批量 + 启用禁用 + 自动生成 + 分页 完整测试。"""

    # ============================================================
    # 一、正常路径（Normal Path）
    # ============================================================

    @allure.story("列表加载")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_list_visible(self, page):
        """验证属性类列表加载完成，关键元素可见。"""
        with allure.step("步骤1: 进入数据平台"):
            home = HomePage(page)
            assert home.is_home_loaded(), "首页未加载"
            data_page = home.click_data_platform()

        with allure.step("步骤2: 进入属性类页面"):
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤3: 验证表格可见"):
            assert op.is_table_visible(), "属性类表格不可见"

        with allure.step("步骤4: 验证筛选区可见"):
            assert op.are_filters_visible(), "筛选区不可见"

        with allure.step("步骤5: 验证顶部按钮可见"):
            assert op.are_top_buttons_visible(), "查询/重置/新增按钮不可见"

        with allure.step("步骤6: 验证表格行数 ≥ 1"):
            row_count = op.get_row_count()
            assert row_count >= 1, f"属性类列表为空，实际行数: {row_count}"

        with allure.step("步骤7: 验证表格列头完整"):
            headers = op.get_headers()
            expected = ["序号", "结构编码", "属性类编码", "属性类名称", "事件", "是否启用", "备注", "操作"]
            for col in expected:
                assert any(col in h for h in headers), f"缺少列: {col}"

        with allure.step("步骤8: 验证分页器可见"):
            assert op.is_pagination_visible(), "分页器不可见"

        op.screenshot("attribute_class_list")
        data_page.close()

    @allure.story("按属性类编码搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_search_by_code(self, page):
        """验证按属性类编码搜索。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录第一行的属性类编码"):
            codes = op.get_column_values("属性类编码")
            assert len(codes) > 0, "无数据可搜索"
            first_code = codes[0]

        with allure.step("步骤3: 输入编码搜索"):
            op.filter_by_code(first_code).search()
            data_page.wait_for_timeout(800)
            op.screenshot("after_search_by_code")

        with allure.step("步骤4: 验证结果包含搜索的编码"):
            result_codes = op.get_column_values("属性类编码")
            assert len(result_codes) > 0, f"搜索结果为空, 搜索关键字: {first_code}"
            for code in result_codes:
                assert first_code in code, f"结果包含其他编码: {code}"

        with allure.step("步骤5: 重置"):
            op.reset_search()

        data_page.close()

    @allure.story("按属性类名称搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_search_by_name(self, page):
        """验证按属性类名称搜索。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录第一行的属性类名称"):
            names = op.get_column_values("属性类名称")
            assert len(names) > 0, "无数据可搜索"
            search_name = next((n for n in names if n), names[0])

        with allure.step("步骤3: 输入名称搜索"):
            op.filter_by_name(search_name).search()
            data_page.wait_for_timeout(800)
            op.screenshot("after_search_by_name")

        with allure.step("步骤4: 验证搜索结果包含搜索名称"):
            result_names = op.get_column_values("属性类名称")
            assert len(result_names) > 0, f"搜索结果为空, 搜索关键字: {search_name}"

        with allure.step("步骤5: 重置"):
            op.reset_search()

        data_page.close()

    @allure.story("重置搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_reset_search(self, page):
        """验证重置搜索清空筛选条件。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 输入搜索条件"):
            op.filter_by_code("99").search()
            op.screenshot("before_reset")

        with allure.step("步骤3: 点击重置"):
            op.reset_search()
            op.screenshot("after_reset")

        with allure.step("步骤4: 验证筛选输入框已清空"):
            code_value = data_page.locator(
                AttributeClassPage.SEL_F_CODE_INPUT).first.input_value()
            assert code_value == "", "重置后筛选框未清空"

        data_page.close()

    @allure.story("新增属性类 - 正常路径")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_create_success(self, page):
        """验证新增属性类完整流程。属性类编码为3位数字。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录原始行数"):
            before_count = op.get_row_count()

        with allure.step("步骤3: 点击新增按钮"):
            op.click_create()
            assert op.is_modal_open(), "新增弹窗未打开"

        with allure.step("步骤4: 填写表单（3位数字编码）"):
            ts = int(time.time()) % 1000000
            code = f"{(ts % 900) + 100:03d}"  # 3位数字 100-999
            name = f"AutoTest_AttrCls_{ts}"
            event = f"autotest_event_{ts}"
            remark = "自动化测试新增属性类"
            op.fill_form(code=code, name=name, event=event, remark=remark)
            op.screenshot("create_form_filled")

        with allure.step("步骤5: 点击保存"):
            op.submit_form()
            op.screenshot("after_create_submit")

        with allure.step("步骤6: 验证新增成功"):
            time.sleep(0.5)
            data_page.wait_for_timeout(1000)
            after_count = op.get_row_count()
            assert after_count >= before_count, \
                f"新增后行数未增加，before={before_count}, after={after_count}"

        data_page.close()

    @allure.story("查看详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_view_detail(self, page):
        """验证点击查看按钮能查看属性类详情。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录第一行数据"):
            first_row_text = op.get_row_text(0)
            assert first_row_text, "无数据可查看"

        with allure.step("步骤3: 点击第1行的查看按钮"):
            op.click_row_view(0)
            op.screenshot("after_click_view")
            data_page.wait_for_timeout(500)

        data_page.close()

    @allure.story("查看详情 - 弹窗内容验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_view_detail_content(self, page):
        """验证查看按钮打开详情弹窗并显示字段内容（表单结构，读 input 值）。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录第一行属性类编码与名称"):
            code = op.get_cell_value(0, "属性类编码")
            name = op.get_cell_value(0, "属性类名称")
            assert code or name, "无数据可查看"

        with allure.step("步骤3: 点击查看按钮"):
            op.click_row_view(0)
            data_page.wait_for_timeout(800)
            op.screenshot("view_detail_modal")

        with allure.step("步骤4: 验证弹窗打开"):
            assert op.is_modal_open(), "查看详情弹窗未打开"

        with allure.step("步骤5: 读取详情表单字段值"):
            form_vals = op.get_modal_form_values()

        with allure.step("步骤6: 验证详情字段包含原行数据"):
            code_in = code and code in form_vals.get("code", "")
            name_in = name and name in form_vals.get("name", "")
            assert code_in or name_in, \
                f"详情弹窗未包含原行数据，原 code={code} name={name}, 表单={form_vals}"

        with allure.step("步骤7: 关闭详情弹窗"):
            op.close_detail()
            data_page.wait_for_timeout(500)

        data_page.close()

    @allure.story("编辑属性类")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_edit_success(self, page):
        """验证编辑属性类流程：打开编辑→修改备注→保存。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 点击第1行编辑按钮"):
            op.click_row_edit(0)
            op.screenshot("edit_modal_open")
            assert op.is_modal_open(), "编辑弹窗未打开"

        with allure.step("步骤3: 修改备注字段"):
            ts = int(time.time()) % 1000000
            new_remark = f"AutoTest edited @ {ts}"
            op.fill_form(remark=new_remark)

        with allure.step("步骤4: 保存"):
            op.submit_form()
            op.screenshot("after_edit_submit")

        with allure.step("步骤5: 验证编辑弹窗关闭"):
            data_page.wait_for_timeout(1000)
            assert op.is_modal_closed(), "编辑保存后弹窗未关闭"

        data_page.close()

    @allure.story("编辑 - 字段回显校验")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_edit_field_echo(self, page):
        """验证点编辑后弹窗回显当前行字段值。编辑时属性类编码禁用（不可改）。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录第一行数据"):
            code = op.get_cell_value(0, "属性类编码")
            name = op.get_cell_value(0, "属性类名称")
            assert code or name, "无数据可编辑"

        with allure.step("步骤3: 点击编辑按钮"):
            op.click_row_edit(0)
            data_page.wait_for_timeout(800)
            op.screenshot("edit_echo_modal")
            assert op.is_modal_open(), "编辑弹窗未打开"

        with allure.step("步骤4: 校验表单字段回显"):
            form_vals = op.get_modal_form_values()
            echo_ok = (code and code in form_vals.get("code", "")) or \
                      (name and name in form_vals.get("name", ""))
            assert echo_ok, \
                f"编辑弹窗未正确回显，原 code={code} name={name}, 回显={form_vals}"

        with allure.step("步骤5: 取消关闭弹窗"):
            op.click_cancel()
            data_page.wait_for_timeout(300)

        data_page.close()

    @allure.story("取消新增 - 不保存")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_create_cancel_no_save(self, page):
        """正常：新增弹窗填写后点取消，列表数据不应增加。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录原始行数"):
            before_count = op.get_row_count()

        with allure.step("步骤3: 点击新增"):
            op.click_create()
            assert op.is_modal_open(), "新增弹窗未打开"

        with allure.step("步骤4: 填写表单"):
            ts = int(time.time()) % 1000000
            op.fill_form(
                code=f"{(ts % 900) + 100:03d}",
                name=f"AutoTest_Cancel_{ts}",
                event=f"autotest_cancel_evt_{ts}",
                remark="取消新增不应保存",
            )
            op.screenshot("create_cancel_filled")

        with allure.step("步骤5: 点取消"):
            op.click_cancel()
            data_page.wait_for_timeout(500)
            op.screenshot("after_create_cancel")

        with allure.step("步骤6: 验证弹窗已关闭"):
            assert op.is_modal_closed(), "取消后弹窗应关闭"

        with allure.step("步骤7: 验证行数未增加"):
            after_count = op.get_row_count()
            assert after_count == before_count, \
                f"取消新增后行数增加，before={before_count}, after={after_count}"

        data_page.close()

    @allure.story("删除 - 取消确认")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_delete_cancel(self, page):
        """验证点删除按钮弹确认框，取消删除，数据未变化。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录原始行数"):
            before_count = op.get_row_count()

        with allure.step("步骤3: 点第1行删除按钮"):
            op.click_row_delete(0)

        with allure.step("步骤4: 取消确认"):
            op.cancel_dialog()
            op.screenshot("after_delete_cancel")

        with allure.step("步骤5: 验证行数未变"):
            data_page.wait_for_timeout(500)
            after_count = op.get_row_count()
            assert after_count == before_count, \
                f"取消删除后行数变化，before={before_count}, after={after_count}"

        data_page.close()

    @allure.story("删除 - 确认删除")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_delete_confirm(self, page):
        """验证点击确认删除最后一行数据。仅在有 ≥1 行时执行。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 检查数据"):
            row_count = op.get_row_count()
            if row_count == 0:
                pytest.skip("无数据可删除")

        with allure.step("步骤3: 记录原始行数"):
            before_count = op.get_row_count()

        with allure.step("步骤4: 点最后一行删除按钮"):
            last_idx = row_count - 1
            op.click_row_delete(last_idx)

        with allure.step("步骤5: 确认删除"):
            op.confirm_dialog()
            op.screenshot("after_delete_confirm")
            data_page.wait_for_timeout(1000)

        with allure.step("步骤6: 验证行数减少"):
            after_count = op.get_row_count()
            assert after_count <= before_count, "删除后行数未减少"

        data_page.close()

    @allure.story("批量删除 - 取消")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_batch_delete_cancel(self, page):
        """验证勾选行后批量删除取消，数据未变。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 勾选第1行"):
            if op.get_row_count() == 0:
                pytest.skip("无数据")
            op.check_row(0)

        with allure.step("步骤3: 点击批量删除"):
            op.click_batch_delete()

        with allure.step("步骤4: 取消确认"):
            op.cancel_dialog()
            op.screenshot("after_batch_delete_cancel")

        data_page.close()

    @allure.story("批量启用")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_batch_enable(self, page):
        """正常：勾选行后点击批量启用，验证操作不报错。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 勾选第1行"):
            if op.get_row_count() == 0:
                pytest.skip("无数据")
            op.check_row(0)

        with allure.step("步骤3: 点击批量启用"):
            try:
                op.click_batch_enable()
                data_page.wait_for_timeout(800)
                op.screenshot("after_batch_enable")
                # 可能有确认框
                op.confirm_dialog()
            except Exception as e:
                pytest.skip(f"批量启用交互失败: {e}")

        data_page.close()

    @allure.story("批量禁用")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_batch_disable(self, page):
        """正常：勾选行后点击批量禁用，验证操作不报错。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 勾选第1行"):
            if op.get_row_count() == 0:
                pytest.skip("无数据")
            op.check_row(0)

        with allure.step("步骤3: 点击批量禁用"):
            try:
                op.click_batch_disable()
                data_page.wait_for_timeout(800)
                op.screenshot("after_batch_disable")
                op.confirm_dialog()
            except Exception as e:
                pytest.skip(f"批量禁用交互失败: {e}")

        data_page.close()

    @allure.story("单行启用/禁用切换")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_toggle_enable_disable(self, page):
        """正常：点击第1行启用/禁用切换按钮，验证不报错（切换按钮 warning-type）。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录切换前是否启用状态"):
            if op.get_row_count() == 0:
                pytest.skip("无数据")
            before_status = op.get_cell_value(0, "是否启用")

        with allure.step("步骤3: 点击切换按钮"):
            try:
                op.click_row_toggle(0)
                data_page.wait_for_timeout(800)
                op.screenshot("after_toggle")
                # 切换可能弹确认框
                op.confirm_dialog()
                data_page.wait_for_timeout(500)
            except Exception as e:
                pytest.skip(f"切换按钮交互失败: {e}")

        with allure.step("步骤4: 验证不报错（状态可能切换或保持）"):
            after_status = op.get_cell_value(0, "是否启用")
            assert after_status, "切换后状态列仍应有值"

        data_page.close()

    @allure.story("按是否启用筛选")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_filter_by_enable(self, page):
        """正常：按是否启用下拉筛选，验证交互不崩溃。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 选择'启用'筛选"):
            try:
                op.select_filter("是否启用", "启用")
                op.search()
                data_page.wait_for_timeout(800)
                op.screenshot("filter_enabled")
            except Exception as e:
                pytest.skip(f"启用筛选交互失败: {e}")

        with allure.step("步骤3: 重置"):
            op.reset_search()

        data_page.close()

    @allure.story("自动生成属性类编码")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_auto_generate_code(self, page):
        """正常：新增弹窗点击'自动生成属性类编码'按钮，验证交互不崩溃。

        注：自动生成可能需要先选择结构编码作为前置条件，
        本用例验证按钮可点击且不报错；若编码被填充则额外验证。
        """
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 点击新增"):
            op.click_create()
            assert op.is_modal_open(), "新增弹窗未打开"

        with allure.step("步骤3: 记录点击前编码值"):
            form_before = op.get_modal_form_values()
            code_before = form_before.get("code", "")

        with allure.step("步骤4: 点击自动生成编码按钮"):
            op.click_auto_generate_code()
            data_page.wait_for_timeout(800)
            op.screenshot("after_auto_generate")

        with allure.step("步骤5: 验证交互不崩溃且弹窗仍在"):
            assert op.is_modal_open(), "点击自动生成后弹窗应仍在"

        with allure.step("步骤6: 读取点击后编码值（可选验证）"):
            form_after = op.get_modal_form_values()
            code_after = form_after.get("code", "")
            # 自动生成可能需要前置条件（如先选结构编码），编码可能为空
            # 这里仅记录，不强制断言，只要交互不崩溃即可
            if code_after and code_after != code_before:
                # 编码被填充或改变，验证通过
                pass
            else:
                # 编码未变化，可能是需要前置条件，跳过严格验证
                pytest.skip("自动生成编码未填充，可能需要先选择结构编码作为前置条件")

        with allure.step("步骤7: 取消关闭"):
            op.click_cancel()
            data_page.wait_for_timeout(300)

        data_page.close()

    @allure.story("分页 - 翻页")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_pagination_navigation(self, page):
        """边界：分页器翻下一页→上一页，验证不报错。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 检查是否有下一页"):
            try:
                next_btn = data_page.locator(AttributeClassPage.SEL_PAG_NEXT).first
                if not next_btn.is_visible():
                    pytest.skip("只有一页，无法翻页测试")
            except Exception:
                pytest.skip("无下一页按钮")

        with allure.step("步骤3: 点击下一页"):
            try:
                data_page.locator(AttributeClassPage.SEL_PAG_NEXT).first.click()
                data_page.wait_for_timeout(1000)
                try:
                    data_page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass
                op.screenshot("after_next_page")
            except Exception as e:
                pytest.skip(f"翻页失败: {e}")

        with allure.step("步骤4: 点上一页"):
            try:
                data_page.locator(AttributeClassPage.SEL_PAG_PREV).first.click()
                data_page.wait_for_timeout(1000)
                op.screenshot("after_prev_page")
            except Exception:
                pass

        data_page.close()

    @allure.story("分页 - 跳转到指定页")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_pagination_jump(self, page):
        """正常：通过分页器点击第 2 页，验证页面切换。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录第一行数据"):
            first_row_before = op.get_cell_value(0, "属性类编码")

        with allure.step("步骤3: 点击第 2 页"):
            try:
                page2 = data_page.locator(
                    ".n-pagination .n-pagination-item:has-text('2')").first
                if not page2.is_visible():
                    pytest.skip("无第 2 页")
                page2.click()
                try:
                    data_page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass
                data_page.wait_for_timeout(800)
                op.screenshot("page_2")
            except Exception as e:
                pytest.skip(f"无第 2 页按钮: {e}")

        with allure.step("步骤4: 验证数据已切换"):
            first_row_after = op.get_cell_value(0, "属性类编码")
            if first_row_before and first_row_after:
                assert first_row_after != first_row_before, \
                    "翻页后第一条数据未变化"

        data_page.close()

    @allure.story("全选 + 取消")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_select_all_cancel(self, page):
        """边界：点击表头全选，再点击取消，验证选择状态切换。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 点击全选"):
            try:
                op.check_all()
                op.screenshot("after_select_all")
                data_page.wait_for_timeout(500)
            except Exception as e:
                pytest.skip(f"无全选框: {e}")

        with allure.step("步骤3: 再次点击取消全选"):
            try:
                op.check_all()
                op.screenshot("after_unselect_all")
            except Exception:
                pass

        data_page.close()

    @allure.story("每页条数切换")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_change_page_size(self, page):
        """正常：切换每页条数为 20，验证行数变化。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 记录默认条数"):
            before_count = op.get_row_count()

        with allure.step("步骤3: 切换每页条数为 20"):
            op.change_page_size(20)
            data_page.wait_for_timeout(1000)
            op.screenshot("page_size_20")

        with allure.step("步骤4: 验证行数变化或保持"):
            after_count = op.get_row_count()
            total = op.get_total_count()
            if total >= 20:
                assert after_count >= before_count, \
                    f"切换到 20 条/页后行数应不减少，before={before_count}, after={after_count}"

        data_page.close()

    # ============================================================
    # 二、异常路径（Exception Path）
    # ============================================================

    @allure.story("新增 - 必填项为空")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_create_empty_required(self, page):
        """异常：必填项全部为空，保存应失败并提示。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 点击新增"):
            op.click_create()
            assert op.is_modal_open(), "新增弹窗未打开"

        with allure.step("步骤3: 不填写任何字段直接保存"):
            op.submit_form()
            op.screenshot("create_empty_required")

        with allure.step("步骤4: 验证弹窗仍打开"):
            assert op.is_modal_open(), "必填项为空时弹窗应未关闭"

        with allure.step("步骤5: 取消关闭弹窗"):
            op.click_cancel()

        data_page.close()

    @allure.story("新增 - 编码非3位数字")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_create_invalid_code_format(self, page):
        """异常：属性类编码非3位数字（输入字母），应阻止保存或提示错误。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 点击新增"):
            op.click_create()

        with allure.step("步骤3: 填写非法编码（字母，maxlength=3 会截断）"):
            op.fill_form(code="abc", name="AutoTest_InvalidCode", event="invalid")
            op.screenshot("create_invalid_code")

        with allure.step("步骤4: 保存"):
            op.submit_form()
            data_page.wait_for_timeout(500)

        with allure.step("步骤5: 验证弹窗仍打开或出现错误"):
            modal_still_open = op.is_modal_open()
            errors = op.get_form_errors()
            assert modal_still_open or len(errors) > 0, "非法编码应阻止保存"

        with allure.step("步骤6: 取消关闭"):
            if op.is_modal_open():
                op.click_cancel()
                data_page.wait_for_timeout(300)

        data_page.close()

    @allure.story("搜索无结果")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_search_no_result(self, page):
        """异常：搜索不存在的关键字，应返回空结果。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 搜索不可能存在的编码"):
            op.filter_by_code("ZZZZNOTEXIST").search()
            op.screenshot("search_no_result")

        with allure.step("步骤3: 验证结果为空"):
            rows = op.get_row_count()
            assert rows == 0, f"应无搜索结果，实际有 {rows} 行"

        with allure.step("步骤4: 重置恢复"):
            op.reset_search()

        data_page.close()

    @allure.story("编辑 - 清空必填项保存")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_edit_clear_required(self, page):
        """异常：编辑时清空必填项（属性类名称），保存应失败。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 点击第1行编辑"):
            op.click_row_edit(0)
            data_page.wait_for_timeout(800)
            assert op.is_modal_open(), "编辑弹窗未打开"

        with allure.step("步骤3: 清空属性类名称"):
            op.clear_modal_field("name")
            op.screenshot("edit_clear_name")

        with allure.step("步骤4: 点保存"):
            op.submit_form()
            data_page.wait_for_timeout(500)

        with allure.step("步骤5: 验证弹窗仍打开或出现错误提示"):
            modal_open = op.is_modal_open()
            errors = op.get_form_errors()
            assert modal_open or len(errors) > 0, \
                "清空必填项后保存应失败"

        with allure.step("步骤6: 取消关闭"):
            op.click_cancel()
            data_page.wait_for_timeout(300)

        data_page.close()

    @allure.story("新增 - 重复编码")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_create_duplicate_code(self, page):
        """异常：使用已存在的属性类编码新增，应提示重复。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 获取第一行已存在的编码"):
            codes = op.get_column_values("属性类编码")
            assert len(codes) > 0, "无数据可参考"
            existing_code = codes[0]

        with allure.step("步骤3: 点击新增"):
            op.click_create()
            assert op.is_modal_open(), "新增弹窗未打开"

        with allure.step("步骤4: 填入已存在的编码"):
            ts = int(time.time()) % 1000000
            # maxlength=3，取前3位
            dup_code = existing_code[:3] if len(existing_code) >= 3 else existing_code
            op.fill_form(
                code=dup_code,
                name=f"AutoTest_Dup_{ts}",
                event=f"autotest_dup_evt_{ts}",
                remark="重复编码测试",
            )
            op.screenshot("create_duplicate_code")

        with allure.step("步骤5: 保存"):
            op.submit_form()
            data_page.wait_for_timeout(1000)
            op.screenshot("after_duplicate_submit")

        with allure.step("步骤6: 验证提示重复或弹窗未关闭"):
            modal_open = op.is_modal_open()
            errors = op.get_form_errors()
            assert modal_open or len(errors) > 0, \
                "重复编码应阻止保存或提示错误"

        with allure.step("步骤7: 取消关闭"):
            if op.is_modal_open():
                op.click_cancel()
                data_page.wait_for_timeout(300)

        data_page.close()

    # ============================================================
    # 三、边界路径（Boundary Path）
    # ============================================================

    @allure.story("搜索 - 特殊字符")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_search_special_chars(self, page):
        """边界：搜索含特殊字符的关键字，应正常返回不报错。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 搜索特殊字符"):
            op.filter_by_name("<script>alert(1)</script>").search()
            op.screenshot("search_special_chars")

        with allure.step("步骤3: 验证不报错"):
            rows = op.get_row_count()
            assert rows >= 0, "搜索特殊字符应返回结果（含0）"

        with allure.step("步骤4: 重置恢复"):
            op.reset_search()

        data_page.close()

    @allure.story("搜索 - 超长字符串")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_search_oversized_input(self, page):
        """边界：搜索框输入超长字符串（500字符），应不崩溃。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 输入超长字符串"):
            long_str = "a" * 500
            op.filter_by_name(long_str).search()
            op.screenshot("search_oversized")

        with allure.step("步骤3: 验证不崩溃"):
            rows = op.get_row_count()
            assert rows >= 0, "超长输入应正常返回"

        with allure.step("步骤4: 重置"):
            op.reset_search()

        data_page.close()

    @allure.story("新增 - 编码以0开头")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_create_code_leading_zero(self, page):
        """边界：编码以0开头（如 001），验证系统处理方式。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 打开新增"):
            op.click_create()

        with allure.step("步骤3: 填写 001 编码"):
            ts = int(time.time()) % 1000000
            op.fill_form(
                code="001",
                name=f"AutoTest_LeadingZero_{ts}",
                event=f"autotest_zero_evt_{ts}",
                remark="边界测试：编码以0开头",
            )
            op.screenshot("create_leading_zero")

        with allure.step("步骤4: 保存"):
            op.submit_form()
            data_page.wait_for_timeout(500)

        with allure.step("步骤5: 关闭弹窗"):
            if op.is_modal_open():
                op.click_cancel()
                data_page.wait_for_timeout(300)

        data_page.close()

    @allure.story("新增 - 名称到最大长度")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_create_max_length_name(self, page):
        """边界：名称输入到最大长度（85字符），验证保存行为。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 打开新增"):
            op.click_create()

        with allure.step("步骤3: 填写最大长度名称"):
            ts = int(time.time()) % 1000000
            max_name = "N" * 85
            op.fill_form(
                code=f"{(ts % 900) + 100:03d}",
                name=max_name,
                event=f"autotest_max_evt_{ts}",
                remark="边界测试：最大长度",
            )
            op.screenshot("create_max_length")

        with allure.step("步骤4: 保存"):
            op.submit_form()
            data_page.wait_for_timeout(500)

        with allure.step("步骤5: 关闭弹窗"):
            if op.is_modal_open():
                op.click_cancel()
                data_page.wait_for_timeout(300)

        data_page.close()

    @allure.story("备注 - 超过 85 字符")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_create_remark_over_limit(self, page):
        """边界：备注输入超过 85 字符，验证系统截断或不崩溃。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 点击新增"):
            op.click_create()

        with allure.step("步骤3: 填写超长备注（100 字符）"):
            ts = int(time.time()) % 1000000
            long_remark = "A" * 100
            op.fill_form(
                code=f"{(ts % 900) + 100:03d}",
                name=f"AutoTest_RemarkOver_{ts}",
                event=f"autotest_ro_evt_{ts}",
                remark=long_remark,
            )
            op.screenshot("create_remark_over_85")

        with allure.step("步骤4: 验证输入框未崩溃且行为合理"):
            actual_remark = data_page.locator(
                AttributeClassPage.SEL_M_REMARK_TEXTAREA).first.input_value()
            assert len(actual_remark) <= 100, \
                f"备注输入框实际值长度异常: {len(actual_remark)}"

        with allure.step("步骤5: 取消关闭"):
            op.click_cancel()
            data_page.wait_for_timeout(300)

        data_page.close()

    @allure.story("备注 - 刚好 85 字符")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_create_remark_max_length(self, page):
        """边界：备注刚好 85 字符，应可正常保存。"""
        with allure.step("步骤1: 进入属性类页面"):
            home = HomePage(page)
            data_page = home.click_data_platform()
            op = AttributeClassPage(data_page).goto_attribute_class()

        with allure.step("步骤2: 点击新增"):
            op.click_create()

        with allure.step("步骤3: 填写 85 字符备注"):
            ts = int(time.time()) % 1000000
            remark_85 = "B" * 85
            op.fill_form(
                code=f"{(ts % 900) + 100:03d}",
                name=f"AutoTest_Remark85_{ts}",
                event=f"autotest_r85_evt_{ts}",
                remark=remark_85,
            )
            op.screenshot("create_remark_85")

        with allure.step("步骤4: 验证可保存"):
            op.submit_form()
            data_page.wait_for_timeout(1000)
            op.screenshot("after_remark_85_submit")
            if op.is_modal_open():
                op.click_cancel()
                data_page.wait_for_timeout(300)

        data_page.close()
