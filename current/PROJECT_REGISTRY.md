# 自主项目管理 - PM Delegation Pattern
# 用于龙虾业务情报管理

## 使用方式

### 1. 启动项目
```
用户: "启动AI情报日报项目"

主代理:
1. 读取 STATE.yaml
2. 检查项目是否存在
3. 若不存在 → sessions_spawn(label="pm-ai-intel", task="...")
4. 若存在 → sessions_send(label="pm-ai-intel", message="[任务]")
```

### 2. PM 子代理工作流程

**pm-ai-intel 子代理启动后：**
1. 读取 ~/.openclaw/workspace/STATE.yaml
2. 查找分配给它的任务
3. 更新任务状态为 in_progress
4. 执行任务（搜索、分析、生成报告）
5. 更新 STATE.yaml 状态为 done
6. 向主代理报告完成

### 3. 并行执行示例

**场景：同时进行AI情报和呼吸药情报**
```
主代理同时 spawn:
- sessions_spawn(label="pm-ai-intel", task="搜集AI科技情报")
- sessions_spawn(label="pm-pharma", task="搜集呼吸药情报")

两个子代理并行工作，各自更新 STATE.yaml
```

## 主代理规则

- 0-2 个工具调用（只 spawn/send）
- 不直接执行任务
- 只做策略和协调

## PM 命名规范

```
pm-{项目}-{范围}

示例:
- pm-ai-intel        (AI情报主PM)
- pm-pharma          (呼吸药情报PM)
- pm-invest          (投资跟踪PM)
```

## STATE.yaml 更新规范

子代理完成任务后必须更新：
```yaml
tasks:
  - id: task-001
    status: done          # pending → in_progress → done/blocked
    completed: 2026-03-05T15:30:00Z
    output: "报告链接或文件路径"
    notes: "完成说明"
```

## 测试命令

启动AI情报PM:
```
sessions_spawn(
  label="pm-ai-intel",
  task="读取 ~/.openclaw/workspace/STATE.yaml，执行ID为ai-daily-2026-03-05的任务，搜集今日AI科技情报并生成报告",
  mode="session"
)
```
