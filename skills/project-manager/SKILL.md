---
name: project-manager
description: |
  项目管理工具。规范化项目开发流程，自动创建项目结构、生成文档模板、跟踪开发进度�?  
  **使用场景�?*
  (1) 启动新项目时
  (2) 需要创建迭代计划时
  (3) 需要记录架构决策（ADR）时
  (4) 需要生成测试报告时
  (5) 用户提到"项目管理"�?迭代"�?ADR"�?项目结构"
  
  **关键词：** 项目管理, 迭代计划, ADR, 架构决策, 测试报告, 项目结构
---

# Project Manager

规范化项目开发流程，自动创建项目结构、生成文档模板、跟踪开发进度�?
## 何时使用

- 启动新项目时
- 需要创建迭代计划时
- 需要记录架构决策时
- 需要生成测试报告时

## 核心功能

### 1. 初始化项�?创建标准项目结构和基础文档

### 2. 管理迭代
创建迭代计划、跟踪进度、生成测试报�?
### 3. 记录决策
使用 ADR (Architecture Decision Record) 记录重大决策

### 4. 生成文档
根据模板快速生成各类项目文�?
---

## 使用方法

### 初始化新项目
```bash
node scripts/init-project.js <project-name>
```

### 创建迭代
```bash
node scripts/create-iteration.js <project-name> <version>
```

### 记录决策
```bash
node scripts/create-adr.js <project-name> <decision-title>
```

---

## 项目结构规范

详见 `templates/PROJECT-STRUCTURE.md`

---

_创建�?026-03-07_

## Usage Logging

每次触发后执行以下脚本记录调用情况：

```bash
node ~/.openclaw/skills/_shared/log-usage.mjs "project-manager" "<触发原因>" "<结果>"
```
