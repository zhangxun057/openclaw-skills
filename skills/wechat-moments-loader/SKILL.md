---
name: wechat-moments-loader
description: "自动打开微信朋友圈，滚动加载内容，调用WeFlow导出HTML+媒体和JSON结构化数据到本地。触发词：朋友圈更新、刷新朋友圈、加载朋友圈、朋友圈采集、朋友圈下载。支持绝对时间（20260409T08）和相对时间（5h/30m/2d）入参，按日期+序号保存数据。"
version: 0.5.0
---

# 微信朋友圈数据采集器

定时触发，自动加载朋友圈并导出 HTML+媒体 和 JSON结构化数据 到本地。

## 前置条件

1. 微信已登录并在后台运行（系统托盘）
2. WeFlow已安装且可用（首次自动启动）
3. 首次使用运行安装：`python scripts/setup.py`

## 使用方法

```bash
cd ~/.openclaw/skills/wechat-moments-loader

# 按日期范围（大模型翻译自然语言后调用）
python scripts/loader.py --start 20260409 --end 20260410

# 按小时精度
python scripts/loader.py --start 20260409T08 --end 20260409T14

# 相对时间（5小时前到当前）
python scripts/loader.py --start 5h

# 仅滚动不导出
python scripts/loader.py --start 5h --skip-weflow

# 仅打开朋友圈
python scripts/loader.py --open-only
```

## 时间参数格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 绝对日期 | 20260409 | 某天0点 |
| 绝定日期+小时 | 20260409T08 | 某天8点 |
| 相对小时 | 5h | 5小时前 |
| 相对分钟 | 30m | 30分钟前 |
| 相对天 | 2d | 2天前 |
| 省略end | -- | 默认当前时间 |

## 数据存储

```
朋友圈数据/
├── moments_20260409_120000.html       # HTML文件（人类查看/备份）
├── moments_20260409_120000/           # 对应媒体目录
│   ├── media_0001.jpg
│   ├── media_0002.mp4
│   └── ...
├── 20260409_120000.json               # JSON结构化数据（分析主数据源）
├── moments_20260409_140000.html       # 同一天第二次采集
├── moments_20260409_140000/
├── 20260409_140000.json
└── status.json                        # 状态记录
```

同一天多次采集不覆盖，序号递增。

## JSON导出说明

每次导出 HTML 的同时，自动导出 JSON 结构化数据：
- 文件名：`{timestamp}.json`（如 `20260409_120000.json`）
- 位置：与 HTML 同级目录
- 内容：`{ "success": true, "count": N, "timeline": [...] }`
- 包含字段：tid, id, username, nickname, createTime, contentDesc, media, likes, comments
- 优先尝试从 `/sns/export` 返回数据获取，回退到 `/sns/timeline` 逐好友获取

## 版本历史

- v0.5.0: 新增 JSON 结构化数据导出
- v0.4.0: HTML + 媒体导出

## 详细文档

- `references/usage.md` - 完整参数说明、故障排除、status.json格式
