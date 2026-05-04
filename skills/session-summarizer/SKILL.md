---
name: session-summarizer
description: |
  会话摘要技能。将指定 agent 全天的所有会话合并为 1 条结构化摘要。
  用于：(1) 为 todolist-manager 每日复盘提供输入，(2) 为 diary-assistant 日记撰写提供输入。
  
  **核心设计**：
  - 数据源：C:\Users\44452\.openclaw\chat-logs\{agent}\{date}_{sessionId}.jsonl（多个）
  - 输出：C:\Users\44452\.openclaw\chat-logs\summaries\{agent}_{date}_merged.md（1 个）
  - 上下文防范：总大小 >500KB 时使用 subagent
  
  **触发方式**：
  - 定时任务：[cron:{jobId} session-summary] 日期：YYYY-MM-DD, Agent: {agentId}
  - 手动触发：按照 <session-summarizer>技能，总结 {date} {agent} 的会话
version: 2.2.0
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
  C:\Users\44452\.openclaw\chat-logs\{agent}\{date}_*.jsonl（该 agent 全天所有会话）

处理：
  1. 扫描并过滤隔离会话
  2. 合并所有会话内容为一个消息集合
  3. 按总大小判断处理模式：
       ├─ 总大小 < 200KB → 直接分析
       ├─ 总大小 200-500KB → 分段分析（200 条/段）
       └─ 总大小 > 500KB → subagent 隔离处理
  4. 生成单条合并摘要

输出：
  C:\Users\44452\.openclaw\chat-logs\summaries\{agent}_{date}_merged.md
```

---

## 摘要结构

```markdown
# 会话摘要 · {agent} · {date}

**原始文件**：{date}_*.jsonl（合并 {N} 个会话）
**摘要生成时间**：YYYY-MM-DD HH:mm:ss
**消息总数**：X 条
**时间跨度**：HH:mm ~ HH:mm
**摘要字数**：Z 字

---

## 第一部分：任务视角（供日报使用）

**【新增】用户投入量（顶置）**：
- 用户消息：X 条，X 字，~X token
- 主要投入：描述用户花最多精力做的事情
- 时间跨度：HH:MM ~ HH:MM

**【新增】主线概述**：
一句话说明今天整体在干什么，串联全天。

### 1.1 核心交付（主线）⭐
- **任务名称**（时间段）
  - 为什么做：背景/需求
  - 做了什么：关键行动
  - 产出什么：具体结果
  - 版本/状态变化

### 1.2 其他交付
- **任务名称**（时间段）
  - 关键产出/结果

### 1.3 进行中任务
- **任务名称**（时间段）
  - 当前进度
  - 下一步动作
  - 阻塞点（如有）

### 1.4 断线头
- **事项名称**（中断位置）
  - 投入程度（对话轮数/消息数）
  - 根因分析
  - 临时绕过方案（如有）
  - 优先级（高/中/低）

### 1.5 新增待办
- **事项名称**
  - 产生原因
  - 是否独立可交付
  - 建议优先级

**【新增】关联前序**：
- 来自记忆的相关背景（如昨天的未完成事项、长期项目进展等）

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

## 第三部分：运行问题记录（龙虾进化专用）

**说明**：扫描 session 文件，提取工具执行层和模型调用层的真实异常，形成可追溯的问题档案。

**问题列表**：
（无问题则写「无」）

| # | 时间 | 层级 | 工具/模型 | 问题类型 | 描述 | Session文件 |
|---|------|------|----------|---------|------|------------|
| 1 | HH:MM | 🔴工具/🟡模型 | exec/Python | 引号转义失效 | `python -c` 内联代码中 f-string 引号被 PowerShell 截断 | {filename} |
| 2 | HH:MM | 🔴工具 | exec | 编码失败 | GBK 无法编码 emoji/生僻字，导致 UnicodeEncodeError | {filename} |

**汇总**：
```
运行问题记录：N个（🔴X / 🟡Y / ⚠️Z）
数据来源：sessions.json → session 文件直接扫描
涉及 session：X 个
```

---

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

### Step 3: 合并所有会话 + 统计用户输入

**将所有会话文件内容合并为一个消息数组，按时间排序；同时统计用户输入量**（用于摘要顶置显示）：

