---
name: skill-polisher
description: |
  技能优化专家。当已有技能需要迭代优化时触发。
  用于：(1) 诊断技能问题，(2) 提出修改方案（不超过 3 条），(3) 精确增删改查，(4) 测试验证。
  不用于：从零创建新技能（用 skill-creator）、技能打包分发、技能故障排查。
  触发场景：用户说"优化 xxx 技能"、"改进 xxx"、"xxx 技能有问题"、"迭代 xxx skill"。
version: 3.0.0 (沟通规范 + 编写规范 + 变更审计)
---

# Skill Polisher - 技能优化专家

## 核心原则（全局适用）

| 原则 | 检查时机 | 说明 |
|------|---------|------|
| **奥卡姆剃刀** | Step 3/5 | 必要最小化，每次修改≤3 处/50 行 |
| **避免过拟合** | Step 2/6 | 泛化为"[企业名称]"仍成立，不硬编码个例 |
| **目标一致性** | Step 2 | 服务于技能初始目标，不偏离核心用途 |

---

## 6 步迭代流程

### Step 1: 问题诊断

**目标：** 理解是个例问题还是共性缺陷

**动作：**
1. 读取用户反馈的具体案例
2. 询问：这个问题出现几次？在什么场景下？
3. 判断：是个例（特定数据/配置）还是共性（技能设计缺陷）

**输出：** 问题描述 + 发生场景

**示例：**
```
问题：customer-research 搜索到多个同名公司时没有确认话术
场景：搜索"清格科技"返回北京/上海/深圳 3 家公司
类型：共性缺陷（缺少多公司确认机制）
```

---

### Step 2: 原则检查

**目标：** 用三原则分析问题根因

**动作：** 读取 `references/iteration-principles.md`，对照检查

**检查清单：**
- [ ] 是否违反奥卡姆剃刀？（过度复杂/冗余）
- [ ] 是否过拟合个例？（硬编码特定数据）
- [ ] 是否偏离目标？（添加了非核心功能）

**输出：** 问题分析报告

---

### Step 3: 备份（讨论前必须完成）⭐

**目标：** 确保可回滚（在任何修改之前）

**动作：**
1. 手动备份 SKILL.md 文件（如无自动脚本）
2. 验证备份文件是否存在
3. 记录备份文件名

**备份命令（PowerShell）：**
```powershell
$backupName = "SKILL.md.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item "<skill-path>\SKILL.md" "<skill-path>\$backupName"
```

**强制检查清单**（必须逐项打勾，否则禁止进入 Step 4）：
- [ ] 备份文件已生成（检查文件是否存在）
- [ ] 备份文件名已记录（格式：`SKILL.md.backup.YYYYMMDD-HHMMSS`）
- [ ] 备份文件大小 > 0（非空文件）

**输出：** 备份文件名（如 `SKILL.md.backup.20260405-111716`）

**⚠️ 未备份禁止进入 Step 4（提出方案）！**

---

### Step 4: 提出修改方案（等待确认）⭐

**目标：** 精确修改方案（≤3 条）

**动作：**
1. 输出完整技能文件提纲，定位修改段落在第几章第几节
2. 设计修改方案，每条明确：位置 + 原内容 + 新内容
3. 使用下方规定的呈现格式
4. **等待用户确认**后再执行

---

**呈现格式规则（禁止使用 Markdown 表格）：**

**规则 A — 局部修改（段落内少量增删）：**
用论文查重式。在同一段内用删除线标出要删除的内容，用 `+` 前缀标出新增内容。让用户一眼看出改了什么。

示例：
```
原文：~~过滤隔离~~ 提取「任务视角」部分
```

**规则 B — 整段替换（整体换掉）：**
用两个代码块并列，第一个标"原文"，第二个标"修改后"。

**规则 C — 脚本/代码级内容：**
不贴完整代码。只讲方向和原则：哪段脚本要替换、换成什么逻辑、输入输出是什么。用户审核在文本级别，代码细节由 AI 自行实现。

---

**确认话术模板**（必须使用）：
```
张总，修改方案共 X 条：
1. ...
2. ...
3. ...

请确认是否执行？回复"确认"或"可以"后我立即修改。
```

