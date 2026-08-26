"""探查 对象类 新增弹窗 + 行内操作按钮"""
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
            LoginPage(page).login(
                auth_cfg.get("username", ""),
                auth_cfg.get("password", ""),
            )
            mgr.save_auth_state()
            page.wait_for_load_state("networkidle", timeout=30000)
            page.wait_for_timeout(1500)

        new_page = HomePage(page).click_data_platform()
        new_page.wait_for_timeout(2500)
        new_page.wait_for_load_state("networkidle", timeout=15000)

        if "login" in new_page.url:
            auth_cfg = config.auth_config()
            LoginPage(new_page).login(
                auth_cfg.get("username", ""),
                auth_cfg.get("password", ""),
            )
            new_page.wait_for_load_state("networkidle", timeout=30000)
            new_page.wait_for_timeout(2000)

        # 进入对象类
        new_page.locator(".n-menu-item-content").filter(has_text="元数据管理").first.click()
        new_page.wait_for_timeout(800)
        new_page.locator(".n-menu-item-content").filter(has_text="对象类").first.click()
        new_page.wait_for_timeout(2500)
        new_page.wait_for_load_state("networkidle", timeout=15000)
        print(f"[probe] URL: {new_page.url}")

        out_dir = ROOT / "reports" / "probe_metadata"
        out_dir.mkdir(parents=True, exist_ok=True)

        # 看操作列有哪些按钮
        print("\n=== 操作列按钮（第1行）===")
        try:
            row = new_page.locator(".n-data-table-tbody tr").first
            ops = row.locator("td").last.locator("button, .n-button")
            print(f"  第1行操作列按钮数: {ops.count()}")
            for i in range(ops.count()):
                try:
                    txt = ops.nth(i).inner_text().strip()
                    vis = ops.nth(i).is_visible()
                    title = ops.nth(i).get_attribute("title") or ""
                    print(f"    [{i}] text='{txt}' vis={vis} title='{title}'")
                except Exception as e:
                    print(f"    [{i}] ERR: {e}")
        except Exception as e:
            print(f"  ERR: {e}")

        # 查看筛选区所有 select 选项
        print("\n=== 筛选区 select 选项 ===")
        try:
            selects = new_page.locator(".n-data-table").locator("xpath=preceding-sibling::*").locator(".n-select")
            print(f"  筛选区 select 数: {selects.count()}")
            for i in range(selects.count()):
                try:
                    base = selects.nth(i)
                    # select 前的 label
                    label = base.locator("xpath=preceding-sibling::*[1]").inner_text().strip()
                    print(f"  select[{i}] label='{label}'")
                except Exception as e:
                    print(f"  select[{i}] ERR: {e}")
        except Exception as e:
            print(f"  ERR: {e}")

        # 直接看筛选 form-item 的所有 label
        print("\n=== 筛选 form-item label ===")
        try:
            form_items = new_page.locator(".n-form-item")
            for i in range(form_items.count()):
                try:
                    label = form_items.nth(i).locator(".n-form-item-label").inner_text().strip()
                    inputs = form_items.nth(i).locator("input").count()
                    sels = form_items.nth(i).locator(".n-base-selection").count()
                    print(f"  form_item[{i}] label='{label}'  inputs={inputs}  selects={sels}")
                except Exception as e:
                    print(f"  form_item[{i}] ERR: {e}")
        except Exception as e:
            print(f"  ERR: {e}")

        # 点新增按钮看弹窗
        print("\n=== 点击新增按钮 ===")
        new_page.locator("button:has-text('新增')").first.click()
        new_page.wait_for_timeout(1000)

        # 找弹窗
        modal_sels = [".n-modal", ".n-dialog", ".n-drawer", ".n-card:has-text('新增对象类')", ".n-card:has-text('对象类')"]
        for sel in modal_sels:
            try:
                m = new_page.locator(sel)
                if m.count() > 0 and m.first.is_visible():
                    print(f"  找到弹窗: {sel}")
                    # 弹窗内 form-item
                    fis = m.first.locator(".n-form-item")
                    print(f"  弹窗 form-item 数: {fis.count()}")
                    for i in range(fis.count()):
                        try:
                            label = fis.nth(i).locator(".n-form-item-label").inner_text().strip()
                            inputs = fis.nth(i).locator("input").count()
                            sels = fis.nth(i).locator(".n-base-selection").count()
                            tas = fis.nth(i).locator("textarea").count()
                            radios = fis.nth(i).locator(".n-radio").count()
                            print(f"    [{i}] label='{label}'  inputs={inputs}  selects={sels}  textarea={tas}  radio={radios}")
                        except Exception as e:
                            print(f"    [{i}] ERR: {e}")

                    # 弹窗底部按钮
                    btns = m.first.locator("button")
                    print(f"  弹窗按钮数: {btns.count()}")
                    for i in range(btns.count()):
                        try:
                            txt = btns.nth(i).inner_text().strip()
                            vis = btns.nth(i).is_visible()
                            if vis and txt:
                                print(f"    [{i}] '{txt}'")
                        except Exception:
                            pass

                    new_page.screenshot(path=str(out_dir / "create_modal.png"), full_page=False)
                    break
            except Exception as e:
                print(f"  {sel} ERR: {e}")

        print(f"\n[probe] 完成。产物目录: {out_dir}")
    finally:
        mgr.close()


if __name__ == "__main__":
    main()
