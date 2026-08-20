"""
钉钉机器人推送 - 仿 API 框架
路径: utils/dingtalk.py
根据通过率自动选择消息模板，失败用例 Top5。
"""
from __future__ import annotations

import time
import hmac
import hashlib
import base64
import urllib.parse
import json

import requests

from utils import config


def _sign(secret: str) -> tuple[str, str]:
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def send_report(stats: dict, excel_out: dict = None) -> str:
    """推送测试报告到钉钉。"""
    nt = config.load_notification().get("dingtalk", {})
    webhook = nt.get("webhook_url", "")
    secret = nt.get("secret", "")
    if not webhook or "access_token" not in webhook:
        return "钉钉 webhook 未配置，跳过推送"

    total = stats.get("total", 0)
    passed = stats.get("passed", 0)
    failed = stats.get("failed", 0)
    broken = stats.get("broken", 0)
    skipped = stats.get("skipped", 0)
    pass_rate = stats.get("pass_rate", 0)

    # 消息正文（必须包含机器人关键词，默认关键词 "测试"）
    failed_top = stats.get("failed_cases", [])[:5]
    fail_lines = []
    for c in failed_top:
        fail_lines.append(f"- {c.get('name', '')}: {c.get('status_message', '')[:60]}")
    fail_block = "\n".join(fail_lines) if fail_lines else "无"

    project = config.project_name()
    text = (
        f"【{project}】UI 自动化测试报告\n"
        f"通过率: {pass_rate}%\n"
        f"总数: {total} | 通过: {passed} | 失败: {failed} | 异常: {broken} | 跳过: {skipped}\n"
        f"失败 Top5:\n{fail_block}\n"
        f"测试（关键词）"
    )

    url = webhook
    if secret:
        ts, sign = _sign(secret)
        url = f"{webhook}&timestamp={ts}&sign={sign}"

    payload = {
        "msgtype": "text",
        "text": {"content": text},
        "at": {
            "atMobiles": nt.get("mention_mobiles", []),
            "isAtAll": nt.get("at_all", False),
        },
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get("errcode") == 0:
            return "HTTP 200  errcode=0  ← 钉钉推送成功"
        return f"HTTP {resp.status_code}  {data}"
    except Exception as e:
        return f"钉钉推送异常: {e}"
