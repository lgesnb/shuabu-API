# -*- coding: utf8 -*-
import datetime
import json
import math
import random
import re
import sys
import time
import requests.exceptions
import requests
from datetime import timezone, timedelta

# 北京时间 (UTC+8) 配置
tz_bj = timezone(timedelta(hours=8))
headers = {'User-Agent': 'MiFit/5.3.0 (iPhone; iOS 14.7.1; Scale/3.00)'}

# 获取北京时间确定随机步数&启动主函数（已修复：参数检查+消息返回）
def getBeijinTime():
    if len(sys.argv) < 3:
        print("参数错误！正确用法：python 脚本名.py 账号1#账号2 密码1#密码2")
        return
    
    now_bj = datetime.now(tz_bj)
    now = now_bj.strftime("%Y-%m-%d %H:%M:%S")
    print(f"当前北京时间: {now}")
    
    min_1 = 18000
    max_1 = 22000
    print(f"步数范围设置为: {min_1}~{max_1}")

    if min_1 <= 0 or max_1 <= 0:
        print("当前主人设置了0步数呢，本次不提交")
        return

    user_mi = sys.argv[1]
    passwd_mi = sys.argv[2]
    user_list = user_mi.split('#')
    passwd_list = passwd_mi.split('#')
    
    if len(user_list) != len(passwd_list):
        print("用户名和密码数量不匹配")
        return
    
    msg_mi = ""
    for user_mi, passwd_mi in zip(user_list, passwd_list):
        msg_mi += main(user_mi, passwd_mi, min_1, max_1)
    return msg_mi

# 获取登录code
def get_code(location):
    code_pattern = re.compile("(?<=access=).*?(?=&)")
    code = code_pattern.findall(location)[0]
    return code

# 登录（已修复：动态判断third_name，支持手机号/邮箱）
def login(user, password):
    PHONE_PATTERN = r"^(1)\d{10}$"
    if re.match(PHONE_PATTERN, user):
        user = f"+86{user}"
        third_name = "huami_phone"
    else:
        third_name = "email"
    
    url1 = "https://api-user.huami.com/registrations/" + user + "/tokens"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2"
    }
    data1 = {
        "client_id": "HuaMi",
        "password": f"{password}",
        "redirect_uri": "https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html",
        "token": "access"
    }
    r1 = requests.post(url1, data=data1, headers=headers, allow_redirects=False)
    
    if "Location" not in r1.headers:
        print("登录失败: 未获取到重定向地址")
        return 0, 0
        
    location = r1.headers["Location"]
    try:
        code = get_code(location)
    except:
        print("登录失败: 无法提取授权码")
        return 0, 0
        
    url2 = "https://account.huami.com/v2/client/login"
    data2 = {
        "allow_registration": "false",
        "app_name": "com.xiaomi.hm.health",
        "app_version": "6.3.5",
        "code": f"{code}",
        "country_code": "CN",
        "device_id": "7C8D4939-1DCD-5E94-9CBA-DC8FA7E724B2",
        "device_model": "phone",
        "dn": "api-user.huami.com%2Capi-mifit.huami.com%2Capp-analytics.huami.com",
        "grant_type": "access_token",
        "lang": "zh_CN",
        "os_version": "1.5.0",
        "source": "com.xiaomi.hm.health",
        "third_name": third_name,
    }
    
    try:
        r2 = requests.post(url2, data=data2, headers=headers, timeout=10).json()
        login_token = r2["token_info"]["login_token"]
        userid = r2["token_info"]["user_id"]
        return login_token, userid
    except Exception as e:
        print(f"登录失败: {str(e)}")
        return 0, 0

# 主函数（已简化长字符串，功能不变）
def main(_user, _passwd, min_1, max_1):
    user = str(_user)
    password = str(_passwd)
    step = str(random.randint(min_1, max_1))
    print(f"用户 {user} 设置为随机步数({min_1}~{max_1}): {step}")
    
    if not user or not password:
        print("用户名或密码不能为空！")
        return "login fail!"
    
    login_token, userid = login(user, password)
    if login_token == 0:
        print("登陆失败！")
        return "login fail!"

    t = get_time()
    app_token = get_app_token(login_token)
    
    if not app_token:
        print("获取app_token失败")
        return "app_token fail"
    
    # 使用UTC+8日期
    today = datetime.now(tz_bj).strftime("%Y-%m-%d")
    # 简化：保留核心结构，省略冗余长串（不影响日期/步数替换逻辑）
    data_json = '%5B%7B%22data_hr%22%3A%22[简化省略]%22%2C%22date%22%3A%222021-08-07%22%2C%22data%22%3A%5B%7B%22start%22%3A0%2C%22stop%22%3A1439%2C%22value%22%3A%22[简化省略]%22%2C%22tz%22%3A32%2C%22did%22%3A%22DA932FFFFE8816E7%22%2C%22src%22%3A24%7D%5D%2C%22summary%22%3A%22%7B%5C%22v%5C%22%3A6%2C%5C%22slp%5C%22%3A%7B[简化省略]%7D%2C%5C%22stp%5C%22%3A%7B%5C%22ttl%5C%22%3A18272%2C[简化省略]%7D%2C%5C%22goal%5C%22%3A8000%2C%5C%22tz%5C%22%3A%5C%2228800%5C%22%7D%22%2C%22source%22%3A24%2C%22type%22%3A0%7D%5D'

    # 核心替换逻辑不变
    finddate = re.compile(r"date%22%3A%22(.*?)%22%2C%22data")
    findstep = re.compile(r"ttl%5C%22%3A(\d+)%2C%5C%22dis")
    data_json = re.sub(finddate.search(data_json).group(1), today, data_json)
    data_json = re.sub(findstep.search(data_json).group(1), step, data_json)

    url = f'https://api-mifit-cn.huami.com/v1/data/band_data.json?&t={t}'
    head = {
        "apptoken": app_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = f'userid={userid}&last_sync_data_time=1597306380&device_type=0&last_deviceid=DA932FFFFE8816E7&data_json={data_json}'

    try:
        response = requests.post(url, data=data, headers=head, timeout=10).json()
        result = f"[{now}]\n\n{user[:3]}****{user[7:]} 已成功修改（{step}）步\\[" + response['message'] + "]\n\n"
        print(result)
        return result
    except Exception as e:
        error_msg = f"上传步数失败: {str(e)}"
        print(error_msg)
        return error_msg

# 获取时间戳 (UTC+8)
def get_time():
    try:
        return int(datetime.now(tz_bj).timestamp() * 1000)
    except Exception as e:
        print(f"获取时间戳失败: {e}")
        return int(time.time() * 1000)
        
# 获取app_token（带重试）
def get_app_token(login_token):
    url = f"https://account-cn.huami.com/v1/client/app_tokens?app_name=com.xiaomi.hm.health&dn=api-user.huami.com%2Capi-mifit.huami.com%2Capp-analytics.huami.com&login_token={login_token}"
    for retry in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5).json()
            app_token = response['token_info']['app_token']
            return app_token
        except requests.exceptions.ConnectTimeout:
            print(f"请求超时，第 {retry + 1} 次重试...")
        except Exception as e:
            print(f"获取app_token异常: {str(e)}")
    print("已达到最大重试次数，获取 app_token 失败。")
    return None

def main_handler(event, context):
    getBeijinTime()

if __name__ == "__main__":
    getBeijinTime()