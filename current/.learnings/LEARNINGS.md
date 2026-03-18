# Learnings Log

记录所有学到的教训、用户纠正、知识更新和最佳实践

---

## [LRN-20250305-001] best_practice

**Logged**: 2025-03-05T10:15:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
创建 .learnings/ 目录结构启用自我改进机制

### Details
通过记录错误、教训和功能请求，实现：
1. 跨会话记忆保持
2. 重复问题检测
3. 知识晋升到核心配置文件

### Suggested Action
- 定期回顾 pending 条目
- 高优先级项升级到 AGENTS.md / SOUL.md / TOOLS.md

### Metadata
- Source: user_request
- Related Files: .learnings/ERRORS.md, .learnings/FEATURE_REQUESTS.md
- Tags: self-improvement, setup

---

## [LRN-20250305-002] best_practice

**Logged**: 2025-03-05T10:38:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
按虾总指示安装群里介绍的所有技能，已安装6个新技能

### Details
已安装技能列表:
1. feishu-lark (飞书综合增强)
2. feishu-doc (飞书云文档)
3. feishu-drive (飞书云盘)
4. pdf-to-markdown (PDF转Markdown)
5. docker-best-practices (Docker最佳实践)
6. github-cli (GitHub CLI增强)

安装失败(超时):
- steipete/clawdis@github (克隆超时)
- aj-geddes/useful-ai-prompts@markdown-documentation (克隆超时)

### Suggested Action
- 在 AGENTS.md 中维护已安装技能清单
- 虾总或小龙虾群里发新技能时，自动安装并更新列表

### Metadata
- Source: user_request
- Related Files: AGENTS.md
- Tags: skills, feishu, installation

---

## [LRN-20250305-003] best_practice

**Logged**: 2025-03-05T17:30:00+08:00
**Priority**: critical
**Status**: resolved
**Area**: config

### Summary
从今日群聊学习项目管理最佳实践：子囊霉素研发转中试项目案例

### Details
**关键经验（来自 ou_1b7aaa9ea284327f7089885e4a9e13ba）：**
1. 使用 OpenClaw 制定项目管理计划
2. 自动设定分工和权限
3. 形成飞书多维表格（Bitable）跟踪工作
4. 各小组持续完善表格内容
5. OpenClaw 持续追踪并提醒

**可复用的工作流：**
```
项目启动 → 制定计划 → 自动分工/权限 → 创建Bitable → 持续追踪 → 主动提醒
```

### Suggested Action
- [x] 学习该模式并记录
- [ ] 在项目启动时主动提供此工作流
- [ ] 检查 Bitable API 能力以支持追踪功能
- [ ] 设置提醒/心跳检查机制

### Metadata
- Source: group_chat
- Related Files: AGENTS.md, feishu-bitable tools
- Tags: project-management, bitable, workflow, automation

---

## [LRN-20250305-004] knowledge_gap

**Logged**: 2025-03-05T17:30:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
学习私聊 vs 群聊的消息发送策略

### Details
- 群聊中：公开讨论、@提醒、共享信息
- 私聊时：敏感信息、个人任务、一对一沟通
- 需要根据内容敏感度选择渠道

### Suggested Action
- 涉及个人信息时主动询问"需要私发吗？"
- 在群聊中避免暴露敏感数据

### Metadata
- Source: group_chat
- Related Files: SOUL.md
- Tags: communication, privacy, feishu

---

## [LRN-20250305-005] best_practice

**Logged**: 2025-03-05T22:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
安装并学习 OCR 文字识别技能：paddleocr-text-recognition + mistral-ocr

### Details
**已安装技能：**
1. `paddleocr-text-recognition` (217 installs) - 中文识别效果佳
2. `mistral-ocr` (86 installs) - PDF处理能力强，直接转Markdown

**使用场景：**
- 提取图片/截图中的文字
- PDF 文档转 Markdown
- 发票/票据/表格识别
- 扫描件数字化

**配置要求：**
- PaddleOCR: 需配置 PADDLEOCR_OCR_API_URL 和 PADDLEOCR_ACCESS_TOKEN
- Mistral OCR: 需 MISTRAL_API_KEY（$2/1000页）

### Suggested Action
- [x] 安装技能
- [x] 学习使用方法
- [ ] 获取 API 密钥后测试
- [ ] 结合实际业务场景应用

### Metadata
- Source: user_request
- Related Files: AGENTS.md
- Tags: ocr, paddleocr, mistral, image-processing

---

## 记录模板

### Correction（用户纠正）

```markdown
## [LRN-YYYYMMDD-XXX] correction

**Logged**: ISO-8601 timestamp
**Priority**: high/medium/low
**Status**: pending
**Area**: frontend/backend/infra/tests/docs/config

### Summary
一句话描述被纠正的内容

### Details
- 之前怎么做（错误）
- 用户纠正了什么
- 正确做法是什么

### Suggested Action
如何避免再犯，具体改进步骤

### Metadata
- Source: user_feedback
- Related Files: 
- Tags: 

---
```

### Best Practice（最佳实践）

```markdown
## [LRN-YYYYMMDD-XXX] best_practice

**Logged**: ISO-8601 timestamp
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
发现的高效方法或技巧

### Details
- 场景描述
- 传统做法的问题
- 改进后的做法
- 为什么更好

### Suggested Action
是否推广到 AGENTS.md 或文档

### Metadata
- Source: discovery
- Related Files: 
- Tags: 

---
```

### Knowledge Gap（知识盲区）

```markdown
## [LRN-YYYYMMDD-XXX] knowledge_gap

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
之前不知道的关键信息

### Details
- 之前的理解
- 正确的事实
- 信息来源

### Suggested Action
更新知识库或文档

### Metadata
- Source: external_reference
- Related Files: 
- Tags: 

---
```

## 状态说明

| 状态 | 含义 |
|------|------|
| pending | 待处理 |
| in_progress | 正在处理 |
| resolved | 已解决 |
| promoted | 已晋升到核心配置 |
| wont_fix | 决定不处理 |

## 优先级说明

| 优先级 | 含义 |
|--------|------|
| critical | 阻塞核心功能、安全风险 |
| high | 显著影响、高频发生 |
| medium | 中等影响、有 workaround |
| low | 轻微不便、边界情况 |
