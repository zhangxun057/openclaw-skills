# 项目结构规范

## 标准目录结构

```
projects/{project-name}/
├── README.md                 # 项目概述（入口）
├── spec/                     # 规格说明
│   ├── PRD.md               # 产品需求文档
│   ├── technical-design.md  # 技术设计
│   └── api-spec.md          # API 规格
├── docs/                     # 开发文档
│   ├── setup.md             # 环境搭建
│   ├── architecture.md      # 架构说明
│   └── changelog.md         # 变更日志
├── iterations/               # 迭代记录
│   ├── v0.1/
│   │   ├── plan.md          # 迭代计划
│   │   ├── test-report.md   # 测试报告
│   │   └── retrospective.md # 复盘
│   └── v0.2/
├── decisions/                # 架构决策记录
│   ├── 001-title.md
│   └── 002-title.md
├── src/                      # 源代码
└── tests/                    # 测试代码
```

## 核心文档说明

### README.md
项目入口，包含：
- 一句话描述
- 当前状态
- 快速链接
- 团队信息

### spec/PRD.md
产品需求文档，包含：
- 背景与目标
- 功能需求（用户故事 + 验收标准）
- 非功能需求
- 里程碑

### iterations/vX.X/plan.md
迭代计划，包含：
- 迭代目标
- 任务列表
- 验收标准
- 风险和时间安排

### decisions/XXX-title.md
架构决策记录（ADR），包含：
- 背景
- 决策内容
- 理由
- 备选方案
- 后果

---
_更新：2026-03-07_
