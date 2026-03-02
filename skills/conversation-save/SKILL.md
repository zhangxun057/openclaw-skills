---
name: conversation-save
description: "对话存档技能。自动保存每日对话记录到transcripts目录。"
---

# Skill: 对话存档

## 用途
自动保存每日对话记录，防止对话历史丢失。

## 触发方式

**方式1：每次session开始时执行**
- 手动触发

**方式2：定时自动执行（推荐）**
- 执行本skill会自动创建每日定时任务
- 每天23:59自动保存当天对话

## 保存位置
~/.openclaw/workspace/memory/transcripts/YYYY-MM-DD/

## 自动创建定时任务

执行本skill时会自动检查并创建「每日对话存档」定时任务。

---
_贡献者: jjsbot_
_日期: 2026-03-01_
