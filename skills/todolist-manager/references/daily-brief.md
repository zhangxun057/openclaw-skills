# Daily Work Brief - 每日工作简报

## 核心目标

每天早上自动分析所有虾的工作记录，匹配待办事项进展，生成简报并根据有限权限自动更新任务状态。

---

## 完整流程

### Step 1: 读取待办事项

```javascript
// 1. 加载所有 todolist
const todolists = await loadAllTodolists()

// 2. 路由到目标表（通常是"龙虾养成计划"）
const targetList = todolists[0]

// 3. 读取所有未完成任务
const tasks = await feishu_bitable_app_table_record({
  action: "list",
  app_token: targetList.app_token,
  table_id: "tblU1u2KzTmZIqdw",
  filter: {
    conjunction: "and",
    conditions: [{
      field_name: "任务状态",
      operator: "isNot",
      value: ["已完成"]
    }]
  },
  page_size: 50
})
```

### Step 2: 扫描所有虾的工作记录

**2.1 确定时间范围**
```javascript
// 早上9:00执行，分析昨天的工作
const yesterday = new Date()
yesterday.setDate(yesterday.getDate() - 1)
const dateStr = yesterday.toISOString().split('T')[0] // 2026-03-17
```

**2.2 读取所有虾的 session 日志**
```javascript
const agents = ['guaiguaixia', 'pipipixia', 'lelexia', 'zhuizhuixia', 'main']
const allSessions = []

for (const agent of agents) {
  const sessionsPath = `C:\\Users\\44452\\.openclaw\\agents\\${agent}\\sessions`
  
  // 列出昨天的 session 文件
  const files = exec(`Get-ChildItem -Path ${sessionsPath} -Filter "*.jsonl" | Where-Object { $_.LastWriteTime -gt "${dateStr}" }`)
  
  allSessions.push({
    agent: agent,
    files: files
  })
}
```

### Step 3: 匹配任务与对话

**3.1 提取任务关键词**
```javascript
function extractKeywords(taskTitle) {
  // 简单分词，提取2-4字的关键词
  const keywords = []
  
  // 示例："微信自动回复" → ["微信", "自动回复", "回复"]
  // 示例："diary-assistant skill" → ["diary", "assistant", "skill"]
  
  return keywords
}
```

**3.2 使用 grep 快速定位**
```javascript
for (const task of tasks.records) {
  const title = task.fields["任务名称"]
  const keywords = extractKeywords(title)
  
  // 在所有 session 中搜索关键词
  const grepCmd = `Select-String -Path "C:\\Users\\44452\\.openclaw\\agents\\*\\sessions\\*.jsonl" -Pattern "${keywords.join('|')}" -SimpleMatch`
  
  const matches = exec(grepCmd)
  
  // 提取匹配的 session 文件和行号
  task.relatedSessions = parseGrepResult(matches)
}
```

**3.3 读取相关对话详情**
```javascript
for (const task of tasks.records) {
  if (task.relatedSessions.length === 0) continue
  
  const conversations = []
  
  for (const session of task.relatedSessions) {
    // 只读取匹配行附近的内容（前后5行）
    const content = readSessionContext(session.file, session.lineNumber, 5)
    conversations.push({
      agent: session.agent,
      content: content,
      timestamp: session.timestamp
    })
  }
  
  task.conversations = conversations
}
```

### Step 4: 判断进展并自动更新

**4.1 判断任务状态**
```javascript
for (const task of tasks.records) {
  const currentStatus = task.fields["任务状态"]
  const log = task.fields["任务日志"] || ""
  const conversations = task.conversations || []
  
  let newStatus = currentStatus
  let newLog = log
  let progressSummary = ""
  
  // 判断是否有进展
  if (conversations.length > 0) {
    // 提取进展内容
    progressSummary = summarizeProgress(conversations)
    
    // 追加日志
    newLog += `\n\n【${new Date().toLocaleDateString('zh-CN')}】\n${progressSummary}`
    
    // 判断状态变更
    if (currentStatus === "未启动") {
      newStatus = "进行中"
    } else if (isCompleted(conversations, task.fields["任务描述"])) {
      newStatus = "待验收(AI提交)"
    }
  }
  
  task.suggestedStatus = newStatus
  task.suggestedLog = newLog
  task.progressSummary = progressSummary
}
```

**4.2 权限控制规则**

AI 可以自动更新的状态：
- ✅ 未启动 → 进行中
- ✅ 进行中 → 待验收(AI提交)
- ✅ 任务日志（追加）

AI 不能自动更新的状态：
- ❌ 待验收(AI提交) → 已完成（需要用户批复）
- ❌ 任何状态 → 已放弃/取消

**4.3 执行自动更新**
```javascript
for (const task of tasks.records) {
  if (task.suggestedStatus === task.fields["任务状态"]) continue
  
  // 只更新允许的状态变更
  const allowedTransitions = [
    ["未启动", "进行中"],
    ["进行中", "待验收(AI提交)"]
  ]
  
  const transition = [task.fields["任务状态"], task.suggestedStatus]
  const isAllowed = allowedTransitions.some(t => 
    t[0] === transition[0] && t[1] === transition[1]
  )
  
  if (isAllowed) {
    await feishu_bitable_app_table_record({
      action: "update",
      app_token: targetList.app_token,
      table_id: "tblU1u2KzTmZIqdw",
      record_id: task.record_id,
      fields: {
        "任务状态": task.suggestedStatus,
        "任务日志": task.suggestedLog,
        "日志最后更新日期": Date.now()
      }
    })
    
    task.autoUpdated = true
  }
}
```

