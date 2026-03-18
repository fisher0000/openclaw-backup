# OpenClaw Workspace Backup Repository

## 目录结构

```
.
├── current/          # 当前最新备份（镜像工作区）
├── daily/            # 每日备份归档
│   ├── 2026-03-11/
│   ├── 2026-03-12/
│   └── ...
├── weekly/           # 每周备份归档
│   ├── 2026-week10/
│   └── ...
└── archives/         # 月度/年度归档
```

## 备份策略

- **Current**: 实时同步，始终是最新状态
- **Daily**: 每天17:00自动备份，保留30天
- **Weekly**: 每周日备份，保留12周
- **Archive**: 每月1日归档，长期保留

## 恢复方法

```bash
# 恢复到特定日期
git checkout <commit-hash>

# 或者从daily文件夹复制
cp -r daily/2026-03-11/* ~/workspace/
```
