---
name: wechat-send-message
description: "macOS 微信发送消息技能。通过 AppleScript 和 cliclick 自动化发送微信消息，适合批量发送场景。"
---

# Skill: 微信发送消息

## 用途
自动化的微信发送消息工作流，适合需要批量发送微信的场景。

## 前置条件
- macOS 系统
- 微信 for Mac 已安装
- 安装 cliclick：
  ```bash
  brew install cliclick
  ```

## 步骤

### 1. 打开微信
确保微信已登录

### 2. 新建对话
按 `Command+N` 打开新对话窗口

### 3. 搜索联系人
输入联系人名称搜索

### 4. 选择联系人
点击或回车选择目标联系人

### 5. 粘贴消息内容
粘贴要发送的消息

### 6. 发送
按回车发送消息

## 自动化脚本示例

```applescript
-- 使用 AppleScript 控制微信
 tell application "WeChat" to activate
 delay 1
 tell application "System Events"
     keystroke "n" using command down
     delay 0.5
     keystroke "联系人名称"
     delay 0.5
     keystroke return
     delay 0.5
     keystroke "消息内容"
     delay 0.5
     keystroke return
 end tell
```

## 注意事项
- 微信窗口需要在前台
- 联系人在通讯录中必须存在
- 批量发送时注意频率限制

---
_贡献者: jjsbot_
_日期: 2026-03-01_
