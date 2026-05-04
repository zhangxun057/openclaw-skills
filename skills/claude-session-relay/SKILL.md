---
name: claude-session-relay
description: |
  丑丑虾通过 CLI 操纵 Claude Code 进行多轮对话。

  **触发场景**：用户说"和 CC 对话"、"让 Claude Code 做事"、"查看 CC 会话历史"、"继续上次的 CC 会话"

  **核心功能**：
  1. 列出历史会话（按时间排序，展示摘要）
  2. 选择历史会话恢复多轮对话
  3. 新建单轮任务
  4. 传话模式：用户 ↔ Claude Code 双向传递
  5. 支持"透传模式"和"优化模式"两种指令处理方式

  **与 Claude Code 对话的工作流**：
  - 用户以对话形式描述需求
  - 丑丑虾翻译为 CLI 命令执行
  - CC 的输出完整返回给用户（不压缩、不调整）
author: 乖乖虾
version: 1.1.0
---

# Claude Session Relay

丑丑虾通过 CLI 操纵 Claude Code 的传话工具。

## 调用方式优先级

> Windows PowerShell 传参时中文编码极易损坏，以下是实测有效的方法，按可靠性排序。

### 🥇 主选：PS1 脚本文件法（最稳定）

**适用场景**：任何需要传中文指令的场景。

```powershell
# 1. 把任务写入文件（UTF-8，无 BOM）
$task = @"
你的指令内容（支持中文）
"@
Set-Content -Path "$env:TEMP\cc-task.txt" -Value $task -Encoding utf8

# 2. 用 PS1 脚本封装调用
$script = @'
Set-Location "C:\Users\44452\Desktop\model-switch-v2-test"
$msg = Get-Content "$env:TEMP\cc-task.txt" -Raw
claude -p $msg 2>&1
'@
$script | Out-File -FilePath "$env:TEMP\run-cc.ps1" -Encoding utf8

# 3. 执行
powershell -ExecutionPolicy Bypass -File "$env:TEMP\run-cc.ps1"
```

**原理**：PowerShell `-File` 参数不经过命令行解析，不触发编码转换，UTF-8 内容原样传给子进程。

**关键点**：
- 脚本文件必须用 `-Encoding utf8` 写入
- 用 `$env:TEMP` 避免路径中文问题
- 脚本文件存 `.ps1`，用 `-ExecutionPolicy Bypass -File` 执行

### 🥈 备选一：直接交互法（无编码问题）

**适用场景**：短指令、无中文、或纯英文指令。

```powershell
claude -p "your English command here" 2>&1
```

**优点**：最简单，无编码问题
**缺点**：中文乱码，指令太长会被截断

### 🥉 备选二：直接 resume 会话（多轮对话）

**适用场景**：恢复历史会话进行多轮对话。

```powershell
claude --resume <session_id>
```

**注意**：session_id 必须有效。查历史：`history.jsonl` 或 `claude sessions list`

### 🚫 避免使用

- ❌ `claude -p "中文内容"` — 命令行参数直接传中文，PowerShell 编码必乱
- ❌ `cmd /c claude -p "..."` — CMD 同样有编码问题
- ❌ `&&` 串联命令在 PowerShell 中 — `&&` 在 PowerShell 是无效的语法分隔符

---

## 工作模式

### 模式一：透传模式（用户无特殊要求时默认）

用户的输入**直接转发**给 Claude Code，不修改、不补充、不压缩。

透传时使用 **PS1 脚本文件法**（主选），确保中文不乱码。

```powershell
# 丑丑虾执行：写入任务文件
Set-Content -Path "$env:TEMP\cc-task.txt" -Value "用户指令" -Encoding utf8
# 再用 powershell -File 执行 PS1 脚本（见上方主选方案）
```

### 模式二：优化模式（用户明确说"帮我思考/完善/扩充"）

丑丑虾**先理解和扩充需求**，再发给 Claude Code。

```
用户：需求大概是这样，你帮我完善后再发给 CC
→ 丑丑虾：理解需求 → 补充细节 → 扩充表述
→ 写入任务文件
→ 执行 CLI
→ 完整返回 CC 输出
```


**判断规则**：用户没有明确要求优化时，默认透传。

---

## 命令参考

### 列出历史会话

```powershell
claude sessions list
```

读取 `~/.claude/history.jsonl`，按时间倒序显示所有会话：

```
[1] sessionId | 项目目录 | 时间 | 首条消息摘要
[2] ...
```

### 查看会话详情

```powershell
claude --resume <session_id> --print "summary()"
```

### 新建单轮会话

```powershell
claude -p "<指令>" --output-format json
```

### 恢复历史会话（多轮对话）

```powershell
claude --resume <session_id>
```

多轮模式下，每次输入会延续上下文，适合持续迭代任务。

---

## 完整工作流

### 第一步：列出会话

丑丑虾执行 `claude sessions list`，展示会话列表给用户选择。

### 第二步：用户选择会话

用户说"我要用第3个"或"用 session_id 是 xxx 的"。

### 第三步：进入多轮对话

丑丑虾用 `claude --resume <session_id>` 恢复会话，模型有完整上下文。

### 第四步：持续传话

- **透传模式**：用户说什么，丑丑虾直接把那句话发给 CC
- **优化模式**：丑丑虾先完善需求，再发给 CC

**CC 的输出**：`不压缩、不改写、完整吐给用户`。

---

## Session ID 管理

Session ID 格式：`87c7951e-bbf7-43cf-885e-5176e3ef87ba`（UUID v4，36字符）

**已知会话**：

| Session ID | 简介 |
|-----------|------|
| `87c7951e-bbf7-43cf-885e-5176e3ef87ba` | 虾工作台 v2-test（fallback 模型配置） |

**获取方式**：从 `claude sessions list` 输出或 `~/.claude/history.jsonl` 的 `sessionId` 字段读取。

---

## Usage Logging (Auto-injected)

每次触发后追加记录到 `~/.openclaw/skill-logs/claude-session-relay/log.md`。

```markdown
## [YYYY-MM-DD HH:mm:ss]
- **User Request**: <用户请求>
- **Action**: <执行的操作>
- **Result**: <结果>
```

```bash
mkdir -p ~/.openclaw/skill-logs/claude-session-relay
echo "## [$(date '+%Y-%m-%d %H:%M:%S')]" >> ~/.openclaw/skill-logs/claude-session-relay/log.md
echo "- **User Request**: <请求>" >> ~/.openclaw/skill-logs/claude-session-relay/log.md
echo "- **Action**: <操作>" >> ~/.openclaw/skill-logs/claude-session-relay/log.md
echo "- **Result**: <结果>" >> ~/.openclaw/skill-logs/claude-session-relay/log.md
echo "" >> ~/.openclaw/skill-logs/claude-session-relay/log.md
```
