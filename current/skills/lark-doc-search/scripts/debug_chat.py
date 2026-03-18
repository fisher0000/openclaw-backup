#!/usr/bin/env python3
"""
获取群聊历史消息 - 调试版本
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta

# 飞书应用凭证
APP_ID = "cli_a90ebb6fe8f81bd2"
APP_SECRET = "clSwYtz2CqvDfon3bKP2sh0wGBiV4nrT"

# 运维群ID
CHAT_ID = "oc_0a1d28a4189be0e8c881a4ca7f4f04d2"


def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        result = resp.json()
        if result.get("code") == 0:
            return result.get("tenant_access_token")
        else:
            print(f"获取token失败: {result}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None


def check_app_info(token):
    """检查应用信息和权限"""
    url = "https://open.feishu.cn/open-apis/application/v3/apps"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        result = resp.json()
        print(f"应用信息: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    except Exception as e:
        print(f"获取应用信息失败: {e}")


def get_chat_members(token, chat_id):
    """获取群成员列表"""
    url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        result = resp.json()
        
        if result.get("code") == 0:
            members = result.get("data", {}).get("items", [])
            print(f"\n👥 群成员数量: {len(members)}")
            for m in members[:10]:  # 只显示前10个
                print(f"  - {m.get('name', '未知')} ({m.get('member_id_type')}: {m.get('member_id', '未知')[:20]}...)")
            if len(members) > 10:
                print(f"  ... 还有 {len(members) - 10} 人")
            return members
        else:
            print(f"获取群成员失败: {result}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None


def get_chat_history(token, chat_id):
    """获取群聊历史消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 计算今天的时间范围（毫秒时间戳）
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = int(today.timestamp() * 1000)
    end_time = int(time.time() * 1000)
    
    print(f"\n查询时间范围:")
    print(f"  开始: {today.strftime('%Y-%m-%d %H:%M:%S')} ({start_time})")
    print(f"  结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({end_time})")
    
    # 尝试不同的 container_id_type
    id_types = ["chat", "chat_id"]
    
    all_messages = []
    
    for id_type in id_types:
        print(f"\n尝试使用 container_id_type='{id_type}'...")
        
        params = {
            "container_id_type": id_type,
            "container_id": chat_id,
            "start_time": start_time,
            "end_time": end_time,
            "page_size": 50
        }
        
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            result = resp.json()
            
            print(f"API响应: {json.dumps(result, indent=2, ensure_ascii=False)[:800]}")
            
            if result.get("code") == 0:
                data = result.get("data", {})
                items = data.get("items", [])
                print(f"✅ 使用 '{id_type}' 成功，获取到 {len(items)} 条消息")
                all_messages.extend(items)
            else:
                print(f"❌ 使用 '{id_type}' 失败: {result.get('msg')}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    return all_messages


def main():
    print("=" * 60)
    print("飞书群消息查询（调试模式）")
    print("=" * 60)
    
    print("\n🔑 正在获取 tenant_access_token...")
    token = get_tenant_access_token()
    if not token:
        print("❌ 获取 token 失败")
        sys.exit(1)
    print("✅ Token 获取成功")
    
    # 检查应用信息
    print("\n📋 检查应用信息...")
    check_app_info(token)
    
    # 获取群成员
    print("\n👥 正在获取群成员...")
    members = get_chat_members(token, CHAT_ID)
    
    # 获取历史消息
    print("\n📨 正在获取历史消息...")
    messages = get_chat_history(token, CHAT_ID)
    
    if messages:
        print(f"\n✅ 总共获取到 {len(messages)} 条消息")
        
        # 显示消息详情
        print("\n📝 消息详情:")
        for i, msg in enumerate(messages[:10], 1):  # 只显示前10条
            sender = msg.get("sender", {})
            create_time = int(msg.get("create_time", 0)) / 1000
            time_str = datetime.fromtimestamp(create_time).strftime("%H:%M:%S")
            
            print(f"\n  [{i}] {time_str}")
            print(f"      发送者: {sender.get('id', '未知')} ({sender.get('sender_type', '未知')})")
            print(f"      类型: {msg.get('msg_type', '未知')}")
            
            body = msg.get("body", {})
            content = body.get("content", "")
            try:
                content_obj = json.loads(content)
                text = content_obj.get("text", str(content_obj)[:100])
            except:
                text = content[:100] if content else "[无内容]"
            print(f"      内容: {text[:80]}...")
    else:
        print("\n⚠️ 未获取到任何消息")
        print("\n可能的原因:")
        print("  1. 应用缺少 '获取单聊、群组历史消息' 权限 (im:message.history:readonly)")
        print("  2. 应用需要发布新版本才能使权限生效")
        print("  3. 群内没有今天的消息")
        print("  4. Bot 不在该群内")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
