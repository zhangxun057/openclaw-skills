---
name: cloudflare-deploy
description: "Cloudflare Pages 自动部署配置。使用场景：(1) 将 GitHub 前端项目自动部署到 Cloudflare Pages，(2) 配置 CI/CD 自动发布流程，(3) 设置 API Token 和 GitHub Actions。支持 React/Vue/Next.js 等主流框架。"
---

# Cloudflare Pages 自动部署

将 GitHub 仓库自动部署到 Cloudflare Pages 的完整配置指南。

## 前置条件

- GitHub 账号
- Cloudflare 账号
- 已推送到 GitHub 的前端项目

## 创建 Cloudflare API Token

### 步骤

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 点击右上角头像 → **My Profile**
3. 选择左侧 **API Tokens** 标签
4. 点击 **Create Token**
5. 选择 **Custom token** 模板

### Token 配置

| 字段 | 值 |
|------|-----|
| **Token name** | `GitHub Actions Deploy` |
| **Permissions** | Cloudflare Pages:Edit |
| **Account Resources** | Include: 你的账号 |
| **Zone Resources** | Include: All zones |

点击 **Continue to summary** → **Create Token**

### ⚠️ 重要：保存 Token

**创建后立即复制 Token，只显示一次！**

## 获取 Cloudflare 配置信息

### Account ID

1. 进入 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 右侧边栏找到 **Account ID**
3. 复制这串字符

### Project Name

1. 进入 **Pages** 页面
2. 创建或选择已有项目
3. 项目名称为创建时填写的 `Project name`

## 在 GitHub 配置 Secrets

进入你的 GitHub 仓库：

```
Settings → Secrets and variables → Actions → New repository secret
```

添加以下 Secrets：

| Secret 名称 | 值 |
|-------------|-----|
| `CLOUDFLARE_API_TOKEN` | 刚才创建的 API Token |
| `CLOUDFLARE_ACCOUNT_ID` | 你的 Account ID |

## 创建 GitHub Actions 工作流

### 1. 创建工作流文件

```bash
mkdir -p .github/workflows
touch .github/workflows/deploy.yml
```

### 2. 基础配置（静态网站）

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

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: your-project-name
          directory: ./dist
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

### 3. 带构建的配置（React/Vue/Next.js 等）

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

### 4. 不同框架的 directory 配置

| 框架 | directory 值 |
|------|--------------|
| Vite | `./dist` |
| Create React App | `./build` |
| Next.js (静态导出) | `./out` |
| Nuxt.js | `./dist` 或 `.output/public` |
| Vue CLI | `./dist` |
| Hugo | `./public` |
| 纯 HTML | `./` 或 `./public` |

## 直接连接（无需 GitHub Actions）

如果不需要自定义构建流程，可直接在 Cloudflare 连接 GitHub：

1. 进入 Cloudflare Pages → **Create a project**
2. 选择 **Connect to Git**
3. 授权 Cloudflare 访问你的 GitHub 账号
4. 选择仓库
5. 配置构建设置

**优点**：更简单，自动监听 push
**缺点**：无法自定义复杂流程

## 完整配置清单

部署前确认以下信息：

- [ ] Cloudflare API Token 已创建
- [ ] Account ID 已记录
- [ ] Project Name 已确认
- [ ] GitHub Secrets 已配置
- [ ] 工作流文件已提交到 `.github/workflows/`
- [ ] directory 路径与构建输出一致

## 常见问题

### 1. 部署失败 "Failed to publish"

检查点：
- API Token 是否有 Pages:Edit 权限
- Project Name 是否与 Cloudflare 中一致
- directory 路径是否正确

### 2. 构建成功但页面 404

- 检查 `directory` 是否指向正确的构建输出目录
- 确认构建命令生成了静态文件

### 3. 环境变量

如需在构建时使用环境变量：

```yaml
- name: Build
  run: npm run build
  env:
    VITE_API_KEY: ${{ secrets.VITE_API_KEY }}
```

### 4. 自定义域名

在 Cloudflare Pages 项目设置 → **Custom domains** 中配置

## 使用 Wrangler CLI（可选）

本地测试部署：

```bash
# 安装 Wrangler
npm install -g wrangler

# 登录
wrangler login

# 本地预览
wrangler pages dev ./dist

# 手动部署
wrangler pages deploy ./dist --project-name=your-project
```

---
_Updated: 2026-02-28_
