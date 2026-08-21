"""
🚀 一键全链路入口 - AI 驱动 UI 自动化 Pipeline
路径: scripts/run_pipeline.py

流程照搬 API 框架的链路，但设计模式采用市面流行的 AI 驱动 UI 自动化
（Midscene / zeroStep / AutoPlaywright）：
    [1] 导入文档       把 PRD/蓝湖/截图放进 UI_input_files/
    [2] 文档解析       parsers/ → 统一 UIRequirement 结构
    [3] AI 生成用例    ai/generators → Page Object + pytest 用例（LLM）
    [4] 执行用例       pytest + Playwright（含自愈）
    [5] 输出结果       Excel（PASS 绿底/FAIL 红底）
    [6] 生成报告       Allure HTML
    [7] 推送钉钉       通过率 + 失败 Top5
    [8] CI/CD          GitHub Actions（push 触发，本脚本本地等价执行）

用法：
    python scripts\\run_pipeline.py
    python scripts\\run_pipeline.py --skip-gen   # 跳过 AI 生成阶段，直接跑已有用例
    python scripts\\run_pipeline.py --gen-only   # 只生成用例不执行
"""
from __future__ import annotations

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils import config


# ============================================================
# [1] 导入文档
# ============================================================
def stage1_import():
    print("[1/8] 📥 检查输入端文档...")
    inp = config.input_config()
    dirs = {
        "prd": ROOT / inp.get("prd_dir", "UI_input_files/prd"),
        "lanhu": ROOT / inp.get("lanhu_dir", "UI_input_files/lanhu"),
        "screenshot": ROOT / inp.get("screenshot_dir", "UI_input_files/screenshots"),
    }
    for name, d in dirs.items():
        if d.exists():
            files = [f for f in d.iterdir() if not f.name.startswith(".") and f.suffix]
            print(f"[1/8]   {name}: {len(files)} 个文件 → {d}")
        else:
            print(f"[1/8]   {name}: 目录不存在（{d}）")
    return {"input_dirs": {k: str(v) for k, v in dirs.items()}}


# ============================================================
# [2] 文档解析 → UIRequirement
# ============================================================
def stage2_parse():
    print("[2/8] 📑 解析文档为统一 UIRequirement...")
    from parsers import parse
    t0 = time.time()
    try:
        req = parse()
    except Exception as e:
        print(f"[2/8] ❌ 解析异常: {e}")
        print(f"[2/8]    💡 检查 UI_input_files/ 下文件格式是否正确，或查看上方解析进度定位卡在哪一步")
        raise
    out_path = ROOT / "UI_input_files" / "parsed_requirement.json"
    req.to_json(str(out_path))
    print(f"[2/8] ✅ mode={req.input_mode}, 解析到 {len(req.pages)} 个页面/场景 ({time.time()-t0:.1f}s)")
    print(f"[2/8]    产物: {out_path}")
    # 明细
    for i, pg in enumerate(req.pages, 1):
        print(f"[2/8]    [{i}/{len(req.pages)}] {pg.name}  elements={len(pg.elements)} vps={len(pg.validation_points)} desc_len={len(pg.description)}")
    return req


# ============================================================
# [3] AI 生成用例（Page Object + 测试用例）
# ============================================================
def stage3_generate(req, gen_only: bool = False):
    print("[3/8] 🤖 AI 生成 Page Object + 测试用例...")
    ai_cfg = config.get("ai", {}) or {}
    if not ai_cfg.get("enabled", True):
        print("[3/8] ⏭️  config.ai.enabled=false，跳过 AI 生成（使用已有用例）")
        return {"page_files": [], "test_files": [], "skipped": True}
    if not req.pages:
        print("[3/8] ⏭️  无解析结果，跳过生成（使用已有用例）")
        return {"page_files": [], "test_files": [], "skipped": True}

    from ai.generators import page_object_gen, test_case_gen
    total = len(req.pages)
    print(f"[3/8]   将为 {total} 个页面生成 Page Object + 测试用例")
    t0 = time.time()

    try:
        page_files = page_object_gen.generate(req)
    except Exception as e:
        print(f"[3/8] ❌ Page Object 生成异常: {e}")
        page_files = []

    try:
        test_files = test_case_gen.generate(req, page_files=page_files)
    except Exception as e:
        print(f"[3/8] ❌ 测试用例生成异常: {e}")
        test_files = []

    print(f"[3/8]   Page Object 生成 {len(page_files)} 个文件")
    for pf in page_files:
        print(f"[3/8]     📄 {pf}")
    print(f"[3/8]   测试用例生成 {len(test_files)} 个文件")
    for tf in test_files:
        print(f"[3/8]     📄 {tf}")

    # trae 模式下生成器会落盘 prompt 到 ai/.pending，需对话 AI 接管
    pending = list((ROOT / "ai" / ".pending").glob("*.txt")) if (ROOT / "ai" / ".pending").exists() else []
    if pending:
        print(f"[3/8] ⚠️  检测到 {len(pending)} 个待执行 AI 任务（ai/.pending/）")
        for pt in pending:
            print(f"[3/8]     📋 {pt}  ({pt.stat().st_size} chars)")
        print(f"[3/8]    → 在 Trae 对话中读取这些任务并产出代码，或配置 config.ai.mode=api 无人值守")
        if gen_only:
            print(f"[3/8] --gen-only 模式：停止后续阶段 ({time.time()-t0:.1f}s)，等待 AI 产出代码")
            return {"page_files": page_files, "test_files": test_files, "pending": len(pending)}
    print(f"[3/8] ⏱ 生成阶段耗时 {time.time()-t0:.1f}s")
    return {"page_files": page_files, "test_files": test_files, "pending": len(pending)}


