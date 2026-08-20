# 数据平台 UI 自动化测试框架

> **架构**：Python + Playwright + Pytest + Allure + POM + **AI 引擎**
> **设计模式**：市面流行的 AI 驱动 UI 自动化（Midscene / zeroStep / AutoPlaywright 风格）
> **Pipeline 流程**（照搬 API 框架链路）：导入文档 → 文档解析 → **AI 生成用例** → 执行用例 → 输出结果 → 生成报告 → 推送钉钉 → CI/CD
> **输入端**：PRD 文档 / 蓝湖地址 / 原型截图（支持混合交叉印证）

## 一、目录结构

```
test_ui_sjpt/
├── config/                           # 配置文件
│   ├── config.yaml                  # 测试环境 & 账号 & 浏览器 & AI 引擎配置
│   └── notification.json             # 钉钉机器人配置
├── ai/                               # 🤖 AI 引擎层（核心）
│   ├── llm_client.py                 # LLM 调用封装（trae 对话接管 / api 直调）
│   ├── self_healing.py               # 自愈定位器（Midscene 风格，失败自动找替代定位）
│   ├── generators/                   # AI 生成器
│   │   ├── page_object_gen.py        # 需求 → Page Object 代码
│   │   ├── test_case_gen.py          # 需求 → pytest 用例代码
│   │   └── locator_gen.py            # 截图/标注 → Playwright 定位
│   ├── prompts/                      # Prompt 模板库
│   │   ├── page_object.md
│   │   ├── test_case.md
│   │   └── locator.md
│   ├── .pending/                     # trae 模式待执行 AI 任务
│   └── .done/                        # 已完成 AI 任务
├── parsers/                          # 📑 输入端解析层（独立于 utils）
│   ├── requirement_model.py          # 统一 UIRequirement 数据模型
│   ├── prd_parser.py                 # PRD 解析（docx/pdf/md）
│   ├── lanhu_parser.py               # 蓝湖解析（在线/导出）
│   ├── screenshot_parser.py          # 原型截图解析
│   └── __init__.py                   # parse() 统一调度
├── pages/                            # POM 页面对象层（AI 生成或手写）
│   ├── base_page.py                  # 基类（封装 Playwright + 自愈钩子）
│   ├── login/                        # 登录模块
│   └── data_integration/             # 数据集成模块
├── common/                           # 公共组件（与 pages/ 同级）
│   ├── navigation.py                 # 导航/菜单
│   └── dialog.py                     # 通用对话框/Toast
├── utils/                            # 基础设施（纯工具）
│   ├── browser.py                    # Playwright 浏览器管理
│   ├── auth.py                       # SSO 登录
│   ├── config.py                     # 配置读取
│   ├── assertions.py                 # UI 断言
│   ├── screenshot.py                 # 截图管理
│   ├── locator_parser.py             # 定位规范化
│   ├── excel_export.py               # Excel 导出（PASS 绿底/FAIL 红底）
│   └── dingtalk.py                   # 钉钉推送
├── tests/                            # 测试用例（AI 生成或手写）
│   ├── conftest.py                   # pytest fixtures（page/登录态/失败截图）
│   ├── test_login.py
│   └── test_data_integration.py
├── scripts/
│   ├── run_pipeline.py               # 🚀 8 阶段一键 Pipeline
│   └── gen_templates.py              # 生成 Excel 模板
├── UI_input_files/                   # 输入端
│   ├── prd/                          # PRD 文档
│   ├── screenshots/                  # 原型截图
│   └── lanhu/                        # 蓝湖导出
├── UI_output_files/                  # 输出（Excel）
│   ├── test_ui_results/
│   └── bug_list/
├── reports/                          # 运行产物
│   ├── allure-results/
│   ├── allure-report/
│   ├── screenshots/                  # 失败截图
│   └── self_healing/                 # 自愈记录
├── .github/workflows/test.yml        # CI/CD
├── requirements.txt
├── pytest.ini
└── README.md
```

## 二、核心设计：AI 驱动 UI 自动化

对标 Midscene / zeroStep / AutoPlaywright 的设计模式，三层分离：

```
输入端(parsers) → AI 引擎(ai) → 制品(pages/tests) → 执行(utils+playwright)
   PRD/蓝湖/截图    生成器+自愈      Page Object+用例      自愈+截图+断言
```

### 2.1 Pipeline 8 阶段（照搬 API 框架链路 + AI 生成阶段）

| 阶段 | 说明 | 产物 |
|------|------|------|
| [1] 导入文档 | 把 PRD/蓝湖/截图放进 `UI_input_files/` | 输入文件清单 |
| [2] 文档解析 | `parsers/` → 统一 `UIRequirement` | `parsed_requirement.json` |
| [3] **AI 生成用例** | `ai/generators` → Page Object + pytest 用例 | `pages/*.py` `tests/*.py` |
| [4] 执行用例 | pytest + Playwright（含自愈） | `allure-results/` |
| [5] 输出结果 | Excel（PASS 绿底 / FAIL 红底） | `UI_output_files/` |
| [6] 生成报告 | Allure HTML | `allure-report/index.html` |
| [7] 推送钉钉 | 通过率 + 失败 Top5 + 自愈统计 | 钉钉消息 |
| [8] CI/CD | GitHub Actions（push 触发） | 报告/Excel Artifact |

