---
name: session-summarizer
description: |
  会话摘要技能。从 ChatLogs 读取原始对话，提炼结构化摘要。
  用于：(1) 为 todolist-manager 每日复盘提供输入，(2) 为 diary-assistant 日记撰写提供输入。
  
  **核心设计**：
  - 数据源：C:\Users\44452\.openclaw\chat-logs\{agent}\{date}_{sessionId}.jsonl
  - 输出：C:\Users\44452\.openclaw\chat-logs\summaries\{agent}_{date}_{sessionId}.md
  - 上下文防范：subagent 隔离处理 + 分段读取（>200KB 自动分段）
  
  **触发方式**：
  - 定时任务：[cron:{jobId} session-summary] 日期：YYYY-MM-DD, Agent: {agentId}
  - 手动触发：按照 <session-summarizer>技能，总结 {date} {agent} 的会话
version: 1.1.0
author: 乖乖虾
---

# Session Summarizer - 会话摘要技能

## 核心目标

**解决上下文溢出问题**：将完整会话压缩为高质量摘要，供下游技能（todolist-manager、diary-assistant）使用。

**设计原则**：
- 字数灵活：根据对话量调整（每个会话 3000-5000 字）
- 结构化输出：任务视角（日报）+ 反思视角（日记）
- 上下文安全：>200KB 自动分段，>500KB 使用 subagent
- 可追溯：文件名可反向索引到原始 ChatLogs

---

## 触发条件

### 定时任务触发（主要场景）

```
[cron:{jobId} session-summary] 按照 <session-summarizer>技能，执行会话摘要
日期：YYYY-MM-DD
Agent: {agentId}
输出目录：chat-logs/summaries/
```

### 手动触发（可选）

```
按照 <session-summarizer>技能，总结 2026-04-04 guaiguaixia 的会话
```

---

## 数据流

```
输入：
  C:\Users\44452\.openclaw\chat-logs\{agent}\{date}_{sessionId}.jsonl

处理：
  ├─ 文件大小 < 200KB → 直接分析
  ├─ 文件大小 200-500KB → 分段分析（200 条/段）
  └─ 文件大小 > 500KB → subagent 隔离处理

输出：
  C:\Users\44452\.openclaw\chat-logs\summaries\{agent}_{date}_{sessionId}.md
```

---

## 摘要结构

```markdown
# 会话摘要 · {agent} · {date}

**原始文件**：`{date}_{sessionId}.jsonl`
**摘要生成时间**：YYYY-MM-DD HH:mm:ss
**消息总数**：X 条
**时间跨度**：HH:mm ~ HH:mm
**摘要字数**：Z 字

---

## 第一部分：任务视角（供日报使用）

### 1.1 已完成任务
- **任务名称**（时间段）
  - 关键产出/结果
  - 完成标志

### 1.2 进行中任务
- **任务名称**（时间段）
  - 当前进度
  - 下一步动作
  - 阻塞点（如有）

### 1.3 断线头检测
- **事项名称**（中断位置）
  - 投入程度（对话轮数）
  - 中断原因
  - 后续建议
  - 优先级（高/中/低）

### 1.4 新增待办
- **事项名称**
  - 产生原因
  - 是否独立可交付
  - 建议优先级

---

## 第二部分：反思视角（供日记使用）

### 2.1 主要业务进展
### 事件名称
**背景**：为什么做这件事
**行动**：具体做了什么
**结果**：产出什么
**意义**：对业务的价值

### 2.2 重要决策
### 决策内容
**选项对比**：方案 A/B 优缺点
**最终选择**：方案 X
**考虑因素**：为什么选这个
**影响范围**：影响哪些后续工作

### 2.3 方法论与反思
### 方法论名称
**来源事件**：从哪个具体问题中提炼
**核心内容**：方法论的具体表述
**适用场景**：什么时候可以用
**反例警示**：什么情况下不适用

### 2.4 客户/业务洞察
### 洞察主题
**发现**：具体观察到什么
**数据来源**：从哪个对话中得出
**业务含义**：对业务的启示
**后续行动**：建议跟进什么

---

## 第三部分：元数据

- 原始路径：`C:\Users\44452\.openclaw\chat-logs\{agent}\{date}_{sessionId}.jsonl`
- 摘要路径：`C:\Users\44452\.openclaw\chat-logs\summaries\{agent}_{date}_{sessionId}.md`
- 消息总数：X 条
- 处理模式：直接/分段/subagent
- 分段数：N（仅分段模式）
- 摘要字数：Z 字
- 生成时间：YYYY-MM-DD HH:mm:ss
```

