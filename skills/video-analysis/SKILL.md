---
name: video-analysis
description: >
  视频内容深度分析：分析视频、提炼视频内容、将视频转换成脚本/逐字稿、提取屏幕文字/代码、总结核心观点。
  使用小米 MiMo-V2-Omni 原生视频理解（非截帧），支持本地文件和在线URL（B站/抖音/小红书/YouTube等）。
  触发词：分析视频、视频总结、视频转写、帮我看看这个视频、这个视频讲了什么、视频里说了啥、
  把视频里的操作步骤列出来、提取视频中的代码/文字、把视频转成脚本。
  不用于：视频剪辑、视频下载、纯图片分析。
---

# Video Analysis Skill

使用 MiMo-V2-Omni 进行原生视频分析（视频+音频同时理解，非截帧）。

## 核心原理

Omni API 接受视频直链 URL + 自定义提示词，同时处理视频帧（fps 可调）和音频，一次性返回分析结果。

**关键特性：**
- 不是截帧：模型同时理解视频帧 + 音频流 + 时序关系
- 自定义 prompt：不写则默认 "describe this video"，**必须自定义才能获得高质量输出**
- 无状态：每次调用独立，不支持追问，**必须一步到位**

## 配置

环境变量 `MIMO_API_KEY`（或调用时 `--api-key "你的key"`）。设置方法见平台文档。

## 快速使用

```bash
python scripts/analyze_video.py ./video.mp4 -p "你构造的prompt"
python scripts/analyze_video.py "https://www.bilibili.com/video/BV1xxx/" -p "prompt" -d 120
```

Prompt 由 agent 根据下方"Prompt 构造"规则动态生成，不使用默认值。

## 工作流程

```
用户请求 → 1. 判断意图深度
         → 2. 获取视频（下载/转码）
         → 3. 动态构造 Prompt
         → 4. 调用 Omni API
         → 5. 返回结果
         → 6. 用户追问 → 截取片段 → 重复 3-5
```

**默认策略：** 需求模糊时先做索引（低成本），有了索引再精准深挖。

## Prompt 构造 ⭐ 核心

### 三条规则

**规则 1：判断用户意图深度**

| 用户说的话 | 意图 | 策略 |
|---|---|---|
| "帮我看看讲了啥" "最近有什么新东西" | 了解概况 | → 结构化索引（时间轴+每段概括），不逐字转写 |
| "帮我转写" "详细说说04:00那段" | 深入内容 | → 逐字转写 + 时间戳 |
| "帮我拆脚本" "镜头语言分析" | 拆解形式 | → 分镜头分析（景别/运镜/画面/声音） |
| "提炼金句/洞察/公式" | 压缩精华 | → 极致压缩，限制数量 |
| "分析这个广告/教程" | 综合分析 | → 根据视频类型，选最匹配的策略 |

**规则 2：prompt = 角色定义 + 任务 + 输出要求**

- 第一句：角色定义（动态，根据场景）
- 中间：任务描述 + 输出项
- 末尾：格式要求
- 可选：对话上下文压缩（1-2句）

**规则 3：无状态，一步到位**

所有信息必须在一次调用中获取。需求模糊先做索引，再基于索引定位片段深挖。

### Prompt 示例（自然语言）

**了解概况**
```
你是一个视频内容编辑。分析这个视频，输出结构化索引。
输出：[MM:SS-MM:SS] 一句话概括这段内容。
不需要逐字转写。附关键人物/品牌/术语出现位置。
```

**深入内容**
```
你是一个语音转写编辑。逐字转写这个视频的内容。
要求：逐字转写，带 [MM:SS] 时间戳，标注语气变化（强调、停顿）。
```

**拆解广告**
```
你是一个广告脚本分析师。逐镜头拆解这个广告片。
每个镜头：[MM:SS] 景别 + 运镜 + 画面（主体+动作+场景）+ 声音（台词+音乐+音效）+ 转场。
最后总结：叙事结构、节奏分析、情绪曲线。
```

**压缩精华**
```
你是一个演讲金句编辑。从这个长视频中提炼精华。
严格输出：5个金句（原话+时间戳）+ 5个核心洞察（一句话+解释）。
不要：逐字转写、大纲、背景介绍。
```

### 场景参考

5 个典型场景的详细 prompt 设计见 `references/scenarios.md`，按需加载。

## 参数调优

| 参数 | 口播+PPT | 教程演示 | 广告/运镜 | Vlog |
|---|---|---|---|---|
| fps | 0.5-1 | 1-2 | 1-2 | 0.5-1 |
| resolution | default | default/max | max | default |
| max_tokens | 4096 | 4096-8192 | 8192 | 4096 |

## 成本估算

| 视频时长 | fps=1, default | fps=2, default |
|---|---|---|
| 30秒 | ~2500 tokens | ~4500 tokens |
| 1分钟 | ~9000 tokens | ~16000 tokens |
| 5分钟 | ~45000 tokens | ~80000 tokens |
| 10分钟 | ~90000 tokens | ~160000 tokens |

超过 5 分钟的视频建议先截取关键片段（--duration）。

