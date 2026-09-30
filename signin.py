python
    #!/usr/bin/env python3

    import json
    import os
    import sys
    from datetime import datetime
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
    from zoneinfo import ZoneInfo
                                                                    
    BASE_URL = "https://api.xbapi.com/v1/app"
    TIMEZONE = ZoneInfo("Asia/Shanghai")
                                                                        ACCOUNT = os.environ.get("XB_ACCOUNT", "")
    PASSWORD = os.environ.get("XB_PASSWORD", "")


    def request(method, path, body=None, session_key=""):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if session_key:
            headers["thirdSession"] = session_key
            headers["platform"] = "APP"

        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")

        request_obj = Request(
            BASE_URL + path,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request_obj, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            detail = error.read().decode("utf-8",
    errors="replace")[:300]
            raise RuntimeError(f"HTTP {error.code}: {detail}")
    from error
                                                                            except URLError as error:
            raise RuntimeError(f"网络错误：{error.reason}") from error


    def today_string():
        return datetime.now(TIMEZONE).strftime("%Y-%m-%d")          

    def main():
        if not ACCOUNT:
            raise RuntimeError("未配置 GitHub Secret：XB_ACCOUNT")

        if not PASSWORD:
            raise RuntimeError("未配置 GitHub Secret：XB_PASSWORD")

        login_result = request(                                                 "POST",                                                             "/m/user/login",                                                    body={                                                                  "account": ACCOUNT,                                                 "password": PASSWORD,                                           },                                                              )                                                                                                                                       if login_result.get("code") != 200:                                     raise RuntimeError(
                "登录失败：" + str(login_result.get("msg",
    login_result))
            )

        user_data = login_result.get("data") or {}
        session_key = user_data.get("sessionKey")

        if not session_key:
            raise RuntimeError("登录响应中没有 sessionKey")

        sign_info_result = request(
            "GET",
            "/m/sign/info",
            session_key=session_key,
        )

        if sign_info_result.get("code") != 200:
            raise RuntimeError(
                "查询签到状态失败："
                + str(sign_info_result.get("msg",
    sign_info_result))
            )

        sign_info = sign_info_result.get("data") or {}
        sign_time = str(sign_info.get("signTime") or "")

        if sign_time[:10] == today_string():
            print(
                "✅ 无限云盘签到\n"
                "状态：今日已签到\n"
                f"连续签到：{sign_info.get('connectNum', 0)} 天\n"
                f"积分：{sign_info.get('totalPoints', 0)}"
            )
            return

        add_sign_result = request(
            "POST",
            "/m/sign/add",
            session_key=session_key,
        )

        if add_sign_result.get("code") != 200:
            raise RuntimeError(
                "签到失败：" + str(add_sign_result.get("msg",
    add_sign_result))
            )

        result_data = add_sign_result.get("data") or {}

        print(
            "✅ 无限云盘签到\n"                                                 "状态：签到成功\n"
            f"连续签到："
            f"{result_data.get('connectNum',
    sign_info.get('connectNum', 0))} 天\n"
            f"积分："
            f"{result_data.get('totalPoints',
    sign_info.get('totalPoints', 0))}"
        )


    if name == "main":
        try:
            main()
        except Exception as error:
            print(
                "❌ 无限云盘签到\n"
                "状态：失败\n"
                f"原因：{error}"
            )
            sys.exit(1)
