# 测试用例生成 Prompt 模板
# 占位符：{{PROJECT}} {{PAGE_NAME}} {{PAGE_DESC}} {{VALIDATION}} {{PAGE_IMPORTS}}

你是 pytest + Playwright 测试用例专家。基于以下页面需求与已有 Page Object，生成 pytest 用例。

## 项目
{{PROJECT}}

## 页面
- 名称：{{PAGE_NAME}}
- 描述：
{{PAGE_DESC}}

## 校验点（必须覆盖到的断言）
{{VALIDATION}}

## 可用的 Page Object import
{{PAGE_IMPORTS}}

## 输出要求
1. 用 `@allure.feature` 标注模块、`@allure.story` 标注场景、`@allure.severity` 标注严重级别
2. 用 `@pytest.mark.P0` / `P1` / `P2` 标注优先级
3. 用例方法签名 `def test_xxx(self, page):`，直接使用 fixture 注入的 page
4. 每个用例结尾调用 `<PageObj>(page).screenshot("用例名")` 留证据
5. 一个用例只验证一个校验点；失败信息要清晰
6. 至少覆盖：正常主流程(P0)、必填校验(P1)、边界/异常(P2)
7. 只输出 ```python 代码块```，不要解释

## 代码骨架
```python
import pytest
import allure
from pages.xxx.xxx_page import XxxPage

@allure.feature("{{PAGE_NAME}}")
class TestXxx:
    @allure.story("主流程")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_main_flow(self, page):
        p = XxxPage(page)
        p.goto_xxx()
        # ...操作
        p.expect_visible(p.SEL_TABLE, "列表可见")
        p.screenshot("main_flow")
```
