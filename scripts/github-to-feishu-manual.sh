#!/bin/bash
# GitHub → 飞书云盘 同步 - 手动触发脚本
# 使用方法: ./github-to-feishu-manual.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/github-to-feishu-sync.py"

echo "========================================"
echo "GitHub → 飞书云盘 手动同步"
echo "========================================"
echo ""
echo "源: https://github.com/fisher0000/obsidian/tree/main/KB"
echo "目标: 飞书云盘知识库"
echo ""

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: 脚本不存在: $PYTHON_SCRIPT"
    exit 1
fi

echo "开始同步..."
echo ""

/usr/bin/python3 "$PYTHON_SCRIPT"

EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ 同步成功完成"
else
    echo "✗ 同步失败 (退出码: $EXIT_CODE)"
fi

exit $EXIT_CODE