**⚠️ 强制检查**：
- [ ] 是否已输出完整提纲并定位到具体段落？
- [ ] 是否已使用规定的呈现格式？
- [ ] 是否逐字展示了文本级修改内容？
- [ ] 是否已等待用户确认？（检查下一条用户消息）
- [ ] 用户是否明确回复"确认"或"可以"？

**输出：** 修改方案（等待确认）

**未确认禁止执行 Step 5！**

---

### Step 5: 执行修改（检查：用户确认 + 备份已完成）⭐

**⚠️ 前置条件检查**（必须全部满足，否则禁止执行）：

**检查清单**：
- [ ] 用户已明确回复"确认"或"可以"（Step 4 的确认话术）
- [ ] 备份文件已生成（文件名：`________`，Step 3 已完成）
- [ ] 修改方案 ≤3 条（奥卡姆剃刀原则）

**伪代码检查**：
```javascript
if (!userConfirmed) {
    throw Error("❌ 用户未确认，禁止执行修改");
}
if (!backupFileExists) {
    throw Error("❌ 备份文件不存在，禁止执行修改");
}
```

**全部检查通过后，才能执行修改！**

---

**目标：** 精确增删改查

**动作：**
1. 使用 `edit` 工具进行精确替换
2. 每次修改后验证文件完整性
3. 更新 `version`（major.minor.patch）

---

**SKILL.md 编写规范（来自 skill-creator 核心原则）：**

**1. 起始句式（强制 · 写入时遵守）**

只允许使用以下句式开头：
- ✅ 祈使句：`执行 X`、`读取...`、`如果 X 则 Y`
- ✅ 定义句：`X 是...`、`X 包含...`
- ✅ 条件句：`当 X 时`、`如果 X`、`前置条件：...`

禁止使用：
- ❌ 讨论句：`建议...`、`这样改的好处是...`、`因为...所以...`
- ❌ 解释句：`这段话的目的是...`、`我们这样设计是因为...`
- ❌ 历史句：`之前的问题是...`、`修改前...`

---

**2. 段落结构模板（强制 · 写入时遵守）**

每个功能段落必须包含以下三要素（顺序可调整）：

```
**目的/触发条件**：什么时候用这个功能
**执行步骤**：具体怎么做（代码/脚本/命令）
**输出/结果**：做完后产生什么
```

示例：
```markdown
### 读取会话摘要

**触发**：定时任务消息包含 `[cron:xxx session-summary]`

**执行**：
```powershell
$summaries = Get-ChildItem "chat-logs/summaries/*_${date}_*.md"
```

**输出**：`scratchpad/task-summary-${date}.md`
```

---

**3. 内容分类（强制 · 只允许写入以下三类）**

- **做什么**：目标、触发条件、判断标准、禁止操作
- **怎么做**：执行步骤、代码/脚本、输出路径、工具调用
- **什么条件下做**：前置条件、降级逻辑、错误处理

不属于以上三类的文字一律不写。

---

**4. 写入后自检（强制 · 二元判断）**

逐段问三个问题，答案必须是"是"：
- [ ] 这段的起始句是祈使句/定义句/条件句吗？（不是 → 重写）
- [ ] 这段属于"做什么/怎么做/什么条件下做"之一吗？（不是 → 删除）
- [ ] 这段面向未来执行还是面向过去讨论？（过去 → 删除）

---

**版本规范：**
- **Major** (X.0.0): 突破性改动/重构
- **Minor** (x.X.0): 新功能/大优化
- **Patch** (x.x.X): Bug 修复/小调整

**输出：** 修改完成 + 新版本号

---

### Step 6: 变更审计（回头看）⭐ 新增

**目标：** 检查修改是否只在约定范围内，防止越界修改

**为什么要这一步：** AI 修改技能时容易"顺手"优化未讨论的内容，导致技能面目全非。必须对照备份和修改议题做客观检查。

**动作：**
1. 创建一个隔离子会话（subagent），发送以下三样内容：
   - **A. 备份原文**（修改前的 Skill 全文）
   - **B. 修改后全文**（修改后的 Skill 全文）
   - **C. 修改议题**（用户确认过的修改清单和意图）