```javascript
async function mergeAllSessions(files) {
  let allMessages = [];
  let userChars = 0, userMsgs = 0, aiMsgs = 0;
  
  for (const file of files) {
    const content = await read({ path: file.path });
    const messages = content.split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line));
    
    for (const msg of messages) {
      if (msg.role === 'user') {
        userMsgs++;
        // 去除消息引用/代码块等干扰字符估算纯文本长度
        const text = (msg.text || '').replace(/\[\[.*?\]\]|\{.*?\}|```[\s\S]*?```/g, 'X');
        userChars += text.length;
      } else if (msg.role === 'assistant') {
        aiMsgs++;
      }
    }
    
    allMessages = allMessages.concat(messages);
  }
  
  // 按时间排序
  allMessages.sort((a, b) => new Date(a.time) - new Date(b.time));
  
  const userTokens = Math.round(userChars * 1.5); // 中文中文字符约1.5 token/字
  
  return { allMessages, userStats: { msgs: userMsgs, chars: userChars, tokens: userTokens, aiMsgs } };
}
```

**输出**：`{ allMessages, userStats: { msgs, chars, tokens, aiMsgs } }`

---

### Step 4: 判断处理模式

```javascript
function determineMode(totalSizeKB) {
  if (totalSizeKB < 200) {
    return { mode: "direct", segments: 1 };
  } else if (totalSizeKB < 500) {
    const segments = Math.ceil(totalSizeKB / 100);
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

### Step 5: 执行摘要

#### 模式 A：直接处理（<200KB）

```javascript
async function summarizeDirect(allMessages, userStats, totalSessions) {
  const summary = await analyzeMessages(allMessages, userStats, totalSessions);
  return summary;
}
```

#### 模式 B：分段处理（200-500KB）

```javascript
async function summarizeSegmented(allMessages, userStats, totalSessions) {
  const segmentSize = 200;
  const segments = chunk(allMessages, segmentSize);
  
  let accumulatedSummary = "";
  
  for (let i = 0; i < segments.length; i++) {
    const isLast = (i === segments.length - 1);
    const prompt = buildSegmentPrompt(segments[i], accumulatedSummary, isLast);
    
    const result = await callModel(prompt);
    
    if (isLast) {
      // 最后一段：输出结构化摘要
      return formatStructuredSummary(result, allMessages, userStats, totalSessions, agent, date);
    } else {
      // 中间段：累积为纯文本，供下一段使用
      accumulatedSummary = result;
    }
  }
}

function buildSegmentPrompt(segment, previousSummary, isLast) {
  const base = `已累积摘要（如有）：${previousSummary || "无"}

新消息段（${segment.length}条）：
${segment.map(m => `[${m.time}] ${m.role}: ${m.text.substring(0, 200)}`).join('\n')}`;
  
  if (isLast) {
    return base + `

任务：分析以上所有消息段，输出完整的结构化摘要（包含任务视角和反思视角）。`;
  } else {
    return base + `

任务：分析新消息段，输出累积摘要（不超过 3000 字），供下一段继续累积。`;
  }
}

function formatStructuredSummary(accumulatedText, allMessages, userStats, totalSessions, agent, date) {
  const prompt = `将以下累积摘要整理为结构化格式：

${accumulatedText}

消息总数：${allMessages.length} 条
用户消息：${userStats.msgs} 条，${userStats.chars} 字，~${userStats.tokens} token
会话数：${totalSessions} 个

请严格按以下格式输出（章节标题不得修改）：
# 会话摘要 · ${agent} · ${date}

## 第一部分：任务视角（供日报使用）

## 第二部分：反思视角（供日记使用）

## 第三部分：运行问题记录（龙虾进化专用）`;
  
  return callModel(prompt);
}
```

#### 模式 C：subagent 隔离处理（>500KB）

```javascript
async function summarizeWithSubagent(allMessages, date, agent) {
  const content = allMessages.map(m => JSON.stringify(m)).join('\n');
  
  const subagent = await sessions_spawn({
    task: `分析以下合并会话，输出结构化摘要。摘要格式：
1. 第一部分：任务视角（已完成/进行中/断线头/新增待办）
2. 第二部分：反思视角（主要进展/重要决策/方法论/业务洞察）
3. 第三部分：运行问题记录（龙虾进化专用）`,
    attachments: [{
      name: `merged_${date}.jsonl`,
      content: content,
      encoding: "utf8"
    }],
    mode: "run",
    cleanup: "delete",
    timeoutSeconds: 600
  });
  
  return subagent.result;
}

// ---------- 工具函数 ----------

