#!/bin/bash
# OpenClaw Workspace Backup Script

WORKSPACE="/home/node/.openclaw/workspace"
BACKUP_DIR="/tmp/backup-repo"
DATE=$(date +%Y-%m-%d)
WEEK=$(date +%Y-week%V)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== OpenClaw Backup Script ===${NC}"
echo "Date: $DATE"
echo "Week: $WEEK"

# 1. 更新current目录
echo -e "\n${YELLOW}[1/4] Updating current/ directory...${NC}"
rm -rf "$BACKUP_DIR/current/*"
cp -r "$WORKSPACE"/* "$BACKUP_DIR/current/" 2>/dev/null
echo -e "${GREEN}✓ Current directory updated${NC}"

# 2. 创建每日备份
echo -e "\n${YELLOW}[2/4] Creating daily backup...${NC}"
mkdir -p "$BACKUP_DIR/daily/$DATE"
cp -r "$WORKSPACE"/* "$BACKUP_DIR/daily/$DATE/" 2>/dev/null
echo -e "${GREEN}✓ Daily backup created: daily/$DATE/${NC}"

# 3. 如果是周日，创建每周备份
if [ "$DAY_OF_WEEK" -eq 7 ]; then
    echo -e "\n${YELLOW}[3/4] Creating weekly backup...${NC}"
    mkdir -p "$BACKUP_DIR/weekly/$WEEK"
    cp -r "$WORKSPACE"/* "$BACKUP_DIR/weekly/$WEEK/" 2>/dev/null
    echo -e "${GREEN}✓ Weekly backup created: weekly/$WEEK/${NC}"
else
    echo -e "\n${YELLOW}[3/4] Skipping weekly backup (not Sunday)${NC}"
fi

# 4. 清理旧备份（保留30天）
echo -e "\n${YELLOW}[4/4] Cleaning old backups...${NC}"
find "$BACKUP_DIR/daily" -type d -mtime +30 -exec rm -rf {} + 2>/dev/null
find "$BACKUP_DIR/weekly" -type d -mtime +84 -exec rm -rf {} + 2>/dev/null
echo -e "${GREEN}✓ Old backups cleaned${NC}"

# Git提交
echo -e "\n${YELLOW}[Git] Committing changes...${NC}"
cd "$BACKUP_DIR"
git add -A
git commit -m "Backup: $DATE - Daily backup" || echo "No changes to commit"
git push origin main
echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"

echo -e "\n${GREEN}=== Backup Complete ===${NC}"
