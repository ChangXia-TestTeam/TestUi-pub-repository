"""
SSO 登录（UI 版）- 仿 API 框架 utils/auth.py
路径: utils/auth.py
两种登录策略：
    1) Fast Token：直接调登录 API 取 access_token，注入 cookie/localStorage，跳过 UI 登录流程
    2) UI 登录：走浏览器登录页，保存 storage_state 供后续复用
优先级：storage_state 缓存 > 环境变量 AUTH_TOKEN > UI 登录
"""
from __future__ import annotations

import os
import time
from typing import Optional

import requests

from utils import config


def _login_api(base_url: str, auth: dict) -> Optional[dict]:
    """调用登录接口换取 token / cookies。"""
    login_api = auth.get("login_api")
    if not login_api:
        return None
    url = base_url.rstrip("/") + login_api
    payload = {"username": auth.get("username"), "password": auth.get("password")}
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=config.timeout_config().get("request", 30))
        if resp.status_code < 300:
            return resp.json()
    except Exception as e:
        print(f"[auth] 登录接口异常: {e}")
    return None


def login_via_page(page, auth: dict):
    """
    UI 登录：在浏览器中走登录页。
    子类可在 login_page.py 中重写具体元素定位与流程。
    这里只做通用占位，真正实现请见 pages/login/login_page.py。
    """
    from pages.login.login_page import LoginPage
    LoginPage(page).login(auth.get("username", ""), auth.get("password", ""))


def get_or_login(browser_mgr) -> dict:
    """
    获取登录态：
        - 若 storage_state 文件已存在 → 由 BrowserManager 启动时自动复用
        - 若环境变量 AUTH_TOKEN → 注入到 localStorage
        - 否则走 UI 登录并保存 storage_state
    返回：{"source": "storage_state" | "env_token" | "ui_login" | "api_token"}
    """
    auth = config.auth_config()
    base_url = config.base_url()
    page = browser_mgr.page

    # 1) 环境变量 Token（用于跳过登录，定位问题排查）
    env_token = os.environ.get("AUTH_TOKEN")
    if env_token:
        page.goto(base_url)
        try:
            page.evaluate(f"localStorage.setItem('access_token', '{env_token}')")
        except Exception:
            pass
        return {"source": "env_token", "token": env_token}

    # 2) 尝试 API 快速登录取 Token（比 UI 登录快）
    data = _login_api(base_url, auth)
    if data and _is_login_success(data):
        token = _extract_token(data)
        if token:
            page.goto(base_url)
            try:
                page.evaluate(f"localStorage.setItem('access_token', '{token}')")
            except Exception:
                pass
            browser_mgr.save_auth_state()
            return {"source": "api_token", "token": token}

    # 3) 兜底：UI 登录
    login_via_page(page, auth)
    browser_mgr.save_auth_state()
    return {"source": "ui_login"}


def _is_login_success(data: dict) -> bool:
    """通用判定：code==0 / success==True / 有 token 字段。"""
    if not isinstance(data, dict):
        return False
    if data.get("code") in (0, 200, "0", "200"):
        return True
    if data.get("success") is True:
        return True
    return any(k in data for k in ("token", "access_token", "data"))


def _extract_token(data: dict) -> Optional[str]:
    for key in ("access_token", "token"):
        if data.get(key):
            return data[key]
    inner = data.get("data")
    if isinstance(inner, dict):
        for key in ("access_token", "token"):
            if inner.get(key):
                return inner[key]
    return None


def login_for_token_only() -> Optional[str]:
    """仅用于 Pipeline 第 1 步「真实登录」打印日志，不启动浏览器。"""
    auth = config.auth_config()
    data = _login_api(config.base_url(), auth)
    if data and _is_login_success(data):
        token = _extract_token(data)
        if token:
            return token
    return None