function chunk(arr, size) {
  const result = [];
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size));
  }
  return result;
}
```

---

### Step 6: 分析消息内容

```javascript
async function analyzeMessages(messages, userStats, totalSessions) {
  // 提取关键信息
  const taskClusters = identifyTaskClusters(messages);
  const hangingTasks = detectHangingTasks(taskClusters);
  const decisions = extractDecisions(messages);
  const methodologies = extractMethodologies(messages);
  const insights = extractInsights(messages);
  const mainThread = identifyMainThread(taskClusters, messages); // 识别主线
  
  // 计算时间跨度
  const startTime = messages[0]?.time ? messages[0].time.substring(11, 16) : 'N/A';
  const endTime = messages[messages.length - 1]?.time ? messages[messages.length - 1].time.substring(11, 16) : 'N/A';
  
  // 生成摘要
  const summary = `
# 会话摘要 · ${agent} · ${date}

**原始文件**：${date}_*.jsonl（合并 ${totalSessions} 个会话）
**摘要生成时间**：${new Date().toISOString()}

---

## 第一部分：任务视角（供日报使用）

**【新增】用户投入量（顶置）**：
- 用户消息：${userStats.msgs} 条，${userStats.chars} 字，~${userStats.tokens} token
- 主要投入：${mainThread.userFocus || '日常对话'}
- 时间跨度：${startTime} ~ ${endTime}

**【新增】主线概述**：
${mainThread.summary || '无明显主线'}

### 1.1 核心交付（主线）⭐
${formatCoreDeliverables(taskClusters, mainThread)}

### 1.2 其他交付
${formatOtherDeliverables(taskClusters, mainThread)}

### 1.3 进行中任务
${formatOngoingTasks(taskClusters)}

### 1.4 断线头
${formatHangingTasks(hangingTasks)}

### 1.5 新增待办
${formatNewTodos(taskClusters)}

**【新增】关联前序**：
${mainThread.relatedPrior || '无相关前序记录'}

---

## 第二部分：反思视角（供日记使用）

### 2.1 主要业务进展
${formatBusinessProgress(taskClusters)}

### 2.2 重要决策
${formatDecisions(decisions)}

### 2.3 方法论与反思
${formatMethodologies(methodologies)}

### 2.4 客户/业务洞察
${formatInsights(insights)}

---

## 第三部分：运行问题记录（龙虾进化专用）

**说明**：扫描 session 文件，提取工具执行层和模型调用层的真实异常，形成可追溯的问题档案。

**问题列表**：
（无问题则写「无」）

| # | 时间 | 层级 | 工具/模型 | 问题类型 | 描述 | Session文件 |
|---|------|------|----------|---------|------|------------|
| 1 | HH:MM | 🔴工具/🟡模型 | exec/Python | 引号转义失效 | `python -c` 内联代码中 f-string 引号被 PowerShell 截断 | {filename} |
| 2 | HH:MM | 🔴工具 | exec | 编码失败 | GBK 无法编码 emoji/生僻字，导致 UnicodeEncodeError | {filename} |

**汇总**：
```
运行问题记录：N个（🔴X / 🟡Y / ⚠️Z）
数据来源：sessions.json → session 文件直接扫描
涉及 session：X 个
```
`;
  
  return summary;
}
```

---

### Step 7: 识别对话簇和断线头

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

// ---------- 新增：主线识别函数 ----------

// 识别主线：从对话簇中判断哪条是核心工作线
function identifyMainThread(clusters, messages) {
  if (!clusters || clusters.length === 0) return { summary: '无对话记录', userFocus: '无', relatedPrior: '无' };
  
  // 找出用户投入最多的簇（用消息数和字符数判断）
  const userClusters = clusters.map(c => {
    const userMsgs = c.messages.filter(m => m.role === 'user');
    const userChars = userMsgs.reduce((sum, m) => sum + (m.text || '').length, 0);
    return { ...c, userMsgs: userMsgs.length, userChars };
  });
  
  // 按用户投入排序
  userClusters.sort((a, b) => b.userChars - a.userChars);
  
  const top = userClusters[0];
  
  // 判断是否有明确主线（多轮推进同一事项 = 主线）
  const mainCluster = userClusters.find(c => 
    c.userMsgs >= 3 && c.messageCount >= 6
  ) || top;
  
  // 生成主线一句话
  const topic = mainCluster.topic || '日常任务';
  const msgs = mainCluster.messages;
  const hasDev = msgs.some(m => m.text && (m.text.includes('开') || m.text.includes('开发') || m.text.includes('改') || m.text.includes('实现')));
  const hasDiscuss = msgs.some(m => m.text && (m.text.includes('讨论') || m.text.includes('分析') || m.text.includes('你觉得')));
  const hasDecision = msgs.some(m => m.text && (m.text.includes('同意') || m.text.includes('就这么办') || m.text.includes('确认')));
  
  let summary = '';
  if (hasDev && hasDiscuss) {
    summary = `${topic}：需求讨论 → 技术实现 → 验证交付`;
  } else if (hasDev) {
    summary = `${topic}：开发交付`;
  } else if (hasDiscuss) {
    summary = `${topic}：分析讨论`;
  } else if (hasDecision) {
    summary = `${topic}：决策确认`;
  } else {
    summary = `${topic}：${mainCluster.messageCount} 轮对话`;
  }
  
  // 用户主要在干什么
  const userFocus = msgs.filter(m => m.role === 'user')
    .map(m => extractBrief(m.text))
    .filter(Boolean)
    .slice(0, 3);
  
  return {
    summary,
    userFocus: userFocus.join('；') || '日常对话',
    mainClusterId: mainCluster.topic,
    userMsgs: mainCluster.userMsgs,
    relatedPrior: inferRelatedPrior(topic, messages)
  };
}

// 从消息中提取简短描述
function extractBrief(text) {
  if (!text) return '';
  // 取第一句或前50字
  const first = text.split(/[\n。.]/)[0] || text;
  return first.substring(0, 50).replace(/\[\[.*?\]\]|```[\s\S]*?```/g, '');
}

// 根据主题推断关联前序
function inferRelatedPrior(topic, messages) {
  const topic_lower = (topic || '').toLowerCase();
  
  // 检查是否有明确的"接上文"/"继续"类信号
  const continuationSignal = messages.some(m => 
    m.role === 'user' && m.text && (
      m.text.includes('继续') || 
      m.text.includes('接着') ||
      m.text.includes('昨天') ||
      m.text.includes('上次') ||
      m.text.includes('早上')
    )
  );
  
  if (continuationSignal) {
    // 从用户消息中提取前一天相关描述
    const userMsgs = messages.filter(m => m.role === 'user').map(m => m.text || '');
    const relevant = userMsgs.find(t => t.includes('昨天') || t.includes('上次') || t.includes('继续'));
    if (relevant) return `用户提到："${extractBrief(relevant)}"`;
  }
  
  return '无明确前序关联';
}

// 格式化为核心交付（主线）
function formatCoreDeliverables(clusters, mainThread) {
  if (!clusters || clusters.length === 0) return '无';
  
  // 找出主线簇
  const mainCluster = clusters.find(c => 
    c.topic === mainThread.mainClusterId || 
    (c.topic && c.topic.includes(mainThread.mainClusterId))
  );
  
  if (!mainCluster) {
    // 没有明确主线，返回投入最多的
    const sorted = [...(clusters || [])].sort((a, b) => b.messageCount - a.messageCount);
    if (sorted.length === 0) return '无';
    const top = sorted[0];
    return `**${top.topic || '主要任务'}**（${top.startTime?.substring(11, 16) || '?'} ~ ${top.endTime?.substring(11, 16) || '?'}）\n  - 关键产出：${top.completionNote || '见下方详情'}`;
  }
  
  const start = mainCluster.startTime?.substring(11, 16) || '';
  const end = mainCluster.endTime?.substring(11, 16) || '';
  
  // 从簇内消息提取：背景、行动、结果
  const userMsgs = mainCluster.messages.filter(m => m.role === 'user');
  const firstAsk = userMsgs[0]?.text || '';
  const lastAssistant = [...mainCluster.messages].reverse().find(m => m.role === 'assistant')?.text || '';
  
  // 提取完成信号
  let completionNote = '';
  if (mainCluster.hasCompletionSignal) {
    completionNote = '已完成';
  } else if (lastAssistant.includes('完成') || lastAssistant.includes('✅') || lastAssistant.includes('成功')) {
    completionNote = '已完成';
  } else if (lastAssistant.includes('失败') || lastAssistant.includes('❌')) {
    completionNote = '部分完成';
  } else {
    completionNote = '进行中';
  }
  
  return `**${mainCluster.topic || '主要任务'}**（${start} ~ ${end}）⭐\n  - 背景：${extractBrief(firstAsk)}\n  - 产出：${completionNote}`;
}

// 格式化为其他交付
function formatOtherDeliverables(clusters, mainThread) {
  if (!clusters || clusters.length <= 1) return '无';
  
  // 排除主线
  const others = clusters.filter(c => c.topic !== mainThread.mainClusterId);
  if (others.length === 0) return '无';
  
  return others.map(c => {
    const start = c.startTime?.substring(11, 16) || '';
    const end = c.endTime?.substring(11, 16) || '';
    const note = c.hasCompletionSignal ? '✅' : '⬜';
    return `- **${c.topic || '其他任务'}**（${start} ~ ${end}）${note}\n  - ${c.completionNote || ''}`;
  }).join('\n');
}
```

