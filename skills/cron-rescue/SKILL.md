---
name: cron-rescue
description: |
  Cron 定时任务巡检与救火。自动检查任务执行状态，发现未完成的任务后从断点继续执行，确保关键产出完成。
  **Use this skill when:**
  (1) 用户要求检查定时任务状态（"cron检查"、"看看定时任务"、"巡检cron"）
  (2) 用户发现推送异常，要求排查（"6点半的推送怎么没收到"、"某个任务没完成"）
  (3) 用户要求深度分析某个 cron 任务的执行过程（"分析一下 XXX 怎么失败的"）
  (4) 定时触发：每天 08:00 自动巡检昨日所有任务
  (5) 用户说"cron-rescue"或"救火"
  
  **Keywords:** cron检查, 定时任务, cron诊断, cron巡检, 救火, 任务未完成, 推送异常, 定时任务失败
author: 乖乖虾
version: 1.2.0 (深度诊断 + 精确定位)
---

# Cron Rescue

Cron 定时任务巡检与救火。发现异常 → 从断点继续 → 完成关键产出。

## 核心原则

- **救火优先** — 发现没干完的任务，先推进完成，再汇报
- **不重复** — 利用已完成的成果，从断点接续，不重头来过
- **简明巡检，深度诊断** — 批量检查所有任务时只看表面状态；用户点名分析某一个任务时，直接深度诊断，不经过快速巡检。

## 工作模式

### 模式 A：快速巡检 + 救火（默认）

读取 `~/.openclaw/cron/jobs.json`，检查近 24 小时执行过的所有任务。

**Step 1: 构建状态面板**

```javascript
const jobsPath = 'C:/Users/44452/.openclaw/cron/jobs.json';
const jobs = JSON.parse(fs.readFileSync(jobsPath, 'utf-8')).jobs;
const now = Date.now();
const dayAgo = now - 24 * 60 * 60 * 1000;

// 筛选近24小时执行过的 enabled 任务
const recentJobs = jobs.filter(j => {
  if (!j.enabled) return false;
  const lastRun = j.state?.lastRunAtMs;
  return lastRun && lastRun > dayAgo;
});
```

**Step 2: 状态判断（基于 jobs.json 表面数据）**

| 状态 | 判断规则 |
|------|---------|
| ✅ 正常 | `lastRunStatus: ok` AND `lastDelivered: true` AND `consecutiveErrors: 0` |
| ⚠️ 疑似假成功 | `lastRunStatus: ok` 但 `lastDelivered: false` |
| ❌ 失败 | `lastRunStatus: error` OR `consecutiveErrors > 0` |
| ⚠️ 投递异常 | `lastDeliveryStatus: unknown` 或 `not-delivered` |

**Step 3: 救火推进（核心动作）**

对每个异常任务：

1. **定位隔离会话** — 从 `lastRunAtMs` 换算日期，扫描 `chat-logs/{agentId}/{date}_*.jsonl`，首条消息匹配 `[cron:{jobId}]`
2. **读取完整会话** — 用 `scripts/session-analyzer.js` 解析 JSONL，提取时间轴、工具调用、断点位置
3. **判断断点** — 最后一步做了什么？下一步该做什么？
4. **继续执行** — 在当前会话中，从断点接续完成剩余步骤
5. **确认完成** — 检查关键产出是否已生成（文件、多维表更新、推送）

**Step 4: 输出简报**

直接发送给用户，格式：

```
🚒 Cron 救火简报 (YYYY-MM-DD)
━━━━━━━━━━━━━━━━━━━━━

📋 状态总览
  昨日执行: X个 | ✅正常: X | ⚠️疑似: X | ❌失败: X | 🔧已救火: X

✅ 正常执行 (X个)
  任务名 | agent | 耗时 | 投递状态

🔧 已救火 (X个)
  任务名 → 断点位置 → 已完成内容 → ✅完成

⚠️ 无法自动修复 (X个)
  任务名 | 问题 | 建议操作
```