---

## 执行流程

### Step 1: 解析参数

**从 cron prompt 提取**：
```javascript
// 示例 prompt: "[cron:xxx session-summary] 按照 <session-summarizer>技能，执行会话摘要\n日期：2026-04-04\nAgent: guaiguaixia"

const dateMatch = prompt.match(/日期：(\d{4}-\d{2}-\d{2})/);
const agentMatch = prompt.match(/Agent:\s*(\w+)/);

const date = dateMatch ? dateMatch[1] : yesterday();
const agent = agentMatch ? agentMatch[1] : "guaiguaixia";
```

**输出**：
- `date`: "2026-04-04"
- `agent`: "guaiguaixia"
- `chatlogsDir`: `C:\Users\44452\.openclaw\chat-logs\{agent}\`
- `outputDir`: `C:\Users\44452\.openclaw\chat-logs\summaries\`

---

### Step 2: 扫描文件（不读取内容）

**PowerShell 脚本**：
```powershell
# scan-files.ps1
param(
    [string]$chatlogsDir,
    [string]$date
)

$pattern = "${date}_*.jsonl"
$files = Get-ChildItem -Path $chatlogsDir -Filter $pattern -ErrorAction SilentlyContinue

# 过滤隔离会话（定时任务执行的会话，第一条消息包含 [cron:）
$files = $files | Where-Object {
    try {
        $firstLine = Get-Content $_.FullName -First 1 | ConvertFrom-Json
        return $firstLine.text -notmatch '\[cron:'
    } catch {
        return $true # 无法解析时保留
    }
}

$result = $files | ForEach-Object {
    @{
        filename = $_.Name
        path = $_.FullName
        sizeKB = [math]::Round($_.Length / 1KB, 1)
        sessionId = ($_.BaseName -replace "${date}_", "")
    }
}

$result | ConvertTo-Json -Depth 3
```

**执行**：
```javascript
const scanScript = `C:\Users\44452\.openclaw\skills\session-summarizer\scripts\scan-files.ps1`;
const scanResult = await exec({
  command: `powershell -ExecutionPolicy Bypass -File "${scanScript}" -chatlogsDir "${chatlogsDir}" -date "${date}"`
});

const files = JSON.parse(scanResult.stdout);
```

**输出示例**：
```json
[
  {
    "filename": "2026-04-04_ce03bb73.jsonl",
    "path": "C:\\...\\chat-logs\\guaiguaixia\\2026-04-04_ce03bb73.jsonl",
    "sizeKB": 13.1,
    "sessionId": "ce03bb73"
  },
  {
    "filename": "2026-04-04_b80b0a4a.jsonl",
    "path": "C:\\...\\chat-logs\\guaiguaixia\\2026-04-04_b80b0a4a.jsonl",
    "sizeKB": 5.6,
    "sessionId": "b80b0a4a"
  }
]
```

---

### Step 3: 判断处理模式

```javascript
function determineMode(sizeKB) {
  if (sizeKB < 200) {
    return { mode: "direct", segments: 1 };
  } else if (sizeKB < 500) {
    const segments = Math.ceil(sizeKB / 100); // 每段约 100KB
    return { mode: "segmented", segments };
  } else {
    return { mode: "subagent", segments: 1 };
  }
}
```

**阈值说明**：
- < 200KB → 直接处理（约 100K tokens，安全）
- 200-500KB → 分段处理（每段 200 条消息）
- > 500KB → subagent 隔离处理

---

### Step 4: 执行摘要

#### 模式 A：直接处理（<200KB）

```javascript
async function summarizeDirect(filePath) {
  const content = await read({ path: filePath });
  
  // 解析 JSONL
  const messages = content.split('\n')
    .filter(line => line.trim())
    .map(line => JSON.parse(line));
  
  // 调用模型分析
  const summary = await analyzeMessages(messages);
  
  return summary;
}
```

#### 模式 B：分段处理（200-500KB）

```javascript
async function summarizeSegmented(filePath, segmentCount) {
  const content = await read({ path: filePath });
  const messages = content.split('\n')
    .filter(line => line.trim())
    .map(line => JSON.parse(line));
  
  // 分段：每段 200 条消息
  const segmentSize = 200;
  const segments = chunk(messages, segmentSize);
  
  // 逐段分析，累积摘要
  let accumulatedSummary = "";
  
  for (let i = 0; i < segments.length; i++) {
    const segment = segments[i];
    const segmentSummary = await analyzeSegment(segment, accumulatedSummary);
    accumulatedSummary = segmentSummary;
  }
  
  return accumulatedSummary;
}

