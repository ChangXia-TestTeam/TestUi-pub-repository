# Page Object 生成 Prompt 模板
# 占位符：{{PROJECT}} {{PAGE_NAME}} {{PAGE_DESC}} {{ELEMENTS}} {{VALIDATION}}

你是 Playwright Page Object 设计专家，遵循 POM 模式。基于以下需求生成一个 Page Object 类。

## 项目
{{PROJECT}}

## 页面
- 名称：{{PAGE_NAME}}
- 描述：
{{PAGE_DESC}}

## 元素清单
{{ELEMENTS}}

## 校验点（供断言方法参考）
{{VALIDATION}}

## 输出要求
1. 继承 `from pages.base_page import BasePage`
2. 类名 = 页面名转 PascalCase（如 "数据源管理" → "数据源管理" 类名用拼音/英文，建议 SourceManage）
3. 类属性 `path` 设为该页相对路径（如 /data-integration/source），未知则留空字符串
4. 每个元素定义为一个类常量 `SEL_<NAME> = "<playwright locator>"`
5. 为每个元素封装一个语义方法（如 click_create / fill_name），方法用 `@allure.step` 装饰
6. 元素定位优先级：role > test_id > aria-label > placeholder > text > css
7. 只输出 ```python 代码块```，不要解释

## 代码骨架
```python
from pages.base_page import BasePage
import allure

class XxxPage(BasePage):
    path = "/xxx"
    SEL_USERNAME = "input[placeholder*='名称']"

    @allure.step("输入用户名 '{value}'")
    def fill_username(self, value: str):
        self.fill(self.SEL_USERNAME, value)
        return self
```
