# OpenClaw Skills - 张洵的技能库

张洵的多龙虾技能共享中心

---

## 🦞 技能列表（共 38 个）

### AI & 图像生成
- **agent-tools** - Run 150+ AI apps via inference.sh CLI
- **ai-image-generation** - AI图像生成工具集
- **flux-image** - Flux 图像生成
- **ai-product-photography** - AI产品摄影
- **edge-tts** - Edge TTS 文字转语音
- **jimeng-4-image-generation** - 即梦4图片生成
- **seedream-image-generation** - Seedream 图片生成

### 视频 & 数字人
- **ai-marketing-videos** - AI营销视频生成
- **ai-video-generation** - AI视频生成工具
- **remotion-render** - Remotion 视频渲染
- **jimeng-digital-human** - 即梦数字人

### 微信 & 社交
- **wechat-analyzer** - 微信好友自动化分析与档案生成
- **weflow** - WeFlow 微信聊天记录工具集成
- **wechat-send-message** - macOS微信发送消息
- **baoyu-post-to-wechat** - 宝玉发布到微信
- **wechat-mp-cn** - 微信公众号监控

### 飞书生态
- **feishu-auto-reply** - 飞书消息自动回复
- **feishu-bitable** - 飞书多维表格管理
- **feishu-bitable-upload** - 飞书多维表格附件上传
- **feishu-calendar** - 飞书日历与日程管理
- **feishu-card** - 飞书消息卡片发送
- **feishu-common** - 飞书通用工具
- **feishu-create-doc** - 创建飞书云文档
- **feishu-im-read** - 飞书消息读取
- **feishu-interactive-card** - 飞书交互卡片
- **feishu-task** - 飞书任务管理

### 开发 & 部署
- **browser-automation** - OpenClaw 浏览器自动化操作
- **cloudflare-deploy** - Cloudflare Pages 自动部署
- **skill-creator** - 创建和管理 AgentSkills
- **gateway-restart** - OpenClaw Gateway 服务重启
- **vercel-composition-patterns** - Vercel React 组合模式
- **vercel-react-best-practices** - Vercel React 最佳实践

### 系统 & 工具
- **capability-evolver** - AI 代理自进化引擎
- **task-monitor** - 实时 Web 仪表板
- **cron-generator** - 定时任务创建
- **self-improving-agent** - 自改进代理

### 效率工具
- **todolist-manager** - 个人待办清单
- **diary-assistant** - 日记助手
- **brainstorming** - 头脑风暴
- **interview-tracker** - 客户拜访追踪

### 技能管理
- **skill-radar** - 技能市场雷达
- **skill-auditor** - 技能质量审计
- **swap** - 技能交换
- **find-skills** - 技能搜索
- **search-layer** - 搜索层级

### 内容生成
- **content-extract** - URL 内容提取
- **pdf-generator** - PDF 生成
- **mineru-extract** - MinerU 内容提取

### 目标管理
- **project-manager** - 项目管理

### 其他
- **web-design-guidelines** - Web 设计指南
- **vision-analyzer** - 视觉分析
- **ddg-web-search** - DuckDuckGo 搜索
- **news-aggregator** - 新闻聚合器

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
