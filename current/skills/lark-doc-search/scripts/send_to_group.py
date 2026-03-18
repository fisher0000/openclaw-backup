#!/usr/bin/env python3
"""
查找 Bot 所在的群列表并发送消息
"""

import requests
import json
import sys

# 飞书应用凭证
APP_ID = "cli_a90ebb6fe8f81bd2"
APP_SECRET = "clSwYtz2CqvDfon3bKP2sh0wGBiV4nrT"


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


def get_bot_groups(token):
    """获取 Bot 所在的群列表"""
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    headers = {"Authorization": f"Bearer {token}"}
    
    groups = []
    page_token = None
    
    while True:
        params = {"page_size": 100}
        if page_token:
            params["page_token"] = page_token
            
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            result = resp.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                items = data.get("items", [])
                
                for group in items:
                    groups.append({
                        "chat_id": group.get("chat_id"),
                        "name": group.get("name"),
                        "description": group.get("description", ""),
                        "member_count": group.get("member_count", 0)
                    })
                
                # 检查是否有更多页
                page_token = data.get("page_token")
                if not page_token or not items:
                    break
            else:
                print(f"获取群列表失败: {result}")
                break
                
        except Exception as e:
            print(f"请求异常: {e}")
            break
    
    return groups


def send_group_message(token, chat_id, message):
    """发送群消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "chat_id"}
    
    data = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": message})
    }
    
    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        result = resp.json()
        
        if result.get("code") == 0:
            msg_data = result.get("data", {})
            return {
                "success": True,
                "message_id": msg_data.get("message_id"),
                "chat_id": msg_data.get("chat_id")
            }
        else:
            return {
                "success": False,
                "error": result.get("msg"),
                "code": result.get("code")
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("🔑 正在获取 tenant_access_token...")
    token = get_tenant_access_token()
    if not token:
        print("❌ 获取 token 失败")
        sys.exit(1)
    print("✅ Token 获取成功")
    
    print("\n📋 正在获取 Bot 所在的群列表...")
    groups = get_bot_groups(token)
    print(f"✅ 找到 {len(groups)} 个群")
    
    print("\n🏠 群列表:")
    target_group = None
    for i, group in enumerate(groups, 1):
        name = group.get("name", "未知")
        chat_id = group.get("chat_id", "")
        member_count = group.get("member_count", 0)
        
        print(f"  {i}. {name} (成员: {member_count})")
        print(f"     chat_id: {chat_id}")
        
        # 查找运维群
        if "运维" in name or "openclaw" in name.lower():
            target_group = group
            print(f"     ⭐ 找到目标群！")
    
    if not target_group:
        print("\n❌ 未找到包含'运维'或'openclaw'的群")
        print("请确认群名，或手动指定 chat_id")
        
        # 让用户选择
        if groups:
            print("\n可用的群:")
            for i, group in enumerate(groups, 1):
                print(f"  {i}. {group['name']}")
            
            choice = input("\n请输入要发送消息的群序号 (或按Ctrl+C取消): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(groups):
                    target_group = groups[idx]
                else:
                    print("❌ 无效的选择")
                    sys.exit(1)
            except ValueError:
                print("❌ 请输入数字")
                sys.exit(1)
        else:
            sys.exit(1)
    
    # 发送消息
    chat_id = target_group.get("chat_id")
    group_name = target_group.get("name")
    message = "我找到你了"
    
    print(f"\n📤 正在发送消息到群: {group_name}")
    print(f"   chat_id: {chat_id}")
    print(f"   消息内容: {message}")
    
    result = send_group_message(token, chat_id, message)
    
    if result.get("success"):
        print(f"\n✅ 消息发送成功！")
        print(f"   message_id: {result.get('message_id')}")
    else:
        print(f"\n❌ 消息发送失败")
        print(f"   错误码: {result.get('code')}")
        print(f"   错误信息: {result.get('error')}")


if __name__ == "__main__":
    main()
