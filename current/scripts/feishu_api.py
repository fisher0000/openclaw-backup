#!/usr/bin/env python3
"""
飞书文件上传与发送工具
支持：上传图片/文件到飞书，并发送到指定会话
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any


class FeishuAPI:
    """飞书API客户端"""
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._tenant_token: Optional[str] = None
    
    def _get_tenant_token(self) -> str:
        """获取租户访问令牌"""
        if self._tenant_token:
            return self._tenant_token
            
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") != 0:
            raise Exception(f"获取token失败: {data}")
        
        self._tenant_token = data["tenant_access_token"]
        return self._tenant_token
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_tenant_token()}",
            "Content-Type": "application/json"
        }
    
    def upload_image(self, image_path: str, image_type: str = "message") -> str:
        """
        上传图片到飞书
        
        Args:
            image_path: 图片本地路径
            image_type: 图片类型 (message/avatar)
        
        Returns:
            image_key: 图片key，用于发送消息
        """
        url = f"{self.BASE_URL}/im/v1/images"
        
        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"image_type": image_type}
            headers = {"Authorization": f"Bearer {self._get_tenant_token()}"}
            
            resp = requests.post(url, headers=headers, files=files, data=data)
        
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") != 0:
            raise Exception(f"上传图片失败: {result}")
        
        return result["data"]["image_key"]
    
    def upload_file(self, file_path: str, file_type: str = "stream") -> str:
        """
        上传文件到飞书
        
        Args:
            file_path: 文件本地路径
            file_type: 文件类型 (stream/attachment)
        
        Returns:
            file_key: 文件key，用于发送消息
        """
        url = f"{self.BASE_URL}/im/v1/files"
        
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path)
        
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f)}
            data = {
                "file_type": file_type,
                "file_name": file_name
            }
            headers = {"Authorization": f"Bearer {self._get_tenant_token()}"}
            
            resp = requests.post(url, headers=headers, files=files, data=data)
        
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") != 0:
            raise Exception(f"上传文件失败: {result}")
        
        return result["data"]["file_key"]
    
    def send_text_message(self, receive_id: str, text: str, receive_id_type: str = "chat_id") -> Dict:
        """发送文本消息"""
        url = f"{self.BASE_URL}/im/v1/messages"
        
        params = {"receive_id_type": receive_id_type}
        body = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }
        
        resp = requests.post(url, headers=self.headers, params=params, json=body)
        resp.raise_for_status()
        return resp.json()
    
    def send_image_message(self, receive_id: str, image_key: str, receive_id_type: str = "chat_id") -> Dict:
        """发送图片消息"""
        url = f"{self.BASE_URL}/im/v1/messages"
        
        params = {"receive_id_type": receive_id_type}
        body = {
            "receive_id": receive_id,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key})
        }
        
        resp = requests.post(url, headers=self.headers, params=params, json=body)
        resp.raise_for_status()
        return resp.json()
    
    def send_file_message(self, receive_id: str, file_key: str, receive_id_type: str = "chat_id") -> Dict:
        """发送文件消息"""
        url = f"{self.BASE_URL}/im/v1/messages"
        
        params = {"receive_id_type": receive_id_type}
        body = {
            "receive_id": receive_id,
            "msg_type": "file",
            "content": json.dumps({"file_key": file_key})
        }
        
        resp = requests.post(url, headers=self.headers, params=params, json=body)
        resp.raise_for_status()
        return resp.json()
    
    def upload_and_send_image(self, receive_id: str, image_path: str, receive_id_type: str = "chat_id") -> Dict:
        """上传并发送图片（一键操作）"""
        print(f"📤 上传图片: {image_path}")
        image_key = self.upload_image(image_path)
        print(f"✅ 获取image_key: {image_key}")
        
        print(f"📨 发送图片到: {receive_id}")
        result = self.send_image_message(receive_id, image_key, receive_id_type)
        print(f"✅ 发送成功")
        return result
    
    def upload_and_send_file(self, receive_id: str, file_path: str, receive_id_type: str = "chat_id") -> Dict:
        """上传并发送文件（一键操作）"""
        print(f"📤 上传文件: {file_path}")
        file_key = self.upload_file(file_path)
        print(f"✅ 获取file_key: {file_key}")
        
        print(f"📨 发送文件到: {receive_id}")
        result = self.send_file_message(receive_id, file_key, receive_id_type)
        print(f"✅ 发送成功")
        return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="飞书文件上传与发送工具")
    parser.add_argument("--app-id", default=os.getenv("FEISHU_APP_ID"), help="飞书应用ID")
    parser.add_argument("--app-secret", default=os.getenv("FEISHU_APP_SECRET"), help="飞书应用密钥")
    parser.add_argument("--receive-id", required=True, help="接收者ID (群聊ID或用户ID)")
    parser.add_argument("--id-type", default="chat_id", choices=["chat_id", "open_id", "user_id"], help="ID类型")
    parser.add_argument("--text", help="发送文本消息")
    parser.add_argument("--image", help="上传并发送图片")
    parser.add_argument("--file", help="上传并发送文件")
    
    args = parser.parse_args()
    
    if not args.app_id or not args.app_secret:
        print("❌ 错误: 需要提供 --app-id 和 --app-secret，或设置环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET")
        sys.exit(1)
    
    # 初始化API客户端
    api = FeishuAPI(args.app_id, args.app_secret)
    
    # 执行操作
    if args.text:
        result = api.send_text_message(args.receive_id, args.text, args.id_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.image:
        if not os.path.exists(args.image):
            print(f"❌ 错误: 图片不存在: {args.image}")
            sys.exit(1)
        result = api.upload_and_send_image(args.receive_id, args.image, args.id_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.file:
        if not os.path.exists(args.file):
            print(f"❌ 错误: 文件不存在: {args.file}")
            sys.exit(1)
        result = api.upload_and_send_file(args.receive_id, args.file, args.id_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print("❌ 错误: 需要提供 --text / --image / --file 之一")
        sys.exit(1)


if __name__ == "__main__":
    main()
