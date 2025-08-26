import requests
import random
import sys
import datetime
import pytz
import time

# 执行步数修改操作
def modify_steps(account, password, min_steps, max_steps, timeout=20, max_retries=3):
    steps = random.randint(min_steps, max_steps)
    url = f"https://www.520113.xyz/api/shua?account={account}&password={password}&steps={steps}"
    
    for attempt in range(max_retries):
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
                return True
            else:
                # 获取错误信息
                error_msg = result.get('message', '未知错误')
                # 获取北京时间
                beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                fail_msg = f"[{beijing_time}] 账号 {account[:3]}***{account[-3:]} 修改失败：{error_msg}"
                print(fail_msg)
                return False
                
        except requests.exceptions.Timeout:
            beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            timeout_msg = f"[{beijing_time}] 账号 {account[:3]}***{account[-3:]} 请求超时，{attempt+1}/{max_retries} 次尝试"
            print(timeout_msg)
            
            # 如果是最后一次尝试，直接返回失败
            if attempt == max_retries - 1:
                return False
                
            # 等待一段时间后重试
            time.sleep(5)  # 等待5秒后重试
            
        except requests.exceptions.RequestException as e:
            beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            error_msg = f"[{beijing_time}] 账号 {account[:3]}***{account[-3:]} 请求失败：{e}"
            print(error_msg)
            return False
            
        except ValueError as e:
            beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            error_msg = f"[{beijing_time}] 账号 {account[:3]}***{account[-3:]} 解析 JSON 失败：{e}"
            print(error_msg)
            return False
    
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("错误：缺少账号或密码参数")
        print("用法: python main.py <账号> <密码>")
        sys.exit(1)
    
    min_steps = 18200
    max_steps = 22000
    account = sys.argv[1]
    password = sys.argv[2]
    
    # 设置超时时间为30秒，最大重试次数为3次
    modify_steps(account, password, min_steps, max_steps, timeout=30, max_retries=3)