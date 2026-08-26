"""探查 元数据管理-对象类 页面结构"""
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

        # 点 元数据管理 父菜单
        print("[probe] 点击 '元数据管理' 父菜单...")
        new_page.locator(".n-menu-item-content").filter(has_text="元数据管理").first.click()
        new_page.wait_for_timeout(1000)

        # 看子菜单
        print("\n=== 元数据管理 子菜单 ===")
        items = new_page.locator(".n-menu-item-content")
        cnt = items.count()
        for i in range(cnt):
            try:
                txt = items.nth(i).inner_text().strip()
                vis = items.nth(i).is_visible()
                if vis and txt:
                    print(f"  [{i}] '{txt[:80]}'")
            except Exception:
                pass

        # 点 对象类 子菜单
        print("\n[probe] 点击 '对象类' 子菜单...")
        new_page.locator(".n-menu-item-content").filter(has_text="对象类").first.click()
        new_page.wait_for_timeout(2500)
        new_page.wait_for_load_state("networkidle", timeout=15000)
        print(f"[probe] URL: {new_page.url}")

        out_dir = ROOT / "reports" / "probe_metadata"
        out_dir.mkdir(parents=True, exist_ok=True)
        new_page.screenshot(path=str(out_dir / "object_class.png"), full_page=True)

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
            (".n-checkbox", ".n-checkbox"),
            (".n-radio", ".n-radio"),
            (".n-select", ".n-select"),
            (".n-tree", ".n-tree"),
        ]
        for sel, label in candidates:
            try:
                cnt = new_page.locator(sel).count()
                vis = 0
                for i in range(min(cnt, 10)):
                    try:
                        if new_page.locator(sel).nth(i).is_visible():
                            vis += 1
                    except Exception:
                        pass
                print(f"  {label:<25} total={cnt}, vis={vis}")
            except Exception as e:
                print(f"  {label:<25} ERR {e}")

        # 按钮文本
        print("\n=== 所有按钮文本 ===")
        btns = new_page.locator("button, .n-button__content")
        for i in range(min(btns.count(), 30)):
            try:
                txt = btns.nth(i).inner_text().strip()
                vis = btns.nth(i).is_visible()
                if vis and txt:
                    print(f"  [{i}] '{txt[:60]}'")
            except Exception:
                pass

        # 输入框
        print("\n=== 所有输入框 ===")
        inputs = new_page.locator("input")
        for i in range(min(inputs.count(), 20)):
            try:
                vis = inputs.nth(i).is_visible()
                ph = inputs.nth(i).get_attribute("placeholder") or ""
                typ = inputs.nth(i).get_attribute("type") or ""
                if vis:
                    print(f"  [{i}] placeholder='{ph}'  type='{typ}'")
            except Exception:
                pass

        # 表格列头
        print("\n=== 表格列头 ===")
        try:
            headers = new_page.locator(".n-data-table-th__title")
            for i in range(headers.count()):
                txt = headers.nth(i).inner_text().strip()
                print(f"  [{i}] '{txt}'")
        except Exception as e:
            print(f"  ERR: {e}")

        # 表格第一行数据示例
        print("\n=== 表格第一行 ===")
        try:
            first_row = new_page.locator(".n-data-table-tbody tr").first
            cells = first_row.locator("td")
            for i in range(cells.count()):
                txt = cells.nth(i).inner_text().strip()
                print(f"  td[{i}] '{txt[:80]}'")
        except Exception as e:
            print(f"  ERR: {e}")

        # dump 主内容区 HTML
        try:
            main_html = new_page.locator(".n-layout-content").first.evaluate("el => el.innerHTML")
            (out_dir / "object_class.html").write_text(main_html[:50000], encoding="utf-8")
            print(f"\n[probe] 主内容区 HTML 已存: {out_dir / 'object_class.html'}  len={len(main_html)}")
        except Exception as e:
            print(f"\n[probe] dump HTML ERR: {e}")

        print(f"\n[probe] 完成。产物目录: {out_dir}")
    finally:
        mgr.close()


if __name__ == "__main__":
    main()
