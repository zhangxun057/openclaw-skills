# Skill: OpenClaw 浏览器自动化

## 前置条件

1. Gateway 已启动：`openclaw gateway status` 显示 online
2. 浏览器功能已启用：`~/.openclaw/openclaw.json` 中有 `browser.enabled: true`

**最小配置：**
```json
{
  "browser": {
    "enabled": true,
    "defaultProfile": "openclaw",
    "headless": false
  }
}
```

配置后需重启 Gateway：`openclaw gateway restart`

## 快速检查

```bash
# 检查浏览器服务状态
openclaw browser status

# 应显示：enabled: true, detectedBrowser: "chrome" 或 "edge" 等
```

## 基础操作

### 打开网页

```javascript
// 打开页面并获取 targetId
browser({
  action: "open",
  profile: "openclaw",
  targetUrl: "https://example.com"
})
```

### 获取页面快照

```javascript
// 抓取页面结构（包含 ref 标记可点击元素）
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
// 使用 snapshot 返回的 ref
browser({
  action: "act",
  request: {
    kind: "click",
    ref: "e12"  // 从 snapshot 获取的 ref
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

**推荐用 `openclaw`**：全自动，无需人工干预

## 完整流程示例

```javascript
// 1. 打开页面
const page = await browser({
  action: "open",
  profile: "openclaw",
  targetUrl: "https://x.com/some_post"
});

// 2. 等待加载（可选）
await new Promise(r => setTimeout(r, 3000));

// 3. 抓取内容
const snapshot = await browser({
  action: "snapshot",
  profile: "openclaw",
  targetId: page.targetId
});

// 4. 提取信息（从 snapshot 内容中分析）
// 5. 关闭标签（可选）
await browser({
  action: "close",
  targetId: page.targetId
});
```

## 故障排除

**错误："Can't reach the OpenClaw browser control service"**

1. 检查 Gateway：`openclaw gateway status`
2. 检查浏览器配置：`browser.enabled` 是否为 true
3. 重启 Gateway：`openclaw gateway restart`

**错误："Browser disabled"**

配置文件中添加 `browser.enabled: true` 并重启

**页面打不开/空白**

- 某些网站需要登录或有反爬机制
- 尝试截图查看实际渲染结果
- 检查 `headless: false` 是否能看到浏览器窗口

---
_Updated: 2026-02-28_
