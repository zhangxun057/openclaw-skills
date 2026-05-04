---
name: skill-radar
description: 每日自动监控市场热门 Skill，智能推荐值得安装的新技能。从 skills.sh、GitHub、ClawHub、扣子 Coze 抓取热门榜单，自动过滤已安装、重复、高风险技能，识别近期爆火趋势，生成精选日报。**焦点关注模式**：根据新增待办事项定向搜索相关技能。触发条件：(1) 用户提到"skill 雷达"、"技能推荐"、"有什么新 skill"，(2) 定时任务（每天 10:00、14:00），(3) 用户询问"最近有什么好用的技能"。
author: 张洵
source: 原创
version: 3.0.0
---

# Skill Radar - 技能雷达

每日自动监控市场热门 Skill，智能推荐值得安装的新技能。

## 核心功能

1. **多源抓取** — skills.sh (Trending) / 🦞 虾评 Skill（重点源）/ find-skills（主动搜索）
2. **智能过滤** — 自动排除已安装、重复、高风险技能
3. **焦点关注** — 🆕 根据**新增待办**定向搜索相关技能（仅今天 + 昨天）
4. **去重记忆** — 7 天内不重复推荐同一 skill

## 使用方式

### 手动触发
用户说"skill 雷达"、"推荐新技能"、"有什么好用的 skill"时自动触发。

### 定时任务
在 `HEARTBEAT.md` 中添加：
```markdown
## 定期检查项
- 每天 10:00、14:00 - 运行 skill-radar 生成日报
```

## 执行流程

### 1. 读取已安装 skill 列表

```bash
ls ~/.openclaw/skills > installed.txt
```

### 2. 读取历史推荐记录（7 天去重）

```javascript
const historyPath = '~/.openclaw/workspace/skill-logs/skill-radar/history.json';
const history = JSON.parse(fs.readFileSync(historyPath));

// 计算 7 天前的时间戳
const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);

// 过滤掉 7 天内推荐过的
const recentRecommendations = history.recommendations
  .filter(r => r.timestamp > sevenDaysAgo)
  .map(r => r.skillName);

console.log('📋 7 天内已推荐:', recentRecommendations);
```

### 3. 焦点关注检索（仅新增待办）

**🆕 关键优化：只读取今天 + 昨天新增的待办，避免重复搜索**

```javascript
// 1. 读取待办事项（龙虾养成计划）
const app_token = 'Ms0Sbx75jahr5QsX4vQc8rnxn2f';
const table_id = 'tblU1u2KzTmZIqdw';

const tasks = await feishu_bitable_app_table_record({
  action: "list",
  app_token,
  table_id,
  page_size: 100
});

// 2. 计算时间范围（今天 + 昨天）
const now = Date.now();
const twoDaysAgo = now - (2 * 24 * 60 * 60 * 1000);

// 3. 筛选新增待办（派发日期在最近 2 天内 + 未完成）
const newTasks = [];
for (const task of tasks.records) {
  const status = task.fields['任务状态'];
  if (status === '已完成' || status === '取消') continue;
  
  const dispatchDate = task.fields['派发日期'];
  if (!dispatchDate || dispatchDate < twoDaysAgo) continue;
  
  newTasks.push(task);
}

console.log('🎯 新增待办:', newTasks.length, '个');

// 4. 提取关键词
const keywords = [];
for (const task of newTasks) {
  const title = task.fields['任务名称']?.[0]?.text || '';
  const desc = task.fields['任务描述']?.map(d => d.text).join(' ') || '';
  
  // 中英文关键词映射
  const keywordMap = {
    '微信': 'wechat',
    '飞书': 'lark',
    '朋友圈': 'moments',
    '多模态': 'multimodal',
    'agents': 'agents',
    '多实例': 'multi-instance',
    '仪表盘': 'dashboard',
    '可视化': 'visualization',
    '语音': 'voice',
    'TTS': 'tts',
    '定时任务': 'cron',
    '心跳': 'heartbeat',
    '网页搜索': 'web search',
    '网页抓取': 'web scraping',
    '调研': 'research',
    'Deep Research': 'deep research',
    '网关': 'gateway',
    'tool': 'tool',
    '自建': 'custom'
  };
  
  const text = `${title} ${desc}`.toLowerCase();
  for (const [cn, en] of Object.entries(keywordMap)) {
    if (text.includes(cn.toLowerCase()) || text.includes(en.toLowerCase())) {
      keywords.push(en);
    }
  }
}

const uniqueKeywords = [...new Set(keywords)];
console.log('🔑 搜索关键词:', uniqueKeywords);

// 5. 用 find-skills 搜索（仅当有关键词时）
const focusSkills = [];
if (uniqueKeywords.length > 0) {
  for (const keyword of uniqueKeywords) {
    const result = await exec(`npx skills find "${keyword}"`);
    const skills = parseSkillsOutput(result.stdout);
    skills.forEach(s => {
      s.focusMatch = keyword;
      s.score = 100;  // 焦点匹配最高优先级
      s.source = 'find-skills';
    });
    focusSkills.push(...skills);
  }
}

return focusSkills;
```

### 4. 抓取热门 skill（广撒网）

**🦞 虾评 Skill（重点源）**

