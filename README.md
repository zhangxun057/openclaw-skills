# OpenClaw Skills - 张洵的技能库

张洵的多龙虾技能共享中心

---

## 🦞 技能列表（共 19 个）

### AI & 图像生成
- **agent-tools** - Run 150+ AI apps via inference.sh CLI
- **ai-image-generation** - AI图像生成工具集
- **flux-image** - Flux 图像生成
- **ai-product-photography** - AI产品摄影

### 视频 & 数字人
- **ai-marketing-videos** - AI营销视频生成
- **ai-video-generation** - AI视频生成工具
- **remotion-render** - Remotion 视频渲染
- **jimeng-digital-human** - 即梦数字人

### 微信 & 社交
- **wechat-analyzer** - 微信好友自动化分析与档案生成
- **weflow** - WeFlow 微信聊天记录工具集成
- **wechat-send-message** - 微信消息发送
- **baoyu-post-to-wechat** - 宝玉发布到微信

### 开发 & 部署
- **browser-automation** - OpenClaw 浏览器自动化操作
- **cloudflare-deploy** - Cloudflare Pages 自动部署流程
- **skill-creator** - Create or update AgentSkills
- **gateway-restart** - OpenClaw Gateway 服务重启

### 系统 & 工具
- **capability-evolver** - A self-evolution engine for AI agents
- **task-monitor** - Real-time web dashboard for OpenClaw sessions
- **swap** - 技能交换平台

---

## 🚀 使用方式

### 通过 ClawHub 安装（推荐）

```bash
clawhub install <skill-name>
```

### 手动安装

1. 克隆仓库: `git clone https://github.com/zhangxun057/openclaw-skills.git`
2. 复制技能文件夹到 `~/.openclaw/skills/`
3. 重启 OpenClaw

---

## 📝 提交新技能

访问 [技能共享网站](https://claw-skills.pages.dev) 提交表单，系统自动创建 GitHub Issue 等待审核。

---

## 📦 技能结构

```
skill-name/
└── SKILL.md              # 技能文档（带 YAML frontmatter）
```

**SKILL.md 必须包含**:
```yaml
---
name: skill-name
description: "技能描述"
---
```

---

_Repository: https://github.com/zhangxun057/openclaw-skills_  
_Website: https://claw-skills.pages.dev_
