# -*- coding: utf8 -*-
import datetime
import random
import re
import sys
import requests
import requests.exceptions
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, quote  # 对标URLSearchParams，处理参数编码

# 核心配置：完全对齐参考代码的请求头（补充Origin必传字段）
tz_bj = timezone(timedelta(hours=8))
BASE_HEADERS = {
    'User-Agent': 'MiFit/6.12.0 (MCE16; Android 16; Density/1.5)',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'app_name': 'com.xiaomi.hm.health',
    'Origin': 'https://user.zepp.com'  # 参考代码隐含的必传头
}

# 入口函数：获取时间+设置步数+启动流程
def getBeijinTime():
    now_bj = datetime.now(tz_bj)
    now = now_bj.strftime("%Y-%m-%d %H:%M:%S")
    print(f"当前北京时间: {now}")
    
    # 步数范围（可按需修改）
    min_1, max_1 = 7800, 12200
    print(f"步数范围设置为: {min_1}~{max_1}")
    if min_1 <= 0 or max_1 <= 0:
        print("步数不能为0，本次不提交")
        return

    # 从命令行获取账号密码（格式：user1#user2  pass1#pass2）
    try:
        user_mi = sys.argv[1]
        passwd_mi = sys.argv[2]
        user_list = user_mi.split('#')
        passwd_list = passwd_mi.split('#')
        if len(user_list) != len(passwd_list):
            print("用户名和密码数量不匹配")
            return
    except IndexError:
        print("请传入参数：python 脚本名 用户名列表 密码列表")
        return

    # 批量处理每个账号
    for user, pwd in zip(user_list, passwd_list):
        main(user, pwd, min_1, max_1)

# 1. 对标参考代码：修复登录逻辑（处理重定向头、账号编码、参数对齐）
def login(account, password):
    try:
        # 账号类型判断+处理（完全对齐参考代码）
        is_phone = re.match(r"^(1)\d{10}$", account)
        third_name = "huami_phone" if is_phone else "huami"
        print(f'登录账号类型: {"手机号" if is_phone else "邮箱"}')
        
        # 账号处理：清旧前缀+加+86+解码（避免提前编码问题）
        formatted_account = account
        if is_phone:
            formatted_account = "+86" + account.replace(r"^\+86|^86", "")
        formatted_account = requests.utils.unquote(formatted_account)  # 对标decodeURIComponent
        print(f"最终原始账号: {formatted_account}")

        # 第一步：获取access code（路径编码账号，参数用urlencode对标URLSearchParams）
        encoded_account_url = quote(formatted_account)  # URL路径编码
        url1 = f"https://api-user.zepp.com/registrations/{encoded_account_url}/tokens"
        data1 = urlencode({  # 对标new URLSearchParams
            "client_id": "HuaMi",
            "name": formatted_account,
            "password": password,
            "redirect_uri": "https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html",
            "token": "access",
            "country_code": "CN",
            "json_response": "true",
            "state": "REDIRECTION"
        })

        print(f"第一步请求URL: {url1}")
        print(f"第一步请求数据: {data1}")

        # 禁止重定向，同时兼容200和3xx状态（对标参考代码）
        response1 = requests.post(
            url1, data=data1, headers=BASE_HEADERS,
            allow_redirects=False,
            verify=True
        )
        print(f"第一步响应状态码: {response1.status_code}")
        print(f"第一步响应头: {response1.headers}")

        # 关键：同时处理重定向头和200响应体（对标参考代码逻辑）
        code = None
        if "location" in response1.headers:
            # 从重定向头提取code（复用原getCode逻辑）
            code_match = re.search(r"(?<=access=).*?(?=&)", response1.headers["location"])
            code = code_match.group(0) if code_match else None
            print(f"从重定向头获取code: {code}")
        elif response1.status_code == 200 and response1.json().get("access"):
            code = response1.json()["access"]
            print(f"从响应体获取code: {code}")

        if not code:
            raise Exception("获取access code失败（账号/密码错误或参数异常）")

        # 第二步：获取login_token和user_id（参数完全对齐参考代码）
        url2 = "https://account.zepp.com/v2/client/login"
        data2 = urlencode({
            "allow_registration": "false",
            "app_name": "com.xiaomi.hm.health",
            "app_version": "6.12.0",
            "code": code,
            "country_code": "CN",
            "device_id": "fuck1069-2002-7869-0129-757geoi6sam1",  # 复用参考代码的device_id
            "device_model": "android_phone",
            "dn": "account.zepp.com,api-user.zepp.com,api-mifit.zepp.com,api-watch.zepp.com,app-analytics.zepp.com,api-analytics.huami.com,auth.zepp.com",
            "grant_type": "access_token",
            "source": "com.xiaomi.hm.health",
            "third_name": third_name
        })

        print(f"第二步请求URL: {url2}")
        print(f"第二步请求数据: {data2}")

        response2 = requests.post(
            url2, data=data2, headers=BASE_HEADERS,
            verify=True
        )
        response2_json = response2.json()
        if not response2_json.get("token_info"):
            raise Exception("未获取到token信息")

        login_token = response2_json["token_info"]["login_token"]
        user_id = response2_json["token_info"]["user_id"]
        if not login_token or not user_id:
            raise Exception("token信息不完整")

        print(f"登录成功：loginToken={login_token}, userId={user_id}")
        return {"login_token": login_token, "user_id": user_id}
    except Exception as e:
        print(f"登录失败: {str(e)}")
        return None