## 支持的视频源

本地文件（mp4/mkv/webm/avi/mov）、B站、抖音、小红书、YouTube、直链 URL。

## API 限制

- `media_resolution` 只支持 `default` 或 `max`
- 视频 URL 必须可直接访问（不需要 Referer）
- B站视频需先下载再上传（CDN 需要 Referer）
- 文件大小限制：约 50MB

## 扩展能力 ⭐ （opencli / yt-dlp）

视频分析Skill本身只负责"理解视频"，不负责"找视频"和"下视频"。
这两个环节可以通过 opencli 和 yt-dlp 命令行工具增强。

---

### 工具简介

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| **opencli** | CLI工具，控制Chrome/调用各平台API | `npm install -g @jackwener/opencli` |
| **yt-dlp** | 视频下载（支持B站、抖音、YouTube等） | `pip install yt-dlp` 或 `brew install yt-dlp` |

---

### opencli 常用命令

```bash
# B站
opencli bilibili hot --limit 10              # 热门视频榜
opencli bilibili search "关键词"           # 搜索视频
opencli bilibili comments <bvid> --limit 20 # 视频热门评论
opencli bilibili subtitle <bvid>           # 获取字幕（若有）
opencli bilibili download <bvid>            # 下载视频（需yt-dlp）

# 微博
opencli weibo hot --limit 20               # 微博热搜

# 知乎
opencli zhihu hot                          # 知乎热榜

# 抖音（公开热点，无需登录）
opencli douyin hashtag hot                  # 抖音热点话题

# Twitter/X
opencli twitter trending                    # 趋势话题

# HackerNews
opencli hackernews top --limit 20          # HN Top Stories

# Yahoo Finance
opencli yahoo-finance quote --symbol SH600519  # 茅台股票
```

**完整命令列表：** `opencli list`

---

### yt-dlp 常用命令

```bash
# 下载B站视频
yt-dlp "https://www.bilibili.com/video/BV1xxx"

# 下载抖音视频（需具体链接，不支持搜索页）
yt-dlp "https://www.douyin.com/video/xxxxx"

# 下载YouTube
yt-dlp "https://www.youtube.com/watch?v=xxxxx"

# 查看可用格式
yt-dlp --list-formats "URL"

# 指定格式下载
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" "URL"
```

---

### 扩展应用场景（开脑洞）

#### 1. 自动化情报收集
```
用户: "帮我分析最近关于茅台的热门视频"
→ opencli bilibili search "茅台" → 找到Top10
→ opencli bilibili download <bvid> → 批量下载
→ video-analysis → 分析每个视频
→ 汇总成报告
```

#### 2. 多平台热度对比
```
同一话题，在B站/微博/知乎/抖音的热门程度对比
→ opencli bilibili hot | grep "关键词"
→ opencli weibo hot | grep "关键词"
→ opencli zhihu hot | grep "关键词"
→ opencli douyin hashtag hot | grep "关键词"
```

#### 3. 评论舆情分析
```
视频太专业看不懂？看看评论区怎么说
→ opencli bilibili comments <bvid> --limit 50
→ 分析评论风向：正面/负面/争议点
```

#### 4. 热点追踪流水线
```
用户: "监控西班牙访华的最新视频"
→ 定时任务：每天早上执行 opencli bilibili search "西班牙访华"
→ 发现新视频 → 自动下载
→ 分析 → 推送结果
```

#### 5. 竞品视频研究
```
用户: "分析这几个UP主最近发了什么"
→ opencli bilibili user-videos <uid> --limit 10
→ 批量下载 + 分析
→ 总结竞品内容策略
```

#### 6. 跨平台事件还原
```
一个事件，在不同平台有不同角度报道
→ B站：深度视频分析
→ 微博：热搜和实时讨论
→ 知乎：专业分析
→ 评论：民间声音
→ 汇总成完整事件画像
```

#### 7. 视频素材快速定位
```
用户: "找个合适的酒类广告参考"
→ opencli bilibili search "白酒广告" --limit 20
→ 看标题和评论快速筛选
→ 下载目标视频
→ 分析广告脚本/镜头语言
```

#### 8. 敏感话题监测
```
监控特定话题的视频热度变化
→ opencli bilibili hot --limit 50 > baseline.txt
→ 第二天再跑 → diff对比
→ 发现异常跳升的视频 → 深挖
```

---

### 调用方式

这些工具都是命令行，可以直接用 exec 工具调用：

```bash
# 在对话中触发
→ 请帮我用opencli搜索B站上关于茅台的视频

# agent会自动执行
opencli bilibili search "茅台"
```

**注意：**
- opencli 部分命令需要 Chrome 保持打开且已登录对应网站
- yt-dlp 下载抖音/TikTok 可能需要 cookies（ `--cookies-from-browser chrome`）
- 视频文件较大时，建议先压缩再分析（ffmpeg -vf "scale=1280:-2"）

---

## Usage Logging

每次触发后执行以下脚本记录调用情况：

```bash
node ~/.openclaw/skills/_shared/log-usage.mjs "video-analysis" "<触发原因>" "<结果>"
```
