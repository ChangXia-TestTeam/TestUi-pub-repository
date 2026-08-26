"""探查 元数据管理-属性结构 页面结构 + 新增弹窗 + 操作按钮 class"""
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

        if "login" in page.url or page.locator("input[placeholder*='账号']").count() > 0:
            auth_cfg = config.auth_config()
            LoginPage(page).login(auth_cfg.get("username", ""), auth_cfg.get("password", ""))
            mgr.save_auth_state()
            page.wait_for_load_state("networkidle", timeout=30000)
            page.wait_for_timeout(1500)

        new_page = HomePage(page).click_data_platform()
        new_page.wait_for_timeout(3000)
        if "login" in new_page.url:
            auth_cfg = config.auth_config()
            LoginPage(new_page).login(auth_cfg.get("username", ""), auth_cfg.get("password", ""))
            new_page.wait_for_load_state("networkidle", timeout=30000)
            new_page.wait_for_timeout(2000)

        # 等 SPA 路由完成
        for _ in range(30):
            cur_url = new_page.url
            if "/monitor/home" in cur_url or "/metadata" in cur_url:
                break
            try:
                new_page.locator(".n-layout-sider, .n-menu").first.wait_for(
                    state="visible", timeout=1000)
                break
            except Exception:
                new_page.wait_for_timeout(500)

        # 导航到属性结构（带重试）
        print("[probe] 点击 元数据管理 父菜单...")
        for attempt in range(3):
            try:
                new_page.locator(".n-menu-item-content").filter(
                    has_text="元数据管理").first.wait_for(state="visible", timeout=10000)
                new_page.locator(".n-menu-item-content").filter(
                    has_text="元数据管理").first.click()
                break
            except Exception:
                new_page.wait_for_timeout(1500)
        new_page.wait_for_timeout(1000)

        print("[probe] 点击 属性结构 子菜单...")
        try:
            new_page.locator(".n-menu-item-content").filter(
                has_text="属性结构").first.wait_for(state="visible", timeout=8000)
        except Exception:
            pass
        new_page.locator(".n-menu-item-content").filter(has_text="属性结构").first.click()
        new_page.wait_for_timeout(2500)
        try:
            new_page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        print(f"[probe] URL: {new_page.url}")

        out_dir = ROOT / "reports" / "probe_property"
        out_dir.mkdir(parents=True, exist_ok=True)
        new_page.screenshot(path=str(out_dir / "list.png"), full_page=True)

        # 1. 表格列头
        print("\n=== 表格列头 ===")
        headers = new_page.evaluate("""() => {
            const hs = Array.from(document.querySelectorAll('.n-data-table-th__title'));
            return hs.map(h => h.textContent.trim());
        }""")
        print(headers)

        # 2. 操作列按钮 class（第一行）
        print("\n=== 操作列按钮 ===")
        btns = new_page.evaluate("""() => {
            const rows = document.querySelectorAll('.n-data-table-tbody tr');
            if (rows.length === 0) return [];
            const lastTd = rows[0].querySelectorAll('td');
            const opTd = lastTd[lastTd.length - 1];
            const btns = opTd.querySelectorAll('.n-button');
            return Array.from(btns).map((b, i) => ({
                idx: i,
                cls: b.className,
            }));
        }""")
        for b in btns:
            print(f"  [{b['idx']}] {b['cls']}")

        # 3. 顶部按钮
        print("\n=== 顶部按钮 ===")
        top_btns = new_page.evaluate("""() => {
            const btns = document.querySelectorAll('button, .n-button');
            return Array.from(btns).filter(b => b.offsetParent !== null).map(b => ({
                cls: b.className.substring(0, 80),
                text: b.textContent.trim().substring(0, 20),
            })).filter(b => b.text);
        }""")
        for b in top_btns[:15]:
            print(f"  text='{b['text']}' cls={b['cls']}")

        # 4. 输入框 placeholder
        print("\n=== 可见输入框 ===")
        inputs = new_page.evaluate("""() => {
            const ins = Array.from(document.querySelectorAll('input'));
            return ins.filter(i => i.offsetParent !== null).map(i => ({
                ph: i.getAttribute('placeholder') || '',
                type: i.getAttribute('type') || '',
            }));
        }""")
        for i in inputs[:10]:
            print(f"  placeholder='{i['ph']}' type='{i['type']}'")

        # 5. 分页器
        print("\n=== 分页器文本 ===")
        pag_text = new_page.evaluate("""() => {
            const p = document.querySelector('.n-pagination');
            return p ? p.textContent.trim() : 'NO_PAGINATION';
        }""")
        print(f"  {pag_text}")

        # 6. 点击新增按钮，探查弹窗
        print("\n[probe] 点击新增按钮...")
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
                return {label: labelText, required: required, input: inputTag};
            });
        }""")
        print(modal_fields)

        # 弹窗按钮
        print("\n=== 弹窗按钮 ===")
        modal_btns = new_page.evaluate("""() => {
            const modal = document.querySelector('.n-modal');
            if (!modal || modal.offsetParent === null) return [];
            const btns = modal.querySelectorAll('button, .n-button');
            return Array.from(btns).filter(b => b.offsetParent !== null).map(b => ({
                text: b.textContent.trim().substring(0, 20),
                cls: b.className.substring(0, 60),
            }));
        }""")
        for b in modal_btns:
            print(f"  text='{b['text']}' cls={b['cls']}")

        # 弹窗标题
        title = new_page.evaluate("""() => {
            const modal = document.querySelector('.n-modal');
            if (!modal) return '';
            const t = modal.querySelector('.n-modal__title, .n-card-header__title, .n-modal-title');
            return t ? t.textContent.trim() : '';
        }""")
        print(f"\n=== 弹窗标题: '{title}' ===")

        # 7. 输入框 placeholder（弹窗内）
        print("\n=== 弹窗内输入框 ===")
        modal_inputs = new_page.evaluate("""() => {
            const modal = document.querySelector('.n-modal');
            if (!modal) return [];
            const ins = modal.querySelectorAll('input, textarea');
            return Array.from(ins).map(i => ({
                ph: i.getAttribute('placeholder') || '',
                tag: i.tagName,
                maxlength: i.getAttribute('maxlength') || '',
            }));
        }""")
        for i in modal_inputs:
            print(f"  tag={i['tag']} placeholder='{i['ph']}' maxlength={i['maxlength']}")

        print(f"\n[probe] 完成。产物目录: {out_dir}")
    finally:
        mgr.close()


if __name__ == "__main__":
    main()
