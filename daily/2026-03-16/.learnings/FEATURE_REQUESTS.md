# Feature Requests

记录用户请求的新功能和待实现的能力

---

## [FEAT-20250305-001] auto_scope_check

**Logged**: 2025-03-05T10:15:00+08:00
**Priority**: medium
**Status**: pending
**Area**: config

### Requested Capability
调用飞书API前自动检查权限

### User Context
用户希望避免因权限不足导致的失败，提升体验

### Complexity Estimate
medium

### Suggested Implementation
1. 封装飞书API调用函数
2. 调用前执行 `feishu_app_scopes` 检查
3. 权限不足时给出清晰提示和解决方案

### Metadata
- Frequency: first_time
- Related Features: feishu_upload_file.py

---

## 记录模板

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: ISO-8601 timestamp
**Priority**: high/medium/low
**Status**: pending
**Area**: frontend/backend/infra/tests/docs/config

### Requested Capability
用户想要的功能描述

### User Context
为什么需要这个功能，解决什么问题

### Complexity Estimate
simple/medium/complex

### Suggested Implementation
可能的实现思路，参考什么

### Metadata
- Frequency: first_time/recurring
- Related Features: 相关功能名

---
```

## 实现后更新

当功能实现后：

```markdown
### Implementation
- **Completed**: 2025-03-05T14:00:00+08:00
- **Implementation**: 描述实现方式
- **Files**: 相关文件路径
```

并将 Status 改为 `resolved`
