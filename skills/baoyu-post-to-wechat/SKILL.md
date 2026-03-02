---
name: baoyu-post-to-wechat
description: Posts content to WeChat Official Account via API or Chrome CDP.
---

# Post to WeChat Official Account

## Two Methods

| Method | Speed | Requirements |
|--------|-------|--------------|
| API | Fast | AppID/AppSecret |
| Browser | Slow | Chrome, login session |

## Install
```bash
# Get credentials from mp.weixin.qq.com
# Save to ~/.baoyu-skills/.env
WECHAT_APP_ID=xxx
WECHAT_APP_SECRET=xxx
```

## Usage

```bash
# API method (recommended)
npx -y bun scripts/wechat-api.ts article.md --theme default

# Browser method
npx -y bun scripts/wechat-article.ts --markdown article.md --theme default
```

## Use Cases
- 公众号文章发布
- 图文消息发布
- 自动生成摘要/封面
