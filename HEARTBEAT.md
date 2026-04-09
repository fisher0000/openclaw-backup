# HEARTBEAT.md

> ⚠️ **注意**：此文件仅作为定时任务文档参考
> 实际定时任务配置在：`~/.openclaw/cron/jobs.json`

## 当前定时任务清单（6 个）

| 任务名称 | 执行时间 (北京时间) | 状态 |
|---------|------------------|------|
| daily-core-backup | 每日 17:00 | ✅ 启用 |
| weekly-workspace-backup | 每周五 17:00 | ✅ 启用 |
| 技术部群消息汇总 | 每日 15:30 | ✅ 启用 |
| 研发小群消息汇总 | 每日 15:40 | ✅ 启用 |
| 日报自动生成 | 每日 16:00 | ✅ 启用 |
| github-kb-sync | 工作日 8:00 | ✅ 启用（仅本地备份） |

## 任务详情

### 1. daily-core-backup
- **描述**：每日 17:00 执行 backup-daily.sh 脚本
- **动作**：备份核心文件到 GitHub

### 2. weekly-workspace-backup
- **描述**：每周五 17:00 执行 backup-weekly.sh 脚本
- **动作**：备份整个 workspace 到 GitHub

### 3. 技术部群消息汇总
- **描述**：每日 15:30 汇总技术部群消息
- **群 ID**：oc_2df0cdf639f1385cbacfd200789042bc
- **发送方式**：私聊给用户

### 4. 研发小群消息汇总
- **描述**：每日 15:40 汇总研发小群消息
- **群 ID**：oc_c463887844674a38fb581b954f5ee35b
- **发送方式**：私聊给用户

### 5. 日报自动生成
- **描述**：每日 16:00 自动生成个人日报
- **条件**：非节假日执行
- **脚本**：`bash ~/.openclaw/scripts/daily-report.sh`

### 6. github-kb-sync（GitHub→本地备份同步）
- **描述**：每个工作日 8:00 自动同步 GitHub KB 到本地备份
- **源**：https://github.com/fisher0000/obsidian/tree/main/KB
- **目标**：`/home/node/.openclaw/workspace/KB-backup/`
- **执行流程**：
  1. 从 GitHub 拉取最新文件到本地备份
  2. 检查本地文件夹与 GitHub 是否一致
  3. 如果一致，汇报并结束
  4. 如果不一致，更新本地备份后汇报
- **特性**：
  - 仅本地备份，不自动上传飞书云盘
  - 增量同步（只下载变更文件）
  - 本地永久备份

---

## 如需修改

请编辑 `~/.openclaw/cron/jobs.json`

## 历史记录

- 2026-04-09：github-kb-sync 任务重新配置为仅本地备份模式
- 2026-04-08：更新"技术部小群消息汇总"为"研发小群消息汇总"，明确群 ID
