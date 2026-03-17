---
name: skill-auditor
description: 技能审计员，评估skill质量并生成报告。触发条件：用户说"评估skill"、"检查skill"、"审计skill"、"skill体检"、"全面评估skill"，或定时任务触发。评估维度：规范性等级（1-5星）、规范性评价、功能可用性、累计调用次数。
---

# Skill Auditor（技能审计员）

评估skill质量，发现僵尸skill，保障技能生态健康。

## 触发条件

- 用户说："评估skill"、"检查skill"、"审计skill"、"skill体检"、"全面评估skill"
- 定时任务触发（每周执行）
- 新建skill后手动触发评估

## 评估维度（5个）

### 1. 规范性等级

**评分标准**（1-5星）：

| 星级 | 标准 |
|------|------|
| ⭐ | 仅基本可用，问题较多 |
| ⭐⭐ | 触发条件不清晰，文档简陋 |
| ⭐⭐⭐ | 合格，有改进空间 |
| ⭐⭐⭐⭐ | 良好，文档完整清晰 |
| ⭐⭐⭐⭐⭐ | 优秀，规范且详细 |

**检查项**：
- 是否有完整frontmatter（name, description）
- 触发条件是否清晰明确
- 文档内容是否详细

### 2. 规范性评价

记录具体问题：
- 缺frontmatter
- 缺name/description
- 触发条件不清晰
- 文档质量不佳
- 无使用示例

### 3. 功能可用性

**状态**：
- **正常**：可直接运行
- **无效**：无法运行（缺依赖/缺配置/报错）

**测试方法**：
1. 读取skill的触发条件和描述
2. 根据适用情形生成测试输入
3. 尝试调用skill
4. 判断结果

### 4. 安全评分

**基础检测**（使用 security-scanner.js）：

调用独立扫描器：
```bash
node ~/.openclaw/skills/skill-auditor/security-scanner.js <skill-path>
```

返回 JSON：
```json
{
  "risk_level": "safe|medium|high|critical",
  "score": 0-100,
  "issues": [...]
}
```

**风险等级**：
- 🟢 safe (0-4分) - 无明显风险
- 🟡 medium (5-9分) - 有潜在风险
- 🟠 high (10-19分) - 有较大风险
- 🔴 critical (≥20分) - 严重风险

**检测范围**：
- 任意代码执行 (eval, Function)
- 命令注入 (exec, spawn)
- 数据外泄 (env + fetch)
- 危险删除 (rm -rf)
- 远程脚本执行 (curl | bash)
- 非白名单域名请求

**局限性说明**：
- ⚠️ 基于正则匹配,可能被混淆绕过
- ⚠️ 可能存在误报
- ⚠️ 仅作初筛,不能对抗专业攻击

### 5. 累计调用次数

从日志文件统计：
- 读取 `~/.openclaw/skill-logs/<skill-name>/log.md`
- 统计调用记录数量

## 评估逻辑

```
启动评估
    ↓
读取多维表 "龙虾养成计划 - Skill评估表-正式版"
    ↓
遍历所有skill
    ↓
判断：版本号是否变化 or 未评估过？
    ↓
├─ 是 → 全面评估（规范性等级+规范性评价+功能可用性+调用次数）
│
└─ 否 → 仅更新累计调用次数
    ↓
写入多维表
    ↓
Bot推送评估报告
```

## 多维表配置

**表信息**：
- App Token: `Ms0Sbx75jahr5QsX4vQc8rnxn2f`
- Table ID: `tbl3gLHsyjGGl7iN`
- 表名：Skill评估表-正式版

**字段映射**：

| 评估维度 | 多维表字段 | 示例 |
|----------|-----------|------|
| Skill名称 | Skill名称 | skill-auditor |
| 规范性等级 | 规范性等级 | ⭐⭐⭐⭐ |
| 规范性评价 | 规范性评价 | 文档结构清晰，触发条件明确 |
| 功能可用性 | 功能可用性 | 正常/无效 |
| 安全评分 | 安全评分 | 0 (safe) |
| 安全风险 | 安全风险 | 无风险 / 检测到3个高危项 |
| 版本号 | 版本号 | 1.0.0 |
| 累计调用次数 | 累计调用次数 | 2 |
| 分类 | 分类 | 技能管理 |

**提交示例**：

```javascript
// 更新评估结果到多维表
await feishu_bitable_app_table_record({
  action: "update",
  app_token: "Ms0Sbx75jahr5QsX4vQc8rnxn2f",
  table_id: "tbl3gLHsyjGGl7iN",
  record_id: recordId,
  fields: {
    "规范性等级": "⭐⭐⭐⭐",
    "规范性评价": "文档结构清晰，触发条件明确",
    "功能可用性": "正常",
    "安全评分": 0,
    "安全风险": "无风险",
    "版本号": "1.0.0",
    "累计调用次数": callCount
  }
});
```

## 评估报告格式

**Bot推送内容**：

```
📊 Skill评估报告 [YYYY-MM-DD]

本次评估：X个skill
├─ 全面评估：X个（新增/更新）
│   ├─ skill-a ⭐⭐⭐⭐ 正常 🟢safe
│   └─ skill-b ⭐⭐⭐ 无效 🔴critical（检测到3个高危项）
│
├─ 快速更新：X个
│   └─ skill-c 调用12次
│
└─ 问题skill：X个
    ├─ skill-d ⭐⭐ 无效
    └─ skill-e 🔴critical 安全风险
```

## 执行步骤

### Step 1: 读取多维表

获取所有skill记录：
- 调用 `feishu_bitable_app_table_record` action=list
- 读取所有记录

### Step 2: 遍历评估

对每个skill：

1. 读取SKILL.md内容
2. 检查frontmatter完整性
3. 评估文档质量
4. 测试功能可用性
5. **执行安全扫描**（调用 security-scanner.js）
6. 统计调用次数

### Step 3: 写入多维表

调用 `feishu_bitable_app_table_record` action=update

### Step 4: 推送报告

通过Bot发送评估报告给用户。

## 规范性检查细则

### 必须项（缺失扣2星）

- `name` - 技能名称
- `description` - 技能描述（含触发条件）

### 推荐项（缺失扣1星）

- `author` - 作者信息
- `version` - 版本号
- 触发条件说明（在description或body中）
- 使用示例

### 文档质量

- 内容充实、结构清晰 → 加1星
- 有使用示例 → 加0.5星
- 过于简陋（<100字） → 减1星

## 功能测试细则

### 测试输入生成

根据skill描述自动生成测试输入：

| skill | description | 测试输入 |
|-------|-------------|----------|
| weather | "用户说天气时触发" | "今天北京天气怎么样？" |
| github | "查看PR状态" | "帮我看看PR #123的状态" |

### 测试判断

- 执行成功 → 正常
- 报错/无响应 → 无效
- 缺依赖/API Key → 无效（备注原因）

## Usage Logging (Final Step)

Every time this skill is triggered, append a record to `log.md`:

```bash
echo "## [$(date '+%Y-%m-%d %H:%M:%S')]" >> ~/.openclaw/skill-logs/skill-auditor/log.md
echo "- **Trigger**: <评估类型: 全面评估/快速更新/单点测试>" >> ~/.openclaw/skill-logs/skill-auditor/log.md
echo "- **Skills Evaluated**: <skill列表>" >> ~/.openclaw/skill-logs/skill-auditor/log.md
echo "" >> ~/.openclaw/skill-logs/skill-auditor/log.md
```
