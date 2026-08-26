"""
元数据管理 - 属性类 页面 POM
路径: pages/metadata/attribute_class_page.py
对应 DolphinScheduler 路由: /metadata/attribute-class
从首页 → 数据平台 → 元数据管理 → 属性类 进入。

页面结构（探查确认）:
- 筛选区: 结构编码(下拉) / 属性类名称(输入) / 属性类编码(输入) / 是否启用(下拉)
- 顶部按钮: 查询 / 重置 / 新增 / 批量删除(error) / 批量启用(success) / 批量禁用(warning)
- 表格列: 序号 / 结构编码 / 属性类编码 / 属性类名称 / 事件 / 是否启用 / 备注 / 操作
- 操作列每行4个图标按钮(div.n-button): 查看(info) / 编辑(primary) / 启用-禁用切换(warning) / 删除(error)
- 新增弹窗: 结构编码*(下拉) / 属性类编码*(3位数字输入) / 属性类名称*(85字符) /
            事件(85字符) / 是否启用(开关默认开) / 备注(85字符TEXTAREA)
- 弹窗额外按钮: 自动生成属性类编码
- 分页器: 共N条 / 页码 / 每页条数 / 跳转输入框
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class AttributeClassPage(BasePage):
    """元数据管理 - 属性类 页面。"""

    path = "/metadata/attribute-class"

    # ---- 菜单导航 ----
    SEL_MENU_METADATA = ".n-menu-item-content:has-text('元数据管理')"
    SEL_MENU_ATTRIBUTE_CLASS = ".n-menu-item-content:has-text('属性类')"

    # ---- 筛选区 form-item ----
    SEL_FILTER_FORM = ".n-card .n-form"
    SEL_F_STRUCT_SELECT = ".n-form-item:has-text('结构编码') .n-base-selection"
    SEL_F_NAME_INPUT = ".n-form-item:has-text('属性类名称') input"
    SEL_F_CODE_INPUT = ".n-form-item:has-text('属性类编码') input"
    SEL_F_ENABLE_SELECT = ".n-form-item:has-text('是否启用') .n-base-selection"

    # ---- 顶部操作按钮 ----
    SEL_SEARCH_BTN = "button:has-text('查询')"
    SEL_RESET_BTN = "button:has-text('重置')"
    SEL_CREATE_BTN = "button:has-text('新增')"
    SEL_BATCH_DELETE_BTN = "button:has-text('批量删除')"
    SEL_BATCH_ENABLE_BTN = "button:has-text('批量启用')"
    SEL_BATCH_DISABLE_BTN = "button:has-text('批量禁用')"

    # ---- 表格 ----
    SEL_TABLE = ".n-data-table"
    SEL_TABLE_ROW = ".n-data-table-tbody tr"
    SEL_TABLE_HEADER = ".n-data-table-th__title"
    SEL_TABLE_CHECKBOX_ALL = ".n-data-table-th .n-checkbox"

    # ---- 操作列按钮（按颜色类型，div.n-button 也匹配 class 选择器）----
    # 探查确认：info=查看, primary=编辑, warning=启用/禁用切换, error=删除
    # 注意：属性类的切换按钮是 warning-type（与对象类的 success-type 不同）
    SEL_OP_VIEW = ".n-button--info-type"
    SEL_OP_EDIT = ".n-button--primary-type"
    SEL_OP_TOGGLE = ".n-button--warning-type"
    SEL_OP_TOGGLE_ALT = ".n-button--success-type"  # 切换后状态可能变 success
    SEL_OP_DELETE = ".n-button--error-type"

    # ---- 分页器 ----
    SEL_PAGINATION = ".n-pagination"
    SEL_PAG_TOTAL = ".n-pagination__total, [class*='pagination'] [class*='total']"
    SEL_PAG_INPUT = ".n-pagination .n-input__input-el"
    SEL_PAG_NEXT = ".n-pagination .n-pagination-next, .n-pagination button:has-text('>')"
    SEL_PAG_PREV = ".n-pagination .n-pagination-prev, .n-pagination button:has-text('<')"

    # ---- 新增/编辑弹窗 ----
    SEL_MODAL = ".n-modal"
    SEL_MODAL_TITLE = ".n-modal .n-modal__title, .n-modal .n-card-header__title, .n-modal-title"
    # 结构编码（下拉选择，必填）
    SEL_M_STRUCT_SELECT = ".n-modal .n-form-item:has-text('结构编码') .n-base-selection"
    # 属性类编码（输入框，3位数字，必填，编辑时禁用）
    SEL_M_CODE_INPUT = ".n-modal .n-form-item:has-text('属性类编码') input"
    # 属性类名称（输入框，85字符，必填）
    SEL_M_NAME_INPUT = ".n-modal .n-form-item:has-text('属性类名称') input"
    # 事件（输入框，85字符，选填）
    SEL_M_EVENT_INPUT = ".n-modal .n-form-item:has-text('事件') input"
    # 是否启用（开关，默认开）
    SEL_M_ENABLE_SWITCH = ".n-modal .n-form-item:has-text('是否启用') .n-switch"
    # 备注（文本域，85字符，选填）
    SEL_M_REMARK_TEXTAREA = ".n-modal .n-form-item:has-text('备注') textarea"
    SEL_M_CANCEL_BTN = ".n-modal button:has-text('取消')"
    SEL_M_SAVE_BTN = ".n-modal button:has-text('保存')"
    SEL_M_CLOSE_BTN = ".n-modal .n-base-close"
    # 自动生成属性类编码按钮
    SEL_M_AUTO_CODE_BTN = ".n-modal button:has-text('自动生成属性类编码')"

    # ---- 确认弹窗（删除/批量操作/启用禁用切换）----
    # 覆盖三种弹窗：n-dialog / n-popconfirm / n-modal
    SEL_CONFIRM_OK_BTN = (".n-dialog button:has-text('确定'), "
                          ".n-popconfirm button:has-text('确认'), "
                          ".n-modal button:has-text('确定'), "
                          ".n-modal button:has-text('确认')")
    SEL_CONFIRM_CANCEL_BTN = (".n-dialog button:has-text('取消'), "
                              ".n-popconfirm button:has-text('取消'), "
                              ".n-modal button:has-text('取消')")

    # ---- 消息提示 ----
    SEL_MESSAGE = ".n-message, .n-message-wrapper"
    SEL_MESSAGE_SUCCESS = ".n-message--success-type, .n-message:has-text('成功')"
    SEL_MESSAGE_ERROR = ".n-message--error-type, .n-message:has-text('失败')"

    # ---- 空数据提示 ----
    SEL_EMPTY_TIP = ".n-data-table-empty .n-data-empty, .n-data-empty"

    def __init__(self, page: Page):
        super().__init__(page)

    # ---- 导航 ----
    @allure.step("从数据平台首页进入属性类页面")
    def goto_attribute_class(self):
        """点击 元数据管理 父菜单 → 属性类 子菜单。

        兼容 SPA 客户端路由延迟：先等 URL 稳定，再等菜单容器可见，最后点击。带重试机制。
        """
        # 1. 等待 SPA 路由完成（URL 从 /ui/ 跳到 /monitor/home）
        for _ in range(30):
            cur_url = self.page.url
            if "/monitor/home" in cur_url or "/metadata" in cur_url:
                break
            try:
                self.page.locator(".n-layout-sider, .n-menu").first.wait_for(
                    state="visible", timeout=1000
                )
                break
            except Exception:
                self.page.wait_for_timeout(500)
        else:
            try:
                self.page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            self.page.wait_for_timeout(2000)

        # 2. 元数据管理 父菜单（带重试）
        clicked = False
        for attempt in range(3):
            try:
                self.page.locator(self.SEL_MENU_METADATA).first.wait_for(
                    state="visible", timeout=10000
                )
                self.page.locator(self.SEL_MENU_METADATA).first.click()
                clicked = True
                break
            except Exception:
                self.page.wait_for_timeout(1500)
                try:
                    self.page.locator(".n-layout-sider").first.scroll_into_view_if_needed(
                        timeout=2000
                    )
                except Exception:
                    pass
        if not clicked:
            self.page.locator(self.SEL_MENU_METADATA).first.click(timeout=5000)
        self.page.wait_for_timeout(1000)

        # 3. 属性类 子菜单
        try:
            self.page.locator(self.SEL_MENU_ATTRIBUTE_CLASS).first.wait_for(
                state="visible", timeout=8000
            )
        except Exception:
            pass
        self.page.locator(self.SEL_MENU_ATTRIBUTE_CLASS).first.click()
        self.page.wait_for_timeout(1500)
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        self.wait_for(self.SEL_TABLE_ROW)
        return self

    # ---- 校验 ----
    @allure.step("校验属性类表格可见")
    def is_table_visible(self) -> bool:
        try:
            self.page.locator(self.SEL_TABLE).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    @allure.step("校验顶部按钮可见")
    def are_top_buttons_visible(self) -> bool:
        try:
            for sel in [self.SEL_SEARCH_BTN, self.SEL_RESET_BTN, self.SEL_CREATE_BTN]:
                self.page.locator(sel).first.wait_for(state="visible", timeout=3000)
            return True
        except Exception:
            return False

    @allure.step("校验分页器可见")
    def is_pagination_visible(self) -> bool:
        try:
            self.page.locator(self.SEL_PAGINATION).first.wait_for(state="visible", timeout=3000)
            return True
        except Exception:
            return False

    @allure.step("校验筛选区可见")
    def are_filters_visible(self) -> bool:
        try:
            self.page.locator(self.SEL_F_NAME_INPUT).first.wait_for(state="visible", timeout=3000)
            self.page.locator(self.SEL_F_CODE_INPUT).first.wait_for(state="visible", timeout=3000)
            return True
        except Exception:
            return False

    # ---- 数据提取 ----
    @allure.step("获取表格行数")
    def get_row_count(self) -> int:
        return self.page.locator(self.SEL_TABLE_ROW).count()

    @allure.step("获取表格列头")
    def get_headers(self) -> list[str]:
        hs = self.page.locator(self.SEL_TABLE_HEADER)
        return [hs.nth(i).inner_text().strip() for i in range(hs.count())]

    @allure.step("获取第 {index} 行文本")
    def get_row_text(self, index: int = 0) -> str:
        rows = self.page.locator(self.SEL_TABLE_ROW)
        if rows.count() > index:
            return rows.nth(index).inner_text()
        return ""

    @allure.step("获取指定列的所有值")
    def get_column_values(self, header_name: str) -> list[str]:
        """根据列名取该列所有单元格文本，使用 data-col-key 精确匹配。"""
        js = """(headerName) => {
            const headers = Array.from(document.querySelectorAll('.n-data-table-th__title'));
            let colKey = null;
            for (const h of headers) {
                if (h.textContent.includes(headerName)) {
                    const th = h.closest('th');
                    colKey = th ? th.getAttribute('data-col-key') : null;
                    break;
                }
            }
            if (!colKey) return [];
            const tds = document.querySelectorAll('td[data-col-key="' + colKey + '"]');
            return Array.from(tds).map(td => td.textContent.trim());
        }"""
        try:
            return self.page.evaluate(js, header_name)
        except Exception:
            return []

    @allure.step("获取第 {row_index} 行指定列的值")
    def get_cell_value(self, row_index: int, header_name: str) -> str:
        js = """(args) => {
            const headerName = args.headerName;
            const rowIndex = args.rowIndex;
            const headers = Array.from(document.querySelectorAll('.n-data-table-th__title'));
            let colKey = null;
            for (const h of headers) {
                if (h.textContent.includes(headerName)) {
                    const th = h.closest('th');
                    colKey = th ? th.getAttribute('data-col-key') : null;
                    break;
                }
            }
            if (!colKey) return '';
            const tds = document.querySelectorAll('td[data-col-key="' + colKey + '"]');
            if (rowIndex >= tds.length) return '';
            return tds[rowIndex].textContent.trim();
        }"""
        try:
            return self.page.evaluate(js, {"headerName": header_name, "rowIndex": row_index})
        except Exception:
            return ""

    @allure.step("获取总记录数（从分页器）")
    def get_total_count(self) -> int:
        try:
            el = self.page.locator(self.SEL_PAG_TOTAL).first
            txt = el.inner_text()
            import re
            m = re.search(r"(\d+)", txt)
            return int(m.group(1)) if m else 0
        except Exception:
            return 0

    @allure.step("查找匹配指定列值的行索引")
    def find_row_by_column(self, header_name: str, value: str) -> int:
        vals = self.get_column_values(header_name)
        for i, v in enumerate(vals):
            if value in v:
                return i
        return -1

    # ---- 交互：搜索/筛选 ----
    @allure.step("输入属性类名称筛选 '{name}'")
    def filter_by_name(self, name: str):
        self.page.locator(self.SEL_F_NAME_INPUT).first.fill(name)
        return self

    @allure.step("输入属性类编码筛选 '{code}'")
    def filter_by_code(self, code: str):
        self.page.locator(self.SEL_F_CODE_INPUT).first.fill(code)
        return self

    @allure.step("选择下拉筛选项 '{label}' = '{option}'")
    def select_filter(self, label: str, option: str):
        """选择筛选下拉的某项。label 对应筛选 form-item 的 label。"""
        form_item = self.page.locator(f".n-form-item:has-text('{label}')").first
        form_item.locator(".n-base-selection").first.click()
        self.page.wait_for_timeout(300)
        dropdown = self.page.locator(
            ".n-base-select-option, .n-select-option, .n-base-select-menu"
        )
        opt = dropdown.filter(has_text=option).first
        try:
            opt.wait_for(state="visible", timeout=3000)
            opt.click()
            self.page.wait_for_timeout(200)
        except Exception:
            pass
        return self

    @allure.step("点击查询")
    def search(self):
        self.page.locator(self.SEL_SEARCH_BTN).first.click()
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        return self

    @allure.step("点击重置")
    def reset_search(self):
        self.page.locator(self.SEL_RESET_BTN).first.click()
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        return self

    # ---- 交互：行选择 ----
    @allure.step("勾选第 {index} 行（0-based）")
    def check_row(self, index: int):
        rows = self.page.locator(self.SEL_TABLE_ROW)
        if rows.count() > index:
            rows.nth(index).locator(".n-checkbox").first.click()
        return self

    @allure.step("勾选所有行")
    def check_all(self):
        self.page.locator(self.SEL_TABLE_CHECKBOX_ALL).first.click()
        return self

    # ---- 交互：行操作按钮 ----
    @allure.step("点击第 {row_index} 行的查看按钮")
    def click_row_view(self, row_index: int = 0):
        rows = self.page.locator(self.SEL_TABLE_ROW)
        if rows.count() > row_index:
            rows.nth(row_index).locator(self.SEL_OP_VIEW).first.click()
            self.page.wait_for_timeout(500)
            try:
                self.page.locator(self.SEL_MODAL).first.wait_for(state="visible", timeout=5000)
            except Exception:
                pass
        return self

    @allure.step("点击第 {row_index} 行的编辑按钮")
    def click_row_edit(self, row_index: int = 0):
        rows = self.page.locator(self.SEL_TABLE_ROW)
        if rows.count() > row_index:
            rows.nth(row_index).locator(self.SEL_OP_EDIT).first.click()
            self.page.wait_for_timeout(500)
            try:
                self.page.locator(self.SEL_MODAL).first.wait_for(state="visible", timeout=5000)
            except Exception:
                pass
        return self

    @allure.step("点击第 {row_index} 行的启用/禁用切换按钮")
    def click_row_toggle(self, row_index: int = 0):
        """点击启用/禁用切换按钮。

        属性类页面切换按钮默认 warning-type，切换后可能变 success-type。
        优先 warning-type，fallback success-type。
        """
        rows = self.page.locator(self.SEL_TABLE_ROW)
        if rows.count() > row_index:
            row = rows.nth(row_index)
            toggle = row.locator(self.SEL_OP_TOGGLE).first
            try:
                toggle.wait_for(state="visible", timeout=3000)
            except Exception:
                toggle = row.locator(self.SEL_OP_TOGGLE_ALT).first
            toggle.click()
            self.page.wait_for_timeout(500)
        return self

    @allure.step("点击第 {row_index} 行的删除按钮")
    def click_row_delete(self, row_index: int = 0):
        rows = self.page.locator(self.SEL_TABLE_ROW)
        if rows.count() > row_index:
            rows.nth(row_index).locator(self.SEL_OP_DELETE).first.click()
            self.page.wait_for_timeout(500)
        return self

    # ---- 交互：顶部按钮 ----
    @allure.step("点击新增按钮")
    def click_create(self):
        self.page.locator(self.SEL_CREATE_BTN).first.click()
        try:
            self.page.locator(self.SEL_MODAL).first.wait_for(state="visible", timeout=5000)
        except Exception:
            pass
        return self

    @allure.step("点击批量删除")
    def click_batch_delete(self):
        self.page.locator(self.SEL_BATCH_DELETE_BTN).first.click()
        return self

    @allure.step("点击批量启用")
    def click_batch_enable(self):
        self.page.locator(self.SEL_BATCH_ENABLE_BTN).first.click()
        return self

    @allure.step("点击批量禁用")
    def click_batch_disable(self):
        self.page.locator(self.SEL_BATCH_DISABLE_BTN).first.click()
        return self

    # ---- 弹窗操作 ----
    @allure.step("填写新增/编辑表单")
    def fill_form(self, struct: str = "", code: str = "", name: str = "",
                  event: str = "", remark: str = ""):
        """填写弹窗表单。

        Args:
            struct: 结构编码（下拉选择的选项文本，如 "CODEXUT结构(91)"）
            code: 属性类编码（3位数字）
            name: 属性类名称
            event: 事件
            remark: 备注
        """
        if struct:
            # 下拉选择结构编码
            sel = self.page.locator(self.SEL_M_STRUCT_SELECT).first
            try:
                sel.click()
                self.page.wait_for_timeout(300)
                opt = self.page.locator(
                    ".n-base-select-option, .n-select-option, .n-base-select-menu"
                ).filter(has_text=struct).first
                opt.wait_for(state="visible", timeout=3000)
                opt.click()
                self.page.wait_for_timeout(200)
            except Exception:
                pass
        if code:
            self.page.locator(self.SEL_M_CODE_INPUT).first.fill(code)
        if name:
            self.page.locator(self.SEL_M_NAME_INPUT).first.fill(name)
        if event:
            self.page.locator(self.SEL_M_EVENT_INPUT).first.fill(event)
        if remark:
            self.page.locator(self.SEL_M_REMARK_TEXTAREA).first.fill(remark)
        return self

    @allure.step("点击保存")
    def click_save(self):
        self.page.locator(self.SEL_M_SAVE_BTN).first.click()
        self.page.wait_for_timeout(500)
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        return self

    @allure.step("点击取消")
    def click_cancel(self):
        self.page.locator(self.SEL_M_CANCEL_BTN).first.click()
        return self

    @allure.step("点击关闭(X)")
    def click_close(self):
        try:
            self.page.locator(self.SEL_M_CLOSE_BTN).first.click()
        except Exception:
            pass
        return self

    @allure.step("点击保存并等待弹窗关闭")
    def submit_form(self):
        self.page.locator(self.SEL_M_SAVE_BTN).first.click()
        try:
            self.page.wait_for_timeout(500)
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        return self

    @allure.step("点击自动生成属性类编码")
    def click_auto_generate_code(self):
        """点击'自动生成属性类编码'按钮，自动填充编码。"""
        try:
            btn = self.page.locator(self.SEL_M_AUTO_CODE_BTN).first
            btn.wait_for(state="visible", timeout=3000)
            btn.click()
            self.page.wait_for_timeout(500)
        except Exception:
            pass
        return self

    # ---- 确认弹窗 ----
    @allure.step("确认弹窗")
    def confirm_dialog(self):
        """点击确认/确定按钮，覆盖 dialog/modal/popconfirm 三种弹窗。"""
        try:
            ok = self.page.locator(self.SEL_CONFIRM_OK_BTN).first
            ok.wait_for(state="visible", timeout=3000)
            ok.click()
            self.page.wait_for_timeout(500)
        except Exception:
            pass
        return self

    @allure.step("取消确认弹窗")
    def cancel_dialog(self):
        try:
            cancel = self.page.locator(self.SEL_CONFIRM_CANCEL_BTN).first
            cancel.wait_for(state="visible", timeout=3000)
            cancel.click()
            self.page.wait_for_timeout(500)
        except Exception:
            pass
        return self

    # ---- 消息提示 ----
    @allure.step("等待消息提示出现")
    def wait_for_message(self, timeout_ms: int = 3000) -> str:
        try:
            self.page.locator(self.SEL_MESSAGE).first.wait_for(state="visible", timeout=timeout_ms)
            return self.page.locator(self.SEL_MESSAGE).first.inner_text().strip()
        except Exception:
            return ""

    @allure.step("等待成功消息")
    def wait_for_success_message(self, timeout_ms: int = 3000) -> bool:
        try:
            self.page.locator(self.SEL_MESSAGE_SUCCESS).first.wait_for(
                state="visible", timeout=timeout_ms
            )
            return True
        except Exception:
            return False

    @allure.step("等待错误消息")
    def wait_for_error_message(self, timeout_ms: int = 3000) -> bool:
        try:
            self.page.locator(self.SEL_MESSAGE_ERROR).first.wait_for(
                state="visible", timeout=timeout_ms
            )
            return True
        except Exception:
            return False

    # ---- 校验弹窗状态 ----
    @allure.step("校验弹窗是否打开")
    def is_modal_open(self) -> bool:
        try:
            return self.page.locator(self.SEL_MODAL).first.is_visible()
        except Exception:
            return False

    @allure.step("校验弹窗是否关闭（带等待）")
    def wait_modal_closed(self, timeout_ms: int = 5000) -> bool:
        try:
            self.page.locator(self.SEL_MODAL).first.wait_for(
                state="hidden", timeout=timeout_ms
            )
            return True
        except Exception:
            return False

    @allure.step("校验弹窗是否关闭")
    def is_modal_closed(self) -> bool:
        try:
            return not self.page.locator(self.SEL_MODAL).first.is_visible()
        except Exception:
            return True

    @allure.step("获取表单必填项错误提示")
    def get_form_errors(self) -> list[str]:
        errs = []
        try:
            errors = self.page.locator(".n-form-item-feedback__line, .n-form-item-feedback")
            for i in range(errors.count()):
                try:
                    txt = errors.nth(i).inner_text().strip()
                    if txt:
                        errs.append(txt)
                except Exception:
                    pass
        except Exception:
            pass
        return errs

    # ---- 开关切换 ----
    @allure.step("切换弹窗内'是否启用'开关")
    def toggle_modal_enable(self):
        try:
            sw = self.page.locator(self.SEL_M_ENABLE_SWITCH).first
            sw.click()
            self.page.wait_for_timeout(200)
        except Exception:
            pass
        return self

    @allure.step("获取'是否启用'开关状态")
    def get_modal_enable_state(self) -> str:
        """返回 'checked' 或 'unchecked'。"""
        try:
            sw = self.page.locator(self.SEL_M_ENABLE_SWITCH).first
            cls = sw.get_attribute("class") or ""
            return "checked" if "n-switch--active" in cls or "n-switch--checked" in cls else "unchecked"
        except Exception:
            return "unknown"

    # ---- 表单字段回显获取 ----
    @allure.step("获取弹窗表单字段值（用于编辑回显校验）")
    def get_modal_form_values(self) -> dict:
        """获取弹窗内各字段的当前值。"""
        vals = {}
        # 结构编码（下拉，取选中项文本）
        try:
            sel = self.page.locator(self.SEL_M_STRUCT_SELECT).first
            vals["struct"] = sel.inner_text().strip()
        except Exception:
            vals["struct"] = ""
        try:
            vals["code"] = self.page.locator(self.SEL_M_CODE_INPUT).first.input_value()
        except Exception:
            vals["code"] = ""
        try:
            vals["name"] = self.page.locator(self.SEL_M_NAME_INPUT).first.input_value()
        except Exception:
            vals["name"] = ""
        try:
            vals["event"] = self.page.locator(self.SEL_M_EVENT_INPUT).first.input_value()
        except Exception:
            vals["event"] = ""
        try:
            vals["remark"] = self.page.locator(self.SEL_M_REMARK_TEXTAREA).first.input_value()
        except Exception:
            vals["remark"] = ""
        vals["enable"] = self.get_modal_enable_state()
        return vals

    @allure.step("清空弹窗指定字段")
    def clear_modal_field(self, field: str):
        """清空弹窗中的某个字段。field: code/name/event/remark。"""
        sel_map = {
            "code": self.SEL_M_CODE_INPUT,
            "name": self.SEL_M_NAME_INPUT,
            "event": self.SEL_M_EVENT_INPUT,
            "remark": self.SEL_M_REMARK_TEXTAREA,
        }
        sel = sel_map.get(field)
        if sel:
            try:
                self.page.locator(sel).first.fill("")
            except Exception:
                pass
        return self

    # ---- 详情弹窗 ----
    @allure.step("获取详情弹窗文本内容")
    def get_detail_text(self) -> str:
        try:
            modal = self.page.locator(self.SEL_MODAL).first
            modal.wait_for(state="visible", timeout=3000)
            return modal.inner_text().strip()
        except Exception:
            return ""

    @allure.step("关闭详情弹窗")
    def close_detail(self):
        try:
            for sel in [".n-modal button:has-text('取消')",
                        ".n-modal button:has-text('关闭')",
                        ".n-modal button:has-text('确定')",
                        ".n-modal .n-base-close"]:
                btn = self.page.locator(sel).first
                if btn.is_visible():
                    btn.click()
                    break
            self.page.wait_for_timeout(300)
        except Exception:
            pass
        return self

    # ---- 分页控制 ----
    @allure.step("切换每页条数为 {size}")
    def change_page_size(self, size: int):
        try:
            selector = self.page.locator(
                ".n-pagination .n-pagination-size, .n-pagination [class*='size']"
            ).first
            selector.click()
            self.page.wait_for_timeout(300)
            opt = self.page.locator(
                ".n-base-select-option, .n-select-option"
            ).filter(has_text=str(size)).first
            opt.click()
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
        except Exception:
            pass
        return self

    @allure.step("跳转到第 {page_no} 页")
    def jump_to_page(self, page_no: int):
        try:
            inp = self.page.locator(self.SEL_PAG_INPUT).first
            inp.fill(str(page_no))
            self.page.keyboard.press("Enter")
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
        except Exception:
            pass
        return self

    @allure.step("点击指定页码按钮 {page_no}")
    def click_page_number(self, page_no: int):
        try:
            btn = self.page.locator(
                f".n-pagination .n-pagination-item:has-text('{page_no}')"
            ).first
            btn.click()
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
        except Exception:
            pass
        return self
