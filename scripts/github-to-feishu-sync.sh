#!/bin/bash
# GitHub → 飞书云盘 定时同步脚本
# 每天自动同步 GitHub 仓库到飞书云盘

# 配置
GITHUB_REPO="https://github.com/fisher0000/obsidian"
GITHUB_BRANCH="main"
GITHUB_SUBDIR="KB"
LOCAL_TEMP_DIR="/tmp/github-kb-sync"
FEISHU_ROOT_FOLDER_TOKEN="Ofu0fS87fl5SHwdTZSmcmXoQnse"
LOG_FILE="/home/node/.openclaw/workspace/logs/github-kb-sync.log"
LOCK_FILE="/tmp/github-kb-sync.lock"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 防止重复运行
if [ -f "$LOCK_FILE" ]; then
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] 同步已在运行中，跳过${NC}" | tee -a "$LOG_FILE"
    exit 0
fi
touch "$LOCK_FILE"

# 清理函数
cleanup() {
    rm -f "$LOCK_FILE"
    rm -rf "$LOCAL_TEMP_DIR"
}
trap cleanup EXIT

echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ========== 开始 GitHub → 飞书云盘同步 ==========${NC}" | tee -a "$LOG_FILE"

# 1. 克隆/拉取 GitHub 仓库
echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] 步骤1: 从 GitHub 拉取最新代码...${NC}" | tee -a "$LOG_FILE"

if [ -d "$LOCAL_TEMP_DIR/.git" ]; then
    cd "$LOCAL_TEMP_DIR"
    git fetch origin "$GITHUB_BRANCH" 2>&1 | tee -a "$LOG_FILE"
    git reset --hard "origin/$GITHUB_BRANCH" 2>&1 | tee -a "$LOG_FILE"
else
    rm -rf "$LOCAL_TEMP_DIR"
    git clone --depth 1 --branch "$GITHUB_BRANCH" "$GITHUB_REPO" "$LOCAL_TEMP_DIR" 2>&1 | tee -a "$LOG_FILE"
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] 错误: GitHub 拉取失败${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

KB_DIR="$LOCAL_TEMP_DIR/$GITHUB_SUBDIR"
if [ ! -d "$KB_DIR" ]; then
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] 错误: KB 目录不存在: $KB_DIR${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] GitHub 拉取成功${NC}" | tee -a "$LOG_FILE"

# 2. 获取飞书云盘现有文件列表
echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] 步骤2: 获取飞书云盘现有文件列表...${NC}" | tee -a "$LOG_FILE"

# 调用 OpenClaw 工具获取文件列表
# 注意：这里需要通过 feishu_drive_file 工具实现
# 暂时记录需要同步的文件

# 3. 遍历本地文件并同步到飞书
echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] 步骤3: 开始同步文件到飞书云盘...${NC}" | tee -a "$LOG_FILE"

upload_count=0
skip_count=0
error_count=0

# 递归遍历 KB 目录
find "$KB_DIR" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.pdf" -o -name "*.docx" -o -name "*.xlsx" \) | while read -r file_path; do
    # 计算相对路径
    rel_path="${file_path#$KB_DIR/}"
    filename=$(basename "$file_path")
    
    # 获取文件修改时间
    file_mtime=$(stat -c %Y "$file_path")
    
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] 处理: $rel_path${NC}" | tee -a "$LOG_FILE"
    
    # 获取或创建子文件夹token
    subdir=$(dirname "$rel_path")
    if [ "$subdir" = "." ]; then
        folder_token="$FEISHU_ROOT_FOLDER_TOKEN"
    else
        # 需要创建子文件夹并获取token
        # 这里调用 OpenClaw 工具
        folder_token=$(get_or_create_folder "$subdir" "$FEISHU_ROOT_FOLDER_TOKEN")
    fi
    
    # 检查文件是否已存在且未修改
    if needs_upload "$filename" "$file_mtime" "$folder_token"; then
        # 上传文件
        echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] 上传: $filename${NC}" | tee -a "$LOG_FILE"
        
        # 调用 OpenClaw 上传工具
        # openclaw tools feishu_drive_file action=upload file_path="$file_path" folder_token="$folder_token"
        
        # 记录上传
        record_upload "$filename" "$file_mtime" "$folder_token"
        ((upload_count++))
    else
        echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] 跳过(未变更): $filename${NC}" | tee -a "$LOG_FILE"
        ((skip_count++))
    fi
done

# 4. 清理飞书云盘中已删除的文件（可选）
echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] 步骤4: 检查飞书云盘中已删除的文件...${NC}" | tee -a "$LOG_FILE"

# 获取飞书文件列表并对比
# 删除 GitHub 中不存在的文件

echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ========== 同步完成 ==========${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}上传: $upload_count, 跳过: $skip_count, 错误: $error_count${NC}" | tee -a "$LOG_FILE"

exit 0

# 辅助函数（需要通过 OpenClaw 工具实现）
get_or_create_folder() {
    local folder_name="$1"
    local parent_token="$2"
    # 调用 feishu_drive_file 工具创建或获取文件夹
    # 返回 folder_token
    echo "$parent_token"  # 临时返回父文件夹token
}

needs_upload() {
    local filename="$1"
    local mtime="$2"
    local folder_token="$3"
    # 检查文件是否需要上传
    # 对比本地记录和飞书文件信息
    return 0  # 临时返回需要上传
}

record_upload() {
    local filename="$1"
    local mtime="$2"
    local folder_token="$3"
    # 记录上传信息到本地数据库
    local record_file="/tmp/github-kb-sync-records.txt"
    echo "$folder_token:$filename:$mtime" >> "$record_file"
}
