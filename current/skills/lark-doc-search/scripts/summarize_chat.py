#!/usr/bin/env python3
"""
获取群聊历史消息并汇总
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta
from collections import defaultdict

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


def get_chat_history(token, chat_id, start_time=None, end_time=None):
    """
    获取群聊历史消息
    
    Args:
        token: tenant_access_token
        chat_id: 群ID
        start_time: 开始时间戳（毫秒）
        end_time: 结束时间戳（毫秒）
    """
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}"}
    
    all_messages = []
    page_token = None
    
    # 计算今天的时间范围
    if not start_time:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = int(today.timestamp() * 1000)
    if not end_time:
        end_time = int(time.time() * 1000)
    
    print(f"查询时间范围: {datetime.fromtimestamp(start_time/1000)} ~ {datetime.fromtimestamp(end_time/1000)}")
    
    while True:
        params = {
            "container_id_type": "chat",
            "container_id": chat_id,
            "start_time": start_time,
            "end_time": end_time,
            "page_size": 50
        }
        if page_token:
            params["page_token"] = page_token
        
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            result = resp.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                items = data.get("items", [])
                
                for msg in items:
                    all_messages.append({
                        "message_id": msg.get("message_id"),
                        "sender": msg.get("sender", {}),
                        "create_time": msg.get("create_time"),
                        "msg_type": msg.get("msg_type"),
                        "body": msg.get("body", {}),
                        "mentions": msg.get("mentions", [])
                    })
                
                # 检查是否有更多页
                page_token = data.get("page_token")
                has_more = data.get("has_more", False)
                
                if not has_more or not page_token:
                    break
            else:
                print(f"获取消息失败: {result}")
                return None
                
        except Exception as e:
            print(f"请求异常: {e}")
            return None
    
    return all_messages


def analyze_messages(messages):
    """分析消息，汇总统计"""
    if not messages:
        return {
            "total_count": 0,
            "participants": {},
            "messages_by_hour": {},
            "content_summary": []
        }
    
    # 按时间排序（最新的在前面，需要反转）
    messages = sorted(messages, key=lambda x: int(x.get("create_time", 0)))
    
    # 统计参与者
    participants = defaultdict(lambda: {
        "name": "未知",
        "id_type": "",
        "message_count": 0,
        "first_msg_time": None,
        "last_msg_time": None
    })
    
    # 按小时统计
    messages_by_hour = defaultdict(int)
    
    # 消息内容摘要
    content_summary = []
    
    for msg in messages:
        sender = msg.get("sender", {})
        sender_id = sender.get("id", "unknown")
        sender_name = sender.get("id", "未知用户")[:20]  # 简化显示
        
        # 更新参与者信息
        participants[sender_id]["message_count"] += 1
        participants[sender_id]["id_type"] = sender.get("sender_type", "")
        
        create_time = int(msg.get("create_time", 0)) / 1000
        create_datetime = datetime.fromtimestamp(create_time)
        time_str = create_datetime.strftime("%H:%M")
        
        if participants[sender_id]["first_msg_time"] is None:
            participants[sender_id]["first_msg_time"] = time_str
        participants[sender_id]["last_msg_time"] = time_str
        
        # 按小时统计
        hour_key = create_datetime.strftime("%H:00")
        messages_by_hour[hour_key] += 1
        
        # 提取消息内容
        msg_type = msg.get("msg_type", "")
        body = msg.get("body", {})
        content = body.get("content", "")
        
        # 尝试解析JSON内容
        try:
            content_obj = json.loads(content)
            if "text" in content_obj:
                text = content_obj["text"]
            else:
                text = str(content_obj)[:100]
        except:
            text = content[:100] if content else f"[{msg_type}消息]"
        
        # 截断过长的消息
        if len(text) > 80:
            text = text[:80] + "..."
        
        content_summary.append({
            "time": time_str,
            "sender": sender_name,
            "type": msg_type,
            "content": text
        })
    
    return {
        "total_count": len(messages),
        "participants": dict(participants),
        "messages_by_hour": dict(messages_by_hour),
        "content_summary": content_summary
    }


def format_report(analysis):
    """格式化输出报告"""
    report = []
    report.append("=" * 60)
    report.append("📊 OpenClaw运维群 今日消息汇总")
    report.append("=" * 60)
    report.append("")
    
    # 总体统计
    report.append(f"📈 总消息数: {analysis['total_count']} 条")
    report.append("")
    
    # 参与者统计
    participants = analysis['participants']
    report.append(f"👥 参与人数: {len(participants)} 人")
    report.append("-" * 40)
    
    # 按消息数排序
    sorted_participants = sorted(
        participants.items(),
        key=lambda x: x[1]['message_count'],
        reverse=True
    )
    
    for idx, (user_id, info) in enumerate(sorted_participants, 1):
        report.append(f"  {idx}. {user_id[:20]}...")
        report.append(f"     消息数: {info['message_count']} 条")
        report.append(f"     活跃时段: {info['first_msg_time']} ~ {info['last_msg_time']}")
        report.append("")
    
    # 时间分布
    report.append("⏰ 消息时间分布")
    report.append("-" * 40)
    for hour, count in sorted(analysis['messages_by_hour'].items()):
        bar = "█" * count
        report.append(f"  {hour}: {bar} ({count}条)")
    report.append("")
    
    # 消息内容摘要
    report.append("📝 消息内容摘要")
    report.append("-" * 40)
    
    # 只显示最近20条，避免过长
    summary = analysis['content_summary'][-20:]
    for msg in summary:
        report.append(f"  [{msg['time']}] {msg['sender'][:15]}: {msg['content']}")
    
    if len(analysis['content_summary']) > 20:
        report.append(f"  ... 还有 {len(analysis['content_summary']) - 20} 条消息")
    
    report.append("")
    report.append("=" * 60)
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    
    return "\n".join(report)


def main():
    print("🔑 正在获取 tenant_access_token...")
    token = get_tenant_access_token()
    if not token:
        print("❌ 获取 token 失败")
        sys.exit(1)
    print("✅ Token 获取成功")
    
    print("\n📨 正在获取今日群消息...")
    messages = get_chat_history(token, CHAT_ID)
    
    if messages is None:
        print("❌ 获取消息失败")
        sys.exit(1)
    
    print(f"✅ 获取到 {len(messages)} 条消息")
    
    print("\n📊 正在分析消息...")
    analysis = analyze_messages(messages)
    
    print("\n" + format_report(analysis))


if __name__ == "__main__":
    main()