```javascript
// 打开虾评首页抓取 Top20
await browser({ action: "open", url: "https://xiaping.coze.site/" });
await browser({ action: "act", request: { kind: "wait", timeMs: 3000 }});

const snapshot = await browser({ action: "snapshot", snapshotFormat: "ai" });
const xiapingSkills = parseXiapingSnapshot(snapshot);

xiapingSkills.forEach(s => {
  s.source = 'xiaping';
  s.score = 50;  // 虾评基础分
});
```

**skills.sh - Trending 榜单**

```javascript
// 打开 Trending 页面抓取 Top20
await browser({ action: "open", url: "https://skills.sh/trending" });
await browser({ action: "act", request: { kind: "wait", timeMs: 3000 }});

const snapshot = await browser({ action: "snapshot", snapshotFormat: "ai" });
const trendingSkills = parseTrendingSnapshot(snapshot);

trendingSkills.forEach(s => {
  s.source = 'skills.sh';
  s.score = 40;  // Trending 基础分
});
```

### 5. 合并 + 去重 + 排序

```javascript
// 合并所有来源
const allSkills = [...focusSkills, ...xiapingSkills, ...trendingSkills];

// 去重（按 skill 名称）
const uniqueSkills = [];
const seen = new Set();
for (const skill of allSkills) {
  if (seen.has(skill.name)) continue;
  seen.add(skill.name);
  uniqueSkills.push(skill);
}

// 排除已安装和 7 天内推荐过的
const filteredSkills = uniqueSkills.filter(s => 
  !installed.includes(s.name) && 
  !recentRecommendations.includes(s.name)
);

// 排序权重
filteredSkills.forEach(s => {
  // 焦点匹配 +100
  if (s.focusMatch) s.score += 100;
  
  // 安装量加分
  if (s.installs > 10000) s.score += 30;
  else if (s.installs > 1000) s.score += 20;
  else if (s.installs > 100) s.score += 10;
  
  // 评分加分
  if (s.rating > 4.5) s.score += 20;
  else if (s.rating > 4.0) s.score += 10;
});

// 按分数降序排序
filteredSkills.sort((a, b) => b.score - a.score);

// 取前 10 个推荐
const topSkills = filteredSkills.slice(0, 10);
```

### 6. 生成日报

```markdown
【🦞 Skill 雷达 | YYYY-MM-DD】

━━━━━━━━━━━━━━━━━━━

【🎯 为你找到的（基于新增待办）】

1. **skill-name** ⭐⭐⭐⭐⭐
   匹配：你新增的待办「任务名称」
   能力：一句话描述
   安装量：X.XK
   安装：`npx skills add owner/repo@skill`

━━━━━━━━━━━━━━━━━━━

【🔥 热门精选（虾评 + Trending）】

2. **another-skill** ⭐⭐⭐⭐
   虾评热门 | 评分 4.8 | 下载 1.2K
   
3. **trending-skill** ⭐⭐⭐⭐
   Trending #5 | 安装 5.2K

━━━━━━━━━━━━━━━━━━━

【📊 本次排除】
- 已安装：X 个
- 7 天内推荐过：Y 个

━━━━━━━━━━━━━━━━━━━

💬 对哪个感兴趣？回复数字我帮你安装

⏰ 下次扫描：今日 14:00 / 明日 10:00
```

### 7. 更新历史记录

```javascript
// 写入推荐历史
const history = {
  recommendations: [
    ...history.recommendations,
    ...topSkills.map(s => ({
      skillName: s.name,
      timestamp: Date.now(),
      source: s.source,
      reason: s.focusMatch ? `匹配待办：${s.focusMatch}` : '热门精选'
    }))
  ]
};

fs.writeFileSync(historyPath, JSON.stringify(history, null, 2));
```

## 配置说明

**config.json 位置：** `~/.openclaw/workspace/skill-logs/skill-radar/config.json`

```json
{
  "focus": {
    "enabled": true,
    "app_token": "Ms0Sbx75jahr5QsX4vQc8rnxn2f",
    "table_id": "tblU1u2KzTmZIqdw",
    "lookbackDays": 2
  },
  "sources": {
    "xiaping": true,
    "skills.sh": true,
    "find-skills": true
  },
  "filters": {
    "excludeInstalled": true,
    "excludeRecent": true,
    "recentDays": 7
  },
  "output": {
    "maxRecommendations": 10
  }
}
```

## 数据存储

```
skill-logs/skill-radar/
├── config.json           # 配置文件
├── history.json          # 历史推荐记录（7 天去重）
├── installed.txt         # 已安装 skill 快照
└── log.md               # 使用日志
```

## 使用日志

每次触发后执行以下脚本记录调用情况：

```bash
node ~/.openclaw/skills/_shared/log-usage.mjs "skill-radar" "<触发原因>" "<结果>"
```

## 版本更新

### v3.0.0 (2026-03-29)
- 🆕 只读取今天 + 昨天新增待办，避免重复搜索
- 🆕 中英文关键词映射，提升 find-skills 命中率
- 🆕 7 天去重逻辑完善
- 🔧 多源兼顾：find-skills + 虾评 + skills.sh

### v2.0.0 (2026-03-16)
- 🆕 焦点关注模式
- 🆕 深度分析报告

### v1.0.0 (2026-03-15)
- 🆕 初始版本
