---
name: morning-briefing
description: |
  定制个人早报推送。基于全网新闻聚合，根据用户兴趣领域智能筛选，生成个性化每日简报。
  支持科技/财经/AI/体育等多领域，可定时推送到飞书。
---

# 定制个人早报推送

一键生成专属早报！基于全网新闻聚合能力，根据用户兴趣领域智能筛选，生成个性化每日简报。

---

## 核心功能

### 1. 智能领域筛选
- 用户指定兴趣领域（科技/财经/AI/体育/娱乐等）
- 自动从28+信源中筛选相关内容
- 关键词智能扩展（如"AI"→"AI,LLM,GPT,Claude,Agent"）

### 2. 多维度早报模板
- **综合早报**：全领域重点新闻汇总
- **科技早报**：科技圈大事件、技术趋势
- **财经早报**：股市动态、经济要闻
- **AI早报**：AI/大模型最新进展
- **行业早报**：特定行业深度分析

### 3. 个性化配置
- 早报标题自定义
- 内容深度可选（简报/详报）
- 信源偏好设置
- 发布时间提醒

### 4. 定时推送
- 每日定时生成
- 支持多时段推送
- 推送渠道可选

---

## 使用方式

```bash
# 生成综合早报
python3 scripts/generate_briefing.py --type general

# 生成科技早报
python3 scripts/generate_briefing.py --type tech --keyword "AI,大模型"

# 生成AI领域早报（深度版）
python3 scripts/generate_briefing.py --type ai --deep

# 生成今日要闻摘要
python3 scripts/generate_briefing.py --type headline --limit 10
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|-------|
| --type | 早报类型 | general |
| --keyword | 关键词筛选 | 无 |
| --deep | 深度阅读模式 | false |
| --limit | 每源条目数 | 10 |
| --title | 自定义标题 | 今日早报 |
| --save | 保存到文件 | true |

### 早报类型

| 类型 | 说明 |
|------|------|
| general | 综合早报 |
| tech | 科技早报 |
| finance | 财经早报 |
| ai | AI早报 |
| headline | 今日要闻 |
| custom | 自定义领域 |

---

## 输出示例

```markdown
# 📰 科技早报 | 2026年3月10日

## 🔥 今日热点
1. **英伟达发布新一代AI芯片** - 性能提升3倍，定价$1999
2. **OpenAI推出GPT-5** - 多模态能力大幅增强

## 📊 大公司动态
- 苹果WWDC定档6月
- 谷歌I/O预告AI新品

## 🔬 技术前沿
- 新一代大模型训练成本下降50%
- 开源社区持续繁荣

## 💡 观点与分析
（深度分析内容）

---
📊 数据来源：Hacker News, GitHub Trending, 36Kr, 微博热搜
⏰ 生成时间：2026-03-10 08:00
```

---

## 触发词

- 早报
- 今日早报
- 科技早报
- 财经早报
- AI早报
- 定制早报
- morning briefing
- 每日简报

---

## 依赖

- Python 3.8+
- requests
- beautifulsoup4
- (可选) playwright - 用于深度阅读

安装：`pip install -r requirements.txt`

---

## 进阶使用

### 自定义模板
在 `templates/` 目录下创建自定义模板：
- `tech_template.md` - 科技早报模板
- `finance_template.md` - 财经早报模板

### 定时任务
结合cron实现每日自动生成：
```bash
# 每日8:00生成科技早报
0 8 * * * python3 /path/to/scripts/generate_briefing.py --type tech
```

---

## 适用场景

- 📱 个人资讯获取
- 📊 行业趋势跟踪
- 🎯 专业领域研究
- 📰 内容创作素材
- 🤖 Agent能力增强
