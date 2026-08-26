"""探查属性类页面操作列按钮结构"""
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

        if "login" in page.url or page.locator("input[placeholder*='账号'], input[name='username']").count() > 0:
            print("[probe] 登录...")
            auth_cfg = config.auth_config()
            LoginPage(page).login(auth_cfg.get("username", ""), auth_cfg.get("password", ""))
            mgr.save_auth_state()
            page.wait_for_load_state("networkidle", timeout=30000)
            page.wait_for_timeout(1500)

        new_page = HomePage(page).click_data_platform()
        new_page.wait_for_timeout(2500)
        new_page.wait_for_load_state("networkidle", timeout=15000)

        if "login" in new_page.url:
            auth_cfg = config.auth_config()
            LoginPage(new_page).login(auth_cfg.get("username", ""), auth_cfg.get("password", ""))
            new_page.wait_for_load_state("networkidle", timeout=30000)
            new_page.wait_for_timeout(2000)

        # 进入属性类页面
        new_page.locator(".n-menu-item-content:has-text('元数据管理')").first.click()
        new_page.wait_for_timeout(1000)
        new_page.locator(".n-menu-item-content:has-text('属性类')").first.click()
        new_page.wait_for_timeout(2500)
        try:
            new_page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        print(f"[probe] URL: {new_page.url}")

        # 操作列按钮完整 HTML
        print("\n=== 操作列第一行所有按钮 outerHTML ===")
        op_html = new_page.evaluate("""() => {
            const tr = document.querySelector('.n-data-table-tbody tr');
            if (!tr) return 'NO_ROW';
            const td = tr.querySelector('td:last-child');
            if (!td) return 'NO_LAST_TD';
            const btns = td.querySelectorAll('button, .n-button, [class*="n-button"]');
            return Array.from(btns).map(b => {
                return {
                    tag: b.tagName,
                    cls: (b.className || '').substring(0, 100),
                    text: b.textContent.trim().substring(0, 30),
                    html: b.outerHTML.substring(0, 200)
                };
            });
        }""")
        print(op_html)

        # 操作列最后一列所有元素
        print("\n=== 操作列第一行所有子元素 ===")
        op_all = new_page.evaluate("""() => {
            const tr = document.querySelector('.n-data-table-tbody tr');
            if (!tr) return 'NO_ROW';
            const td = tr.querySelector('td:last-child');
            if (!td) return 'NO_LAST_TD';
            const els = td.querySelectorAll('*');
            return Array.from(els).slice(0, 30).map(e => {
                return e.tagName + '.' + (e.className || '').substring(0, 50);
            });
        }""")
        print(op_all)

        # 用 data-col-key="actions" 精确取操作列
        print("\n=== data-col-key=actions 单元格内容 ===")
        actions_cell = new_page.evaluate("""() => {
            const tds = document.querySelectorAll('td[data-col-key="actions"]');
            if (tds.length === 0) return 'NO_ACTIONS_TD';
            const td = tds[0];
            return {
                html: td.innerHTML.substring(0, 1000),
                buttons: Array.from(td.querySelectorAll('button')).map(b => (b.className || '').substring(0, 80))
            };
        }""")
        print(actions_cell)

        # 截图操作列
        out_dir = ROOT / "reports" / "probe_attribute_class"
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            new_page.locator(".n-data-table-tbody tr").first.locator("td:last-child").screenshot(
                path=str(out_dir / "op_column.png"))
            print(f"[probe] 操作列截图: {out_dir / 'op_column.png'}")
        except Exception as e:
            print(f"[probe] 截图失败: {e}")

        # 分页器完整信息
        print("\n=== 分页器完整信息 ===")
        pag_info = new_page.evaluate("""() => {
            const p = document.querySelector('.n-pagination');
            if (!p) return 'NO_PAG';
            const total = p.querySelector('[class*="total"], .n-pagination__total');
            const items = Array.from(p.querySelectorAll('.n-pagination-item, [class*="pagination-item"]')).map(i => i.textContent.trim());
            const size = p.querySelector('[class*="size"], .n-pagination-size');
            const input = p.querySelector('input');
            return {
                totalText: total ? total.textContent.trim() : '',
                pageItems: items,
                sizeText: size ? size.textContent.trim() : '',
                hasInput: !!input
            };
        }""")
        print(pag_info)

        # 总记录数
        print("\n=== 总记录数（从分页器文本）===")
        total_txt = new_page.evaluate("""() => {
            const p = document.querySelector('.n-pagination');
            if (!p) return '';
            return p.textContent.trim().substring(0, 200);
        }""")
        print(total_txt)

        print("\n[probe] 完成")

    finally:
        try:
            mgr.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