### Step 5: 生成简报

**5.1 简报格式**
```markdown
## 📊 每日工作简报 - YYYY年MM月DD日

### 一、有进展的任务（X项）

【任务名称】
- 当前状态：进行中
- 负责虾：皮皮虾
- 昨日进展：完成了 WeFlow API 集成测试
- 已自动更新：状态改为"进行中"，日志已追加
- 下一步：继续完成消息发送功能

【任务名称】
- 当前状态：待验收(AI提交)
- 负责虾：乖乖虾
- 昨日进展：diary-assistant skill 已完成开发和测试
- 已自动更新：状态改为"待验收(AI提交)"
- 等待验收：请确认是否完成

### 二、无进展的任务（X项）

【任务名称】
- 当前状态：未启动
- 建议：本周是否启动？

### 三、需要你批复的任务（X项）

【任务名称】
- 当前状态：待验收(AI提交)
- 完成情况：已达成所有目标
- 请批复：是否验收通过？
  - 回复"任务X验收通过" → 我将状态改为"已完成"
  - 回复"任务X还差xxx" → 我回退状态并追加日志
```

**5.2 发送简报**
```javascript
const briefContent = generateBrief(tasks)

// 通过飞书发送
await message({
  action: "send",
  channel: "feishu",
  to: "user:ou_7a7dc2b5500d01e1863a26e145bf1b58",
  message: briefContent
})
```

### Step 6: 等待用户批复

**6.1 批复格式识别**
```
用户回复示例：
- "任务2验收通过"
- "diary-assistant 验收通过"
- "任务3还差文档"
```

**6.2 执行批复**
```javascript
// 解析用户批复
const approval = parseUserFeedback(userMessage)

if (approval.action === "approve") {
  // 更新为已完成
  await feishu_bitable_app_table_record({
    action: "update",
    app_token: targetList.app_token,
    table_id: "tblU1u2KzTmZIqdw",
    record_id: approval.taskId,
    fields: {
      "任务状态": "已完成",
      "实际完成日期": Date.now()
    }
  })
} else if (approval.action === "reject") {
  // 回退状态并追加日志
  await feishu_bitable_app_table_record({
    action: "update",
    app_token: targetList.app_token,
    table_id: "tblU1u2KzTmZIqdw",
    record_id: approval.taskId,
    fields: {
      "任务状态": "进行中",
      "任务日志": existingLog + `\n\n【${new Date().toLocaleDateString('zh-CN')}】\n用户反馈：${approval.reason}`
    }
  })
}
```

---

## 关键技术点

### 1. 完成判断逻辑

```javascript
function isCompleted(conversations, description) {
  // 方法1：关键词匹配
  const completionKeywords = [
    "已完成", "完成了", "做完了",
    "已实现", "已上线", "已部署",
    "验证通过", "测试通过"
  ]
  
  const hasCompletionKeyword = conversations.some(conv => 
    completionKeywords.some(kw => conv.content.includes(kw))
  )
  
  // 方法2：子任务完成度
  if (description.includes("1.") || description.includes("2.")) {
    const items = description.match(/\d+\./g)?.length || 0
    const completedCount = conversations.filter(conv => 
      /已完成|完成了|做完了/.test(conv.content)
    ).length
    
    return completedCount >= items
  }
  
  return hasCompletionKeyword
}
```

### 2. 进展摘要生成

```javascript
function summarizeProgress(conversations) {
  // 提取关键信息
  const summary = []
  
  for (const conv of conversations) {
    // 提取动作词
    const actions = extractActions(conv.content)
    summary.push(`${conv.agent}：${actions}`)
  }
  
  return summary.join("\n")
}
```

### 3. Grep 结果解析

```javascript
function parseGrepResult(grepOutput) {
  // 解析 Select-String 输出
  // 格式：C:\path\to\file.jsonl:123:content
  
  const results = []
  const lines = grepOutput.split('\n')
  
  for (const line of lines) {
    const match = line.match(/(.+\.jsonl):(\d+):(.+)/)
    if (match) {
      results.push({
        file: match[1],
        lineNumber: parseInt(match[2]),
        content: match[3],
        agent: extractAgentFromPath(match[1])
      })
    }
  }
  
  return results
}
```

---

## 性能优化

### Token 消耗估算

- 读取待办事项：~2K tokens
- Grep 搜索：0 tokens（代码执行）
- 读取相关对话：~5K tokens（只读匹配部分）
- 生成简报：~3K tokens
- **总计：~10K tokens**（相比全文扫描节省90%）

### 执行时间估算

- 读取待办事项：~2秒
- Grep 搜索：~1秒
- 读取相关对话：~3秒
- 更新多维表：~5秒
- **总计：~11秒**

---

## 错误处理

### 1. 找不到对话日志
```javascript
if (allSessions.length === 0) {
  return "昨天没有工作记录，跳过复盘"
}
```

### 2. 多维表更新失败
```javascript
try {
  await updateTask(task)
} catch (error) {
  console.log(`任务 ${task.title} 更新失败：${error.message}`)
  // 继续处理其他任务
}
```

### 3. 用户批复格式错误
```javascript
if (!approval.taskId) {
  return "无法识别任务，请使用格式：任务X验收通过"
}
```

---

_Created: 2026-03-18_
_Version: 1.0_
