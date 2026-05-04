---
name: bocha-search
description: |
  博查 AI 搜索。当用户需要搜索网络信息、查找资料、了解最新新闻时使用。
  调用博查 API 快速获取搜索结果，支持"搜索 + 访问"组合工作流。
  触发词：搜索、search、查找、查询、帮我找、搜一下、AI搜索、博查。
version: 2.1.0
---

# 博查 AI 搜索 Skill

## 核心功能

通过博查 API 进行网络搜索，返回 URLs + 摘要，可选全文抓取。

## 工作流程

```
用户请求搜索 → 调用 bocha_search.py → 博查API返回URLs → 可选：访问内容
```

## 快速使用

### 命令行

```bash
# 搜索关键词（返回 URLs + 摘要）
python3 scripts/bocha_search.py "搜索关键词" -n 5

# 只搜索不访问内容（更快）
python3 scripts/bocha_search.py "搜索关键词" --no-visit

# 搜索并自动访问第一个结果获取全文
python3 scripts/bocha_search.py "搜索关键词" -n 3 --visit-first

# JSON 格式输出（AI 友好）
python3 scripts/bocha_search.py "搜索关键词" --json

# 指定时间范围
python3 scripts/bocha_search.py "搜索关键词" --freshness pw   # 本周
python3 scripts/bocha_search.py "搜索关键词" --freshness pd   # 今天
```

### 在对话中使用

当用户要求搜索时：
1. 调用 `bocha_search.py` 获取搜索结果
2. 将结果以简洁列表形式展示
3. 如需详细内容，用 `web_fetch` 抓取全文

## API 配置

| 配置项 | 值 |
|--------|-----|
| API Key | `sk-130edef213334cdb8f9ae08a09a5b106` |
| 端点 | `https://api.bochaai.com/v1/web-search` |
| 脚本路径 | `scripts/bocha_search.py` |

## 触发关键词

当用户说以下词语时激活：
- 搜索、search、查找、查询
- 帮我找、搜一下、AI搜索、博查

## 输出格式

### 默认格式
```
[博查搜索] "关键词" - 找到 5 条结果
============================================================

1. 标题
   URL: https://...
   摘要: 简要描述...
   来源: 网站名
   发布: 2026-04-24
```

### JSON 格式 (`--json`)
```json
[
  {
    "title": "标题",
    "url": "https://...",
    "snippet": "摘要",
    "summary": "AI 摘要",
    "siteName": "来源",
    "datePublished": "发布日期"
  }
]
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 搜索关键词 | 必填 |
| `-n / --count` | 返回结果数量 | 5 |
| `--no-visit` | 只搜索不访问 | false |
| `--visit-first` | 访问第一个结果全文 | false |
| `--json` | JSON 格式输出 | false |
| `--freshness` | 时间范围 (pd/pw/pm/py) | 不限 |

## 与其他搜索工具的对比

| 工具 | 优势 | 劣势 |
|------|------|------|
| **博查搜索** | 免费、快速、支持摘要 | 无 |
| `web_fetch` | 直接抓全文 | 需要先有 URL |
| `serper-search` | Google 结果 | 收费 |
| 浏览器搜索 | 可交互 | 慢 |

## 最佳实践

1. **快速搜索**：先用 `--no-visit` 获取结果列表
2. **深入研究**：选中 URL 后用 `web_fetch` 抓全文
3. **对比分析**：多次搜索 + 汇总
4. **AI 输出**：用 `--json` 方便解析
