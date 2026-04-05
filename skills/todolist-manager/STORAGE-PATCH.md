# Todolist Manager - 持久化存储补丁

**日期：** 2026-03-21  
**原因：** 定时任务推送可能失败，需要先存储再推送

---

## 统一存储位置

**所有临时文件统一存储到：**
```
C:\Users\44452\.openclaw\agents\guaiguaixia\workspace\scratchpad\
```

---

## 新增代码

在每日复盘逻辑的末尾，添加：

```javascript
// ============================================================
// 🆕 持久化存储：先存储，再推送
// ============================================================

/**
 * 将每日复盘报告保存到本地文件
 * @param {string} report - 生成的复盘报告（Markdown 格式）
 */
function persistDailyReport(report) {
  const fs = require('fs')
  const path = require('path')
  
  // 生成文件名（按日期）
  const today = new Date().toISOString().split('T')[0]  // '2026-03-21'
  
  // 统一存储到工作区的 scratchpad 目录
  const reportPath = `C:\\Users\\44452\\.openclaw\\agents\\guaiguaixia\\workspace\\scratchpad\\daily-brief-${today}.md`
  
  // 确保目录存在
  const dir = path.dirname(reportPath)
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
    console.log(`📁 创建目录：${dir}`)
  }
  
  // 写入文件
  fs.writeFileSync(reportPath, report, 'utf-8')
  console.log(`✅ 每日复盘已保存：${reportPath}`)
  
  return reportPath
}

// ============================================================
// 使用示例（在每日复盘函数中）
// ============================================================

async function performDailyReview() {
  // 1. 读取多维表格，更新任务状态
  const tasks = await reviewTasks()
  
  // 2. 检测断线头
  const threads = await detectInterruptedThreads()
  
  // 3. 生成复盘报告
  const report = generateReport(tasks, threads)
  
  // 4. 🆕 持久化存储（先存储！）
  const savedPath = persistDailyReport(report)
  
  // 5. 然后再推送到飞书（推送失败也不影响已存储的结果）
  // 定时系统会自动推送这个返回值
  return report
}
```

---

## 报告格式

```markdown
# 每日复盘 - YYYY 年 MM 月 DD 日

**生成时间：** HH:MM
**执行 Agent：** guaiguaixia

---

## 【一、任务状态更新】

- 标记为待验收：X 项
- 发现逾期任务：Y 项

### 待验收任务
| 任务名称 | 原状态 | 新状态 |
|---------|-------|-------|
| [任务 1] | 进行中 | 待验收 (AI 提交) |

### 逾期任务
| 任务名称 | 截止日期 | 当前状态 |
|---------|---------|---------|
| [任务 2] | 2026-03-20 | 未启动 |

---

## 【二、断线头检测】

从昨日对话中发现 **N 个未完成事项**：

| # | 类型 | 任务 | 中断原因 |
|---|------|------|---------|
| 1 | 中断 | 实现飞书自动回复功能 | 缺密钥 |
| 2 | 未完成 | 迭代 Todolist Manager | - |
| 3 | 中断 | 部署新网站 | 报错 |

---

## 【三、今日待办】

（来自 todolist 中状态为"进行中"的任务）

| 优先级 | 任务名称 | 当前进展 |
|-------|---------|---------|
| P1 | [任务 1] | [进展描述] |
| P2 | [任务 2] | [进展描述] |

---

## 【四、推送状态】

- 飞书推送：✅ 成功 / ❌ 失败
- 本地存储：✅ 已完成

> 如推送失败，请查看此文件获取复盘内容。

---

*记录者：乖乖虾 🐢🦞*
```

---

## 所有定时任务存储位置（统一规范）

| 任务 | 存储路径 | 文件命名 |
|------|---------|---------|
| **每日复盘** | `scratchpad/daily-brief-YYYY-MM-DD.md` | Markdown |
| **日记** | `scratchpad/diary-YYYY-MM-DD.md` | Markdown |
| **Skill 雷达** | `scratchpad/skill-radar-YYYY-MM-DD.json` | JSON |
| **InStreet 学习** | `scratchpad/instreet-learn-YYYY-MM-DD.md` | Markdown |
| **工作简报** | `scratchpad/work-brief-YYYY-MM-DD.md` | Markdown |

**完整路径示例：**
```
C:\Users\44452\.openclaw\agents\guaiguaixia\workspace\scratchpad\
├── daily-brief-2026-03-21.md       # 每日复盘
├── diary-2026-03-21.md             # 日记
├── skill-radar-2026-03-21.json     # 雷达扫描
├── instreet-learn-2026-03-21.md    # InStreet 学习
└── work-brief-2026-03-21.md        # 工作简报
```

---

## 测试方法

1. 手动触发每日复盘：
   ```
   按照 <todolist-manager> 技能，执行"每日复盘"
   ```

2. 检查输出：
   - 控制台应打印：`✅ 每日复盘已保存：C:\Users\44452\.openclaw\agents\guaiguaixia\workspace\scratchpad\daily-brief-2026-03-21.md`
   - 飞书应收到推送

3. 验证文件：
   ```bash
   type C:\Users\44452\.openclaw\agents\guaiguaixia\workspace\scratchpad\daily-brief-2026-03-21.md
   ```

---

## 优势

1. **统一位置** - 所有临时文件在一个地方，方便查找
2. **推送失败也不丢数据** - 本地文件始终存在
3. **历史可追溯** - 每天的记录都保存，方便回顾
4. **调试方便** - 可以直接查看文件内容，不需要查 cron 日志

---

_补丁版本：1.1_
_应用日期：2026-03-21_
