---
name: skill-radar
description: 每日自动监控市场热门Skill，智能推荐值得安装的新技能。从 skills.sh、GitHub、ClawHub、扣子Coze 抓取热门榜单，自动过滤已安装、重复、高风险技能，识别近期爆火趋势，生成精选日报。**新增焦点关注模式**：根据待办事项定向搜索相关技能。触发条件：(1) 用户提到"skill雷达"、"技能推荐"、"有什么新skill"，(2) 定时任务（每天10:00、14:00），(3) 用户询问"最近有什么好用的技能"。
author: 张洵
source: 原创
version: 2.0.0
---

# Skill Radar - 技能雷达

每日自动监控市场热门Skill，智能推荐值得安装的新技能。

## 核心功能

1. **多源抓取** - skills.sh (All Time + Trending) / GitHub / ClawHub / 扣子Coze
2. **智能过滤** - 自动排除已安装、重复、高风险技能
3. **趋势分析** - 识别近期爆火的新技能（Trending榜单）
4. **焦点关注** - 🆕 根据待办事项定向搜索相关技能
5. **去重记忆** - 7天内不重复推荐同一skill

## 使用方式

### 手动触发
用户说"skill雷达"、"推荐新技能"、"有什么好用的skill"时自动触发。

### 定时任务
在 `HEARTBEAT.md` 中添加：
```markdown
## 定期检查项
- 每天 10:00、14:00 - 运行 skill-radar 生成日报
```

## 执行流程

### 1. 读取已安装skill列表

```bash
ls ~/.openclaw/workspace/skills > installed.txt
ls ~/.openclaw/skills >> installed.txt
```

### 2. 焦点关注检索（🆕 新增）

**从待办事项提取关键词，定向搜索**

```javascript
// 1. 读取配置
const configPath = '~/.openclaw/workspace/skill-logs/skill-radar/config.json';
const config = JSON.parse(fs.readFileSync(configPath));

if (!config.focus?.enabled) {
  console.log('⏭️ 焦点关注模式未启用');
  return [];
}

// 2. 读取待办事项
const tasks = await feishu_bitable_app_table_record({
  action: "list",
  app_token: config.focus.bitable.app_token,
  table_id: config.focus.bitable.table_id,
  page_size: 50
});

// 3. 提取关键词（只关注未完成任务）
const keywords = [];
for (const task of tasks.records) {
  const status = task.fields['任务状态'];
  if (status === '已完成' || status === '取消') continue;
  
  const title = task.fields['任务名称']?.[0]?.text || '';
  const desc = task.fields['任务描述']?.map(d => d.text).join(' ') || '';
  
  // 简单提取：匹配技术词汇
  const text = `${title} ${desc}`;
  const matches = text.match(/微信|飞书|多维表|agent|skill|PDF|可视化|仪表盘|网关|消息|归档/gi);
  if (matches) keywords.push(...matches);
}

const uniqueKeywords = [...new Set(keywords.map(k => k.toLowerCase()))];
console.log('🎯 焦点关键词:', uniqueKeywords);

// 4. 用 find-skills 搜索
const focusSkills = [];
for (const keyword of uniqueKeywords) {
  const result = await exec(`npx skills find "${keyword}"`);
  // 解析输出，提取 skill 信息
  const skills = parseSkillsOutput(result.stdout);
  skills.forEach(s => {
    s.focusMatch = keyword;
    s.score = 100;  // 焦点匹配最高优先级
  });
  focusSkills.push(...skills);
}

return focusSkills;
```

**配置文件（config.json）：**
```json
{
  "focus": {
    "enabled": true,
    "source": "bitable",
    "bitable": {
      "app_token": "Ms0Sbx75jahr5QsX4vQc8rnxn2f",
      "table_id": "tblU1u2KzTmZIqdw"
    }
  },
  "sources": {
    "skills.sh": true,
    "github": false,
    "clawhub": false,
    "coze": false
  }
}
```

### 3. 抓取热门skill（广撒网）

**skills.sh - Trending + All Time**

使用 `browser` 工具抓取：

```javascript
// 1. 打开 Trending 页面
await browser({ action: "open", url: "https://skills.sh/trending" });
await browser({ action: "act", request: { kind: "wait", timeMs: 3000 }});

// 2. 点击所有 "+X more" 展开按钮
const snapshot = await browser({ action: "snapshot", snapshotFormat: "ai" });
const moreButtons = snapshot.match(/\[ref=(\d+)\].*?\+\d+ more/g);
for (const btn of moreButtons) {
  const ref = btn.match(/ref=(\d+)/)[1];
  await browser({ action: "act", request: { kind: "click", ref }});
  await browser({ action: "act", request: { kind: "wait", timeMs: 1000 }});
}

// 3. 抓取完整列表
const fullSnapshot = await browser({ action: "snapshot", snapshotFormat: "ai" });
const skills = parseSkillsList(fullSnapshot);

// 保存
fs.writeFileSync('daily-scan/trending.json', JSON.stringify(skills, null, 2));
```

