---
name: wechat-moments-preparer
description: |
  朋友圈数据准备引擎。读取 raw/ 目录最新 JSON，增量去重，并发 LLM 提取四维度（events/traits/post_type/signals），
  写入 logs/YYYY-MM-DD.jsonl 和 profiles/，供分析报告使用。
  触发词：朋友圈数据准备、准备朋友圈数据、朋友圈提取、moments prepare。
version: 1.0.0
---

# 朋友圈数据准备引擎

从 wechat-moments-loader 导出的原始数据中提取帖子，增量去重，并发 LLM 分析后写入 log 和用户时间线。

## 数据目录结构

**项目根目录：** `~/.openclaw/projects/moments-analysis/`
```
moments-analysis/
├── raw/                    ← loader 产出（原始数据）
│   └── YYYYMMDD_HHMMSS.json
├── logs/                   ← 分析日志（原子化，JSONL，只增不改）
│   └── YYYY-MM-DD.jsonl
├── profiles/               ← 用户时间线（每用户一个 JSONL）
│   ├── wxid_xxx.jsonl
│   └── whitelist.json      ← 白名单（人工维护）
├── state/                  ← 临时文件
│   └── new_posts.json
└── checkpoint.json         ← 已处理帖子 ID 去重
```

---

## 工具规范

- 所有文件操作使用 Python 脚本，禁止 PowerShell 处理中文路径
- JSON 文件读取必须指定 `encoding='utf-8'`
- 执行脚本使用完整路径

---

## 执行流程

### Phase 0: 数据准备

```bash
python C:\Users\44452\.openclaw\skills\wechat-moments-analyzer\scripts\prepare_data.py
```

读取 `raw/` 最新 JSON，比对 checkpoint，输出新帖子到 `state/new_posts.json`。

- 输出 `OK: N new posts...` → 继续 Phase 1
- 输出 `NO_DATA` → 触发 wechat-moments-loader 拉取新数据后重试
- 输出 `NO_RAW_DIR` / `READ_ERROR` → 报错退出

读取白名单：`profiles/whitelist.json`（JSON 数组，wxid 列表）。白名单用户发帖时 image_trigger 强制为 1。

### Phase 1: 并发分析（后台运行）

```bash
python C:\Users\44452\.openclaw\skills\wechat-moments-analyzer\scripts\run_batch.py \
  --posts-file ~/.openclaw/projects/moments-analysis/state/new_posts.json \
  --batch-size 10 \
  --output-file ~/.openclaw/projects/moments-analysis/state/analyzed.json \
  --max-workers 10 \
  --max-concurrent-batches 10
```

脚本自动完成：
1. 并发提取 4 维度（events / traits / post_type / signals）
2. 写入 `logs/YYYY-MM-DD.jsonl`
3. 更新 `profiles/wxid_xxx.jsonl`
4. 更新 `checkpoint.json`

**重要：** 此脚本耗时较长（100条约6分钟，300条约18分钟），必须后台运行，不等待结果：

```bash
nohup python C:\Users\44452\.openclaw\skills\wechat-moments-analyzer\scripts\run_batch.py \
  --posts-file ... --output-file ... > ~/.openclaw/projects/moments-analysis/state/run.log 2>&1 &
echo $! > ~/.openclaw/projects/moments-analysis/state/run.pid
```

立即回复用户"数据准备已启动，约 N 分钟后完成"。

---

## 断点续跑

脚本支持断点续跑，中断后重新运行自动从 checkpoint 恢复。

---

## Usage Logging

```bash
node ~/.openclaw/skills/_shared/log-usage.mjs "wechat-moments-preparer" "<触发原因>" "<结果>"
```