### 模式 B：深度诊断（单任务分析）

用户点名分析某一个 cron 任务时，直接使用本模式（不经过模式 A）：

**Step 1: 完整会话分析**

运行 `scripts/session-analyzer.js` 输出完整时间轴：

```bash
node ~/.openclaw/skills/cron-rescue/scripts/session-analyzer.js <会话文件路径>
```

**Step 2: 根因定位**

重点检查：
- 每轮 thinking 内容（模型在想什么）
- 工具调用是否成功
- 是否有 idle timeout、typo、RecordIdNotFound 等错误
- thinking 是否泄露到正文输出
- 模型是否在某一步卡死

**Step 3: 输出诊断报告**

```
🔍 深度诊断报告：{任务名}
━━━━━━━━━━━━━━━━━━━━━

📅 执行时间轴
  [时间] 事件 → 结果

🎯 根因
  问题定位：XXX
  触发条件：XXX

🔧 修复动作
  已完成：XXX
  
📊 执行数据
  Token 消耗: input=XX, output=XX, total=XX
  工具调用: XX次
  思考轮次: XX次

## 诊断报告持久化

深度诊断完成后，必须生成结构化 Markdown 报告并保存。

**存储目录**：`~/.openclaw/cron/diagnostics/`
- 不存在时自动创建
- 目录用于归档所有诊断报告

**文件命名**：`YYYY-MM-DD_任务名_问题简述.md`
- 任务名提取自 cron job name（去掉空格和特殊字符）
- 问题简述用 2-4 个关键词概括根因
- 示例：`2026-04-15_朋友圈分析_超时排查.md`

**报告模板**：

```markdown
# 诊断报告：{任务名}

- **日期**：YYYY-MM-DD
- **诊断人**：{agent 名称}
- **触发原因**：{用户反馈 | 自动巡检 | 定期审查}
- **会话来源**：{chat-logs 路径或 session ID}

## 问题摘要
一句话描述问题现象。

## 执行时间轴
| 时间 | 事件 | 结果 |
|------|------|------|

## 根因分析
问题定位与触发条件。

## 问题分类
- [ ] 编码问题（字符编码、路径乱码等）
- [ ] 超时问题（操作超时、idle timeout 等）
- [ ] 配置问题（参数错误、权限缺失等）
- [ ] 模型行为问题（thinking 泄露、假成功等）
- [ ] 技能设计问题（流程缺陷、断点缺失等）
- [ ] 其他：____

## 修复建议
| 优先级 | 动作 | 状态 |
|--------|------|------|

