"""临时探查操作列按钮结构"""
import re
from pathlib import Path

html = Path('reports/probe_metadata/object_class.html').read_text(encoding='utf-8')

# 找表格 tbody 部分
idx = html.find('n-data-table-tbody')
if idx < 0:
    print("未找到 n-data-table-tbody")
    raise SystemExit(0)

snippet = html[idx:idx + 10000]

# 找所有 n-button 相关 class
classes = re.findall(r'class="([^"]*n-button[^"]*)"', snippet)
print("=== n-button classes (操作列) ===")
for c in sorted(set(classes)):
    print(f"  {c}")

# 找第一行操作列的所有按钮（取最后一个 td 中的 button）
print("\n=== 操作列按钮 HTML 片段 ===")
# 找所有 td 内容
tds = re.findall(r'<td[^>]*>(.*?)</td>', snippet, re.DOTALL)
print(f"共 {len(tds)} 个 td")
# 看最后一个 td（通常是操作列）
if tds:
    last_td = tds[-1] if len(tds) > 9 else tds[-1]
    # 提取 button 标签
    btn_matches = re.findall(r'<button[^>]*>.*?</button>', last_td, re.DOTALL)
    print(f"操作列 button 数量: {len(btn_matches)}")
    for i, b in enumerate(btn_matches[:6]):
        # 取 class 属性
        cls_m = re.search(r'class="([^"]*)"', b)
        cls = cls_m.group(1) if cls_m else ""
        # 取 title/aria-label
        title_m = re.search(r'(?:title|aria-label)="([^"]*)"', b)
        title = title_m.group(1) if title_m else ""
        # 取内部文本
        inner = re.sub(r'<[^>]+>', '', b).strip()
        print(f"  [{i}] class='{cls[:80]}' title='{title}' text='{inner[:30]}'")

# 找 n-button--* 后缀
print("\n=== n-button--* 类型 ===")
types = re.findall(r'(n-button--\w+-type)', snippet)
for t in sorted(set(types)):
    print(f"  {t}")