async function analyzeSegment(segment, previousSummary) {
  const prompt = `
    已累积摘要（如有）：
    ${previousSummary || "无"}
    
    新消息段（${segment.length}条）：
    ${segment.map(m => `[${m.time}] ${m.role}: ${m.text.substring(0, 200)}`).join('\n')}
    
    任务：
    1. 分析新消息段的任务视角和反思视角
    2. 合并到已累积摘要
    3. 输出新的累积摘要（保持简洁，不超过 5000 字）
  `;
  
  // 调用模型
  const result = await callModel(prompt);
  return result;
}
```

#### 模式 C：subagent 隔离处理（>500KB）

```javascript
async function summarizeWithSubagent(filePath, sessionId, date, agent) {
  const subagent = await sessions_spawn({
    task: `分析会话文件 ${filePath}，输出结构化摘要`,
    attachments: [{
      name: `${sessionId}.jsonl`,
      content: await read({ path: filePath }),
      encoding: "utf8"
    }],
    mode: "run",
    cleanup: "delete",
    timeoutSeconds: 600
  });
  
  return subagent.result;
}
```

---

### Step 5: 分析消息内容

```javascript
async function analyzeMessages(messages) {
  // 提取关键信息
  const taskClusters = identifyTaskClusters(messages);
  const hangingTasks = detectHangingTasks(taskClusters);
  const decisions = extractDecisions(messages);
  const methodologies = extractMethodologies(messages);
  const insights = extractInsights(messages);
  
  // 生成摘要
  const summary = `
# 会话摘要 · ${agent} · ${date}

**原始文件**：\`${filename}\`
**摘要生成时间**：${new Date().toISOString()}
**消息总数**：${messages.length} 条
**时间跨度**：${messages[0].time} ~ ${messages[messages.length-1].time}

---

## 第一部分：任务视角

### 1.1 已完成任务
${formatCompletedTasks(taskClusters)}

### 1.2 进行中任务
${formatOngoingTasks(taskClusters)}

### 1.3 断线头检测
${formatHangingTasks(hangingTasks)}

### 1.4 新增待办
${formatNewTodos(taskClusters)}

---

## 第二部分：反思视角

### 2.1 主要业务进展
${formatBusinessProgress(taskClusters)}

### 2.2 重要决策
${formatDecisions(decisions)}

### 2.3 方法论与反思
${formatMethodologies(methodologies)}

### 2.4 客户/业务洞察
${formatInsights(insights)}

---

## 第三部分：元数据

- 原始路径：\`${filePath}\`
- 消息总数：${messages.length} 条
- 处理模式：${mode}
- 摘要字数：约${estimateWords(summary)}字
- 生成时间：${new Date().toISOString()}
`;
  
  return summary;
}
```

---

### Step 6: 识别对话簇和断线头

```javascript
// 识别对话簇（多轮对话→同一任务）
function identifyTaskClusters(messages) {
  const clusters = [];
  let currentCluster = null;
  
  for (const msg of messages) {
    // 基于时间窗口和关键词相似度判断
    if (!currentCluster || isTopicSwitch(msg, currentCluster)) {
      if (currentCluster) clusters.push(currentCluster);
      currentCluster = {
        topic: extractTopic(msg),
        startTime: msg.time,
        messages: [msg]
      };
    } else {
      currentCluster.messages.push(msg);
      currentCluster.endTime = msg.time;
    }
  }
  
  if (currentCluster) clusters.push(currentCluster);
  
  return clusters.map(c => ({
    ...c,
    messageCount: c.messages.length,
    duration: calculateDuration(c.startTime, c.endTime),
    hasCompletionSignal: detectCompletionSignal(c.messages)
  }));
}