---

### Step 8: 输出摘要文件

```javascript
async function writeSummary(agent, date, summary) {
  const outputDir = `C:\Users\44452\.openclaw\chat-logs\summaries\`;
  
  // 确保目录存在
  await exec({ command: `mkdir -p "${outputDir}"` });
  
  // 文件名：{agent}_{date}_merged.md（每天每个 agent 只输出 1 个文件）
  const filename = `${agent}_${date}_merged.md`;
  const outputPath = `${outputDir}${filename}`;
  
  await write({ path: outputPath, content: summary });
  
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
  const match = s.match(/## 反思视角汇总([\s\S]*?)## 第三部分：运行问题记录/);
  return match ? match[1] : "";
}).join('\n\n');

// 用于日记撰写
```

---

## 反向索引

**从摘要文件定位原始 ChatLogs**：

```javascript
function getOriginalPath(summaryFilename) {
  // 输入：guaiguaixia_2026-04-04_merged.md
  const match = summaryFilename.match(/(\w+)_(\d{4}-\d{2}-\d{2})_merged\.md/);
  if (!match) return null;
  
  const [, agent, date] = match;
  return `C:\\Users\\44452\\.openclaw\\chat-logs\\${agent}\\${date}_*.jsonl`;
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

## 运行问题记录（龙虾进化专用）

**数据来源**：
```
索引文件：C:\Users\44452\.openclaw\agents\{agent}\sessions.json
session文件：C:\Users\44452\.openclaw\agents\{agent}\sessions\{uuid}.jsonl
```

**sessions.json 结构**：键为 session key，值为 `{sessionId, updatedAt, sessionFile}`，其中 `sessionFile` 指向实际 session 文件。

**session 文件格式**：每行一个 JSON 对象，type 字段区分消息类型：
- `{"type":"message", "message":{...}}` — 消息，role=user/assistant
- `{"type":"toolResult", "isError":true, "content":[...]}` — 工具执行失败（重点扫描）
- `{"type":"toolCall", ...}` — 工具调用
- `{"type":"custom", "customType":"openclaw.sessions_yield", ...}` — 内部事件

**⚠️ 溢出风险**：原始 session 文件可能达 1MB 以上，直接塞给 LLM 会溢出。必须先运行扫描脚本提取异常记录，再将扫描结果喂给 LLM 生成第三部分。

**扫描脚本**（`scripts/scan_session_errors.ps1`）：
```powershell
# 读取 sessions.json，获取目标 agent 的 session 文件列表
# 对每个 session 文件，按行扫描：
#   - toolResult isError=true → 提取错误内容
#   - message 含 error/fail/timeout/exception/traceback 关键词 → 提取片段
#   - 按 HH:MM 标记时间，提取 Session 文件名
# 输出：结构化异常列表（每条含：时间、层级、工具/模型、问题类型、描述、文件名）
```

**扫描信号关键词**（参考，不穷举）：
- 工具层：`SyntaxError` / `UnicodeDecodeError` / `UnicodeEncodeError` / `PathNotFound` / `TerminatorExpectedAtEndOfString` / `'gbk' codec` / `FileNotFoundError`
- 模型层：`idle timeout` / `timed out` / `timeout`
- 网络层：`fetch failed` / `Connection refused` / `ECONNREFUSED`

**输出格式**：
```
| # | 时间 | 层级 | 工具/模型 | 问题类型 | 描述 | Session文件 |
|---|------|------|----------|---------|------|------------|
| 1 | HH:MM | 🔴工具 | exec | 引号转义失效 | python -c 内联代码中 f-string 引号被 PowerShell 截断 | {filename} |
```

**汇总行**：
```
运行问题记录：N个（🔴X / 🟡Y / ⚠️Z）
数据来源：sessions.json → session 文件直接扫描
涉及 session：X 个
```

如无异常：`运行问题记录：0个（无）`

---

## 使用日志

每次触发后执行以下脚本记录调用情况：

```bash
node ~/.openclaw/skills/_shared/log-usage.mjs "session-summarizer" "<触发原因>" "<结果>"
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
_版本：2.2.0_
_作者：乖乖虾_

_最后更新：2026-04-22_
_更新说明：第三部分「运行问题记录」已移除，功能迁移至 agent-retrospective。
