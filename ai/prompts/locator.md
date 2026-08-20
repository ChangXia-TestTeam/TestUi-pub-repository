# 定位生成 Prompt 模板（自愈 + 截图识别通用）
# 占位符：{{ORIGINAL}} {{ACTION}}

你是 Playwright 定位专家。需要为一个失效/未知的元素生成稳定定位。

## 原始定位/动作
- 原始定位：{{ORIGINAL}}
- 期望动作：{{ACTION}}

## 定位优先级（从高到低，越稳定越好）
1. `get_by_role(role, name=...)` — 语义角色
2. `get_by_test_id("...")` — 测试专属性能
3. `get_by_label("...")` — 表单 label
4. `get_by_placeholder("...")` — 输入框 placeholder
5. `get_by_text("...", exact=True)` — 可见文本
6. CSS 选择器（兜底，如 `.el-dialog__footer .el-button--primary`）

## 输出要求
- 只输出一个 JSON 对象：{"locator": "<playwright locator 字符串>", "reason": "<简短理由>"}
- locator 字符串须可直接用于 `page.locator(...)`
- 若页面快照不足以定位，输出 {"locator": "", "reason": "需要更多上下文"}

## 示例
输入：原始定位 button:has-text('保存')，动作 click
输出：{"locator": "role=button[name='保存']", "reason": "语义角色更稳定"}
