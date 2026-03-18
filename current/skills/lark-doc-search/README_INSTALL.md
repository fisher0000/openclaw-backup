# Lark 群管理技能 - 安装说明

## 📦 版本信息
- **版本**: v2.0
- **作者**: OpenClaw
- **更新日期**: 2026-02-26
- **大小**: 21KB

---

## 📂 文件内容

```
lark-doc-search/
├── SKILL.md                      # 技能说明文档
├── README_INSTALL.md             # 本安装说明
└── scripts/
    ├── lark_group_manager.py     # 群管理工具（主程序）⭐
    ├── lark_doc_search.py        # 飞书文档搜索
    ├── send_to_group.py          # 发送消息示例
    ├── summarize_chat.py         # 消息汇总示例
    └── ...                       # 其他辅助脚本
```

---

## 🚀 安装步骤

### 方式1：解压到技能目录

```bash
# 1. 解压到 OpenClaw 技能目录
unzip lark-doc-search-v2.0.zip -d ~/.openclaw/workspace/skills/

# 2. 验证安装
ls ~/.openclaw/workspace/skills/lark-doc-search/
```

### 方式2：使用 OpenClaw 命令安装

```bash
# 如果 OpenClaw 支持技能安装命令
openclaw skills install lark-doc-search-v2.0.zip
```

---

## ⚙️ 配置说明

### 1. 修改飞书应用凭证

编辑 `scripts/lark_group_manager.py`，修改以下变量：

```python
APP_ID = "cli_a90ebb6fe8f81bd2"          # 你的飞书应用ID
APP_SECRET = "clSwYtz2CqvDfon3bKP2sh0wGBiV4nrT"  # 你的飞书应用Secret
```

### 2. 所需权限

确保飞书应用已开启以下权限：

- ✅ `im:chat:readonly` - 获取群组信息
- ✅ `im:chat:read` - 查看群信息
- ✅ `im:message:send` - 发送消息
- ✅ `im:message:send_as_bot` - 以应用身份发消息
- ✅ `im:chat.members:read` - 查看群成员

---

## 🎯 快速开始

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/lark-doc-search/scripts

# 1. 搜索群
python3 lark_group_manager.py search "运维"

# 2. 查看群详情
python3 lark_group_manager.py info <chat_id>

# 3. 发送消息
python3 lark_group_manager.py send <chat_id> "Hello World"

# 4. 批量群发
python3 lark_group_manager.py broadcast "运维" "通知内容" --dry-run
```

---

## 📖 完整文档

详见 `SKILL.md` 文件。

---

## 🔧 依赖安装

```bash
pip3 install requests
```

---

## 🐛 常见问题

### Q1: 提示权限不足？
A: 检查飞书应用是否已开启相关权限，并**发布应用版本**使权限生效。

### Q2: 搜索不到群？
A: 确保Bot在目标群内，或该群是公开群。

### Q3: 发送消息失败？
A: 检查Bot是否在群里，以及是否有发言权限。

---

## 📮 反馈与支持

如有问题，请联系技能作者或提交 Issue。

---

**Enjoy! 🎉**
