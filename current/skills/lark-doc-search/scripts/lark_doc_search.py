#!/usr/bin/env python3
"""
飞书开放平台文档搜索技能
通过 MCP stdio 协议调用飞书开发者文档搜索
"""

import subprocess
import json
import sys
import argparse
import os
import time


class LarkMCPClient:
    """MCP 客户端，用于与飞书文档搜索服务通信"""
    
    def __init__(self):
        self.process = None
        self.request_id = 0
        
    def start(self):
        """启动 MCP server"""
        cmd = ["npx", "-y", "@larksuiteoapi/lark-mcp", "recall-developer-documents"]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # 行缓冲
            )
            # 等待服务启动
            time.sleep(2)
            return True
        except Exception as e:
            print(f"启动 MCP server 失败: {e}", file=sys.stderr)
            return False
            
    def stop(self):
        """停止 MCP server"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                
    def send_request(self, method: str, params: dict = None) -> dict:
        """发送 MCP 请求"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        if params:
            request["params"] = params
            
        request_json = json.dumps(request) + "\n"
        
        try:
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # 读取响应
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line)
            return {}
        except Exception as e:
            return {"error": str(e)}
            
    def list_tools(self) -> list:
        """列出可用工具"""
        response = self.send_request("tools/list")
        if "result" in response and "tools" in response["result"]:
            return response["result"]["tools"]
        return []
        
    def call_tool(self, name: str, arguments: dict) -> dict:
        """调用工具"""
        response = self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        return response


def search_docs(query: str, timeout: int = 30) -> str:
    """
    搜索飞书开放平台开发者文档
    
    Args:
        query: 搜索关键词
        timeout: 超时时间（秒）
        
    Returns:
        搜索结果文本
    """
    client = LarkMCPClient()
    
    try:
        # 启动服务
        if not client.start():
            return "无法启动 MCP 服务"
            
        # 列出工具
        tools = client.list_tools()
        if not tools:
            return "无法获取工具列表，服务可能未正常启动"
            
        # 使用已知的飞书文档搜索工具
        tool_name = "openplatform_developer_document_recall"
        
        # 调用搜索工具
        response = client.call_tool(tool_name, {"query": query})
        
        if "error" in response:
            return f"搜索出错: {response['error']}"
            
        if "result" in response:
            return format_search_result(response["result"])
            
        return "未返回搜索结果"
        
    except Exception as e:
        return f"搜索异常: {str(e)}"
    finally:
        client.stop()


def format_search_result(result: dict) -> str:
    """格式化搜索结果"""
    if not result:
        return "无搜索结果"
        
    output = []
    
    # 处理 content 字段
    if "content" in result:
        content = result["content"]
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    item_type = item.get("type", "")
                    if item_type == "text":
                        text = item.get("text", "")
                        if text:
                            output.append(text)
                    elif item_type == "resource":
                        resource = item.get("resource", {})
                        output.append(f"📄 {resource.get('name', '文档')}")
                        if "text" in resource:
                            output.append(resource["text"])
                else:
                    output.append(str(item))
        else:
            output.append(str(content))
            
    # 处理直接返回的文本
    if "text" in result:
        output.append(result["text"])
        
    if not output:
        # 返回原始 JSON 便于调试
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    return "\n\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="飞书开放平台文档搜索")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--list-tools", "-l", action="store_true",
                        help="列出可用工具后退出")
    
    args = parser.parse_args()
    
    if args.list_tools:
        client = LarkMCPClient()
        if client.start():
            time.sleep(2)
            tools = client.list_tools()
            client.stop()
            
            print("可用工具列表:")
            for tool in tools:
                print(f"\n  📌 {tool.get('name', '未知')}")
                print(f"     描述: {tool.get('description', '无')}")
        else:
            print("无法启动 MCP 服务")
        return
    
    # 执行搜索
    result = search_docs(args.query)
    print(result)


if __name__ == "__main__":
    main()
