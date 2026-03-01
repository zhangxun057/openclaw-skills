---
name: zhangxun-gateway-restart
description: "OpenClaw Gateway重启技能。用于配置修改后生效、Gateway无响应或浏览器服务报错时使用。"
---

# Skill: OpenClaw Gateway 重启

## 用途
修改 `openclaw.json` 配置后需要生效，或 Gateway 无响应、浏览器服务报错时使用。

## 前置条件
- OpenClaw 已安装
- Gateway 命令行工具可用

## 步骤

### 1. 检查当前状态

```bash
openclaw gateway status
```

### 2. 重启 Gateway

```bash
openclaw gateway restart
```

### 3. 验证重启成功

```bash
openclaw gateway status
```

应显示 `Gateway: online`

## 配置修改后必须重启的场景

| 配置项 | 需要重启 |
|--------|----------|
| `browser.enabled` | ✅ 是 |
| `browser.defaultProfile` | ✅ 是 |
| `gateway.port` | ✅ 是 |
| `channels.*.enabled` | ✅ 是 |
| `agents.defaults.model` | ❌ 否 |
| `models.providers.*.apiKey` | ❌ 否 |

## 常见问题

**重启后端口被占用**
```
Port 18795 is already in use
```
解决：
```bash
# 更换端口
openclaw config set gateway.port 18796
openclaw gateway restart
```

---
_贡献者: jjsbot_
_日期: 2026-03-01_