// 判断断线头
function detectHangingTasks(clusters) {
  return clusters.filter(c => 
    c.messageCount > 10 &&  // 超过 10 轮
    !c.hasCompletionSignal &&  // 无完成标志
    c.duration > 30 * 60 * 1000  // 超过 30 分钟
  ).map(c => ({
    topic: c.topic,
    messageCount: c.messageCount,
    duration: c.duration,
    interruptReason: detectInterruptReason(c),
    suggestion: generateSuggestion(c),
    priority: calculatePriority(c)
  }));
}
```

---

### Step 7: 输出摘要文件

```javascript
async function writeSummary(agent, date, sessionId, summary) {
  const outputDir = `C:\\Users\\44452\\.openclaw\\chat-logs\\summaries\\`;
  
  // 确保目录存在
  await exec({ command: `mkdir -p "${outputDir}"` });
  
  // 文件名：{agent}_{date}_{sessionId}.md
  const filename = `${agent}_${date}_${sessionId}.md`;
  const outputPath = `${outputDir}${filename}`;
  
  await write({ path: outputPath, content: summary });
  
  return {
    filename,
    outputPath,
    originalPath: `C:\\Users\\44452\\.openclaw\\chat-logs\\${agent}\\${date}_${sessionId}.jsonl`
  };
}
```

---

### Step 8: 生成合并视图（可选）

```javascript
async function generateMergedSummary(agent, date, summaries) {
  const merged = `
# 合并摘要 · ${agent} · ${date}

**生成时间**：${new Date().toISOString()}
**原始会话数**：${summaries.length}
**总摘要字数**：${summaries.reduce((acc, s) => acc + s.wordCount, 0)}字

---

## 任务视角汇总
${summaries.map(s => s.taskSection).join('\n\n')}

---

## 反思视角汇总
${summaries.map(s => s.reflectionSection).join('\n\n')}
`;
  
  const filename = `${agent}_${date}_merged.md`;
  const outputPath = `C:\\Users\\44452\\.openclaw\\chat-logs\\summaries\\${filename}`;
  
  await write({ path: outputPath, content: merged });
  
  return { filename, outputPath };
}
```

---

### Step 9: 记录使用日志

```bash
mkdir -p ~/.openclaw/skill-logs/session-summarizer
echo "## [$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')]" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **日期**: ${date}" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **Agent**: ${agent}" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **会话数**: ${files.length}" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **处理模式**: ${mode}" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **结果**: 成功/失败" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "" >> ~/.openclaw/skill-logs/session-summarizer/log.md
```

---

## 内容筛选原则

### ✅ 必须记录

| 类型 | 日报关切 | 日记关切 | 判断标准 |
|------|---------|---------|----------|
| 任务完成/中断 | ✅ | ⚠️ | 用户明确说"完成"/"暂停" |
| 多轮对话簇 | ✅ | ⚠️ | >10 轮对话推进同一事项 |
| 用户明确决策 | ✅ | ✅ | "决定用方案 X" |
| 方法论提炼 | ⚠️ | ✅ | "我发现"/"经验是" |
| 业务洞察 | ⚠️ | ✅ | 客户特征/市场信息 |
| 反思/感想 | ⚠️ | ✅ | "我意识到..." |

### ❌ 不记录（过滤）

| 类型 | 原因 | 示例 |
|------|------|------|
| 技术调试 | 一次性操作 | API Key 配置、Referer 设置 |
| 环境搭建 | 临时性 | 安装依赖、配置路径 |
| 测试数据 | 中间产物 | "选 5 个客户测试" |
| 代码细节 | 代码已记录 | 具体函数实现 |
| 闲聊对话 | 无业务价值 | 问候、闲聊 |
| 工具错误重试 | 过程细节 | "再试一次"/"换个方法" |

---

## 与下游技能的接口

### todolist-manager 读取方式

```javascript
// 读取单个 Agent 的合并摘要
const summaryPath = `C:\\Users\\44452\\.openclaw\\chat-logs\\summaries\\${agent}_${yesterday()}_merged.md`;
const summary = await read({ path: summaryPath });

