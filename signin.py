#!/usr/bin/env python3
"""无限云盘每日签到，并输出适合 Telegram 的结果。"""
import json
import os
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://api.xbapi.com/v1/app"
ACCOUNT = os.environ.get("XB_ACCOUNT", "")
PASSWORD = os.environ.get("XB_PASSWORD", "")


def request(method, path, *, body=None, session=""):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if session:
        headers.update({"thirdSession": session, "platform": "APP"})
    data = None if body is None else json.dumps(body).encode()
    req = Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code}: {detail}") from e
    except URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}") from e


def main():
    if not ACCOUNT or not PASSWORD:
        raise RuntimeError("未配置 XB_ACCOUNT 或 XB_PASSWORD")

    login = request("POST", "/m/user/login", body={"account": ACCOUNT, "password": PASSWORD})
    if login.get("code") != 200 or not isinstance(login.get("data"), dict):
        raise RuntimeError(f"登录失败: {login.get('msg', login)}")
    session = login["data"].get("sessionKey", "")
    if not session:
        raise RuntimeError("登录响应中没有 sessionKey")

    info = request("GET", "/m/sign/info", session=session)
    if info.get("code") != 200:
        raise RuntimeError(f"查询签到状态失败: {info.get('msg', info)}")
    sign = info.get("data") or {}
    sign_time = str(sign.get("signTime") or "")
    today = datetime.now().astimezone().date().isoformat()
    if sign_time[:10] == today:
        print(f"✅ 无限云盘签到\n状态：今日已签到\n连续签到：{sign.get('connectNum', 0)} 天\n积分：{sign.get('totalPoints', 0)}")
        return

    result = request("POST", "/m/sign/add", session=session)
    if result.get("code") != 200:
        message = str(result.get("msg", ""))
        if "已经签到" in message or "已签到" in message:
            print(f"✅ 无限云盘签到\n状态：今日已签到\n连续签到：{sign.get('connectNum', 0)} 天\n积分：{sign.get('totalPoints', 0)}")
            return
        raise RuntimeError(f"签到失败: {result.get('msg', result)}")
    data = result.get("data") or {}
    print(f"✅ 无限云盘签到\n状态：签到成功\n连续签到：{data.get('connectNum', sign.get('connectNum', 0))} 天\n积分：{data.get('totalPoints', sign.get('totalPoints', 0))}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"❌ 无限云盘签到\n状态：失败\n原因：{exc}")
        sys.exit(1)