# ============================================================
# [4] 执行用例（pytest + Playwright，含自愈）
# ============================================================
def stage4_execute():
    print("[4/8] 🧪 执行 pytest 测试用例（含自愈）...")
    cmd = [
        sys.executable, "-m", "pytest",
        str(ROOT / "tests"),
        "-v", "--tb=short",
        "--alluredir", str(ROOT / "reports" / "allure-results"),
        "--clean-alluredir",
        "-n", "2",
    ]
    if config.get("retry.max_retries", 1) > 1:
        cmd += ["--reruns", str(config.get("retry.max_retries"))]
    proc = subprocess.run(cmd, cwd=str(ROOT))
    return {"exit_code": proc.returncode}


# ============================================================
# [5] 输出结果（Excel）
# ============================================================
def stage5_results(stats: dict):
    print("[5/8] 📄 导出 Excel 结果（PASS 绿底/FAIL 红底）...")
    try:
        from utils.excel_export import export_results
        out = export_results(stats)
        print(f"[5/8] ✅ 全量结果: {out['results']}")
        print(f"[5/8] ✅ Bug 清单: {out['bug_list']}")
        return out
    except Exception as e:
        print(f"[5/8] ⚠️ Excel 导出失败: {e}")
        return {}


# ============================================================
# [6] 生成报告（Allure HTML + 自动启动 HTTP 服务器）
# ============================================================
def stage6_report():
    print("[6/8] 📈 生成 Allure HTML 报告...")
    out_dir = ROOT / "reports" / "allure-results"
    html_dir = ROOT / "reports" / "allure-report"

    # Windows 下 allure 是 .bat 文件，subprocess 默认不搜索 .bat 扩展名
    # 使用 shutil.which 解析完整路径后直接调用，避免 shell=True 导致 Java classpath 丢失
    import shutil
    allure_cmd = shutil.which("allure") or shutil.which("allure.bat") or "allure"

    try:
        subprocess.run(
            [allure_cmd, "generate", str(out_dir),
             "-o", str(html_dir), "--clean"],
            check=True,
        )
    except Exception as e:
        print(f"[6/8] ⚠️ Allure 生成失败（可能未安装 allure 命令行）: {e}")
        return ""

    # Allure 报告是 SPA，必须通过 HTTP 服务器托管，直接 file:// 打开会卡在 Loading
    report_port = 8088
    url = f"http://localhost:{report_port}"
    try:
        # 停掉可能残留的旧服务
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", report_port)) == 0:
                print(f"[6/8]   端口 {report_port} 已被占用，尝试释放...")
                # 不强制杀进程，给用户提示
        # 启动新服务器（后台）
        import subprocess as sp
        sp.Popen(
            [sys.executable, "-m", "http.server", str(report_port), "--directory", str(html_dir)],
            cwd=str(ROOT),
            creationflags=0x08000000,  # CREATE_NO_WINDOW (Windows)
        )
        print(f"[6/8] ✅ 报告已生成: {html_dir}")
        print(f"[6/8] 🌐 请通过 HTTP 访问（不要用 file:// 直接打开）:")
        print(f"[6/8]    {url}")
        return url
    except Exception as e:
        print(f"[6/8] ⚠️ HTTP 服务器启动失败: {e}")
        print(f"[6/8]    手动启动: python -m http.server {report_port} --directory {html_dir}")
        return str(html_dir / "index.html")


# ============================================================
# [7] 推送钉钉
# ============================================================
def stage7_dingtalk(stats: dict, excel_out: dict):
    print("[7/8] 📢 推送钉钉通知...")
    try:
        from utils.dingtalk import send_report
        # 附带自愈统计
        from ai.self_healing import stats as heal_stats
        stats["healing"] = heal_stats()
        resp = send_report(stats, excel_out)
        print(f"[7/8] {resp}")
        return resp
    except Exception as e:
        print(f"[7/8] ⚠️ 钉钉推送失败: {e}")
        return {"error": str(e)}


