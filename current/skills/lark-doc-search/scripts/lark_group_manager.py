#!/usr/bin/env python3
"""
飞书群管理技能 - 升级版
支持群搜索、群详情、批量操作等功能
"""

import requests
import json
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# 飞书应用凭证
APP_ID = "cli_a90ebb6fe8f81bd2"
APP_SECRET = "clSwYtz2CqvDfon3bKP2sh0wGBiV4nrT"


class LarkGroupManager:
    """飞书群管理类"""
    
    def __init__(self):
        self.token = None
        
    def get_token(self) -> str:
        """获取 tenant_access_token"""
        if self.token:
            return self.token
            
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=30)
        result = resp.json()
        
        if result.get("code") == 0:
            self.token = result.get("tenant_access_token")
            return self.token
        else:
            raise Exception(f"获取token失败: {result}")
    
    # ========== 群搜索功能 ==========
    
    def search_groups(self, query: str, page_size: int = 20) -> List[Dict]:
        """
        按名称搜索群聊
        
        Args:
            query: 搜索关键词
            page_size: 每页数量
            
        Returns:
            群列表
        """
        token = self.get_token()
        url = "https://open.feishu.cn/open-apis/im/v1/chats/search"
        headers = {"Authorization": f"Bearer {token}"}
        
        all_groups = []
        page_token = None
        
        while True:
            params = {
                "query": query,
                "page_size": min(page_size, 50)
            }
            if page_token:
                params["page_token"] = page_token
            
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            result = resp.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                items = data.get("items", [])
                all_groups.extend(items)
                
                page_token = data.get("page_token")
                if not data.get("has_more") or not page_token:
                    break
            else:
                print(f"搜索失败: {result.get('msg')}")
                break
        
        return all_groups
    
    # ========== 群详情功能 ==========
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict]:
        """
        获取群详细信息
        
        Args:
            chat_id: 群ID
            
        Returns:
            群详情
        """
        token = self.get_token()
        url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}"
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = requests.get(url, headers=headers, timeout=30)
        result = resp.json()
        
        if result.get("code") == 0:
            return result.get("data", {})
        else:
            print(f"获取群详情失败: {result.get('msg')}")
            return None
    
    def get_bot_groups(self) -> List[Dict]:
        """获取Bot所在的所有群"""
        token = self.get_token()
        url = "https://open.feishu.cn/open-apis/im/v1/chats"
        headers = {"Authorization": f"Bearer {token}"}
        
        all_groups = []
        page_token = None
        
        while True:
            params = {"page_size": 100}
            if page_token:
                params["page_token"] = page_token
            
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            result = resp.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                items = data.get("items", [])
                all_groups.extend(items)
                
                page_token = data.get("page_token")
                if not data.get("has_more") or not page_token:
                    break
            else:
                break
        
        return all_groups
    
    def is_bot_in_chat(self, chat_id: str) -> bool:
        """检查Bot是否在群里"""
        token = self.get_token()
        url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members/is_in_chat"
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = requests.get(url, headers=headers, timeout=30)
        result = resp.json()
        
        if result.get("code") == 0:
            return result.get("data", {}).get("is_in_chat", False)
        return False
    
    def get_chat_members(self, chat_id: str) -> List[Dict]:
        """获取群成员列表"""
        token = self.get_token()
        url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members"
        headers = {"Authorization": f"Bearer {token}"}
        
        all_members = []
        page_token = None
        
        while True:
            params = {"page_size": 100}
            if page_token:
                params["page_token"] = page_token
            
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            result = resp.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                items = data.get("items", [])
                all_members.extend(items)
                
                page_token = data.get("page_token")
                if not data.get("has_more") or not page_token:
                    break
            else:
                break
        
        return all_members
    
    # ========== 消息功能 ==========
    
    def send_message(self, chat_id: str, message: str, msg_type: str = "text") -> bool:
        """
        发送群消息
        
        Args:
            chat_id: 群ID
            message: 消息内容
            msg_type: 消息类型(text/post/image等)
            
        Returns:
            是否成功
        """
        token = self.get_token()
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {"receive_id_type": "chat_id"}
        
        if msg_type == "text":
            content = json.dumps({"text": message})
        else:
            content = message
        
        data = {
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": content
        }
        
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        result = resp.json()
        
        if result.get("code") == 0:
            return True
        else:
            print(f"发送失败: {result.get('msg')}")
            return False
    
    def broadcast_message(self, query: str, message: str, dry_run: bool = False) -> Dict:
        """
        批量群发消息
        
        Args:
            query: 群名称关键词
            message: 消息内容
            dry_run: 是否只预览不发送
            
        Returns:
            发送结果统计
        """
        # 搜索匹配的群
        groups = self.search_groups(query)
        
        if not groups:
            print(f"未找到包含 '{query}' 的群")
            return {"success": 0, "failed": 0, "total": 0}
        
        print(f"\n找到 {len(groups)} 个匹配的群:")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group.get('name', '未知')} ({group.get('chat_id', '')})")
        
        if dry_run:
            print(f"\n[试运行模式] 将发送消息到以上 {len(groups)} 个群")
            print(f"消息内容: {message[:50]}...")
            return {"success": 0, "failed": 0, "total": len(groups), "dry_run": True}
        
        # 确认发送
        confirm = input(f"\n确认发送消息到以上 {len(groups)} 个群? (yes/no): ")
        if confirm.lower() != "yes":
            print("已取消")
            return {"success": 0, "failed": 0, "total": 0, "cancelled": True}
        
        # 发送消息
        success = 0
        failed = 0
        
        for group in groups:
            chat_id = group.get("chat_id")
            name = group.get("name", "未知")
            
            if self.send_message(chat_id, message):
                print(f"  ✅ {name}")
                success += 1
            else:
                print(f"  ❌ {name}")
                failed += 1
        
        return {"success": success, "failed": failed, "total": len(groups)}


