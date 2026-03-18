# Lark 群管理技能（升级版）

飞书群管理工具，支持群搜索、群详情查看、消息发送、批量操作等功能。

## 功能特性

### ✅ 已支持功能

| 功能 | 命令 | 说明 |
|------|------|------|
| **群搜索** | `search` | 按名称关键词搜索群聊 |
| **群列表** | `list` | 获取Bot所在的所有群 |
| **群详情** | `info` | 查看群的详细信息（名称、描述、群主、成员数等） |
| **发送消息** | `send` | 给指定群发送消息 |
| **批量群发** | `broadcast` | 按关键词批量给多个群发消息 |
| **权限检查** | `check` | 检查Bot是否在指定群中 |

---

## 使用方法

### 1. 搜索群聊

按名称关键词搜索群：

```bash
# 搜索包含"运维"的群
python3 scripts/lark_group_manager.py search "运维"

# 显示详细信息
python3 scripts/lark_group_manager.py search "运维" --verbose
```

输出示例：
```
找到 1 个群:

序号 群名称         成员数   chat_id
-------------------------------------------
1    OpenClaw运维   0       oc_0a1d28a4189be0e8c881a4ca7f4f04d2
```

---

### 2. 获取群详情

查看群的详细信息：

```bash
python3 scripts/lark_group_manager.py info oc_0a1d28a4189be0e8c881a4ca7f4f04d2
```

输出示例：
```
群详情:
  名称: OpenClaw运维
  描述: 
  成员数: 0
  群主: ou_0ca7bc3d9082f8b2e436b8771a430569
  群模式: group
  群类型: private
  创建时间: 未知
```

---

### 3. 列出Bot所在的所有群

```bash
python3 scripts/lark_group_manager.py list

# 显示详细信息
python3 scripts/lark_group_manager.py list --verbose
```

---

### 4. 发送消息

给指定群发送消息：

```bash
python3 scripts/lark_group_manager.py send \
  "oc_0a1d28a4189be0e8c881a4ca7f4f04d2" \
  "这是一条测试消息"
```

---

### 5. 批量群发

按关键词批量给多个群发消息：

```bash
# 试运行模式（只预览，不实际发送）
python3 scripts/lark_group_manager.py broadcast "运维" "今晚维护通知" --dry-run

# 实际发送
python3 scripts/lark_group_manager.py broadcast "运维" "今晚维护通知"
```

---

### 6. 检查Bot是否在群里

```bash
python3 scripts/lark_group_manager.py check oc_0a1d28a4189be0e8c881a4ca7f4f04d2
```

---

## 依赖

- Python 3.7+
- requests

安装依赖：
```bash
pip3 install requests
```

---

## 配置

脚本中已内置应用凭证：
- `APP_ID`: cli_a90ebb6fe8f81bd2
- `APP_SECRET`: clSwYtz2CqvDfon3bKP2sh0wGBiV4nrT

如需修改，编辑脚本中的对应变量。

---

## 文件结构

```
lark-doc-search/
├── SKILL.md                           # 本文件
└── scripts/
    ├── lark_doc_search.py             # 飞书文档搜索（MCP方式）
    ├── lark_group_manager.py          # 群管理工具（REST API方式）⭐ 新增
    ├── send_to_group.py               # 发送消息示例
    └── summarize_chat.py              # 群消息汇总示例
```

---

## 使用建议

1. **日常运维**: 使用 `search` 快速找到目标群
2. **群管理**: 使用 `info` 查看群详情，了解群主和成员情况
3. **通知推送**: 使用 `broadcast` 批量发送运维通知
4. **权限确认**: 使用 `check` 确认Bot是否有权限操作某群

---

## 更新日志

### v2.0 (2026-02-26)
- ✨ 新增群搜索功能
- ✨ 新增群详情查看
- ✨ 新增批量群发功能
- ✨ 新增权限检查功能
- ✨ 优化命令行接口
- ✨ 支持Python类方式调用
