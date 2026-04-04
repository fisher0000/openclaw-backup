#!/bin/bash
# GitHub → 飞书云盘 定时同步任务
# 每个工作日 8:00 执行
# 
# 配置方法:
#   crontab -e
#   0 8 * * 1-5 /home/node/.openclaw/workspace/scripts/github-to-feishu-cron.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/github-to-feishu-sync.py"
LOG_DIR="/home/node/.openclaw/workspace/logs"
LOG_FILE="$LOG_DIR/github-kb-sync-cron-$(date +%Y%m%d).log"
LOCK_FILE="/tmp/github-kb-sync-cron.lock"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 检查锁文件（防止重复运行）
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "[$(date)] 同步任务已在运行 (PID: $PID)，跳过" >> "$LOG_FILE"
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"

# 清理函数
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

echo "========================================" >> "$LOG_FILE"
echo "[$(date)] GitHub → 飞书云盘 定时同步开始" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 检查 Python 脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "[$(date)] 错误: 脚本不存在: $PYTHON_SCRIPT" >> "$LOG_FILE"
    exit 1
fi

# 运行同步脚本
/usr/bin/python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "========================================" >> "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date)] 同步成功完成" >> "$LOG_FILE"
else
    echo "[$(date)] 同步失败 (退出码: $EXIT_CODE)" >> "$LOG_FILE"
fi
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $EXIT_CODE
