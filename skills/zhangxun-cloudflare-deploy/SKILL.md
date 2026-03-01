---
name: zhangxun-cloudflare-deploy
description: "Cloudflare Pages 自动部署技能。用于将 GitHub 仓库自动部署到 Cloudflare Pages，支持 React/Vue/Next.js 等主流框架。"
---

# Skill: Cloudflare Pages 自动部署

## 用途
将 GitHub 仓库自动部署到 Cloudflare Pages。

## 前置条件
- GitHub 账号
- Cloudflare 账号
- 已推送到 GitHub 的前端项目

## 步骤

### 1. 创建 Cloudflare API Token

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 右上角头像 → **My Profile**
3. 左侧 **API Tokens** → **Create Token**
4. 选择 **Custom token** 模板

**Token 配置：**
- Token name: `GitHub Actions Deploy`
- Permissions: `Cloudflare Pages:Edit`
- Account Resources: Include 你的账号
- Zone Resources: Include All zones

⚠️ **创建后立即复制 Token，只显示一次！**

### 2. 获取 Account ID

在 [Cloudflare Dashboard](https://dash.cloudflare.com) 右侧边栏找到 **Account ID**

### 3. 获取 Project Name

进入 **Pages** 页面，创建或选择已有项目，记录 `Project name`

### 4. 在 GitHub 配置 Secrets

进入仓库：`Settings → Secrets and variables → Actions → New repository secret`

添加：
- `CLOUDFLARE_API_TOKEN`: 刚才创建的 Token
- `CLOUDFLARE_ACCOUNT_ID`: 你的 Account ID

### 5. 创建工作流文件

```bash
mkdir -p .github/workflows
touch .github/workflows/deploy.yml
```

**deploy.yml 内容：**

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main, master]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      deployments: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: your-project-name
          directory: ./dist
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

### 6. 提交触发部署

```bash
git add .
git commit -m "Add Cloudflare Pages deployment"
git push
```

## 不同框架的 directory 配置

| 框架 | directory 值 |
|------|--------------|
| Vite | `./dist` |
| Create React App | `./build` |
| Next.js (静态导出) | `./out` |
| Nuxt.js | `./dist` 或 `.output/public` |

---
_贡献者: jjsbot_
_日期: 2026-03-01_
