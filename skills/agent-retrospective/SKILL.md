---
name: agent-retrospective
description: |
  龙虾每日体检 + 问题处置。扫描 sessions，精准诊断，沉淀病例记录，
  治病救人。体检报告存 evolution，问题解决后更新 pitfalls。
triggers:
  - 每日体检
  - 龙虾进化
  - 健康检查
  - 龙虾复盘
  - 龙虾运营体检
version: 5.2.0
---

# 龙虾体检 · agent-retrospective v5

## 核心原则

- **体检与治病分离**：先诊断、后治疗，不能跳步
- **Agent 自主判断**：扫描后由 Agent 读文件深度分析，不套用固定坑编号
- **坚实的回溯基础**：所有问题在解决前先写体检报告，解决后补充结论
- **Evolution 跟着结论走**：体检时写疾病记录（含问题分析），治病后更新 pitfalls（含结果）

---

## 体检（3步）

### Step 1：全身扫描

**执行**：
```bash
python scripts/health_scan.py --days 1 --date {target_date}
python scripts/scan_session_errors.py {agent} {target_date}
```

**职责**：只负责"找可疑文件"，不做任何判断

**输出**：
- `scripts/scan_result.json`：可疑文件列表 + 原始片段
- 打印摘要：扫描了多少 session/chatlog，多少个含可疑片段

**扫描逻辑**：
- 按时间范围扫 `sessions/` + `chat-logs/main/`
- 用关键词宽泛匹配（error/failed/timeout/失败/异常等）
- 每个可疑文件提取最多3段上下文
- 有片段的文件排在前面

---

### Step 2：精准诊断

**输入**：`scripts/scan_result.json`

**职责**：Agent 读取所有可疑文件，用自己的思辨能力判断：
- 这是什么问题？（新/老）
- 严重程度？（🔴卡死 / 🟡浪费）
- 是否需要治疗？

**不看坑编号**，不套 P001-P005，用自己的理解分析

---

### Step 3：病例记录（体检报告）

**职责**：将 Step 2 的分析结果沉淀到本地

**输出文件**：`evolution/体检报告_YYYY-MM-DD.md`

**报告格式**：
```markdown
# 龙虾体检报告 · YYYY-MM-DD

## 统计总览
- 扫描 session：N 个
- 含可疑片段：X 个
- 问题总数：Y 个

## 老问题追踪

| 坑 | 本期命中 | vs上期 | 趋势 |
|----|---------|-------|------|
| P001 PowerShell编码 | N个session | N→N | 持平/恶化/改善 |

## 运行问题记录（扫描脚本产出）

直接读取 `python scripts/scan_session_errors.py {agent} {target_date}` 的输出，填入下方：

（扫描脚本会自动输出 Markdown 表格，直接粘贴）

运行问题记录：N个（🔴X / 🟡Y / ⚠️Z）
数据来源：`agents/{agent}/sessions/sessions.json` → session 文件扫描
涉及 session：X 个

## 新问题清单

| # | 问题描述 | 特征 | 严重度 | 状态 |
|---|---------|------|-------|------|
| N1 | xxx | yyy | 🔴/🟡 | 待治疗 |

## 处置计划

| 问题 | 处置方式 | 负责人 |
|------|---------|--------|
| P001 | 方案已验证 | 自动 |
| N1 | 独立解决/讨论 | Agent |

---

### Evolution 文件更新时机

| 时机 | 写哪个文件 | 内容 |
|------|----------|------|
| Step 3 完成后 | `evolution/diseases.md` | 追加本次新发现的问题（已有编号的更新状态） |
| Step 3 完成后 | `evolution/pitfalls.md` | 追加已有药方的问题治疗结果 |
| Step 3 完成后 | `evolution/体检报告_YYYY-MM-DD.md` | 完整分析报告 |
| Step 3 完成后 | `evolution/scan_raw/{agent}_YYYY-MM-DD.txt` | 原始扫描结果（由 scan_session_errors.py 直接保存） |
| 治疗后 | `treatments.md` | 追加本次治疗结果 |

---

## 治病（针对每个问题）

### 可独立解决的问题

**阶段 A**：SubAgent1 制定解决方案
```
输入：问题描述 + 上下文片段
输出：
  1. 解决方案（2-3步）
  2. 测试案例（触发条件 + 执行步骤 + 预期结果）
```

**阶段 B**：SubAgent2 执行测试验证
```
输入：测试案例
输出：
  - 有效：问题消失 or 修复确认
  - 无效：问题仍存在
```

**有效 → 写入 pitfalls.md + 更新 treatments.md**
**无效 → 推送讨论

### 屡教不改的老问题

单独分析：
- 连续出现几次了？
- 之前尝试过什么方案？
- 为什么无效？
- 需要换什么思路？

---

## 边界约束

| 只能写/更新 | 绝对不能动 |
|------------|----------|
| `evolution/体检报告_YYYY-MM-DD.md` | Skill 文件本身 |
| `evolution/pitfalls.md` | Cron 配置 |
| `evolution/diseases.md` | openclaw.json |
| `evolution/scan_raw/` | - |

**说明**：`observations.md`（已简化，仅含验证规则）和 `treatments.md`（已废弃，内容并入 pitfalls.md）不再由体检流程写入。

---

## 执行示例

```
用户：执行龙虾体检

Agent：
  Step 1：python health_scan.py --days 1 --date 2026-04-20
  Step 2：读取 scan_result.json + 可疑文件，深度分析
  Step 3：写体检报告 + 更新 diseases.md + pitfalls（如有新药方）
  推送：体检报告摘要

用户：治疗这些问题

Agent：
  对每个问题启动 SubAgent 循环
  有效 → 写 pitfalls.md
  无效 → 推送讨论
```
