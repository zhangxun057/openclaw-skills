---
name: wechat-analyzer
description: "微信好友自动化分析与档案生成工具。集成WeFlow API，自动下载微信联系人、聊天记录、朋友圈、媒体文件，深度分析客户画像（社交强度、互动模式、消费特征），生成标准化客户档案MD文件。适用于私域运营、客户关系管理、社交资产盘点场景。"
---

# WeChat Analyzer - 微信客户自动化分析工具

自动化分析微信好友，生成深度客户档案，助力私域运营变现。

## 功能概述

本Skill实现以下自动化流程：
1. **WeFlow自动集成** - 自动检查、下载、启动WeFlow，打通API
2. **全量数据下载** - 联系人、聊天记录、群聊、朋友圈、图片视频
3. **智能分析** - 深度分析客户画像（社交强度、互动模式、消费特征）
4. **客户逐一盘点** - 生成每位客户的详细档案
5. **档案生成** - 标准化的客户档案MD文件

## 前置条件

- Node.js环境（v16+）
- Python 3.8+
- 微信桌面版（已登录）

## 一键安装与启动

```bash
# 安装并启动完整流程
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/setup_and_run.py
```

此脚本会自动：
1. 检查并下载WeFlow（如未安装）
2. 安装WeFlow依赖
3. 启动WeFlow API服务
4. 等待微信数据库连接
5. 执行全量数据下载
6. 分析并生成客户档案

## 使用流程

### 方式一：全自动模式（推荐）

```bash
# 一键执行完整流程
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/full_pipeline.py \
  --output ~/.openclaw/workspace/客户档案 \
  --download-media \
  --download-moments

# 参数说明：
# --output: 档案输出目录
# --download-media: 下载图片/视频/语音等媒体文件
# --download-moments: 下载朋友圈数据
# --min-messages: 最少消息数阈值（默认50）
# --top-contacts: 分析联系人数（默认全部）
```

### 方式二：分步执行

#### 第一步：启动WeFlow服务
```bash
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/weflow_manager.py --action start
```

此脚本会自动：
- 检查WeFlow是否已安装（未安装则自动下载）
- 安装依赖
- 启动API服务
- 等待服务就绪

#### 第二步：下载全量数据
```bash
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/download_all.py \
  --output ./微信数据 \
  --include-media \
  --include-moments

# 下载内容包括：
# - 所有联系人（contacts/）
# - 所有聊天记录（messages/）
# - 所有群聊（groups/）
# - 媒体文件（media/）
# - 朋友圈（moments/）
# - 会话索引（sessions.json）
```

#### 第三步：客户逐一盘点
```bash
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/analyze_all.py \
  --data-dir ./微信数据 \
  --output ./客户档案

# 为每位客户生成独立档案
```

## 档案输出结构

```
客户档案/
├── 核心客户/
│   ├── 客户A.md
│   ├── 客户B.md
│   └── ...
├── 活跃客户/
│   ├── 客户C.md
│   └── ...
├── 普通客户/
│   └── ...
├── 待激活客户/
│   └── ...
├── 数据报告/
│   ├── 客户分级统计.json
│   ├── 社交强度排行榜.json
│   └── 关键词分析报告.json
└── 媒体文件/
    ├── 客户A_images/
    └── 客户A_videos/
```

## 档案内容模板

每个客户档案包含以下章节：

### 1. 基础画像
- 关系类型（好友/群友/商务）
- 消息数量与互动频率
- 相识时间线

### 2. 社交强度分析
- 消息比例（主动/被动）
- 回复速度与周期
- 互动持续性

### 3. 互动模式分析
- 话题偏好
- 沟通风格
- 情感倾向

### 4. 消费特征推断
- 消费潜力评估
- 品质偏好
- 决策风格

### 5. 价值评估
- 直接价值（消费力）
- 间接价值（影响力、信息价值）
- 网络位置

### 6. 触达策略建议
- 最佳时机
- 沟通方式
- 注意事项

## 客户分级标准

| 级别 | 标准 | 特征 | 策略 |
|------|------|------|------|
| **核心客户** | 消息量>500，互动高频 | 深度关系，强信任 | 优先维护，深度合作 |
| **活跃客户** | 消息量200-500，互动中频 | 活跃联系，有潜力 | 定期触达，挖掘需求 |
| **普通客户** | 消息量50-200，互动低频 | 一般联系 | 保持联系，适时激活 |
| **待激活客户** | 消息量<50，长期沉默 | 弱关系 | 节日问候，寻找契机 |

