import requests
import random
import sys
import datetime
import pytz

# 执行步数修改操作
def modify_steps(account, password, min_steps, max_steps, timeout=20):
    steps = random.randint(min_steps, max_steps)
    url = f"https://www.520113.xyz/api/shua?account={account}&password={password}&steps={steps}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # 检查 HTTP 状态码
        result = response.json()
        
        # 根据实际API返回格式调整判断逻辑
        if result.get('success') == True or result.get('status') == 'success':
            # 获取北京时间
            beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            success_msg = f"[{beijing_time}] 账号 {account[:3]}***{account[-3:]} 修改成功，步数：{steps}"
            print(success_msg)
            return success_msg
        else:
            # 获取错误信息
            error_msg = result.get('message', '未知错误')
            # 获取北京时间
            beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            fail_msg = f"[{beijing_time}] 账号 {account[:3]}***{account[-3:]} 修改失败：{error_msg}"
            print(fail_msg)
            return fail_msg
    except requests.exceptions.RequestException as e:
        beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"[{beijing_time}] 账号 {account[:3]}***{account[-3:]} 请求失败：{e}"
        print(error_msg)
        return error_msg
    except ValueError as e:
        beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"[{beijing_time}] 账号 {account[:3]}***{account[-3:]} 解析 JSON 失败：{e}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("错误：缺少账号或密码参数")
        print("用法: python main.py <账号> <密码>")
        sys.exit(1)
    
    min_steps = 5000
    max_steps = 5200
    account = sys.argv[1]
    password = sys.argv[2]
    
    result = modify_steps(account, password, min_steps, max_steps)
    
    # 将结果写入文件
    with open('result.txt', 'a') as f:
        f.write(result + "\n")