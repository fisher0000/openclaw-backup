#!/bin/bash
# 法规知识库定时同步脚本
# 每6小时执行一次完整同步

SYNC_SCRIPT="/home/node/.openclaw/workspace/scripts/sync-knowledge-base.sh"
LOG_FILE="/home/node/.openclaw/workspace/logs/knowledge-cron.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date)] 定时任务: 开始同步法规知识库..." | tee -a "$LOG_FILE"

# 执行同步
"$SYNC_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

echo "[$(date)] 定时任务: 同步完成" | tee -a "$LOG_FILE"
