---
name: zhangxun-browser-automation
description: "OpenClaw 浏览器自动化技能。用于自动抓取网页、截图、点击输入等操作。支持 openclaw 独立浏览器和 Chrome 扩展两种模式。"
---

# Skill: 浏览器自动化

## 用途
自动化的浏览器操作，包括打开网页、截图、点击元素、输入文本等。

## 前置条件

### 1. Gateway 已启动

```bash
openclaw gateway status
```

应显示 `online`

### 2. 浏览器功能已启用

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "browser": {
    "enabled": true,
    "defaultProfile": "openclaw",
    "headless": false
  }
}
```

配置后重启 Gateway：

```bash
openclaw gateway restart
```

## 基础操作

### 打开网页

```javascript
browser({
  action: "open",
  profile: "openclaw",
  targetUrl: "https://example.com"
})
```

### 获取页面快照

```javascript
browser({
  action: "snapshot",
  profile: "openclaw",
  targetId: "<targetId>"
})
```

### 截图

```javascript
browser({
  action: "screenshot",
  profile: "openclaw",
  targetId: "<targetId>",
  fullPage: true
})
```

### 点击元素

```javascript
browser({
  action: "act",
  request: {
    kind: "click",
    ref: "e12"  // 从 snapshot 获取
  }
})
```

### 输入文本

```javascript
browser({
  action: "act",
  request: {
    kind: "type",
    ref: "e23",
    text: "搜索内容",
    submit: true  // 自动按回车
  }
})
```

## Profile 说明

| Profile | 用途 | 是否需要扩展 |
|---------|------|-------------|
| `openclaw` | 独立浏览器实例（推荐） | 否 |
| `chrome` | 接管现有 Chrome 标签 | 是（需点扩展图标） |

## 完整流程示例

```javascript
// 1. 打开页面
const page = await browser({
  action: "open",
  profile: "openclaw",
  targetUrl: "https://x.com/some_post"
});

// 2. 等待加载
await new Promise(r => setTimeout(r, 3000));

// 3. 抓取内容
const snapshot = await browser({
  action: "snapshot",
  profile: "openclaw",
  targetId: page.targetId
});

// 4. 提取信息
// 5. 关闭标签
await browser({
  action: "close",
  targetId: page.targetId
});
```

---
_贡献者: jjsbot_
_日期: 2026-03-01_
