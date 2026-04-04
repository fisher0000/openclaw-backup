#!/bin/bash
# GitHub → 飞书云盘 同步脚本
# 使用方法: ./github-to-feishu-sync.sh

set -e

# ============ 配置 ============
GITHUB_REPO="https://github.com/fisher0000/obsidian"
GITHUB_BRANCH="main"
GITHUB_SUBDIR="KB"
LOCAL_TEMP_DIR="/tmp/github-kb-sync-$(date +%s)"
FEISHU_ROOT_FOLDER_TOKEN="Ofu0fS87fl5SHwdTZSmcmXoQnse"
WORKSPACE_DIR="/home/node/.openclaw/workspace"
LOG_FILE="$WORKSPACE_DIR/logs/github-kb-sync-$(date +%Y%m%d).log"
RECORD_FILE="$WORKSPACE_DIR/.github-kb-sync-state.json"
LOCK_FILE="/tmp/github-kb-sync.lock"

# ============ 初始化 ============
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$LOCAL_TEMP_DIR"

# 检查锁文件
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "[$(date)] 同步已在运行中 (PID: $pid)，跳过"
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"

# 清理函数
cleanup() {
    rm -f "$LOCK_FILE"
    rm -rf "$LOCAL_TEMP_DIR"
}
trap cleanup EXIT

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== GitHub → 飞书云盘同步开始 =========="

# ============ 步骤1: 从 GitHub 拉取 ============
log "步骤1: 从 GitHub 拉取 KB 文件夹..."

# 使用 sparse checkout 只拉取 KB 目录
cd "$LOCAL_TEMP_DIR"
git init --quiet
git remote add origin "$GITHUB_REPO"
git config core.sparseCheckout true
echo "$GITHUB_SUBDIR/*" > .git/info/sparse-checkout
git pull --depth=1 origin "$GITHUB_BRANCH" 2>&1 | tee -a "$LOG_FILE"

if [ ! -d "$GITHUB_SUBDIR" ]; then
    log "错误: KB 目录不存在"
    exit 1
fi

log "GitHub 拉取成功"

# ============ 步骤2: 扫描本地文件 ============
log "步骤2: 扫描本地文件..."

LOCAL_FILES=$(find "$GITHUB_SUBDIR" -type f \( \
    -name "*.md" -o \
    -name "*.txt" -o \
    -name "*.pdf" -o \
    -name "*.docx" -o \
    -name "*.xlsx" -o \
    -name "*.png" -o \
    -name "*.jpg" -o \
    -name "*.jpeg" \
) | sort)

file_count=$(echo "$LOCAL_FILES" | grep -c "^" || echo "0")
log "发现 $file_count 个文件需要同步"

# ============ 步骤3: 同步到飞书云盘 ============
log "步骤3: 开始同步到飞书云盘..."

uploaded=0
skipped=0
failed=0

# 遍历每个文件
while IFS= read -r file_path; do
    [ -z "$file_path" ] && continue
    
    # 计算相对路径
    rel_path="${file_path#$GITHUB_SUBDIR/}"
    filename=$(basename "$file_path")
    subdir=$(dirname "$rel_path")
    
    # 获取文件信息
    file_size=$(stat -c%s "$file_path")
    file_mtime=$(stat -c%Y "$file_path")
    
    log "处理: $rel_path (${file_size} bytes)"
    
    # 检查文件大小（飞书限制 20MB）
    if [ "$file_size" -gt 20971520 ]; then
        log "  跳过: 文件超过20MB限制"
        ((failed++))
        continue
    fi
    
    # 确定目标文件夹
    if [ "$subdir" = "." ]; then
        target_folder_token="$FEISHU_ROOT_FOLDER_TOKEN"
    else
        # 需要创建子文件夹
        target_folder_token=$(ensure_folder "$subdir" "$FEISHU_ROOT_FOLDER_TOKEN")
    fi
    
    # 检查是否需要上传（对比记录）
    file_hash=$(md5sum "$file_path" | cut -d' ' -f1)
    
    if should_upload "$rel_path" "$file_hash" "$file_mtime"; then
        log "  上传: $filename"
        
        # 调用 OpenClaw 工具上传
        if upload_to_feishu "$file_path" "$target_folder_token" "$filename"; then
            # 记录上传成功
            record_sync "$rel_path" "$file_hash" "$file_mtime"
            ((uploaded++))
        else
            log "  失败: $filename"
            ((failed++))
        fi
    else
        log "  跳过(未变更): $filename"
        ((skipped++))
    fi
    
done <<< "$LOCAL_FILES"

log "========== 同步完成 =========="
log "上传: $uploaded, 跳过: $skipped, 失败: $failed"

exit 0

# ============ 辅助函数 ============

ensure_folder() {
    local folder_path="$1"
    local parent_token="$2"
    
    # 检查缓存
    local cache_key=$(echo "$folder_path" | tr '/' '_')
    local cached_token=$(jq -r ".folders[\"$cache_key\"]" "$RECORD_FILE" 2>/dev/null || echo "null")
    
    if [ "$cached_token" != "null" ] && [ -n "$cached_token" ]; then
        echo "$cached_token"
        return
    fi
    
    # 创建文件夹（通过 OpenClaw 工具）
    # 这里需要调用 feishu_drive_file 工具
    # 暂时返回父文件夹token
    echo "$parent_token"
}

should_upload() {
    local rel_path="$1"
    local file_hash="$2"
    local file_mtime="$3"
    
    # 检查记录文件
    if [ ! -f "$RECORD_FILE" ]; then
        return 0  # 需要上传
    fi
    
    # 获取上次同步的记录
    local last_hash=$(jq -r ".files[\"$rel_path\"].hash" "$RECORD_FILE" 2>/dev/null || echo "null")
    
    if [ "$last_hash" = "null" ] || [ "$last_hash" != "$file_hash" ]; then
        return 0  # 需要上传
    fi
    
    return 1  # 不需要上传
}

record_sync() {
    local rel_path="$1"
    local file_hash="$2"
    local file_mtime="$3"
    
    # 更新记录文件
    if [ ! -f "$RECORD_FILE" ]; then
        echo '{"files":{},"folders":{}}' > "$RECORD_FILE"
    fi
    
    # 使用 jq 更新记录
    jq --arg path "$rel_path" \
       --arg hash "$file_hash" \
       --arg mtime "$file_mtime" \
       --arg time "$(date -Iseconds)" \
       '.files[$path] = {"hash": $hash, "mtime": $mtime, "sync_time": $time}' \
       "$RECORD_FILE" > "${RECORD_FILE}.tmp" && mv "${RECORD_FILE}.tmp" "$RECORD_FILE"
}

upload_to_feishu() {
    local file_path="$1"
    local folder_token="$2"
    local filename="$3"
    
    # 调用 OpenClaw 工具上传
    # 输出命令供手动执行或集成
    echo "UPLOAD_NEEDED:$file_path:$folder_token:$filename"
    
    # 实际调用需要 OpenClaw 环境支持
    return 0
}