# ============================================================
# [8] CI/CD（GitHub Actions，本地等价）
# ============================================================
def stage8_cicd(stats: dict):
    print("[8/8] 🔄 CI/CD 阶段（GitHub Actions 由 push 触发，本地等价执行）...")
    wf = ROOT / ".github" / "workflows" / "test.yml"
    if wf.exists():
        print(f"[8/8]    工作流: {wf}")
        print(f"[8/8]    触发条件: push 到 main/develop / PR 到 main / workflow_dispatch")
        print(f"[8/8]    上传产物: Allure 报告 + Excel 结果（保留 30 天）")
    # Pipeline 通过条件：无 failed 且无 broken（skipped 不影响）
    failed = stats.get("failed", 0)
    broken = stats.get("broken", 0)
    passed = (failed == 0 and broken == 0)
    print(f"[8/8] {'✅ Pipeline 通过' if passed else '❌ Pipeline 失败（CI 将标红 + 钉钉告警）'}")
    return {"passed": passed}


# ============================================================
# 统计（执行后从 allure-results 汇总）
# ============================================================
def collect_stats() -> dict:
    """
    从 allure-results 汇总用例统计。
    处理 rerun 产生的重复记录：相同用例按 (name, fullName) 去重，
    最终状态以最后一条记录为准（rerun 成功则计为 passed）。
    """
    results_dir = ROOT / "reports" / "allure-results"
    case_map: dict[str, dict] = {}  # key: (name|fullName) → 最新一条记录
    if results_dir.exists():
        for f in results_dir.glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            status = d.get("status")
            if status not in ("passed", "failed", "broken", "skipped"):
                continue
            # 用例唯一键：name + fullName 组合，避免重名误合并
            key = f"{d.get('name', '')}|{d.get('fullName', '')}"
            # Allure 时间戳大的为最新结果（rerun 后的）
            ts = d.get("start", 0)
            if key not in case_map or ts >= case_map[key].get("_ts", 0):
                d["_ts"] = ts
                case_map[key] = d

    total = passed = failed = broken = skipped = 0
    failed_cases = []
    for d in case_map.values():
        status = d.get("status")
        name = d.get("name", "")
        full = d.get("fullName", "")
        total += 1
        if status == "passed":
            passed += 1
        elif status == "failed":
            failed += 1
            failed_cases.append({
                "name": name, "full": full,
                "status_message": _extract_status_msg(d),
            })
        elif status == "broken":
            broken += 1
            failed_cases.append({
                "name": name, "full": full,
                "status_message": _extract_status_msg(d),
            })
        elif status == "skipped":
            skipped += 1
    pass_rate = (passed / total * 100) if total else 0
    print(f"[stats] 通过率={pass_rate:.1f}% (total={total} pass={passed} fail={failed} broken={broken} skip={skipped})")
    return {
        "total": total, "passed": passed, "failed": failed,
        "broken": broken, "skipped": skipped,
        "pass_rate": round(pass_rate, 2),
        "failed_cases": failed_cases,
    }


def _extract_status_msg(d: dict) -> str:
    sm = d.get("statusMessage") or ""
    if not sm and d.get("statusTrace"):
        sm = d["statusTrace"].splitlines()[-1]
    return sm[:200]


# ============================================================
# 主流程
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="AI 驱动 UI 自动化 Pipeline")
    parser.add_argument("--skip-gen", action="store_true", help="跳过 AI 生成阶段")
    parser.add_argument("--gen-only", action="store_true", help="只生成用例不执行")
    args = parser.parse_args()

    t0 = time.time()
    config.ensure_dirs()

    s1 = stage1_import()
    req = stage2_parse()

    if args.skip_gen:
        gen_result = {"page_files": [], "test_files": [], "skipped": True}
        print("[3/8] ⏭️  --skip-gen 跳过 AI 生成阶段")
    else:
        gen_result = stage3_generate(req, gen_only=args.gen_only)
        if args.gen_only:
            print(f"\n✅ --gen-only 完成，耗时 {time.time() - t0:.1f}s")
            return 0

    s4 = stage4_execute()
    stats = collect_stats()
    excel_out = stage5_results(stats)
    stage6_report()
    stage7_dingtalk(stats, excel_out)
    stage8_cicd(stats)

    print(f"\n✅ Pipeline 完成，耗时 {time.time() - t0:.1f}s")
    # Pipeline 通过条件：无 failed 且无 broken
    failed = stats.get("failed", 0)
    broken = stats.get("broken", 0)
    return 0 if (failed == 0 and broken == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