# ========== 命令行接口 ==========

def print_groups(groups: List[Dict], verbose: bool = False):
    """打印群列表"""
    if not groups:
        print("未找到群")
        return
    
    print(f"\n找到 {len(groups)} 个群:\n")
    print(f"{'序号':<4} {'群名称':<30} {'成员数':<6} {'chat_id':<30}")
    print("-" * 80)
    
    for i, group in enumerate(groups, 1):
        name = group.get("name", "未知")[:28]
        member_count = group.get("member_count", 0)
        chat_id = group.get("chat_id", "")[:28]
        
        print(f"{i:<4} {name:<30} {member_count:<6} {chat_id:<30}")
    
    if verbose:
        print("\n详细信息:")
        for i, group in enumerate(groups, 1):
            print(f"\n  [{i}] {group.get('name', '未知')}")
            print(f"      chat_id: {group.get('chat_id', '')}")
            print(f"      描述: {group.get('description', '无')[:50]}")


def main():
    parser = argparse.ArgumentParser(description="飞书群管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 搜索群
    search_parser = subparsers.add_parser("search", help="搜索群聊")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    
    # 列出Bot的群
    list_parser = subparsers.add_parser("list", help="列出Bot所在的群")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    
    # 获取群详情
    info_parser = subparsers.add_parser("info", help="获取群详情")
    info_parser.add_argument("chat_id", help="群ID")
    
    # 发送消息
    send_parser = subparsers.add_parser("send", help="发送消息")
    send_parser.add_argument("chat_id", help="群ID")
    send_parser.add_argument("message", help="消息内容")
    
    # 批量发送
    broadcast_parser = subparsers.add_parser("broadcast", help="批量群发")
    broadcast_parser.add_argument("query", help="群名称关键词")
    broadcast_parser.add_argument("message", help="消息内容")
    broadcast_parser.add_argument("--dry-run", action="store_true", help="试运行模式")
    
    # 检查Bot是否在群里
    check_parser = subparsers.add_parser("check", help="检查Bot是否在群里")
    check_parser.add_argument("chat_id", help="群ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = LarkGroupManager()
    
    try:
        if args.command == "search":
            # 搜索群
            groups = manager.search_groups(args.query)
            print_groups(groups, args.verbose)
            
        elif args.command == "list":
            # 列出Bot的群
            groups = manager.get_bot_groups()
            print_groups(groups, args.verbose)
            
        elif args.command == "info":
            # 获取群详情
            info = manager.get_chat_info(args.chat_id)
            if info:
                print(f"\n群详情:")
                print(f"  名称: {info.get('name', '未知')}")
                print(f"  描述: {info.get('description', '无')}")
                print(f"  成员数: {info.get('member_count', 0)}")
                print(f"  群主: {info.get('owner_id', '未知')}")
                print(f"  群模式: {info.get('chat_mode', '未知')}")
                print(f"  群类型: {info.get('chat_type', '未知')}")
                print(f"  创建时间: {info.get('create_time', '未知')}")
            else:
                print("获取群详情失败")
                
        elif args.command == "send":
            # 发送消息
            if manager.send_message(args.chat_id, args.message):
                print("✅ 消息发送成功")
            else:
                print("❌ 消息发送失败")
                
        elif args.command == "broadcast":
            # 批量发送
            result = manager.broadcast_message(args.query, args.message, args.dry_run)
            if not args.dry_run and not result.get("cancelled"):
                print(f"\n发送结果: 成功 {result['success']}/{result['total']}")
                
        elif args.command == "check":
            # 检查Bot是否在群里
            if manager.is_bot_in_chat(args.chat_id):
                print(f"✅ Bot在群 {args.chat_id} 中")
            else:
                print(f"❌ Bot不在群 {args.chat_id} 中")
    
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
