import requests
import random
import sys
import datetime
import pytz

# 执行步数修改操作（已去掉重试逻辑，仅单次请求）
def modify_steps(account, password, min_steps, max_steps, timeout=30):
    steps = random.randint(min_steps, max_steps)
    url = f"https://zepp-life-steps.vercel.app/api/shua?account={account}&password={password}&steps={steps}"
    beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    account_hide = f"{account[:3]}***{account[-3:]}"  # 统一处理账号隐藏，避免重复代码

    try:
        # 单次请求，不重试
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # 触发HTTP错误（如404、500等）
        result = response.json()

        # 按API返回格式判断成功/失败
        if result.get('success') == True or result.get('status') == 'success':
            success_msg = f"[{beijing_time}] 账号 {account_hide} 修改成功，步数：{steps}"
            print(success_msg)
            return True
        else:
            error_msg = result.get('message', '未知错误')
            fail_msg = f"[{beijing_time}] 账号 {account_hide} 修改失败：{error_msg}"
            print(fail_msg)
            return False

    except requests.exceptions.Timeout:
        timeout_msg = f"[{beijing_time}] 账号 {account_hide} 请求超时"
        print(timeout_msg)
        return False

    except requests.exceptions.RequestException as e:
        error_msg = f"[{beijing_time}] 账号 {account_hide} 请求异常({type(e).__name__})：{e}"
        print(error_msg)
        return False

    except ValueError as e:
        error_msg = f"[{beijing_time}] 账号 {account_hide} 解析JSON异常：{e}"
        print(error_msg)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("错误：缺少账号或密码参数")
        print("用法: python main.py <账号> <密码>")
        sys.exit(1)
    
    # 配置参数
    min_steps = 11000
    max_steps = 13000
    account = sys.argv[1]
    password = sys.argv[2]
    
    # 调用函数（已无重试参数）
    result = modify_steps(account, password, min_steps, max_steps, timeout=30)
    
    # 按结果正确退出
    sys.exit(0 if result else 1)