# OpenClaw Skills - 张洵的技能库

张洵的多龙虾技能共享中心

---

## 🦞 技能列表（共 4 个）

### 1. 🔧 gateway-restart
**用途**：OpenClaw Gateway 服务重启

**使用场景**：
- 修改 `openclaw.json` 配置后需要生效
- Gateway 无响应或浏览器服务报错
- 工具提示 "Can't reach the OpenClaw gateway control service"

**核心命令**：
```bash
openclaw gateway restart
```

---

### 2. 🌐 browser-automation
**用途**：浏览器自动化操作

**使用场景**：
- 自动抓取网页内容
- 截图保存页面
- 模拟点击和输入操作
- 自动化网页测试

**核心操作**：
```javascript
// 打开网页
browser({ action: "open", targetUrl: "https://example.com" })

// 获取快照
browser({ action: "snapshot", targetId: "<id>" })

// 截图
browser({ action: "screenshot", targetId: "<id>", fullPage: true })
```

---

### 3. ☁️ cloudflare-deploy
**用途**：Cloudflare Pages 自动部署

**使用场景**：
- 将 GitHub 前端项目自动部署到 Cloudflare Pages
- 配置 CI/CD 自动发布流程
- 支持 React/Vue/Next.js 等主流框架

**核心步骤**：
1. 创建 Cloudflare API Token
2. 在 GitHub 添加 Secrets
3. 创建 `.github/workflows/deploy.yml`
4. push 触发自动部署

---

### 4. 💬 wechat-send-message ⭐ 新
**用途**：macOS 微信发送消息

**使用场景**：
- 批量发送微信消息
- 自动化微信通知

**前置条件**：
- macOS 系统
- 安装 cliclick：`brew install cliclick`

---

## 📦 技能结构

每个技能是一个文件夹：

```
skill-name/
├── SKILL.md              # 技能文档（带 YAML frontmatter）
└── skill-name.skill      # 打包好的安装包（可选）
```

**SKILL.md 必须包含**：
```yaml
---
name: skill-name
description: "技能描述，说明使用场景"
---
```

---

## 🚀 使用方式

### 方式 1：通过 ClawHub 安装（推荐）

```bash
npx clawhub@latest install gateway-restart
npx clawhub@latest install browser-automation
npx clawhub@latest install cloudflare-deploy
npx clawhub@latest install wechat-send-message
```

### 方式 2：手动下载

1. 下载 `.skill` 文件
2. 解压到 `~/.openclaw/skills/`
3. 重启 OpenClaw

### 方式 3：直接复制 SKILL.md

1. 复制 `SKILL.md` 到你的工作区
2. 按文档操作

---

## 📝 提交新技能

### 方式 1：网站表单（推荐，无需 GitHub 权限）

1. 访问 [技能共享网站](https://797b6767.openclaw-skills-hub-7qp.pages.dev)
2. 点击「提交技能」
3. 填写表单（技能名称、贡献者、内容）
4. 系统自动创建 GitHub Issue
5. 张洵审核后合并

### 方式 2：Git 提交（需要写权限）

```bash
# 1. Fork 仓库
git clone https://github.com/zhangxun057/openclaw-skills.git

# 2. 创建技能文件夹
mkdir skills/your-skill-name
cp your-skill.md skills/your-skill-name/SKILL.md

# 3. 打包
python package_skill.py skills/your-skill-name

# 4. 提交
git add .
git commit -m "Add skill: your-skill-name"
git push origin master
```

---

## 🔧 打包脚本

```bash
python package_skill.py skills/your-skill-name
```

生成 `your-skill-name.skill` 文件，可直接分享。

---

_Repository: zhangxun057/openclaw-skills_  
_Website: https://797b6767.openclaw-skills-hub-7qp.pages.dev_
