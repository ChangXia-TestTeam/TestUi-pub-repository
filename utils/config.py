"""
配置读取 - 仿 API 框架 utils/config.py
路径: utils/config.py
负责读取 config/config.yaml 与 config/notification.json，全局单例。
"""
import os
import json
from pathlib import Path
from functools import lru_cache

import yaml

# 项目根目录（本文件位于 <root>/utils/config.py）
ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT_DIR / "config"


@lru_cache(maxsize=1)
def load_config() -> dict:
    """读取 config/config.yaml，返回字典。"""
    cfg_path = CONFIG_DIR / "config.yaml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {cfg_path}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=1)
def load_notification() -> dict:
    """读取 config/notification.json。"""
    nj = CONFIG_DIR / "notification.json"
    if not nj.exists():
        return {}
    with open(nj, "r", encoding="utf-8") as f:
        return json.load(f)


def get(key_path: str, default=None):
    """
    点分路径取值：get('test_env.base_url')
    """
    cfg = load_config()
    node = cfg
    for k in key_path.split("."):
        if isinstance(node, dict) and k in node:
            node = node[k]
        else:
            return default
    return node


def base_url() -> str:
    return get("test_env.base_url")


def project_name() -> str:
    return get("project_name", "未命名项目")


def auth_config() -> dict:
    return get("auth", {})


def browser_config() -> dict:
    return get("browser", {})


def timeout_config() -> dict:
    return get("timeout", {})


def input_config() -> dict:
    return get("input", {})


def screenshot_config() -> dict:
    return get("screenshot", {})


def ensure_dirs():
    """确保运行期输出目录存在。"""
    for d in [
        ROOT_DIR / "reports" / "screenshots",
        ROOT_DIR / "reports" / "allure-results",
        ROOT_DIR / "reports" / "allure-report",
        ROOT_DIR / "reports" / "self_healing",
        ROOT_DIR / "reports" / "videos",
        ROOT_DIR / "UI_output_files" / "test_ui_results",
        ROOT_DIR / "UI_output_files" / "bug_list",
        ROOT_DIR / "UI_input_files" / "prd",
        ROOT_DIR / "UI_input_files" / "screenshots",
        ROOT_DIR / "UI_input_files" / "lanhu",
        ROOT_DIR / "ai" / ".pending",
        ROOT_DIR / "ai" / ".done",
    ]:
        d.mkdir(parents=True, exist_ok=True)
