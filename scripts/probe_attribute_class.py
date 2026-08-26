"""探查 元数据管理-属性类 页面结构"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils import config
from utils.browser import BrowserManager
from pages.home.home_page import HomePage
from pages.data_platform.data_platform_page import DataPlatformPage
from pages.login.login_page import LoginPage


def main():
    mgr = BrowserManager().start()
    try:
        page = mgr.page
        page.goto(config.base_url())
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(1000)

        # 检查是否在登录页，是则登录
        if "login" in page.url or page.locator("input[placeholder*='账号'], input[name='username']").count() > 0:
            print("[probe] 在登录页，执行登录")
            auth_cfg = config.auth_config()
            LoginPage(page).login(
                auth_cfg.get("username", ""),
                auth_cfg.get("password", ""),
            )
            mgr.save_auth_state()
            page.wait_for_load_state("networkidle", timeout=30000)
            page.wait_for_timeout(1500)
            print(f"[probe] 登录后 URL: {page.url}")

        new_page = HomePage(page).click_data_platform()
        new_page.wait_for_timeout(2500)
        new_page.wait_for_load_state("networkidle", timeout=15000)
        print(f"[probe] 数据平台 URL: {new_page.url}")

        # 如果又跳到登录页，对 DolphinScheduler 单独登录
        if "login" in new_page.url:
            print("[probe] DolphinScheduler 需要单独登录")
            auth_cfg = config.auth_config()
            LoginPage(new_page).login(
                auth_cfg.get("username", ""),
                auth_cfg.get("password", ""),
            )
            new_page.wait_for_load_state("networkidle", timeout=30000)
            new_page.wait_for_timeout(2000)
            print(f"[probe] DS 登录后 URL: {new_page.url}")

        dp = DataPlatformPage(new_page)

        # 先输出左侧菜单结构
        print("\n=== 左侧菜单结构 ===")
        menu_items = new_page.evaluate("""() => {
            const items = document.querySelectorAll('.n-menu-item-content, .n-menu-item, [class*="menu-item"]');
            return Array.from(items).slice(0, 40).map(it => {
                const txt = it.textContent.trim().substring(0, 40);
                const cls = (it.className || '').substring(0, 60);
                const vis = it.offsetParent !== null;
                return {text: txt, cls: cls, visible: vis};
            });
        }""")
        print(menu_items)

        # 如果没有 n-menu-item-content，尝试其他选择器
        print("\n=== 所有 a/li 带 menu 文本的元素 ===")
        alt_menu = new_page.evaluate("""() => {
            const sels = ['aside a', 'aside li', '.n-layout-sider a', '.n-layout-sider li',
                          '.n-menu a', '.n-menu li', '[class*="sidebar"] a', '[class*="sidebar"] li'];
            const found = new Set();
            for (const sel of sels) {
                const els = document.querySelectorAll(sel);
                els.forEach(e => {
                    const t = e.textContent.trim();
                    if (t && t.length < 30) found.add(t);
                });
            }
            return Array.from(found).slice(0, 40);
        }""")
        print(alt_menu)

        # 点 元数据管理 父菜单（带重试，兼容多种选择器）
        print("\n[probe] 点击 '元数据管理' 父菜单...")
        meta_clicked = False
        for sel in [".n-menu-item-content:has-text('元数据管理')",
                    ".n-menu-item:has-text('元数据管理')",
                    "[class*='menu-item']:has-text('元数据管理')",
                    "li:has-text('元数据管理')",
                    "a:has-text('元数据管理')"]:
            try:
                loc = new_page.locator(sel).first
                loc.wait_for(state="visible", timeout=3000)
                loc.click()
                meta_clicked = True
                print(f"[probe] 使用选择器点击成功: {sel}")
                break
            except Exception as e:
                print(f"[probe] 选择器失败 {sel}: {e}")
        if not meta_clicked:
            print("[probe] 所有菜单选择器失败")
        new_page.wait_for_timeout(1000)

        # 点 属性类 子菜单（带重试）
        print("[probe] 点击 '属性类' 子菜单...")
        attr_clicked = False
        for sel in [".n-menu-item-content:has-text('属性类')",
                    ".n-menu-item:has-text('属性类')",
                    "[class*='menu-item']:has-text('属性类')",
                    "li:has-text('属性类')",
                    "a:has-text('属性类')"]:
            try:
                loc = new_page.locator(sel).first
                loc.wait_for(state="visible", timeout=3000)
                loc.click()
                attr_clicked = True
                print(f"[probe] 子菜单选择器点击成功: {sel}")
                break
            except Exception as e:
                print(f"[probe] 子菜单选择器失败 {sel}: {e}")
        if not attr_clicked:
            print("[probe] 所有子菜单选择器失败")
        new_page.wait_for_timeout(2500)
        try:
            new_page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        print(f"[probe] URL: {new_page.url}")

        out_dir = ROOT / "reports" / "probe_attribute_class"
        out_dir.mkdir(parents=True, exist_ok=True)
        new_page.screenshot(path=str(out_dir / "attribute_class.png"), full_page=True)

        # 元素统计
        print("\n=== 元素统计 ===")
        candidates = [
            ("table", "table"),
            ("table thead tr", "thead"),
            ("table tbody tr", "tbody tr"),
            (".n-data-table", ".n-data-table"),
            (".n-data-table-tbody tr", "n-dt-tbody tr"),
            ("button", "button"),
            (".n-button", ".n-button"),
            (".n-button__content", "n-button-content"),
            ("input", "input"),
            (".n-input", ".n-input"),
            (".n-pagination", ".n-pagination"),
            (".n-modal", ".n-modal"),
            (".n-dialog", ".n-dialog"),
            (".n-drawer", ".n-drawer"),
            (".n-form-item", ".n-form-item"),
        ]
        for sel, name in candidates:
            try:
                cnt = new_page.locator(sel).count()
                print(f"  {name}: {cnt}")
            except Exception as e:
                print(f"  {name}: ERROR {e}")

        # 表格列头
        print("\n=== 表格列头 ===")
        headers = new_page.evaluate("""() => {
            const hs = Array.from(document.querySelectorAll('.n-data-table-th__title'));
            return hs.map(h => {
                const th = h.closest('th');
                const colKey = th ? th.getAttribute('data-col-key') : null;
                return {text: h.textContent.trim(), colKey: colKey};
            });
        }""")
        print(headers)

        # 筛选区 form-item
        print("\n=== 筛选区 form-item ===")
        filter_items = new_page.evaluate("""() => {
            const form = document.querySelector('.n-card .n-form, .n-form');
            if (!form) return 'NO_FORM';
            const items = form.querySelectorAll('.n-form-item');
            return Array.from(items).map(it => {
                const label = it.querySelector('.n-form-item-label__text, .n-form-item-label');
                const labelText = label ? label.textContent.trim() : '';
                const required = it.querySelector('.n-form-item-label--required') !== null;
                const input = it.querySelector('input, textarea, .n-base-selection, .n-switch');
                const inputTag = input ? input.tagName + '.' + (input.className || '').substring(0, 40) : '';
                const ph = input && input.getAttribute ? input.getAttribute('placeholder') : '';
                return {label: labelText, required: required, input: inputTag, placeholder: ph};
            });
        }""")
        print(filter_items)

        # 顶部按钮
        print("\n=== 顶部按钮 ===")
        btns = new_page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button')).map(b => {
                const cls = b.className || '';
                const txt = b.textContent.trim();
                if (txt && txt.length < 15) return {text: txt, cls: cls.substring(0, 60)};
                return null;
            }).filter(x => x !== null);
        }""")
        print(btns)

        # 操作列第一行的按钮类型
        print("\n=== 操作列第一行按钮 ===")
        op_btns = new_page.evaluate("""() => {
            const tr = document.querySelector('.n-data-table-tbody tr');
            if (!tr) return 'NO_ROW';
            const btns = tr.querySelectorAll('button');
            return Array.from(btns).map(b => {
                const cls = b.className || '';
                const icon = b.querySelector('i, .n-icon, svg');
                const iconCls = icon ? icon.className : '';
                return {cls: cls.substring(0, 80), iconCls: iconCls.substring(0, 50)};
            });
        }""")
        print(op_btns)

        # 分页器
        print("\n=== 分页器 ===")
        pag = new_page.evaluate("""() => {
            const p = document.querySelector('.n-pagination');
            if (!p) return 'NO_PAG';
            return {
                total: (p.querySelector('.n-pagination__total, [class*="total"]') || {}).textContent || '',
                html: p.outerHTML.substring(0, 500)
            };
        }""")
        print(pag)

        # 点击新增按钮，探查弹窗
        print("\n[probe] 点击新增按钮...")
        try:
            new_page.locator("button:has-text('新增')").first.click()
            new_page.wait_for_timeout(1500)
            new_page.screenshot(path=str(out_dir / "create_modal.png"), full_page=False)

            # 弹窗字段
            print("\n=== 新增弹窗字段 ===")
            modal_fields = new_page.evaluate("""() => {
                const modal = document.querySelector('.n-modal');
                if (!modal || modal.offsetParent === null) return 'NO_MODAL';
                const items = modal.querySelectorAll('.n-form-item');
                return Array.from(items).map(it => {
                    const label = it.querySelector('.n-form-item-label__text, .n-form-item-label');
                    const labelText = label ? label.textContent.trim() : '';
                    const required = it.querySelector('.n-form-item-label--required') !== null
                        || it.querySelector('[class*="required"]') !== null;
                    const input = it.querySelector('input, textarea, .n-base-selection, .n-switch');
                    const inputTag = input ? input.tagName + '.' + (input.className || '').substring(0, 40) : '';
                    const ph = input && input.getAttribute ? input.getAttribute('placeholder') : '';
                    const maxLen = input && input.getAttribute ? input.getAttribute('maxlength') : '';
                    return {label: labelText, required: required, input: inputTag, placeholder: ph, maxlength: maxLen};
                });
            }""")
            print(modal_fields)

            # 弹窗标题与按钮
            print("\n=== 弹窗标题与按钮 ===")
            modal_meta = new_page.evaluate("""() => {
                const modal = document.querySelector('.n-modal');
                if (!modal) return 'NO_MODAL';
                const title = modal.querySelector('.n-modal__title, .n-card-header__title, .n-modal-title');
                const btns = Array.from(modal.querySelectorAll('button')).map(b => b.textContent.trim()).filter(t => t);
                return {title: title ? title.textContent.trim() : '', buttons: btns};
            }""")
            print(modal_meta)

            # 关闭弹窗
            try:
                new_page.locator(".n-modal button:has-text('取消')").first.click()
                new_page.wait_for_timeout(500)
            except Exception:
                try:
                    new_page.locator(".n-modal .n-base-close").first.click()
                except Exception:
                    pass
        except Exception as e:
            print(f"[probe] 新增弹窗探查失败: {e}")

        # 点击第一行查看按钮，探查详情
        print("\n[probe] 点击第一行查看按钮...")
        try:
            view_btn = new_page.locator(".n-data-table-tbody tr").first.locator(".n-button--info-type").first
            view_btn.click()
            new_page.wait_for_timeout(1500)
            new_page.screenshot(path=str(out_dir / "view_modal.png"), full_page=False)

            print("\n=== 查看详情弹窗内容 ===")
            detail = new_page.evaluate("""() => {
                const modal = document.querySelector('.n-modal');
                if (!modal || modal.offsetParent === null) return 'NO_MODAL';
                // 看看是 form 还是 descriptions
                const form = modal.querySelector('.n-form');
                const desc = modal.querySelector('.n-descriptions');
                if (form) {
                    const items = form.querySelectorAll('.n-form-item');
                    return {type: 'form', fields: Array.from(items).map(it => {
                        const label = it.querySelector('.n-form-item-label__text, .n-form-item-label');
                        const input = it.querySelector('input, textarea, .n-base-selection, .n-switch');
                        const val = input ? (input.value || input.textContent || '') : '';
                        const disabled = input ? input.hasAttribute('disabled') || input.classList.contains('n-input--disabled') : false;
                        return {label: label ? label.textContent.trim() : '', value: val.trim().substring(0,60), disabled: disabled};
                    })};
                }
                if (desc) {
                    return {type: 'descriptions', text: desc.textContent.trim().substring(0, 500)};
                }
                return {type: 'other', text: modal.textContent.trim().substring(0, 500)};
            }""")
            print(detail)

            # 关闭
            try:
                for sel in [".n-modal button:has-text('取消')",
                            ".n-modal button:has-text('关闭')",
                            ".n-modal button:has-text('确定')",
                            ".n-modal .n-base-close"]:
                    btn = new_page.locator(sel).first
                    if btn.is_visible():
                        btn.click()
                        break
                new_page.wait_for_timeout(500)
            except Exception:
                pass
        except Exception as e:
            print(f"[probe] 查看详情探查失败: {e}")

        # 点击第一行编辑按钮，探查编辑弹窗
        print("\n[probe] 点击第一行编辑按钮...")
        try:
            edit_btn = new_page.locator(".n-data-table-tbody tr").first.locator(".n-button--primary-type").first
            edit_btn.click()
            new_page.wait_for_timeout(1500)
            new_page.screenshot(path=str(out_dir / "edit_modal.png"), full_page=False)

            print("\n=== 编辑弹窗字段 ===")
            edit_fields = new_page.evaluate("""() => {
                const modal = document.querySelector('.n-modal');
                if (!modal || modal.offsetParent === null) return 'NO_MODAL';
                const items = modal.querySelectorAll('.n-form-item');
                return Array.from(items).map(it => {
                    const label = it.querySelector('.n-form-item-label__text, .n-form-item-label');
                    const labelText = label ? label.textContent.trim() : '';
                    const input = it.querySelector('input, textarea, .n-base-selection, .n-switch');
                    const inputTag = input ? input.tagName + '.' + (input.className || '').substring(0, 40) : '';
                    const val = input ? (input.value || input.textContent || '') : '';
                    const disabled = input ? input.hasAttribute('disabled') || input.classList.contains('n-input--disabled') : false;
                    return {label: labelText, input: inputTag, value: val.trim().substring(0, 60), disabled: disabled};
                });
            }""")
            print(edit_fields)

            # 关闭
            try:
                new_page.locator(".n-modal button:has-text('取消')").first.click()
                new_page.wait_for_timeout(500)
            except Exception:
                pass
        except Exception as e:
            print(f"[probe] 编辑弹窗探查失败: {e}")

        print("\n[probe] 探查完成，输出到:", out_dir)

    finally:
        try:
            mgr.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
