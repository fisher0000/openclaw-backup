#!/bin/bash
# 法规知识库同步脚本
# 自动监控本地文件夹变更并同步到飞书云盘

# 配置
LOCAL_BASE="/home/node/法规知识库"
FEISHU_FOLDER_TOKEN="Ofu0fS87fl5SHwdTZSmcmXoQnse"
LOG_FILE="/home/node/.openclaw/workspace/logs/knowledge-sync.log"
LOCK_FILE="/tmp/knowledge-sync.lock"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 防止重复运行
if [ -f "$LOCK_FILE" ]; then
    echo -e "${YELLOW}[$(date)] 同步已在运行中，跳过${NC}" | tee -a "$LOG_FILE"
    exit 0
fi
touch "$LOCK_FILE"

echo -e "${GREEN}[$(date)] 开始同步法规知识库...${NC}" | tee -a "$LOG_FILE"

# 同步函数
sync_folder() {
    local local_dir="$1"
    local category="$2"
    
    echo -e "${YELLOW}[$(date)] 同步分类: $category${NC}" | tee -a "$LOG_FILE"
    
    # 获取飞书该分类文件夹的token
    local folder_token=$(get_folder_token "$category")
    
    if [ -z "$folder_token" ]; then
        echo -e "${RED}[$(date)] 错误: 无法获取 $category 的文件夹token${NC}" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # 遍历本地文件
    for file in "$local_dir"/*.{md,txt,pdf} 2>/dev/null; do
        [ -e "$file" ] || continue
        
        local filename=$(basename "$file")
        local mtime=$(stat -c %Y "$file")
        
        # 检查文件是否需要上传（新文件或已修改）
        if needs_upload "$filename" "$mtime"; then
            echo -e "${YELLOW}[$(date)] 上传: $filename${NC}" | tee -a "$LOG_FILE"
            upload_file "$file" "$folder_token" "$filename"
        fi
    done
}

# 获取分类文件夹token
get_folder_token() {
    local category="$1"
    case "$category" in
        "ICH") echo "MadJfDDtYldc8zdDXiycZnqunoc" ;;
        "NMPA") echo "GRZwfHxW6lfdJFdsWfbcaPOnnTI" ;;
        "FDA") echo "VBuzfII5FltYy4dDqc8cMKIunFf" ;;
        "EMA") echo "CQtbf6MBwlUd6kdBHI6cvmNMngf" ;;
        "研究专题") echo "GTELfptFVlvft5ddVvdcCh1Fn0c" ;;
        *) echo "" ;;
    esac
}

# 检查是否需要上传
needs_upload() {
    local filename="$1"
    local mtime="$2"
    local record_file="/tmp/knowledge-sync-records.txt"
    
    # 如果记录文件不存在，需要上传
    [ ! -f "$record_file" ] && return 0
    
    # 检查文件是否已修改
    local recorded_mtime=$(grep "^$filename:" "$record_file" 2>/dev/null | cut -d: -f2)
    
    if [ "$mtime" != "$recorded_mtime" ]; then
        return 0  # 需要上传
    else
        return 1  # 不需要上传
    fi
}

# 上传文件（使用OpenClaw工具）
upload_file() {
    local file_path="$1"
    local folder_token="$2"
    local filename="$3"
    
    # 这里调用飞书API上传
    # 实际实现需要通过OpenClaw的feishu_drive_file工具
    echo "UPLOAD:$file_path:$folder_token:$filename" 
    
    # 记录上传时间
    local mtime=$(stat -c %Y "$file_path")
    echo "$filename:$mtime" >> /tmp/knowledge-sync-records.txt
}

# 执行同步
sync_folder "$LOCAL_BASE/ICH" "ICH"
sync_folder "$LOCAL_BASE/NMPA" "NMPA"
sync_folder "$LOCAL_BASE/FDA" "FDA"
sync_folder "$LOCAL_BASE/EMA" "EMA"
sync_folder "$LOCAL_BASE/研究专题" "研究专题"

echo -e "${GREEN}[$(date)] 同步完成${NC}" | tee -a "$LOG_FILE"

# 清理锁文件
rm -f "$LOCK_FILE"