## 经验教训
可复用的教训，供其他 cron 任务参考。
```

**更新索引**：每次生成报告后，同步更新 `~/.openclaw/cron/diagnostics/_summary.md`。
按问题分类汇总出现次数，每条关联到具体报告文件。

## 隔离会话定位

**定位流程（精确匹配 jobId）：**

读取 `~/.openclaw/cron/jobs.json`，根据用户线索（任务名关键词、大致时间）匹配目标 job，获取 `jobId`。`lastRunAtMs` 仅作参考，不作为匹配依据。

扫描 `agents/{agentId}/sessions/` 目录下的 session 文件，逐一读取首条 user 消息，提取 `[cron:{jobId}]` 前缀，与目标 jobId 精确匹配（字符串完全一致）。用户提供的"大致时间"仅用于缩小扫描范围，不作为匹配依据。

如目标 job 当天有多个 session（Gateway 宕机后补跑），选择 `state.lastRunAtMs` 最接近的那个。

**⚠️ 禁止行为：** 仅凭时间相近就认定是目标会话。必须先匹配 jobId，再验证时间。

**时间换算（用于缩小扫描范围）：**
```javascript
const runTime = new Date(lastRunAtMs);  // UTC
const dateStr = runTime.toLocaleDateString('sv-SE', { timeZone: 'Asia/Shanghai' });
// 例: 2026-04-12
```

**会话文件优先级：**
- **深度诊断（模式 B）：** 读取 `agents/{agentId}/sessions/{session-id}.jsonl`（完整会话，含 toolUse、toolResult、thinking）
- **快速巡检（模式 A）：** 读取 `chat-logs/{agentId}/{dateStr}_*.jsonl`（轻量摘要，仅 text 字段）

**降级逻辑：** session 文件不存在时（已被自动清理），降级读取 `chat-logs/summaries/{agentId}_{dateStr}_merged.md` 或 `chat-logs/{agentId}/{dateStr}_*.jsonl`。

## 常见故障模式

| 故障 | 症状 | 修复策略 |
|------|------|---------|
| idle timeout | `prompt-error: LLM idle timeout (60s)` | 读取已完成部分，从断点继续 |
| 假成功 | `lastRunStatus: ok` 但无实质产出 | 重头执行或从已有数据接续 |
| 投递失败 | `lastDelivered: false` | 检查产出是否存在，重新推送 |
| RecordIdNotFound | 多维表更新失败 | 检查 record_id 是否正确 |
| 连续错误 | `consecutiveErrors > 0` | 读最近一次会话日志，定位根因 |

## 历史诊断回顾

发现异常任务时，先检查 `~/.openclaw/cron/diagnostics/` 是否有同类问题的历史报告。

**检索规则**：
1. 读取 `_summary.md` 索引，按问题分类查找匹配项
2. 如果同类型问题已出现 ≥2 次，优先应用历史修复建议
3. 共性问题（编码/超时反复出现）应系统性解决，而非逐次救火

---

## 隔离会话注意事项

| 工具 | 是否可用 | 替代方案 |
|------|---------|---------|
| `feishu_task_task` | ❌ 需要 OAuth | 使用 `feishu_bitable_app_table_record` |
| `feishu_bitable_app_table_record` | ✅ | 直接使用 |
| `sessions_history` | ❌ 只能读当前会话树 | 直接读取 chat-logs 文件 |
| `read` (文件) | ✅ | 推荐使用 |

## 辅助脚本

### session-analyzer.js

解析隔离会话 JSONL 文件，输出完整时间轴。

```bash
node ~/.openclaw/skills/cron-rescue/scripts/session-analyzer.js <session-file.jsonl> [--detail]
```

参数：
- `<session-file.jsonl>` — 隔离会话文件路径（必填）
- `--detail` — 输出详细 thinking 内容（可选）

输出内容：
- 每轮交互的时间戳、类型、工具调用、token 消耗
- thinking 摘要（--detail 时输出完整内容）
- 工具调用结果（成功/失败）
- 最终错误（如有）

## Usage Logging (Auto-injected)

每次触发后追加记录到 `~/.openclaw/skill-logs/cron-rescue/log.md`。

**格式：**
```markdown
## [YYYY-MM-DD HH:mm:ss]
- **User Request**: <请求内容>
- **Mode**: <A-巡检/C-深度诊断>
- **Jobs Checked**: <检查的任务列表>
- **Rescue Actions**: <救火动作>
- **Result**: <最终结果>
```

**实现：**
```bash
mkdir -p ~/.openclaw/skill-logs/cron-rescue
echo "## [$(date '+%Y-%m-%d %H:%M:%S')]" >> ~/.openclaw/skill-logs/cron-rescue/log.md
echo "- **User Request**: <请求>" >> ~/.openclaw/skill-logs/cron-rescue/log.md
echo "- **Mode**: <模式>" >> ~/.openclaw/skill-logs/cron-rescue/log.md
echo "- **Result**: <结果>" >> ~/.openclaw/skill-logs/cron-rescue/log.md
echo "" >> ~/.openclaw/skill-logs/cron-rescue/log.md
```
