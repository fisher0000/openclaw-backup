#!/usr/bin/env python3
"""
重新创建「个人知识库」文件夹结构并上传文件
"""

import subprocess
import json
import os

# 本地备份路径
KB_BASE = "/home/node/.openclaw/workspace/KB-backup/KB"

# 文件夹结构
FOLDERS = {
    "ICH": "MadJfDDtYldc8zdDXiycZnqunoc",
    "FDA": "VBuzfII5FltYy4dDqc8cMKIunFf", 
    "EMA": "CQtbf6MBwlUd6kdBHI6cvmNMngf",
    "NMPA CFDA CFDI": "GRZwfHxW6lfdJFdsWfbcaPOnnTI",
    "研究专题": "GTELfptFVlvft5ddVvdcCh1Fn0c"
}

# 根目录文件（不属于任何子文件夹）
ROOT_FILES = [
    "README.md",
    "头孢呋辛酯发补答复 V2-2026.04.01.md"
]

def upload_file(file_path, folder_token):
    """上传单个文件到飞书云盘"""
    cmd = [
        "openclaw", "tools", "feishu_drive_file",
        "action=upload",
        f"file_path={file_path}",
        f"folder_token={folder_token}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def sync_folder(local_folder, folder_token, folder_name):
    """同步整个文件夹"""
    folder_path = os.path.join(KB_BASE, local_folder)
    
    if not os.path.exists(folder_path):
        print(f"❌ 本地文件夹不存在: {folder_path}")
        return 0, 0
    
    files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    success_count = 0
    fail_count = 0
    
    print(f"\n📁 同步 {folder_name}/ ({len(files)} 个文件)")
    print("-" * 60)
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        success, msg = upload_file(file_path, folder_token)
        
        if success:
            print(f"  ✅ {filename}")
            success_count += 1
        else:
            print(f"  ❌ {filename} - {msg[:50]}")
            fail_count += 1
    
    return success_count, fail_count

def main():
    print("=" * 60)
    print("重新同步 GitHub KB 到飞书云盘")
    print("=" * 60)
    
    total_success = 0
    total_fail = 0
    
    # 同步各个子文件夹
    for folder_name, token in FOLDERS.items():
        success, fail = sync_folder(folder_name, token, folder_name)
        total_success += success
        total_fail += fail
    
    # 同步根目录文件
    print(f"\n📁 同步根目录文件")
    print("-" * 60)
    for filename in ROOT_FILES:
        file_path = os.path.join(KB_BASE, filename)
        if os.path.exists(file_path):
            # 根目录使用空 folder_token
            success, msg = upload_file(file_path, "")
            if success:
                print(f"  ✅ {filename}")
                total_success += 1
            else:
                print(f"  ❌ {filename}")
                total_fail += 1
    
    print("\n" + "=" * 60)
    print(f"同步完成: 成功 {total_success} 个, 失败 {total_fail} 个")
    print("=" * 60)

if __name__ == "__main__":
    main()
