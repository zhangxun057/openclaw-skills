# Bocha Search (博查搜索)

**版本**: 1.0

## 触发条件

用户需要搜索网页信息、查询实时数据、获取最新资讯时激活。

## 核心能力

| 能力 | 说明 |
|------|------|
| **网页搜索** | 基于博查 AI 搜索，返回结构化搜索结果 |
| **实时信息** | 获取最新资讯、价格、参数等动态信息 |
| **多轮搜索** | 支持连续搜索多个相关话题 |
| **结果组织** | 自动分类整理搜索结果（事实/观点/数据） |

## API 配置

### 环境变量
```bash
export BOCHA_API_KEY="your-api-key"
```

### 获取 API Key
1. 访问博查官网：https://bocha.ai
2. 注册账号并创建应用
3. 获取 API Key

## 使用方法

### 基础搜索
```bash
python bocha_search.py "Deepseek V4 参数"
```

### 带上下文搜索
```bash
python bocha_search.py "老干妈价格" --context "product_specs"
```

### 多关键词搜索
```bash
python bocha_search.py "抖音直播 UI" "小黄车" "评论弹幕"
```

## 输出格式

### 标准输出
```markdown
## 🔍 搜索结果

**查询**: Deepseek V4 参数

### 事实信息
- 参数量 1.6 万亿
- 上下文 1M tokens
- 发布时间 2026 年春节

### 参考来源
1. [DeepSeek V4 完整技术规格偷跑](https://...)
2. [掌握 DeepSeek V4 核心能力](https://...)
```

### JSON 输出
```json
{
  "query": "Deepseek V4 参数",
  "context": "product_specs",
  "facts": ["参数量 1.6 万亿", "上下文 1M tokens"],
  "sources": [
    {"title": "...", "url": "...", "snippet": "..."}
  ]
}
```

## 搜索上下文类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `product_specs` | 产品参数 | 价格、配置、性能 |
| `visual_style` | 视觉风格 | 设计案例、配色方案 |
| `marketing` | 营销信息 | 活动、促销、权益 |
| `audience` | 受众洞察 | 用户关注点、评价 |
| `competitor` | 竞品对比 | 同类产品对比 |
| `general` | 通用搜索 | 默认类型 |

## 文件结构

```
bocha-search/
├── SKILL.md              # 本文件
├── bocha_search.py       # 博查搜索主脚本
└── search_log.md         # 搜索日志（非缓存）
```

## 与图像生成 Skill 集成

博查搜索是 `seedream-image-generation` skill 的**主选搜索后端**。

### 自动调用流程
```
图像生成请求
    ↓
头脑风暴 → 创意方向
    ↓
定向搜索 → 博查搜索（自动）
    ↓
Prompt 深化 → 注入真实信息
    ↓
图像生成
```

### 手动调用
```python
from bocha_search import BochaSearch

search = BochaSearch()
result = search.search("Deepseek V4 参数", context="product_specs")
print(result["facts"])
```

## 错误处理

### 常见问题

**1. API Key 未配置**
```
错误：BOCHA_API_KEY not configured
解决：设置环境变量 export BOCHA_API_KEY="xxx"
```

**2. 搜索超时**
```
错误：Request timeout
解决：检查网络连接，重试搜索
```

**3. 配额用尽**
```
错误：Quota exceeded
解决：等待下月配额刷新或升级套餐
```

## 配额说明

| 套餐 | 每月搜索次数 | 价格 |
|------|-------------|------|
| 免费版 | 100 次 | ¥0 |
| 基础版 | 1000 次 | ¥99/月 |
| 专业版 | 10000 次 | ¥499/月 |

## 版本历史

- **v1.0** (2026-04-24): 初始版本，支持基础网页搜索

---

_Last Updated: 2026-04-24_
