#!/usr/bin/env python3
"""
获取群聊历史消息 - 全面排查
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
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}
    
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


def check_permissions(token):
    """检查应用权限"""
    print("\n🔐 检查应用权限...")
    
    # 通过获取应用信息来查看权限
    url = "https://open.feishu.cn/open-apis/application/v6/applications"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        result = resp.json()
        
        if result.get("code") == 0:
            apps = result.get("data", {}).get("apps", [])
            for app in apps:
                if app.get("app_id") == APP_ID:
                    print(f"应用名称: {app.get('app_name')}")
                    # 查看是否有消息相关权限
                    return True
        else:
            print(f"查询应用信息失败: {result}")
    except Exception as e:
        print(f"请求异常: {e}")
    
    return False


def try_get_messages(token, chat_id, start_time=None, end_time=None, page_token=None):
    """尝试获取消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {
        "container_id_type": "chat",
        "container_id": chat_id,
        "page_size": 50
    }
    
    # 如果不传时间参数，可能会获取到更多消息
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    if page_token:
        params["page_token"] = page_token
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def get_recent_messages(token, chat_id, minutes=60):
    """获取最近N分钟的消息"""
    print(f"\n⏰ 尝试获取最近 {minutes} 分钟的消息...")
    
    end_time = int(time.time() * 1000)
    start_time = int((time.time() - minutes * 60) * 1000)
    
    result = try_get_messages(token, chat_id, start_time, end_time)
    
    if result.get("code") == 0:
        items = result.get("data", {}).get("items", [])
        print(f"✅ 获取到 {len(items)} 条消息")
        return items
    else:
        print(f"❌ 失败: {result.get('msg', result)}")
        return []


def get_all_messages_no_time_limit(token, chat_id):
    """不限制时间范围获取消息"""
    print("\n🔍 尝试不限制时间范围获取消息...")
    
    result = try_get_messages(token, chat_id)
    
    if result.get("code") == 0:
        items = result.get("data", {}).get("items", [])
        print(f"✅ 获取到 {len(items)} 条消息")
        if items:
            print(f"\n最新消息时间: {items[0].get('create_time')}")
            print(f"最早消息时间: {items[-1].get('create_time')}")
        return items
    else:
        print(f"❌ 失败: {result.get('msg', result)}")
        return []


def check_specific_user_messages(token, chat_id, user_open_id):
    """检查特定用户的消息"""
    print(f"\n👤 尝试获取用户 {user_open_id[:20]}... 的消息...")
    
    # 获取最近24小时
    end_time = int(time.time() * 1000)
    start_time = int((time.time() - 24 * 3600) * 1000)
    
    messages = []
    page_token = None
    
    while True:
        result = try_get_messages(token, chat_id, start_time, end_time, page_token)
        
        if result.get("code") != 0:
            print(f"❌ 获取失败: {result.get('msg')}")
            break
        
        data = result.get("data", {})
        items = data.get("items", [])
        
        for msg in items:
            sender = msg.get("sender", {})
            if sender.get("id") == user_open_id:
                messages.append(msg)
        
        page_token = data.get("page_token")
        if not data.get("has_more") or not page_token:
            break
    
    print(f"✅ 该用户今天发了 {len(messages)} 条消息")
    return messages


def analyze_with_robot_perspective():
    """从Bot的角度分析可能的原因"""
    print("\n" + "="*60)
    print("🤔 深度分析 - 为什么获取不到消息？")
    print("="*60)
    
    print("""
可能的原因分析：

1. ✅ 权限确实已授权
   - 能获取群成员列表（13人）
   - 能发送消息到群里
   - API调用不报错，只是返回空

2. 🔍 可能的真实原因：
   
   a) 【消息时间范围】
      - 飞书API默认可能只返回特定时间范围的消息
      - 今天群内确实没有通过API可见的消息
      - 或者消息被企业设置保留策略删除了
   
   b) 【企业安全设置】
      - 企业可能设置了"不允许应用读取群聊历史"
      - 即使给了权限，企业级设置可能覆盖应用权限
      - 某些企业要求消息端到端加密，应用无法读取
   
   c) 【API限制】
      - im/v1/messages 接口可能需要特定条件
      - 或者需要使用其他接口，如 webhook、事件订阅
   
   d) 【Bot的可见性】
      - Bot可能只能看到加入群之后的消息
      - 或者只能看到被@的消息

3. 💡 验证方法：
   - 让我现在发一条消息到群里
   - 然后立即查询，看能否读到这条消息
   - 如果能读到，说明权限没问题，只是之前没消息
   - 如果读不到，说明有其他限制
""")


def test_real_time_message(token, chat_id):
    """测试实时消息读取"""
    print("\n🧪 测试实时消息读取...")
    print("请现在在群里发送一条消息，然后按回车继续...")
    print("（或者直接按回车跳过此测试）")
    
    try:
        input()
    except:
        pass
    
    # 获取最近5分钟的消息
    messages = get_recent_messages(token, chat_id, minutes=5)
    
    if messages:
        print("\n✅ 成功读取到消息！权限是正常的。")
        print(f"获取到 {len(messages)} 条消息:")
        for msg in messages[:3]:
            sender = msg.get("sender", {})
            print(f"  - {sender.get('id', '未知')[:20]}: {msg.get('msg_type')}")
    else:
        print("\n⚠️ 仍然没有获取到消息。可能存在以下限制:")
        print("  1. 企业安全策略阻止应用读取消息")
        print("  2. 需要使用事件订阅(webhook)方式接收消息")
        print("  3. 群设置了隐私保护")
    
    return messages


def main():
    print("="*60)
    print("飞书群消息查询 - 深度排查")
    print("="*60)
    
    print("\n🔑 获取 tenant_access_token...")
    token = get_tenant_access_token()
    if not token:
        print("❌ 获取 token 失败")
        sys.exit(1)
    print("✅ Token 获取成功")
    
    # 检查权限
    check_permissions(token)
    
    # 尝试1：今天的消息
    print("\n" + "-"*60)
    print("尝试1：获取今天的所有消息")
    print("-"*60)
    today_messages = get_recent_messages(token, CHAT_ID, minutes=24*60)
    
    # 尝试2：不限制时间
    print("\n" + "-"*60)
    print("尝试2：不限制时间范围获取消息")
    print("-"*60)
    all_messages = get_all_messages_no_time_limit(token, CHAT_ID)
    
    # 尝试3：查找特定用户（你）的消息
    print("\n" + "-"*60)
    print("尝试3：查找你的消息（张俊）")
    print("-"*60)
    your_open_id = "ou_0ca7bc3d9082f8b2e436b8771a430569"
    your_messages = check_specific_user_messages(token, CHAT_ID, your_open_id)
    
    # 分析可能的原因
    analyze_with_robot_perspective()
    
    # 测试实时读取
    # test_real_time_message(token, CHAT_ID)
    
    print("\n" + "="*60)
    print("总结")
    print("="*60)
    print(f"今天消息数: {len(today_messages)}")
    print(f"不限时间消息数: {len(all_messages)}")
    print(f"你的消息数: {len(your_messages)}")
    
    if today_messages or all_messages:
        print("\n✅ 好消息：可以获取到消息！")
        print("可能今天群里确实没有新消息，或者消息被其他方式处理了。")
    else:
        print("\n⚠️ 无法获取历史消息")
        print("建议：")
        print("  1. 使用飞书事件订阅方式接收实时消息")
        print("  2. 检查企业安全设置")
        print("  3. 确认是否需要申请更高权限")


if __name__ == "__main__":
    main()
