# OpenClaw Skills - 张洵的技能库

张洵的多龙虾技能共享库（规范版）

---

## 技能列表

| 技能 | 用途 | 安装方式 |
|------|------|----------|
| **gateway-restart** | OpenClaw Gateway 服务重启 | `npx clawhub@latest install gateway-restart` |
| **browser-automation** | 浏览器自动化操作 | `npx clawhub@latest install browser-automation` |
| **cloudflare-deploy** | Cloudflare Pages 自动部署 | `npx clawhub@latest install cloudflare-deploy` |

---

## 目录结构

每个技能是一个文件夹，包含：

```
skill-name/
├── SKILL.md              # 必须，带 YAML frontmatter
├── scripts/              # 可选，可执行脚本
├── references/           # 可选，参考文档
└── assets/               # 可选，资源文件
```

## SKILL.md 规范

必须包含 YAML frontmatter：

```yaml
---
name: skill-name
description: "技能的描述，说明使用场景和触发条件"
---
```

## 使用方式

### 方法 1：通过 ClawHub 安装（推荐）

```bash
npx clawhub@latest install gateway-restart
```

### 方法 2：手动复制

1. 下载 `.skill` 文件
2. 解压到 `~/.openclaw/skills/`
3. 重启 OpenClaw

### 方法 3：直接复制文件夹

1. 复制技能文件夹到工作区
2. 按 SKILL.md 文档操作

---

## 创建新技能

1. 创建文件夹 `skill-{功能}/`
2. 编写 `SKILL.md`（带 frontmatter）
3. 按需添加 `scripts/`、`references/`、`assets/`
4. 运行打包脚本：
   ```bash
   python package_skill.py skill-{功能}/
   ```

---

_Repository: zhangxun057/openclaw-skills_