### 2.2 AI 引擎层（核心差异点）

| 组件 | 作用 | 对标市面工具 |
|------|------|-------------|
| `ai/llm_client.py` | 统一 LLM 调用，支持 trae 对话接管 / api 直调 | 通用 |
| `ai/self_healing.py` | 定位失败时自动找替代定位并回填 | Healenium / Midscene 自愈 |
| `ai/generators/page_object_gen.py` | 需求 → Page Object 代码 | AutoPlaywright |
| `ai/generators/test_case_gen.py` | 需求 → pytest 用例代码 | QA Wolf |
| `ai/generators/locator_gen.py` | 截图 → 视觉识别定位（需 vision 模型） | Midscene 视觉理解 |
| `ai/prompts/*.md` | 标准化 Prompt 模板 | Prompt 工程最佳实践 |

### 2.3 多输入端（PRD / 蓝湖 / 原型截图）

`parsers/` 包实现 4 种输入方式，统一输出 `UIRequirement` 结构：

| 方式 | 输入 | 解析逻辑 |
|------|------|----------|
| A | PRD 文档（docx/pdf/md） | 按标题层级切分页面段落，提取元素清单与校验点 |
| B | 蓝湖分享地址 / 本地导出 | 在线抓取或读取导出 JSON/HTML |
| C | 原型截图（png/jpg） | 每张截图视为一个页面，AI 补充定位 |
| D | 混合输入 | 同名页面交叉印证（PRD 描述 + 蓝湖元素 + 截图证据） |

配置 `config.yaml` 的 `input.mode` 选择解析方式。

### 2.4 自愈机制

`pages/base_page.py` 的 `click/fill` 失败时自动触发 `ai/self_healing`：
1. 从原定位派生语义候选（role/text/aria-label/placeholder）
2. 逐个试探命中
3. 仍失败则 LLM 基于页面快照重新生成定位
4. 命中后记录到 `reports/self_healing/`，并在 Allure 附件展示

开关：`config.ai.self_healing`

## 三、快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt
python -m playwright install chromium

# 2. 配置 config/config.yaml（base_url/账号/AI 模式）

# 3. 生成 Excel 模板（首次）
python scripts/gen_templates.py

# 4. 一键全链路（8 阶段）
python scripts/run_pipeline.py

# 跳过 AI 生成，直接跑已有用例
python scripts/run_pipeline.py --skip-gen

# 只生成用例不执行（trae 模式：等对话 AI 产出代码）
python scripts/run_pipeline.py --gen-only
```

## 四、AI 引擎两种模式

| 模式 | 配置 | 适用场景 |
|------|------|---------|
| `trae` | `ai.mode: "trae"`（默认） | 在 Trae 对话中，生成器落盘 prompt 到 `ai/.pending/`，由对话 AI 产出代码。零额外配置 |
| `api` | `ai.mode: "api"` + `openai_base_url` + `api_key` | HTTP 直调，CI 无人值守 |

## 五、输入端使用

### 方式 A：PRD 文档
把 `.docx` / `.pdf` / `.md` 放到 `UI_input_files/prd/`

### 方式 B：蓝湖
在线：配置 `config.yaml` 的 `input.lanhu_base_url`
本地：把蓝湖导出 JSON/HTML 放到 `UI_input_files/lanhu/`

### 方式 C：原型截图
把 `.png` / `.jpg` 放到 `UI_input_files/screenshots/`

> 提示语：「读取 PRD/蓝湖/截图，解析出页面结构与元素，让 AI 生成 Page Object 和测试用例」

## 六、测试执行

```bash
python scripts/run_pipeline.py              # 一键全链路
pytest tests/test_login.py -v --tb=short     # 单模块
pytest tests/ -m P0 -v                        # P0 冒烟
pytest tests/test_login.py -v -s --tb=long   # 调试
pytest tests/ -n auto                         # 并行
```

## 七、报告输出

- **Allure HTML**：`reports/allure-report/index.html`
- **Excel 结果**：`UI_output_files/test_ui_results/`（PASS 绿底 / FAIL 红底加粗）
- **Bug 清单**：`UI_output_files/bug_list/`（标题 `【{模块}】{用例名} UI → {错误分类} {错误消息}`，可直接导入 TAPD）
- **失败截图**：`reports/screenshots/` + Allure 附件
- **自愈记录**：`reports/self_healing/`（统计被修复的定位数）

## 八、迁移到新项目

修改 4 处即可复用框架：
1. `config/config.yaml`：base_url / 账号 / 登录路径 / AI 配置
2. `config/notification.json`：钉钉机器人
3. 输入端：把新项目 PRD/蓝湖/截图放进 `UI_input_files/`
4. `pages/` `tests/`：AI 生成或手写业务页

框架核心（`ai/`、`parsers/`、`utils/`、`conftest.py`、`run_pipeline.py`）跨项目复用。
