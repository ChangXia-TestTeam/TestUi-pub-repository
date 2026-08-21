"""
🚀 概览页测试一键运行脚本
路径: scripts/run_overview_tests.py

用法:
    python scripts/run_overview_tests.py                     # 跑全部 7 个用例
    python scripts/run_overview_tests.py -k "load"           # 按关键字筛选
    python scripts/run_overview_tests.py -m "P0"             # 按 marker 筛选
    python scripts/run_overview_tests.py -n 2                # 并发数
    python scripts/run_overview_tests.py --headed            # 有头模式
    python scripts/run_overview_tests.py --no-report         # 不生成 Allure HTML 报告
    python scripts/run_overview_tests.py --ci                # CI 模式（headless + 即时退出）
"""
from __future__ import annotations

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OVERVIEW_TEST_FILE = ROOT / "tests" / "test_overview.py"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="概览页面 UI 自动化测试")
    p.add_argument("-k", "--keyword", help="按用例名关键字过滤，如 'load'")
    p.add_argument("-m", "--marker", help="按 pytest marker 过滤，如 'P0'")
    p.add_argument("-n", "--workers", type=int, default=2, help="并发 worker 数，默认 2")
    p.add_argument("--headed", action="store_true", help="有头模式（可见浏览器）")
    p.add_argument("--ci", action="store_true", help="CI 模式（headless + 即时退出）")
    p.add_argument("--no-report", action="store_true", help="不生成 Allure HTML 报告")
    p.add_argument("--alluredir", default="reports/allure-overview", help="Allure 结果目录")
    p.add_argument("--trace", action="store_true", help="启用 Playwright trace")
    p.add_argument("--reruns", type=int, default=3, help="失败重试次数")
    return p.parse_args()


def run_pytest(args: argparse.Namespace) -> int:
    # 设置 HEADLESS 环境变量，config.browser_config() 会读取它
    if args.ci:
        os.environ["HEADLESS"] = "true"
    elif args.headed:
        os.environ["HEADLESS"] = "false"

    # Allure 目录
    allure_dir = ROOT / args.alluredir
    allure_dir.mkdir(parents=True, exist_ok=True)

    # 构建命令
    cmd = [
        sys.executable, "-m", "pytest",
        str(OVERVIEW_TEST_FILE),
        "-v", "--tb=short",
        "-n", str(args.workers),
        f"--alluredir={allure_dir}",
        "--clean-alluredir",
    ]

    if args.keyword:
        cmd += ["-k", args.keyword]
    if args.marker:
        cmd += ["-m", args.marker]
    if args.trace:
        cmd += ["--trace"]
    if args.reruns > 0:
        cmd += [f"--reruns={args.reruns}"]
        cmd += ["--reruns-delay", "1"]

    mode = "无头" if os.environ.get("HEADLESS") in ("true", "1", "yes") else "有头"

    print(f"\n{'='*60}")
    print(f"  概览页 UI 自动化测试")
    print(f"  命令: {' '.join(cmd)}")
    print(f"  模式: {mode}  并发: {args.workers}  重试: {args.reruns}")
    print(f"  结果目录: {allure_dir}")
    print(f"{'='*60}\n")

    t0 = time.time()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(cmd, cwd=str(ROOT), env=env)
    elapsed = time.time() - t0

    print(f"\n{'='*60}")
    print(f"  pytest 退出码: {proc.returncode}  耗时: {elapsed:.1f}s")

    if proc.returncode == 0:
        print(f"  ✅ 全部通过")
    else:
        print(f"  ❌ 存在失败用例")

    # 生成 Allure HTML 报告
    if not args.no_report:
        try:
            html_dir = ROOT / "reports" / "allure-overview-report"
            subprocess.run([
                "allure", "generate", str(allure_dir),
                "-o", str(html_dir), "--clean",
            ], check=True, capture_output=True)
            print(f"  📊 Allure 报告: {html_dir}")
            print(f"  🌐 本地预览: python -m http.server 8090 --directory {html_dir}")
        except FileNotFoundError:
            print(f"  ⚠️  allure 命令未安装，跳过 HTML 报告生成")
            print(f"     安装方式: npm install -g allure-commandline")
        except Exception as e:
            print(f"  ⚠️  Allure 报告生成失败: {e}")

    print(f"{'='*60}\n")
    return proc.returncode


def main():
    args = parse_args()
    return run_pytest(args)


if __name__ == "__main__":
    sys.exit(main())
