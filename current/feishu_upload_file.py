#!/usr/bin/env python3
"""
飞书文件上传并发送脚本
支持：上传文件到飞书，并发送到指定聊天
"""

import requests
import json
import os
from pathlib import Path


class FeishuUploader:
    """飞书文件上传助手"""
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化
        
        Args:
            app_id: 飞书应用的 App ID
            app_secret: 飞书应用的 App Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self._token = None
    
    def _get_tenant_access_token(self) -> str:
        """获取 tenant_access_token"""
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") != 0:
            raise Exception(f"获取token失败: {data}")
        
        return data["tenant_access_token"]
    
    @property
    def token(self) -> str:
        """获取缓存的token（简单实现，生产环境建议加过期处理）"""
        if not self._token:
            self._token = self._get_tenant_access_token()
        return self._token
    
    def upload_file(self, file_path: str, file_type: str = "stream") -> str:
        """
        上传文件到飞书
        
        Args:
            file_path: 本地文件路径
            file_type: 文件类型 (stream/attachment/openupload等)
        
        Returns:
            file_key: 上传后的文件key，用于发送消息
        """
        url = f"{self.BASE_URL}/im/v1/files"
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 准备文件和数据
        with open(file_path, "rb") as f:
            files = {
                "file": (file_path.name, f, "application/octet-stream")
            }
            data = {
                "file_type": file_type,
                "file_name": file_path.name
            }
            
            resp = requests.post(url, headers=headers, files=files, data=data)
        
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") != 0:
            raise Exception(f"上传文件失败: {result}")
        
        file_key = result["data"]["file_key"]
        print(f"✅ 文件上传成功: {file_path.name}")
        print(f"   file_key: {file_key}")
        return file_key
    
    def send_file_message(self, chat_id: str, file_key: str, msg_type: str = "file") -> dict:
        """
        发送文件消息到聊天
        
        Args:
            chat_id: 聊天ID (格式: oc_xxx 或 ou_xxx)
            file_key: 上传文件后获取的file_key
            msg_type: 消息类型 (file/image/audio/media等)
        
        Returns:
            API响应结果
        """
        url = f"{self.BASE_URL}/im/v1/messages"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # 构建消息内容
        if msg_type == "file":
            content = {"file_key": file_key}
        elif msg_type == "image":
            content = {"image_key": file_key}
        else:
            content = {"file_key": file_key}
        
        params = {
            "receive_id_type": "chat_id" if chat_id.startswith("oc_") else "open_id"
        }
        
        payload = {
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": json.dumps(content)
        }
        
        resp = requests.post(url, headers=headers, params=params, json=payload)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") != 0:
            raise Exception(f"发送消息失败: {result}")
        
        print(f"✅ 消息发送成功!")
        print(f"   消息ID: {result['data']['message_id']}")
        return result


def main():
    """示例用法"""
    
    # ============ 配置区域 ============
    # 从环境变量读取（推荐）或直接填写
    APP_ID = os.getenv("FEISHU_APP_ID", "cli_xxxxx")  # 你的 App ID
    APP_SECRET = os.getenv("FEISHU_APP_SECRET", "xxxxxx")  # 你的 App Secret
    
    # 目标聊天ID (群聊: oc_xxxxx, 私聊: ou_xxxxx)
    CHAT_ID = "oc_xxxxxxxxxxxxxxxx"  # 修改为你的聊天ID
    
    # 要上传的文件路径
    FILE_PATH = "/path/to/your/file.pdf"  # 修改为你的文件路径
    # ===================================
    
    # 初始化
    uploader = FeishuUploader(APP_ID, APP_SECRET)
    
    try:
        # 1. 上传文件
        file_key = uploader.upload_file(FILE_PATH)
        
        # 2. 发送文件消息
        result = uploader.send_file_message(CHAT_ID, file_key, msg_type="file")
        
        print("\n🎉 全部完成!")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        raise


# ============ 进阶用法示例 ============

def upload_and_send_image():
    """上传并发送图片示例"""
    uploader = FeishuUploader(
        app_id=os.getenv("FEISHU_APP_ID"),
        app_secret=os.getenv("FEISHU_APP_SECRET")
    )
    
    # 上传图片
    image_key = uploader.upload_file("/path/to/image.png", file_type="image")
    
    # 发送图片消息
    uploader.send_file_message("oc_xxxxxx", image_key, msg_type="image")


def send_to_user():
    """发送给单个用户"""
    uploader = FeishuUploader(
        app_id=os.getenv("FEISHU_APP_ID"),
        app_secret=os.getenv("FEISHU_APP_SECRET")
    )
    
    file_key = uploader.upload_file("report.pdf")
    
    # 使用 open_id 发送给个人
    uploader.send_file_message(
        chat_id="ou_xxxxxx",  # 用户的 open_id
        file_key=file_key,
        msg_type="file"
    )


if __name__ == "__main__":
    main()