### 4. 过滤与排序

**过滤规则：**
- 已安装 → 排除
- 7天内推荐过 → 排除
- 功能重复 → 排除

**排序权重：**
- 焦点匹配：+100 分
- Trending 榜单：+50 分
- 安装量 > 1000：+20 分
- 飞书/字节生态：+15 分

### 5. 深度分析推荐skill（🆕 新增）

**对重点推荐的skill进行深度调研**

```javascript
// 对排序后的前3个skill进行深度分析
const topSkills = sortedSkills.slice(0, 3);

for (const skill of topSkills) {
  // 1. 用 browser 打开 skills.sh 页面
  await browser({ action: "open", url: skill.url });
  await browser({ action: "act", request: { kind: "wait", timeMs: 3000 }});
  
  // 2. 抓取详细信息
  const snapshot = await browser({ action: "snapshot", snapshotFormat: "ai" });
  
  // 3. 提取关键信息
  const analysis = {
    name: skill.name,
    installs: extractInstalls(snapshot),
    stars: extractStars(snapshot),
    author: extractAuthor(snapshot),
    security: extractSecurity(snapshot),
    description: extractDescription(snapshot),
    capabilities: extractCapabilities(snapshot)
  };
  
  // 4. 生成深度分析
  skill.deepAnalysis = generateAnalysis(analysis);
}
```

**深度分析包含：**
- 📊 基本信息（安装量、星标、作者、安全审计）
- 💡 核心能力（这个skill能做什么）
- 🔥 能帮你做什么（关联历史工作和待办）
- 👥 社区评价（优点、缺点、风险）
- 🎬 推荐指数（1-5星）

### 6. 生成日报

**简版日报（快速浏览）：**
```markdown
【龙虾 Skill 雷达 日报】
日期：YYYY-MM-DD
扫描来源：skills.sh Trending / 焦点关注

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【零、🎯 为你定制（基于当前待办）】

1. **skill-name** ⭐⭐⭐⭐⭐
   - 匹配你的待办：「微信自动回复」
   - 能力：微信消息自动处理
   - 来源：clawhub
   - 安装：`npx skills add owner/repo@skill-name`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【一、🔥 今日精选推荐】

2. **another-skill** ⭐⭐⭐⭐
   - Trending 榜单 #3
   - 能力：...
   - 安装量：5.2K

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【二、📊 本次排除】
- 已安装（X个）：skill1, skill2
- 功能重复（Y个）：skill3

【三、💡 趋势洞察】
- 本周最火：飞书集成类 skill（3个上榜）

【四、⏰ 下次扫描】
- 今日 14:00 / 明日 10:00
```

**深度分析报告（详细版）：**
保存到 `skill-logs/skill-radar/deep-analysis-YYYY-MM-DD.md`，包含：
- 每个推荐skill的完整分析
- 实际使用场景示例
- 安装优先级建议
- 风险提示

## 配置说明

**config.json 位置：** `~/.openclaw/workspace/skill-logs/skill-radar/config.json`

**完整配置：**
```json
{
  "focus": {
    "enabled": true,
    "source": "bitable",
    "bitable": {
      "app_token": "你的多维表token",
      "table_id": "待办表ID"
    }
  },
  "sources": {
    "skills.sh": true,
    "github": false,
    "clawhub": false,
    "coze": false
  },
  "filters": {
    "minStars": 10,
    "excludeRisky": true,
    "excludeDuplicate": true
  },
  "output": {
    "maxRecommendations": 10,
    "repeatDays": 7
  }
}
```

## 数据存储

```
skill-logs/skill-radar/
├── config.json           # 配置文件
├── daily-scan/
│   ├── 2026-03-16.json  # 今日扫描结果
│   └── focus.json       # 焦点关注结果
├── history.json         # 历史推荐记录
├── installed.txt        # 已安装skill快照
└── log.md              # 使用日志
```

## 使用日志

每次触发此skill时，追加记录到 `log.md`：

```bash
echo "## [$(date '+%Y-%m-%d %H:%M:%S')]" >> ~/.openclaw/workspace/skill-logs/skill-radar/log.md
echo "- **触发方式**: 手动/定时" >> ~/.openclaw/workspace/skill-logs/skill-radar/log.md
echo "- **焦点关注**: 启用/禁用" >> ~/.openclaw/workspace/skill-logs/skill-radar/log.md
echo "- **扫描结果**: 从 X 个中精选 Y 个（焦点匹配 Z 个）" >> ~/.openclaw/workspace/skill-logs/skill-radar/log.md
echo "" >> ~/.openclaw/workspace/skill-logs/skill-radar/log.md
```
