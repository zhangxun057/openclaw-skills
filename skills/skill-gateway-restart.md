# Skill: OpenClaw Gateway 重启

## 何时使用

- 修改 `openclaw.json` 配置后需要生效
- Gateway 无响应或浏览器服务报错
- 工具提示 "Can't reach the OpenClaw gateway control service"

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
# 查找占用进程并结束，或更换端口
openclaw config set gateway.port 18796
openclaw gateway restart
```

**重启后配置未生效**
- 检查配置文件路径：`~/.openclaw/openclaw.json`
- 确认 JSON 格式正确（可用在线工具验证）
- 重启后等待 5-10 秒再测试

---
_Updated: 2026-02-28_
