---
name: weflow
description: "WeFlow 微信聊天记录工具集成。通过 HTTP API 查询微信聊天记录、会话列表、联系人，导出消息和媒体文件。需要先启动 WeFlow 桌面应用并开启 API 服务。"
tags: [wechat, chat, export, api]
---

# WeFlow - 微信聊天记录集成

通过 WeFlow HTTP API 查询和导出微信聊天记录。

## 前置条件

1. 安装 WeFlow 桌面应用（需微信 4.0+）
2. 启动 WeFlow 并连接数据库
3. 设置 → API 服务 → 启动服务（默认端口 5031）

## 安装 WeFlow

```bash
# 源码构建
cd C:\Users\44452\.openclaw\workspace\WeFlow
npm install
npm run dev

# 或从 Release 下载安装包
# https://github.com/hicccc77/WeFlow/releases
```

## API 基础地址

```
http://127.0.0.1:5031
```

## 常用操作

### 健康检查
```bash
curl http://127.0.0.1:5031/health
```

### 获取会话列表
```bash
curl http://127.0.0.1:5031/api/v1/sessions
# 搜索特定会话
curl "http://127.0.0.1:5031/api/v1/sessions?keyword=工作群&limit=20"
```

### 获取联系人
```bash
curl http://127.0.0.1:5031/api/v1/contacts
curl "http://127.0.0.1:5031/api/v1/contacts?keyword=张三"
```

### 获取聊天记录
```bash
# 基础查询
curl "http://127.0.0.1:5031/api/v1/messages?talker=wxid_xxx&limit=50"

# 时间范围
curl "http://127.0.0.1:5031/api/v1/messages?talker=wxid_xxx&start=20260101&end=20260301&limit=100"

# 关键词搜索
curl "http://127.0.0.1:5031/api/v1/messages?talker=wxid_xxx&keyword=项目进度"

# 导出媒体（图片+语音）
curl "http://127.0.0.1:5031/api/v1/messages?talker=wxid_xxx&media=1&image=1&voice=1&video=0"
```

### 访问媒体文件
```bash
curl http://127.0.0.1:5031/api/v1/media/wxid_xxx/images/image_123.jpg
```

## 输出格式

支持两种格式：
- **原始 JSON**：默认格式
- **ChatLab 格式**：标准化聊天记录交换格式，加 `chatlab=1` 参数

## 使用场景

- 查询特定联系人的聊天记录
- 按时间范围导出消息
- 关键词搜索历史消息
- 导出图片/语音/视频媒体
- 生成聊天分析报告
- 对接外部系统做数据分析
