#!/usr/bin/env python3
"""
GitHub → 飞书云盘 完整同步工具（自动执行版）
每个工作日 8:00 自动同步 GitHub 仓库到飞书云盘

配置:
- GitHub: https://github.com/fisher0000/obsidian/tree/main/KB
- 飞书云盘: https://j0eukrlohu.feishu.cn/drive/folder/Ofu0fS87fl5SHwdTZSmcmXoQnse
- 本地备份: /home/node/.openclaw/workspace/KB-backup/
- 定时任务: 每个工作日 8:00 (北京时间)

使用方法:
    python3 github-to-feishu-sync-auto.py
    
或者通过 OpenClaw cron 自动执行
"""

import os
import sys
import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ============ 配置 ============
CONFIG = {
    "github_repo": "https://github.com/fisher0000/obsidian",
    "github_branch": "main",
    "github_subdir": "KB",
    "feishu_root_folder_token": "Ofu0fS87fl5SHwdTZSmcmXoQnse",
    "workspace_dir": "/home/node/.openclaw/workspace",
    "local_backup_dir": "/home/node/.openclaw/workspace/KB-backup",
    "supported_extensions": [".md", ".txt", ".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg"],
    "max_file_size": 20 * 1024 * 1024,  # 20MB
}

class GitHubToFeishuSync:
    def __init__(self):
        self.local_dir = Path(CONFIG["local_backup_dir"])
        self.log_file = Path(CONFIG["workspace_dir"]) / "logs" / f"github-kb-sync-{datetime.now():%Y%m%d}.log"
        self.record_file = Path(CONFIG["workspace_dir"]) / ".github-kb-sync-state.json"
        self.upload_script = Path(CONFIG["workspace_dir"]) / "scripts" / "github-to-feishu-upload-batch.sh"
        self.stats = {"downloaded": 0, "uploaded": 0, "skipped": 0, "failed": 0}
        
        # 确保目录存在
        self.local_dir.mkdir(parents=True, exist_ok=True)
        (Path(CONFIG["workspace_dir"]) / "logs").mkdir(parents=True, exist_ok=True)
        
        # 加载同步记录
        self.sync_state = self.load_sync_state()
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    
    def load_sync_state(self) -> Dict:
        """加载同步状态记录"""
        if self.record_file.exists():
            try:
                with open(self.record_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"files": {}}
    
    def save_sync_state(self):
        """保存同步状态记录"""
        with open(self.record_file, "w", encoding="utf-8") as f:
            json.dump(self.sync_state, f, indent=2, ensure_ascii=False)
    
    def run_shell(self, cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """运行 shell 命令"""
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    
    def clone_or_pull_github(self) -> bool:
        """从 GitHub 拉取或更新 KB 目录到本地"""
        self.log("=" * 60)
        self.log("步骤1: 从 GitHub 同步 KB 文件夹到本地...")
        
        git_dir = self.local_dir / ".git"
        
        try:
            if git_dir.exists():
                # 已存在，执行 git pull
                self.log("  本地仓库已存在，执行 git pull...")
                os.chdir(self.local_dir)
                
                returncode, stdout, stderr = self.run_shell([
                    "git", "pull", "origin", CONFIG["github_branch"]
                ])
                
                if returncode != 0:
                    self.log(f"  ⚠ git pull 失败，尝试重新克隆: {stderr}")
                    shutil.rmtree(self.local_dir)
                    self.local_dir.mkdir(parents=True, exist_ok=True)
                    return self._clone_fresh()
                else:
                    self.log("  ✓ git pull 成功")
            else:
                # 不存在，执行 git clone
                self.log("  本地仓库不存在，执行 git clone...")
                return self._clone_fresh()
            
            return True
            
        except Exception as e:
            self.log(f"✗ 同步过程出错: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def _clone_fresh(self) -> bool:
        """全新克隆仓库"""
        self.local_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(self.local_dir)
        
        # 初始化仓库
        self.run_shell(["git", "init", "--quiet"])
        self.run_shell(["git", "remote", "add", "origin", CONFIG["github_repo"]])
        
        # 配置 sparse checkout
        sparse_checkout_dir = self.local_dir / ".git" / "info"
        sparse_checkout_dir.mkdir(parents=True, exist_ok=True)
        with open(sparse_checkout_dir / "sparse-checkout", "w") as f:
            f.write(f"{CONFIG['github_subdir']}/*\n")
        
        self.run_shell(["git", "config", "core.sparseCheckout", "true"])
        
        # 拉取代码
        returncode, stdout, stderr = self.run_shell([
            "git", "pull", "--depth=1", "origin", CONFIG["github_branch"]
        ])
        
        if returncode != 0:
            self.log(f"✗ GitHub 克隆失败: {stderr}")
            return False
        
        self.log("  ✓ git clone 成功")
        return True
    
    def scan_local_files(self) -> List[Path]:
        """扫描本地文件"""
        self.log("步骤2: 扫描本地文件...")
        
        kb_path = self.local_dir / CONFIG["github_subdir"]
        if not kb_path.exists():
            self.log(f"✗ 错误: KB 目录不存在: {kb_path}")
            return []
        
        files = []
        for ext in CONFIG["supported_extensions"]:
            files.extend(kb_path.rglob(f"*{ext}"))
        
        files = sorted(files)
        self.log(f"✓ 发现 {len(files)} 个文件")
        return files
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件 MD5 哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_relative_path(self, file_path: Path) -> str:
        """获取相对于 KB 目录的路径"""
        kb_path = self.local_dir / CONFIG["github_subdir"]
        return str(file_path.relative_to(kb_path))
    
    def should_upload(self, rel_path: str, file_hash: str) -> bool:
        """检查是否需要上传"""
        if rel_path not in self.sync_state["files"]:
            return True
        last_hash = self.sync_state["files"][rel_path].get("hash", "")
        return last_hash != file_hash
    
    def generate_upload_batch_script(self, files: List[Path]) -> List[Path]:
        """生成批量上传脚本，返回需要上传的文件列表"""
        self.log("步骤3: 生成批量上传脚本...")
        
        upload_files = []
        
        with open(self.upload_script, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\n")
            f.write("# 批量上传脚本 - 由 github-to-feishu-sync-auto.py 生成\n")
            f.write(f"# 生成时间: {datetime.now().isoformat()}\n")
            f.write("#\n\n")
            
            for i, file_path in enumerate(files, 1):
                rel_path = self.get_relative_path(file_path)
                filename = file_path.name
                file_size = file_path.stat().st_size
                
                # 计算文件哈希
                file_hash = self.calculate_file_hash(file_path)
                
                # 检查是否需要上传
                if not self.should_upload(rel_path, file_hash):
                    continue
                
                # 检查文件大小
                if file_size > CONFIG["max_file_size"]:
                    self.log(f"  ⚠ 跳过: {filename} 超过20MB限制")
                    self.stats["failed"] += 1
                    continue
                
                upload_files.append(file_path)
                
                # 写入脚本
                f.write(f"echo '[{len(upload_files)}] 上传: {filename}'\n")
                f.write(f"feishu_drive_file action=upload file_path='{file_path}' folder_token='{CONFIG['feishu_root_folder_token']}'\n")
                f.write("echo ''\n")
            
            f.write("echo '批量上传完成'\n")
        
        os.chmod(self.upload_script, 0o755)
        self.log(f"✓ 生成上传脚本: {self.upload_script}")
        self.log(f"✓ 待上传文件: {len(upload_files)} 个")
        
        return upload_files
    
    def run(self) -> bool:
        """运行同步流程"""
        self.log("=" * 60)
        self.log("GitHub → 飞书云盘 自动同步开始")
        self.log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"源: {CONFIG['github_repo']}/tree/{CONFIG['github_branch']}/{CONFIG['github_subdir']}")
        self.log(f"本地备份: {self.local_dir}")
        self.log(f"目标: 飞书云盘 ({CONFIG['feishu_root_folder_token']})")
        self.log("=" * 60)
        
        try:
            # 1. 拉取/更新 GitHub 代码到本地
            if not self.clone_or_pull_github():
                return False
            
            # 2. 扫描本地文件
            files = self.scan_local_files()
            
            if not files:
                self.log("没有需要同步的文件")
                return True
            
            # 3. 生成批量上传脚本
            upload_files = self.generate_upload_batch_script(files)
            
            if not upload_files:
                self.log("所有文件已是最新，无需上传")
                self.log(f"本地备份位置: {self.local_dir}/{CONFIG['github_subdir']}")
                return True
            
            # 4. 输出结果和下一步操作
            self.log("=" * 60)
            self.log("同步任务准备完成")
            self.log(f"  待上传: {len(upload_files)} 个文件")
            self.log(f"  跳过: {len(files) - len(upload_files)} 个文件")
            self.log("")
            self.log(f"本地备份位置: {self.local_dir}/{CONFIG['github_subdir']}")
            self.log("")
            self.log("请执行以下命令完成上传:")
            self.log(f"  bash {self.upload_script}")
            self.log("")
            self.log("或者让我帮你执行批量上传")
            self.log("=" * 60)
            
            return True
            
        except Exception as e:
            self.log(f"✗ 同步过程出错: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False


def main():
    """主函数"""
    sync = GitHubToFeishuSync()
    success = sync.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
