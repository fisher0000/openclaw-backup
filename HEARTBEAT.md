# HEARTBEAT.md

> ⚠️ **注意**：此文件仅作为定时任务文档参考
> 实际定时任务配置在：`~/.openclaw/cron/jobs.json`

## 当前定时任务清单（6个）

| 任务名称 | 执行时间(北京时间) | 状态 |
|---------|------------------|------|
| daily-core-backup | 每日 17:00 | ✅ 启用 |
| weekly-workspace-backup | 每周五 17:00 | ✅ 启用 |
| 技术部群消息汇总 | 每日 15:30 | ✅ 启用 |
| 研发小群消息汇总 | 每日 15:40 | ✅ 启用 |
| 日报自动生成 | 每日 16:00 | ✅ 启用 |
| github-kb-sync | 工作日 8:00 | ✅ 启用 |

## 任务详情

### 1. daily-core-backup
- **描述**：每日 17:00 执行 backup-daily.sh 脚本
- **动作**：备份核心文件到GitHub

### 2. weekly-workspace-backup
- **描述**：每周五 17:00 执行 backup-weekly.sh 脚本
- **动作**：备份整个workspace到GitHub

### 3. 技术部群消息汇总
- **描述**：每日 15:30 汇总技术部群消息
- **群ID**：oc_2df0cdf639f1385cbacfd200789042bc
- **发送方式**：私聊给用户

### 4. 研发小群消息汇总
- **描述**：每日 15:40 汇总研发小群消息
- **群ID**：oc_c463887844674a38fb581b954f5ee35b
- **发送方式**：私聊给用户

### 5. 日报自动生成
- **描述**：每日 16:00 自动生成个人日报
- **条件**：非节假日执行
- **脚本**：`bash ~/.openclaw/scripts/daily-report.sh`

### 6. github-kb-sync (GitHub→飞书知识库同步)
- **描述**：每个工作日 8:00 自动同步 GitHub KB 到飞书云盘
- **源**：https://github.com/fisher0000/obsidian/tree/main/KB
- **目标**：飞书云盘知识库 (Ofu0fS87fl5SHwdTZSmcmXoQnse)
- **本地备份**：`/home/node/.openclaw/workspace/KB-backup/`
- **脚本**：`python3 /home/node/.openclaw/workspace/scripts/github-to-feishu-sync-auto.py`
- **定时任务消息**："执行GitHub知识库同步"
- **执行流程**：
  1. 从 GitHub 拉取最新文件到本地备份
  2. 检测变更文件
  3. 生成批量上传脚本
  4. 执行批量上传到飞书云盘
- **特性**：
  - 增量同步（只下载/上传变更文件）
  - 本地永久备份
  - 支持 .md, .txt, .pdf, .docx, .xlsx, 图片等
  - 自动跳过超过20MB的文件

## 如需修改

请编辑 `~/.openclaw/cron/jobs.json`

## 历史记录

- 2026-04-04：新增 GitHub→飞书云盘知识库同步任务（工作日 8:00）
- 2026-04-03：更新"技术部小群消息汇总"为"研发小群消息汇总"，明确群ID
