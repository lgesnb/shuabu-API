import os
import re
import time
from datetime import datetime
import requests  # 不导入dotenv，完全用环境变量

# --------------------------
# 密钥配置：纯读环境变量（不依赖.env）
# --------------------------
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")  # 本地：系统环境变量；GitHub：Secrets
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
TG_API_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

# 校验密钥（启动前检查，避免报错）
if not TG_BOT_TOKEN or not TG_CHAT_ID:
    raise ValueError("请设置环境变量：TG_BOT_TOKEN 和 TG_CHAT_ID（从密码库复制）")

# --------------------------
# 工具函数：提取消息信息
# --------------------------
def extract_current_user(latest_msg_text):
    """从最新消息提取当前用户ID"""
    user_pattern = r"🆔 用户完整ID：(.*?)\n"
    match = re.search(user_pattern, latest_msg_text)
    return match.group(1).strip() if match else None

def is_valid_operation(msg_text):
    """判断是否为有效操作记录"""
    return "🔔 Zeep Life 操作" in msg_text and "🆔 用户完整ID：" in msg_text

def get_all_records():
    """获取所有操作记录（含用户ID和日期）"""
    records = []
    offset = 0
    while True:
        params = {
            "chat_id": TG_CHAT_ID,
            "limit": 100,
            "offset": offset,
            "from_user_id": TG_BOT_TOKEN.split(":")[0]  # 机器人ID
        }
        response = requests.get(f"{TG_API_URL}/getChatHistory", params=params)
        data = response.json()
        
        if not data.get("ok") or not data.get("result"):
            break
        
        for msg in data["result"]:
            if "text" in msg and is_valid_operation(msg["text"]):
                # 提取用户ID和日期
                user = extract_current_user(msg["text"])
                date_match = re.search(r"📅 日期：(.*?)\n", msg["text"])
                if user and date_match:
                    records.append({
                        "user_id": user,
                        "date": date_match.group(1).strip()
                    })
        
        offset += 100
        time.sleep(0.5)
    return records

# --------------------------
# 统计逻辑：4大核心维度
# --------------------------
def calculate_stats(records, current_user):
    """计算：总用户数、总运行次数、当日次数、当前用户次数"""
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "total_users": len(set(r["user_id"] for r in records)),  # 去重算总用户
        "total_runs": len(records),
        "today_runs": sum(1 for r in records if r["date"] == today),
        "current_user": {
            "id": current_user,
            "runs": sum(1 for r in records if r["user_id"] == current_user)
        },
        "today": today
    }

# --------------------------
# 生成回复
# --------------------------
def generate_reply(stats):
    """生成简洁回复"""
    return f"""
📊 【核心运行统计】
━━━━━━━━━━━━━━━━━━━━
• 总用户数：{stats['total_users']} 人
• 总运行次数：{stats['total_runs']} 次
• 当日运行次数（{stats['today']}）：{stats['today_runs']} 次
• 当前用户（{stats['current_user']['id']}）总次数：{stats['current_user']['runs']} 次
    """.strip()

# --------------------------
# 监听与统计
# --------------------------
def run_bot():
    print("✅ 核心统计机器人启动成功（密钥从环境变量读取）")
    last_msg_id = 0
    
    while True:
        # 获取最新1条消息
        params = {"chat_id": TG_CHAT_ID, "limit": 1, "offset": -1}
        response = requests.get(f"{TG_API_URL}/getChatHistory", params=params)
        data = response.json()
        
        if not data.get("ok") or not data.get("result"):
            time.sleep(4)
            continue
        
        latest_msg = data["result"][0]
        msg_id = latest_msg["message_id"]
        msg_text = latest_msg.get("text", "")
        
        # 处理新的有效操作
        if msg_id > last_msg_id and is_valid_operation(msg_text):
            current_user = extract_current_user(msg_text)
            if not current_user:
                print("❌ 无法提取当前用户ID")
                last_msg_id = msg_id
                time.sleep(4)
                continue
            
            # 统计并回复
            print(f"🔍 新操作：用户 {current_user}")
            all_records = get_all_records()
            stats = calculate_stats(all_records, current_user)
            reply = generate_reply(stats)
            
            # 发送回复
            requests.post(f"{TG_API_URL}/sendMessage", json={
                "chat_id": TG_CHAT_ID,
                "text": reply,
                "parse_mode": "Markdown"
            })
            print("✅ 统计结果已发送")
            last_msg_id = msg_id
        
        time.sleep(4)

# --------------------------
# 启动入口
# --------------------------
if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n❌ 机器人已停止")
    except Exception as e:
        print(f"\n❌ 异常：{str(e)}")