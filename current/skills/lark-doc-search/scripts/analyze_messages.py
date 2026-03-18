#!/usr/bin/env python3
"""
详细分析群消息
"""

import requests
import json
import time
from datetime import datetime

APP_ID = "cli_a90ebb6fe8f81bd2"
APP_SECRET = "clSwYtz2CqvDfon3bKP2sh0wGBiV4nrT"
CHAT_ID = "oc_0a1d28a4189be0e8c881a4ca7f4f04d2"


def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=30)
    return resp.json().get("tenant_access_token")


def get_messages(token):
    """获取所有消息（不限制时间）"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}"}
    
    all_messages = []
    page_token = None
    
    while True:
        params = {
            "container_id_type": "chat",
            "container_id": CHAT_ID,
            "page_size": 50
        }
        if page_token:
            params["page_token"] = page_token
        
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        result = resp.json()
        
        if result.get("code") == 0:
            data = result.get("data", {})
            items = data.get("items", [])
            all_messages.extend(items)
            
            page_token = data.get("page_token")
            if not data.get("has_more") or not page_token:
                break
        else:
            break
    
    return all_messages


def analyze(messages):
    print(f"\n共获取到 {len(messages)} 条消息\n")
    
    # 按日期分组
    by_date = {}
    by_user = {}
    
    for msg in messages:
        ts = int(msg.get("create_time", 0)) / 1000
        dt = datetime.fromtimestamp(ts)
        date_key = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M:%S")
        
        sender = msg.get("sender", {})
        sender_id = sender.get("id", "unknown")
        sender_type = sender.get("sender_type", "unknown")
        
        # 解析内容
        body = msg.get("body", {})
        content = body.get("content", "")
        msg_type = msg.get("msg_type", "unknown")
        
        try:
            content_obj = json.loads(content)
            text = content_obj.get("text", str(content_obj)[:50])
        except:
            text = content[:50] if content else f"[{msg_type}]"
        
        # 按日期分组
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append({
            "time": time_str,
            "sender": sender_id[:25],
            "type": sender_type,
            "content": text[:60],
            "msg_type": msg_type
        })
        
        # 按用户统计
        if sender_id not in by_user:
            by_user[sender_id] = {
                "count": 0,
                "type": sender_type,
                "dates": set()
            }
        by_user[sender_id]["count"] += 1
        by_user[sender_id]["dates"].add(date_key)
    
    # 打印按日期分组的消息
    print("="*80)
    print("📅 按日期分布")
    print("="*80)
    
    for date in sorted(by_date.keys(), reverse=True):
        msgs = by_date[date]
        print(f"\n【{date}】共 {len(msgs)} 条消息")
        print("-"*80)
        
        for m in msgs[:20]:  # 每天最多显示20条
            print(f"  {m['time']} | {m['sender']:25} | {m['content']}")
        
        if len(msgs) > 20:
            print(f"  ... 还有 {len(msgs) - 20} 条")
    
    # 打印用户统计
    print("\n" + "="*80)
    print("👥 参与者统计")
    print("="*80)
    
    # 按消息数排序
    sorted_users = sorted(by_user.items(), key=lambda x: x[1]["count"], reverse=True)
    
    for user_id, info in sorted_users:
        dates_str = ", ".join(sorted(info["dates"]))
        print(f"  {user_id[:40]:40} | {info['count']:3}条 | {info['type']:10} | {dates_str}")
    
    # 今天的具体情况
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n" + "="*80)
    print(f"📊 今天（{today}）的消息详情")
    print("="*80)
    
    if today in by_date:
        today_msgs = by_date[today]
        print(f"共 {len(today_msgs)} 条消息\n")
        
        for m in today_msgs:
            print(f"  {m['time']} | {m['sender']:25}")
            print(f"      内容: {m['content']}")
            print()
    else:
        print("今天没有消息\n")
        print("最近有消息的日期:")
        for date in sorted(by_date.keys(), reverse=True)[:5]:
            print(f"  - {date}: {len(by_date[date])} 条")


def main():
    print("="*80)
    print("飞书群消息详细分析")
    print(f"目标群: OpenClaw运维 ({CHAT_ID})")
    print("="*80)
    
    print("\n🔑 获取 token...")
    token = get_token()
    
    print("📥 获取消息...")
    messages = get_messages(token)
    
    analyze(messages)
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
