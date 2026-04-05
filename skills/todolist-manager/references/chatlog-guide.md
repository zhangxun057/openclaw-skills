# Chatlog Location Guide - 对话日志位置指南

## 日志存储结构

```
C:\Users\44452\.openclaw\agents\
├── guaiguaixia\sessions\*.jsonl
├── pipipixia\sessions\*.jsonl
├── lelexia\sessions\*.jsonl
├── zhuizhuixia\sessions\*.jsonl
└── main\sessions\*.jsonl
```

## 日志格式

每个 session 文件是 JSONL 格式（每行一个 JSON 对象）：

```json
{
  "type": "message",
  "id": "abc123",
  "timestamp": "2026-03-18T15:23:48.495Z",
  "message": {
    "role": "user",
    "content": "帮我实现微信自动回复"
  }
}
```

## 快速搜索方法

### 方法1：使用 Select-String（推荐）

```powershell
# 搜索包含"微信"的所有对话
Select-String -Path "C:\Users\44452\.openclaw\agents\*\sessions\*.jsonl" -Pattern "微信" -SimpleMatch

# 搜索多个关键词（OR）
Select-String -Path "C:\Users\44452\.openclaw\agents\*\sessions\*.jsonl" -Pattern "微信|自动回复" 

# 限定时间范围（昨天）
$yesterday = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
Get-ChildItem "C:\Users\44452\.openclaw\agents\*\sessions\*.jsonl" | 
  Where-Object { $_.LastWriteTime -gt $yesterday } | 
  Select-String -Pattern "微信"
```

### 方法2：读取特定 session

```javascript
// 读取完整 session 文件
const sessionPath = "C:\\Users\\44452\\.openclaw\\agents\\guaiguaixia\\sessions\\484e9933-2f31-4374-a3c8-997e9d289a82.jsonl"
const content = await read(sessionPath)

// 解析 JSONL
const lines = content.split('\n').filter(line => line.trim())
const messages = lines.map(line => JSON.parse(line))

// 提取用户和助手的对话
const conversations = messages
  .filter(m => m.type === 'message')
  .map(m => ({
    role: m.message.role,
    content: extractText(m.message.content),
    timestamp: m.timestamp
  }))
```

## 提取文本内容

```javascript
function extractText(content) {
  if (typeof content === 'string') return content
  
  if (Array.isArray(content)) {
    return content
      .filter(item => item.type === 'text')
      .map(item => item.text)
      .join('\n')
  }
  
  return ''
}
```

## 按 Agent 分组

```javascript
const agents = ['guaiguaixia', 'pipipixia', 'lelexia', 'zhuizhuixia', 'main']

for (const agent of agents) {
  const sessionsPath = `C:\\Users\\44452\\.openclaw\\agents\\${agent}\\sessions`
  
  // 列出所有 session 文件
  const files = exec(`Get-ChildItem -Path ${sessionsPath} -Filter "*.jsonl"`)
  
  console.log(`${agent}: ${files.length} sessions`)
}
```

## Memory 压缩记录

除了原始 chatlog，还可以读取压缩后的 memory：

```
C:\Users\44452\.openclaw\agents\{agentId}\workspace\memory\daily-log-YYYY-MM-DD.md
```

Memory 文件是 Markdown 格式，已经过 AI 压缩总结，更适合快速浏览。

---

_Created: 2026-03-18_