2. 让子会话逐条对比并回答：
   - 约定的修改是否都执行了？有无遗漏？
   - 是否有约定之外的修改（多改/多删）？
   - 修改后的 Skill 是否符合 SKILL.md 编写规范？
3. 输出审计报告

**审计结果处理：**
- ✅ 审计通过 → 进入 Step 7（测试验证）
- ❌ 发现问题 → 向用户报告具体问题，回滚到备份版本，重新执行 Step 5

**实现方式：**
```
sessions_spawn({
  task: "你是 Skill 变更审计员。请对比以下三份材料，审计 Skill 修改是否符合约定：\n\n=== 备份原文 ===\n{backup_content}\n\n=== 修改后全文 ===\n{modified_content}\n\n=== 用户确认的修改议题 ===\n{change_proposal}\n\n请逐条回答：\n1. 约定修改是否都执行了？\n2. 是否有约定外的内容被修改？（如有，列出具体位置和原文/新文）\n3. 修改后的 Skill 是否仍保持规范？\n\n输出格式：审计通过/不通过 + 具体问题列表",
  mode: "run",
  cleanup: "delete"
})
```

**输出：** 审计报告（通过/不通过 + 问题列表）

---

### Step 7: 测试验证（原 Step 6，重编号）

**目标：** 验证修改有效性

**动作：**
1. 执行 `scripts/test_skill.py <skill-path>`
2. 或手动运行测试案例（见 `references/test-case-patterns.md`）
3. 记录测试结果

**输出：** 测试报告（通过/失败 + 原因）

---

## 流程对比（修改前后）

| 阶段 | 老流程 | 新流程 | 改进点 |
|------|-------|-------|--------|
| 诊断 | Step 1 | Step 1 | - |
| 原则检查 | Step 2 | Step 2 | - |
| **备份** | Step 4（讨论后） | **Step 3（讨论前）** | ⭐ 提前到讨论前 |
| 提出方案 | Step 3 | Step 4 | 增加沟通格式规范 |
| 修改 | Step 5 | Step 5 | ⭐ 增加 SKILL.md 编写规范 |
| **变更审计** | 无 | **Step 6（新增）** | ⭐ 隔离会话回头看 |
| 测试 | Step 6 | Step 7 | 重编号 |

---

## Bundled Resources

| 资源 | 用途 | 何时使用 |
|------|------|---------|
| `scripts/backup_skill.py` | 自动备份 SKILL.md | Step 3（备份） |
| `scripts/test_skill.py` | 运行技能测试 | Step 7（测试验证） |
| `references/iteration-principles.md` | 迭代原则详解 | Step 2（原则检查） |
| `references/test-case-patterns.md` | 测试案例类型库 | Step 7（测试验证） |
| `references/diff-format-guide.md` | 修改对照格式指南 | Step 4（提出方案） |

---

## 与 skill-creator 的分工

| 场景 | 使用技能 |
|------|---------|
| 从零创建新技能 | `skill-creator` |
| 已有技能迭代优化 | `skill-polisher`（本技能） |
| 技能打包分发 | `skill-creator`（package 命令） |
| 技能故障排查 | 手动调试（非本技能范围） |

---

## Usage Logging (Auto-injected)

Every time this skill is triggered, append a usage record to `~/.openclaw/skill-logs/skill-polisher/log.md`.

**Log format:**

```markdown
## [YYYY-MM-DD HH:mm:ss]
- **User Request**: <what user asked>
- **Action**: diagnose | propose | modify | test
- **Target Skill**: <skill name>
- **Result**: <outcome>
```

**Implementation:**

```bash
mkdir -p ~/.openclaw/skill-logs/skill-polisher
echo "## [$(date '+%Y-%m-%d %H:%M:%S')]" >> ~/.openclaw/skill-logs/skill-polisher/log.md
echo "- **User Request**: <user's request>" >> ~/.openclaw/skill-logs/skill-polisher/log.md
echo "- **Action**: <action>" >> ~/.openclaw/skill-logs/skill-polisher/log.md
echo "- **Target Skill**: <skill name>" >> ~/.openclaw/skill-logs/skill-polisher/log.md
echo "- **Result**: <result>" >> ~/.openclaw/skill-logs/skill-polisher/log.md
echo "" >> ~/.openclaw/skill-logs/skill-polisher/log.md
```