# 2. 新增：对标参考代码的getAppToken单独接口
def get_app_token(login_token):
    try:
        # 完全对齐参考代码的URL参数
        url = (
            f"https://account-cn.zepp.com/v1/client/app_tokens?"
            f"app_name=com.xiaomi.hm.health&"
            f"dn=api-user.zepp.com%2Capi-mifit.zepp.com%2Capp-analytics.zepp.com&"
            f"login_token={login_token}"
        )
        print(f"获取appToken请求URL: {url}")

        response = requests.get(url, headers=BASE_HEADERS, verify=True)
        response_json = response.json()
        app_token = response_json["token_info"].get("app_token")
        if not app_token:
            raise Exception("appToken获取失败")

        print(f"获取appToken成功: {app_token}")
        return app_token
    except Exception as e:
        print(f"获取appToken失败: {str(e)}")
        return None

# 3. 核心：修改提交步数逻辑（保留完整逻辑，简化冗余data_json）
def main(account, pwd, min_step, max_step):
    step = str(random.randint(min_step, max_step))
    print(f"\n用户 {account} - 随机步数：{step}")
    if not account or not pwd:
        print(f"用户 {account} 提交失败：账号/密码为空")
        return

    # 步骤1：登录获取login_token和user_id
    login_result = login(account, pwd)
    if not login_result:
        print(f"用户 {account} 提交失败：登录未通过")
        return
    login_token = login_result["login_token"]
    user_id = login_result["user_id"]

    # 步骤2：单独获取appToken
    app_token = get_app_token(login_token)
    if not app_token:
        print(f"用户 {account} 提交失败：appToken获取失败")
        return

    # 步骤3：处理日期和时间戳（对标参考代码moment+Date.now()）
    today = datetime.now(tz_bj).strftime("%Y-%m-%d")
    t = int(datetime.now(tz_bj).timestamp() * 1000)
    print(f"当前日期: {today}")
    print(f"请求时间戳: {t}")

    # 关键：简化data_json（保留核心结构，替换原超长冗余串，已含日期和步数动态占位）
    data_json = (
        f'%5B%7B%22data_hr%22%3A%22%22%2C%22date%22%3A%22{today}%22%2C'
        f'%22step%22%3A%22{step}%22%2C%22active_minutes%22%3A%2260%22%7D%5D'
    )  # 核心字段：日期、步数、活动分钟数，符合接口格式

    # 提交参数：对齐参考代码
    submit_url = f"https://api-mifit-cn.zepp.com/v1/data/band_data.json?t={t}"
    submit_data = urlencode({
        "userid": user_id,
        "last_sync_data_time": "1755407692",  # 复用参考代码固定值
        "device_type": "0",
        "last_deviceid": "DA932FFFFE8816E7",
        "data_json": data_json  # 使用简化后的核心字符串
    })

    # 提交头：补充apptoken
    submit_headers = {**BASE_HEADERS, "apptoken": app_token}
    print(f"提交步数请求URL: {submit_url}")
    print(f"提交步数请求数据: {submit_data}")

    # 提交步数逻辑
    try:
        response = requests.post(
            submit_url, data=submit_data, headers=submit_headers,
            timeout=10, verify=True
        )
        response_json = response.json()
        if response_json.get("code") != 1:
            raise Exception(f"接口返回异常: {response_json}")
        print(f"用户 {account} 提交成功！响应：{response_json['message']}")
    except Exception as e:
        print(f"用户 {account} 提交失败：{str(e)}")

# 函数入口（兼容命令行和云函数调用）
def main_handler(event, context):
    getBeijinTime()

if __name__ == "__main__":
    getBeijinTime()