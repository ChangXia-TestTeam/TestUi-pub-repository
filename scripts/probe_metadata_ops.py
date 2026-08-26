"""探查 对象类 操作列按钮 icon"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils import config
from utils.browser import BrowserManager
from pages.home.home_page import HomePage
from pages.login.login_page import LoginPage


def main():
    mgr = BrowserManager().start()
    try:
        page = mgr.page
        page.goto(config.base_url())
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(1000)

        if "login" in page.url or page.locator("input[placeholder*='账号'], input[name='username']").count() > 0:
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

        new_page.locator(".n-menu-item-content").filter(has_text="元数据管理").first.click()
        new_page.wait_for_timeout(800)
        new_page.locator(".n-menu-item-content").filter(has_text="对象类").first.click()
        new_page.wait_for_timeout(2500)
        new_page.wait_for_load_state("networkidle", timeout=15000)

        # 操作列按钮的完整 HTML（用 outerHTML）
        print("\n=== 操作列第1行按钮 HTML ===")
        try:
            row = new_page.locator(".n-data-table-tbody tr").first
            ops = row.locator("td").last
            html = ops.evaluate("el => el.outerHTML")
            print(html[:3000])
        except Exception as e:
            print(f"  ERR: {e}")

        # 列出每个按钮的关键属性
        print("\n=== 操作列按钮细节 ===")
        try:
            row = new_page.locator(".n-data-table-tbody tr").first
            ops = row.locator("td").last.locator("button, .n-button, [role=button]")
            for i in range(ops.count()):
                el = ops.nth(i)
                # 找内部 icon 类
                icon_cls = el.evaluate("""el => {
                    let icon = el.querySelector('i, svg, span[class*="icon"]');
                    return icon ? icon.className : '(no icon)';
                }""")
                tooltip = el.evaluate("el => el.getAttribute('title') || el.getAttribute('aria-label') || '(no tooltip)'")
                cls = el.get_attribute("class") or ""
                print(f"  [{i}] class='{cls[:50]}'  icon='{icon_cls}'  tooltip='{tooltip}'")
        except Exception as e:
            print(f"  ERR: {e}")

        # 看表格全部行 + 操作列
        print("\n=== 前 3 行操作列 inner_text ===")
        rows = new_page.locator(".n-data-table-tbody tr")
        for i in range(min(3, rows.count())):
            try:
                last_td_text = rows.nth(i).locator("td").last.inner_text()
                print(f"  行{i}: '{last_td_text}'")
            except Exception as e:
                print(f"  行{i} ERR: {e}")

        # 看分页器总条数
        print("\n=== 分页器 ===")
        try:
            pag = new_page.locator(".n-pagination").first
            total = pag.locator(".n-pagination__total, [class*='total']").count()
            if total > 0:
                txt = pag.locator(".n-pagination__total, [class*='total']").first.inner_text()
                print(f"  总数显示: {txt}")
            print(f"  分页器 HTML 前 500: {pag.evaluate('el => el.outerHTML')[:500]}")
        except Exception as e:
            print(f"  ERR: {e}")

    finally:
        mgr.close()


if __name__ == "__main__":
    main()
