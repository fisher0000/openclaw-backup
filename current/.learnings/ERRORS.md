# Error Log

记录所有命令失败、API异常和意外行为

---

## [ERR-20250305-001] feishu_group_permission

**Logged**: 2025-03-05T10:15:00+08:00
**Priority**: high
**Status**: pending
**Area**: config

### Summary
飞书API功能在群聊和私聊中权限表现不一致

### Error
群聊中某些功能受限，私聊正常

### Context
- 尝试在群聊使用某些API功能
- 私聊时工作正常
- 群聊中报错或无响应

### Suggested Fix
1. 调用API前检查当前上下文（群聊 vs 私聊）
2. 对群聊限制的功能给出明确提示
3. 在 AGENTS.md 中添加飞书权限检查清单

### Metadata
- Reproducible: yes
- Related Files: SOUL.md, AGENTS.md
- See Also: 

---

## 记录模板

```markdown
## [ERR-YYYYMMDD-XXX] command_or_api_name

**Logged**: ISO-8601 timestamp
**Priority**: high/medium/low
**Status**: pending
**Area**: frontend/backend/infra/tests/docs/config

### Summary
简要描述失败内容

### Error
```
实际错误信息或输出
```

### Context
- 尝试执行的命令/操作
- 输入参数
- 环境信息

### Suggested Fix
如果可识别，如何解决这个问题

### Metadata
- Reproducible: yes/no/unknown
- Related Files: 
- See Also: 相关条目ID

---
```

## 常见错误类型

| 错误类型 | 示例 | 优先级 |
|----------|------|--------|
| API权限不足 | `scope missing: im:chat:readonly` | high |
| 命令返回非零 | `exit code 1` | medium |
| 超时 | `Request Timeout` | medium |
| 连接失败 | `Connection refused` | high |
| 意外的输出 | 输出格式与预期不符 | low |

## 解决后更新

当错误修复后，更新条目：

```markdown
### Resolution
- **Resolved**: 2025-03-05T12:00:00+08:00
- **Commit/PR**: abc123 或 #42
- **Notes**: 修复描述
```

并将 Status 改为 `resolved`
