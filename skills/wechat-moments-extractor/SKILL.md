---
name: wechat-moments-extractor
description: |
  朋友圈多维度并行提取器。
  端到端一键完成：提取事件、画像、内容分类、销售信号，并生成 Profile 文档。
  支持 --date 和 --posts-file 参数配置。
---

# 朋友圈多维度并行提取器

从朋友圈帖子中提取事件、画像、分类、信号，并生成用户 Profile 文档。

## 使用方法

```bash
# 定时任务推荐用法
python run_pipeline.py --date 2026-04-26

# 自定义输入文件
python run_pipeline.py --date 2026-04-26 --posts-file C:\path\to\custom.json
```

## 参数

| 参数 | 默认值 | 说明 |
|------|---------|------|
| --date | 必填 | 处理日期，格式 YYYY-MM-DD |
| --posts-file | 自动按日期查找 | 输入JSON文件路径 |

## 端到端流程

```
输入 JSON
    │
    ▼
run_pipeline.py
    │
    ├─► run_batch.py ──► 并发提取（events / traits / signals / post_type）
    │       │
    │       ▼
    │   extracted_YYYY-MM-DD.json
    │
    └─► generate_profiles.py ──► 生成 Profile 文档
            │
            ▼
        profiles_YYYY-MM-DD/
            ├── wxid_001.md
            ├── wxid_002.md
            └── ...
```

## 输出格式

### 提取结果（extracted_YYYY-MM-DD.json）

每条记录：
```json
{
  "wxid": "用户ID",
  "nickname": "昵称",
  "post_type": "内容分类",
  "traits": {...},
  "events": [...],
  "signals": [...]
}
```

### Profile 文档（profiles_YYYY-MM-DD/wxid.md）

每位用户生成一份 Markdown 文档，包含画像摘要、事件列表、销售信号。

## 脚本说明

| 脚本 | 功能 |
|------|------|
| run_pipeline.py | 端到端主入口（一键完成） |
| run_batch.py | 并发提取调度 |
| generate_profiles.py | 生成用户 Profile 文档 |
| extract_events.py | 事件提取 |
| extract_traits.py | 画像提取（字段值 <10 字） |
| extract_post_type.py | 内容分类 |
| extract_signals.py | 信号提取（字段值 <10 字） |
| shared_api.py | 共享 API 调用封装 |

## 容错与降级规范

### 模型Fallback链

主模型：qwen3.6-plus（阿里云百炼）
备选1：qwen3.5-plus（阿里云百炼，同key）
备选2：minimax-m2.7（MiniMax）

切换条件：主模型连续2次超时或报错后自动切换备选1，仍失败则切换备选2。

### 错误隔离

4个提取维度串行独立运行，任一维度失败不影响其他维度。
失败维度返回空值，记录中标记 _failed_fields。

### 重试策略

单模型重试2次，指数退避（5秒、15秒）。
全部模型都失败后，该批次标记为部分完成，跳过继续下一批。

### 断点续跑

每批完成后自动保存中间结果到输出文件。
中断后重新运行，已完成的批次自动跳过。
脚本检测已有输出文件，从最后一条继续。

---

## 提示词

### 事件提取

记录发帖人亲身经历的具体行动，动词开头，禁止社交用语、动态描述、纯转发内容。

### 画像提取

维度：基础信息、教育工作、收入资产、家庭关系、个人特质、消费水平、投资风格、饮酒偏好。

### 内容分类

动态分享、观点输出、内容转发、展示分享、广告推广。

### 信号提取

强信号：人生节点、活动预告、需求暗示。禁止消费展示、饮酒偏好、一般商务动态。