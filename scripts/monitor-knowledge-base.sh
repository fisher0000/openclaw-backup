#!/bin/bash
# 法规知识库实时监控脚本
# 使用 inotifywait 监控文件变更

LOCAL_BASE="/home/node/法规知识库"
SYNC_SCRIPT="/home/node/.openclaw/workspace/scripts/sync-knowledge-base.sh"
LOG_FILE="/home/node/.openclaw/workspace/logs/knowledge-monitor.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date)] 启动法规知识库监控..." | tee -a "$LOG_FILE"
echo "监控目录: $LOCAL_BASE" | tee -a "$LOG_FILE"

# 检查 inotifywait 是否安装
if ! command -v inotifywait &> /dev/null; then
    echo "[$(date)] 错误: inotifywait 未安装" | tee -a "$LOG_FILE"
    echo "请安装 inotify-tools: sudo apt-get install inotify-tools" | tee -a "$LOG_FILE"
    exit 1
fi

# 监控所有子目录的文件创建和修改事件
inotifywait -m -r "$LOCAL_BASE" \
    -e create -e modify -e moved_to \
    --format '%T|%w|%f|%e' \
    --timefmt '%Y-%m-%d %H:%M:%S' |
while read timestamp dir filename event; do
    # 只处理 .md 文件
    if [[ "$filename" == *.md ]]; then
        echo "[$(date)] 检测到变更: $dir$filename ($event)" | tee -a "$LOG_FILE"
        
        # 延迟5秒执行同步（避免频繁操作）
        sleep 5
        
        # 执行同步脚本
        "$SYNC_SCRIPT"
    fi
done
