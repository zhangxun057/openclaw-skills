# Browser 抓取指引

## 前置要求

确保 OpenClaw Gateway 已启动，Browser 工具可用：
```bash
openclaw gateway status
```

---

## 一、抓取 skills.sh

### 步骤

**1. 打开 Trending 页面**
```javascript
await browser({ action: "open", url: "https://skills.sh/trending" });
```

**2. 等待加载**
```javascript
await browser({ action: "act", request: { kind: "wait", timeMs: 3000 }});
```

**3. 点击所有 "+X more" 展开按钮**

先获取 snapshot 找到所有展开按钮的 ref：
```javascript
const snapshot = await browser({ action: "snapshot", snapshotFormat: "ai" });
// 在返回的文本中查找包含 "more from" 的按钮，记录 ref
```

然后点击每个展开按钮：
```javascript
await browser({ action: "act", request: { kind: "click", ref: "e145" }});
await browser({ action: "act", request: { kind: "wait", timeMs: 500 }});
// 重复点击所有展开按钮...
```

**4. 提取完整数据**
```javascript
const skills = await browser({
  action: "act",
  request: {
    kind: "evaluate",
    fn: `() => {
      const rows = document.querySelectorAll('main a[href^="/"]');
      const skills = [];
      rows.forEach((row) => {
        const divs = row.querySelectorAll(':scope > div');
        if (divs.length >= 3) {
          const rank = divs[0]?.textContent?.trim();
          const name = divs[1]?.querySelector('h3')?.textContent?.trim();
          const source = divs[1]?.querySelector('p')?.textContent?.trim();
          const installs = divs[2]?.textContent?.trim();
          if (rank && name && !isNaN(parseInt(rank))) {
            skills.push({rank: parseInt(rank), name, source, installs, url: row.href});
          }
        }
      });
      return skills;
    }`
  }
});
```

**5. 同样方法抓取 All Time**
打开 `https://skills.sh` 重复步骤 2-4

**6. 保存结果**
```javascript
const fs = require('fs');
const data = {
  source: "skills.sh",
  category: "trending+alltime",
  scraped_at: new Date().toISOString(),
  skills: [...trendingSkills, ...alltimeSkills]
};
fs.writeFileSync(
  require('os').homedir() + '/.openclaw/workspace/skill-logs/skill-radar/daily-scan/skills_sh_browser.json',
  JSON.stringify(data, null, 2)
);
```

---

## 二、抓取 ClawHub

### 步骤

**1. 打开页面**
```javascript
await browser({ action: "open", url: "https://clawhub.com" });
```

**2. 等待加载**
```javascript
await browser({ action: "act", request: { kind: "wait", timeMs: 3000 }});
```

**3. 提取数据**
```javascript
const skills = await browser({
  action: "act",
  request: {
    kind: "evaluate",
    fn: `() => {
      const links = document.querySelectorAll('a[href^="/kn"]');
      const skills = [];
      links.forEach(link => {
        const heading = link.querySelector('h3');
        const desc = link.querySelector('p');
        if (heading) {
          skills.push({
            name: heading.textContent.trim(),
            description: desc ? desc.textContent.trim() : '',
            url: link.href,
            source: 'clawhub'
          });
        }
      });
      return skills;
    }`
  }
});
```

**4. 保存结果**
保存到 `~/.openclaw/workspace/skill-logs/skill-radar/daily-scan/clawhub_browser.json`

---

## 三、运行主控脚本

Browser 抓取完成后，运行主控脚本生成日报：
```bash
cd ~/.openclaw/skills/skill-radar/scripts
python skill_radar.py
```

---

## 已知坑点

### skills.sh
- ❗ **必须点击所有 "+X more" 按钮**，否则只能看到部分 skill
- 展开按钮 ref 编号每次会变，需要先 snapshot 再找
- 同作者的 skill 默认折叠在一起

### ClawHub
- ✅ 无折叠，直接抓取即可
- 数据包含 "Highlighted" 和 "Popular" 两个区块

### Coze
- 需要登录后才能看到完整榜单
- 未登录只能看到首页展示的几个 skill

---

## 快速测试命令

```bash
# 测试 GitHub 抓取（无需 Browser）
python scripts/skill_radar.py

# 测试后查看结果
cat ~/.openclaw/workspace/skill-logs/skill-radar/daily-scan/$(date +%Y-%m-%d)_report.txt
```