## 分析维度说明

### 社交强度指标
| 指标 | 含义 | 应用场景 |
|------|------|----------|
| 消息总数 | 关系亲密度 | 判断关系深度 |
| 消息比例 | 主动/被动程度 | 识别关键联系人 |
| 回复速度 | 重视程度 | 判断优先级 |
| 互动持续性 | 关系稳定性 | 预测长期价值 |

### 互动模式分析
- **发起频率**：谁主动发起对话
- **结束方式**：谁结束对话
- **话题分布**：工作/生活/情感等
- **表达方式**：文字/语音/表情/文件

### 消费特征推断
基于聊天内容关键词推断：
- 商务关键词 → 高消费力，决策快
- 技术关键词 → 理性消费，重性价比
- 生活关键词 → 品质消费，重体验
- 价格敏感词 → 价格导向，需优惠

## 自动化任务示例

### 示例1：完整分析流程
```bash
# 一键执行完整流程（含媒体下载）
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/full_pipeline.py \
  --output ~/.openclaw/workspace/客户档案 \
  --download-media \
  --download-moments

# 输出：
# 1. 自动下载WeFlow并启动
# 2. 下载所有微信数据（含媒体）
# 3. 分析所有联系人
# 4. 为每位客户生成档案
# 5. 输出统计报告
```

### 示例2：增量更新
```bash
# 只分析新增或更新的联系人
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/full_pipeline.py \
  --incremental \
  --last-sync 2026-03-01
```

### 示例3：指定客户分析
```bash
# 只分析特定联系人
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/analyze_contact.py \
  --username wxid_xxx \
  --data-dir ./微信数据 \
  --output ./客户档案
```

### 示例4：导出其他格式
```bash
# 导出Excel
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/export.py \
  --format excel \
  --output ./客户档案.xlsx

# 导出Notion
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/export.py \
  --format notion \
  --notion-token xxx
```

## 高级功能

### 1. AI辅助深度分析
```bash
# 使用AI模型分析聊天内容，生成更精准的画像
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/full_pipeline.py \
  --ai-analysis \
  --model kimi-coding/k2p5
```

### 2. 关系图谱生成
```bash
# 生成客户关系网络图谱
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/generate_graph.py \
  --output ./关系图谱.html
```

### 3. 朋友圈分析
```bash
# 分析朋友圈互动情况
python ~/.openclaw/workspace/skills/wechat-analyzer/scripts/analyze_moments.py \
  --data-dir ./微信数据 \
  --output ./朋友圈分析报告.md
```

## 数据安全与隐私

- **本地存储**：所有数据存储在本地，不上传云端
- **加密建议**：客户档案建议加密存储或放在安全目录
- **脱敏处理**：敏感信息（手机号、地址）自动脱敏
- **定期清理**：建议定期清理原始聊天记录，只保留分析结果

## 常见问题

### Q1: WeFlow下载失败？
```bash
# 手动下载WeFlow
git clone https://github.com/hicccc77/WeFlow.git ~/.openclaw/workspace/WeFlow
cd ~/.openclaw/workspace/WeFlow
npm install
```

### Q2: API连接失败？
- 检查WeFlow是否已连接微信数据库
- 检查微信是否在线
- 检查端口5031是否被占用

### Q3: 数据下载不全？
- 首次使用需要等待WeFlow同步完成
- 增加超时时间：`--timeout 600`
- 分批下载：`--batch-size 100`

### Q4: 分析结果不准确？
- 增加消息样本量：`--min-messages 100`
- 启用AI分析：`--ai-analysis`
- 手动调整档案内容

## 扩展开发

### 自定义分析规则
编辑 `scripts/analyzer.py` 中的规则：
```python
# 添加自定义客户类型判断
if '投资' in content and '项目' in content:
    profile['type'] = 'investor'
    profile['level'] = '核心客户'
```

### 自定义档案模板
编辑 `assets/template.md` 修改档案格式

## 相关链接

- WeFlow项目：https://github.com/hicccc77/WeFlow
- 示例档案：见 `assets/examples/`