// 提取任务视角部分
const taskSection = summary.match(/## 任务视角汇总([\s\S]*?)## 反思视角汇总/)[1];

// 解析：
// - 已完成任务 → 更新状态为"待验收"
// - 进行中任务 → 追加日志
// - 断线头 → 创建新 Todo（状态=待确认）
```

### diary-assistant 读取方式

```javascript
// 读取所有 Agent 的合并摘要
const agents = ["guaiguaixia", "lelexia", "main", "pipipixia", "zhuizhuixia"];
const summaries = await Promise.all(
  agents.map(agent => 
    read({ path: `C:\\Users\\44452\\.openclaw\\chat-logs\\summaries\\${agent}_${yesterday()}_merged.md` })
  )
);

// 提取反思视角部分
const reflectionContent = summaries.map(s => {
  const match = s.match(/## 反思视角汇总([\s\S]*?)## 元数据/);
  return match ? match[1] : "";
}).join('\n\n');

// 用于日记撰写
```

---

## 反向索引

**从摘要文件定位原始 ChatLogs**：

```javascript
function getOriginalPath(summaryFilename) {
  // 输入：guaiguaixia_2026-04-04_ce03bb73.md
  const match = summaryFilename.match(/(\w+)_(\d{4}-\d{2}-\d{2})_(\w+)\.md/);
  if (!match) return null;
  
  const [, agent, date, sessionId] = match;
  return `C:\\Users\\44452\\.openclaw\\chat-logs\\${agent}\\${date}_${sessionId}.jsonl`;
}
```

---

## 相关文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 扫描脚本 | `scripts/scan-files.ps1` | 扫描 ChatLogs 文件 |
| 分段脚本 | `scripts/segment-messages.ps1` | 分段处理大文件 |
| subagent 模板 | `templates/subagent-task.md` | subagent 任务模板 |

---

## 使用日志

每次技能触发时，自动记录到 `~/.openclaw/skill-logs/session-summarizer/log.md`：

```bash
mkdir -p ~/.openclaw/skill-logs/session-summarizer
echo "## [$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')]" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **日期**: YYYY-MM-DD" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **Agent**: {agentId}" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **会话数**: X" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **处理模式**: 直接/分段/subagent" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "- **结果**: 成功/失败" >> ~/.openclaw/skill-logs/session-summarizer/log.md
echo "" >> ~/.openclaw/skill-logs/session-summarizer/log.md
```

---

## 定时任务配置示例

```json
[
  {
    "name": "session-summary-guaiguaixia",
    "schedule": "30 23 * * *",
    "command": "openclaw send --agent guaiguaixia --message '[cron:xxx session-summary] 按照 <session-summarizer>技能，执行会话摘要\\n日期：{{yesterday}}\\nAgent: guaiguaixia'",
    "model": "aliyun-bailian/qwen3.5-plus"
  },
  {
    "name": "session-summary-lelexia",
    "schedule": "35 23 * * *",
    "command": "openclaw send --agent lelexia --message '[cron:xxx session-summary] 按照 <session-summarizer>技能，执行会话摘要\\n日期：{{yesterday}}\\nAgent: lelexia'",
    "model": "aliyun-bailian/qwen3.5-plus"
  }
]
```

---

_创建时间：2026-04-05_
_版本：1.0.0_
_作者：乖乖虾_
