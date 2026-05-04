$outputDir = 'C:\Users\44452\.openclaw\chat-logs\summaries'
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force
}

$date = '2026-05-01'
$agent = 'main'
$summary = @"
# 会话摘要 · main · 2026-05-01

**原始文件**：2026-05-01_*.jsonl（合并 0 个真实用户会话）
**摘要生成时间**：2026-05-02 08:53:00
**消息总数**：0 条
**时间跨度**：无用户会话

---

## 第一部分：任务视角（供日报使用）

**【新增】用户投入量（顶置）**：
- 用户消息：0 条，0 字
- 主要投入：无
- 时间跨度：无用户会话

**【新增】主线概述**：
无用户会话记录。main agent 在 2026-05-01 仅执行了定时任务（技能雷达扫描），无真实用户对话。

### 1.1 核心交付（主线）⭐
无

### 1.2 其他交付
无

### 1.3 进行中任务
无

### 1.4 断线头
无

### 1.5 新增待办
无

**【新增】关联前序**：
无

---

## 第二部分：反思视角（供日记使用）

### 2.1 主要业务进展
无

### 2.2 重要决策
无

### 2.3 方法论与反思
无

### 2.4 客户/业务洞察
无

---

## 第三部分：运行问题记录（龙虾进化专用）

**说明**：main agent 在 2026-05-01 仅执行了定时任务，无真实用户会话。

**问题列表**：
（无）

**汇总**：
```
运行问题记录：0个（无）
数据来源：chat-logs/main/2026-05-01_*.jsonl
涉及 session：0 个
```
"@

$filename = "${agent}_${date}_merged.md"
$outputPath = Join-Path $outputDir $filename
$summary | Out-File -FilePath $outputPath -Encoding UTF8

Write-Output "Summary written to: $outputPath"