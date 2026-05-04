---
name: seedream-image-generation
description: |
  图像创意生成技能。当用户要求生成图片、AI 生图、文生图、图生图时使用。
  
  触发场景：
  - 用户说"生成一张 xxx 的图片"、"AI 生图"、"帮我画 xxx"
  - 涉及具体人物/品牌的图像需求（需要参考图搜索）
  - 通用场景/抽象创意图像需求（无需参考图）
  
  核心能力：
  - AI 驱动需求理解（场景识别、参考图判断、创意方向生成）
  - 参考图搜索与视觉验证（Serper + qwen-vl-plus）
  - 图像生成（GPT-Image-2 通过 APIMart）
---

# Image Creative Studio (图像创意工作室)

## 核心原则

**AI 驱动决策** - 语义理解由大模型完成，不是代码硬编码。

**工具调用最小化** - 仅在需要确定性可靠性时使用脚本。

**对话式流程** - 参考 brainstorming skill，用对话理解用户意图。

---

## 触发条件

用户要求生成图片时使用：
- "生成一张 xxx 的图片"
- "AI 生图：xxx"
- "帮我画 xxx"
- "文生图/图生图"

---

## 核心流程

```
用户输入
    ↓
【Step 1: AI 理解需求】→ 调用大模型分析语义
    ├─ 场景类型识别
    ├─ 参考图需求判断
    └─ 创意方向生成
    ↓
【Step 2: 工具调用】
    ├─ Serper 搜索参考图（如需要）
    ├─ qwen-vl-plus 视觉验证
    ├─ 博查搜索背景信息
    └── tools/image2_tool.py → 图像生成
    ↓
【Step 3: 输出】
    └─ 本地保存 + 发送用户
```

---

## Step 1: AI 理解需求（头脑风暴方法）

**核心方法**：用大模型对话式理解，不是代码模板。

**调用大模型**（阿里云百炼 qwen-plus）：

```python
import requests

def understand_user_input(user_input):
    """
    用大模型理解图像生成需求
    """
    prompt = f"""
你是一个图像创意策划总监。用户想要生成一张图片，请理解他的需求。

## 用户输入
"{user_input}"

## 分析任务

### 第一步：语义分析
1. **场景类型**：这是什么场景？（音乐节/代言活动/产品推广/肖像/风景/其他）
2. **主要主体**：有没有具体的人名/品牌名/产品名？
3. **场景元素**：有哪些关键元素？（地点、活动、道具、背景）
4. **参考图需求**：
   - 需要：涉及具体人物（明星/企业家/运动员）或具体品牌/产品
   - 不需要：通用形象（"一个医生"）、抽象创意（"未来城市"）、全球知名 IP（"蜘蛛侠"）
5. **背景复杂度评估**（重要）：
   - 如果参考图中主体（人物/产品）背景杂乱（街道/人群/复杂场景）→ `background_cluttered: true`
   - 如果参考图中主体背景干净（纯色/简单/虚化）→ `background_cluttered: false`
   - 这个评估用于决定是否需要抠图（白底中转方案）

### 第二步：生成创意方向
基于分析，生成 2-3 个创意方向。每个方向应该：
- 有独特的视觉角度
- 考虑用户提到的场景元素
- 实用可执行

### 第三步：提取搜索命题
为每个创意方向，列出需要搜索的背景信息（3-5 个命题）。

## 输出格式（严格 JSON）

{{
    "scene_type": "...",
    "main_subject": "...",
    "scene_elements": ["...", "..."],
    "needs_reference": true/false,
    "reference_query": "如果需要，搜索词（如'张艺兴 照片'），否则 null",
    "reference_reason": "为什么需要/不需要参考图",
    "background_cluttered": true/false,  // 背景复杂度评估（重要！用于决定是否抠图）
    "creative_directions": [
        {{
            "name": "方向名称（4-8 字）",
            "concept": "核心概念（15-30 字）",
            "visual": "视觉描述（50-100 字）",
            "search_needed": ["搜索命题 1", "搜索命题 2", "搜索命题 3"]
        }}
    ],
    "recommended_direction_index": 0,
    "reasoning": "分析逻辑（100-200 字）"
}}

直接输出 JSON，不要有任何额外文字。
"""
    
    headers = {
        "Authorization": "Bearer sk-c3b3d0d532ac408090f1ef09063171da",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是图像创意策划。输出严格 JSON。"},
                {"role": "user", "content": prompt}
            ]
        }
    }
    
    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    result = resp.json()
    content = result["output"]["choices"][0]["message"]["content"]
    
    # 提取 JSON
    import re
    match = re.search(r'\{[\s\S]*\}', content)
    if match:
        return json.loads(match.group())
    return None
```

**API 配置**：
```bash
export DASHSCOPE_API_KEY="sk-c3b3d0d532ac408090f1ef09063171da"
```

---

## Step 2: 工具调用

### 2.1 参考图搜索（如需要）

**何时调用**：`needs_reference = true`

**智能决策：是否需要抠图**

在参考图下载后，根据 AI 分析的 `background_cluttered` 字段决定：

```
参考图下载完成
    ↓
检查 background_cluttered
    ↓
true（背景杂乱） → 执行 Step A: 白底中转方案（抠图逻辑）
    ↓
false（背景干净） → 跳过抠图，直接执行 Step B: 图像生成
```

**判断标准**：
- `background_cluttered: true` → 街道/人群/复杂场景/背景干扰明显
- `background_cluttered: false` → 纯色背景/简单背景/虚化背景/摄影棚拍摄

**搜索策略**（优先级从高到低）：

#### 方案 A：Browser 多引擎搜索（优选）⭐

**工具**：Browser 自动化 + 多引擎图片搜索

**搜索引擎**（按顺序尝试）：
1. **百度图片** - 国内明星资源最丰富 + 近期照片（搜狐/新浪/网易）⭐
2. **必应图片** - 国际资源 + 权威媒体（环球网/人民网）
3. **谷歌图片** - 补充资源（可选）

**执行流程**：
```
Browser 打开百度 → 搜索 "{name}" → 截图 → 提取图片 URL → 下载前 3 张
    ↓（如下载失败）
Browser 打开必应 → 搜索 "{name}" → 截图 → 提取图片 URL → 下载前 3 张
    ↓（如下载失败）
方案 B：博查搜索（主要兜底）
    ↓（如下载失败）
方案 C：Serper API（最终兜底）
```

**下载目标**：主流媒体网站图片
- 搜狐（itc.cn）
- 新浪（sinaimg.cn / sina.com.cn）
- 网易（126.net / 163.com）
- 环球网（huanqiu.com）
- 人民网（people.com.cn）

**优点**：
- ✅ 绕过 API 反爬限制
- ✅ 图片质量更高（主流网站高清图）
- ✅ 来源多样性好（多引擎互补）

---

#### 方案 B：博查搜索（主要兜底）

**何时使用**：Browser 方案失败时

**工具**：
1. 博查搜索 API
2. 阿里云百炼 qwen-vl-plus（视觉验证）

**API 配置**：
```bash
export BOCHA_API_KEY="sk-130edef213334cdb8f9ae08a09a5b106"
```

---

#### 方案 C：Serper API（最终兜底）

**何时使用**：博查搜索也失败时

**工具**：
1. Serper 图片搜索 API
2. 阿里云百炼 qwen-vl-plus（视觉验证）

**验证标准**：
- 分辨率 ≥256x256
- 文件大小 ≥10KB
- 内容匹配（人物/品牌识别）
- 清晰度足够

**API 配置**：
```bash
export SERPER_API_KEY="a1b5573c9dae9041939d841fd602d1abba333ee7"
export DASHSCOPE_API_KEY="sk-c3b3d0d532ac408090f1ef09063171da"
```

---

### 2.1.3 信息搜索（如需要）

**何时调用**：根据 `search_queries` 命题

**工具**：博查搜索 API

**API 配置**：
```bash
export BOCHA_API_KEY="sk-130edef213334cdb8f9ae08a09a5b106"
```

---

### 2.1.5 参考图筛选标准（三层过滤机制）

**方案 A（Browser）特有逻辑**：

**下载策略**：
- 直接从主流媒体网站下载（搜狐/新浪/环球网等）
- 使用 User-Agent + Referer 伪装浏览器请求
- 下载失败时尝试下一张（不纠结单张图片）

**成功标准**：
- 文件大小 ≥10KB
- 图片格式正确（JPG/PNG）
- 能正常打开（非损坏文件）

---

**三层过滤机制**（方案 A/B 通用）：

**第一层：硬性门槛（一票否决）**

| 标准 | 阈值 | 检测方法 |
|------|------|----------|
| 分辨率 | ≥512×512 | PIL 检测 |
| 文件大小 | ≥50KB | 文件属性 |
| 主体识别 | person | qwen-vl-plus |
| 面部可见 | 无遮挡 | qwen-vl-plus |

**第二层：文本分析打分（搜索阶段）**

对每个搜索结果进行文本分析打分：

```python
def analyze_text_score(img):
    score = 0
    reasons = []
    
    # 1. 标题关键词（不根据来源打分，避免偏见）
    title = img.get('title', '')
    positive = [("正面", 3), ("近照", 3), ("写真", 3), ("专访", 2), ("采访", 2), ("少女", 2), ("驻颜", 2)]
    negative = [("截图", -3), ("抓拍", -2), ("模糊", -2)]
    
    for kw, pts in positive:
        if kw in title:
            score += pts
            reasons.append(f"'{kw}' ({pts:+d})")
    
    for kw, pts in negative:
        if kw in title:
            score += pts
            reasons.append(f"'{kw}' ({pts:+d})")
    
    return score, reasons
```

**核心原则**：
- ❌ **不根据来源网站打分**（新浪/百度/搜狐不应影响质量判断）
- ✅ **只根据标题关键词打分**（正面/近照/写真等）
- ✅ **视觉验证才是核心**（分辨率/清晰度/内容匹配）

**搜索词策略**（方案 A/B 略有区别）：

**方案 A（Browser）**：简单搜索词
- `{name}`（不加后缀，让搜索引擎返回最丰富结果）
- 如结果不理想，尝试 `{name} 写真` 或 `{name} 照片`

**方案 B（Serper）**：多搜索词
- `"{name} 正面照 近照"`（获取清晰正面）
- `"{name} 专访 采访"`（获取正式场合）
- `"{name} 写真 肖像"`（获取专业拍摄）
- `"{name} {职业相关}"`（如"董方卓 足球"）

**关键区别**：
- Browser 方案：搜索词简单，靠浏览器截图 + 人工筛选
- Serper 方案：搜索词精细，靠 API 返回 + 文本分析打分

**第三层：来源多样性检查**

下载前检查来源分布：
- 单一来源占比 ≤50%（避免"5 张图 4 张同源"）
- 如有来源集中，补充搜索其他来源

**最终输出**：

展示 Top 3 候选图，每项包含：
- 图片预览
- 综合评分（如 +5 分）
- 评分理由（如"新浪 (+3) + 正面 (+3) + 近照 (+3)"）
- 来源 URL
- 文件大小

---

### 2.2 信息搜索

**何时调用**：根据 `search_queries` 命题

**工具**：博查搜索 API

**API 配置**：
```bash
export BOCHA_API_KEY="sk-130edef213334cdb8f9ae08a09a5b106"
```

---

### 2.3 图像生成

**脚本**：`scripts/image2_tool.py`（GPT-Image-2 通过 APIMart）

**条件流程**：

```
参考图 + AI 分析结果
    ↓
检查 background_cluttered
    ↓
true（背景杂乱） → Step A: 生成白底图 → Step B: 生成最终图
                      (抠图逻辑)          (用白底图参考)
    ↓
false（背景干净） → 直接生成最终图
                      (用原图参考)
```

**调用方式**：
```python
from scripts.image2_tool import generate_and_save

# 方案 1: 直接生成（背景干净）
paths = generate_and_save(
    prompt="图片描述",
    size="1024x1792",
    image=base64_reference,  # 原图
    save_dir="./scratchpad"
)

# 方案 2: 白底中转（背景杂乱）
# Step A: 生成白底图
white_bg = generate_and_save(
    prompt="Extract subject only, pure white background",
    size="1024x1792",
    image=base64_reference,
    save_dir="./scratchpad"
)
# Step B: 用白底图生成最终图
paths = generate_and_save(
    prompt="图片描述 + 目标场景",
    size="1024x1792",
    image=white_bg,  # 白底图
    save_dir="./scratchpad"
)
```

**API 配置**：
```bash
export IMAGE2_API_KEY="sk-C4fVi6uZ78vS0Ip4F0fr8ySnCP5KOwGbCqfWZfiRUfGwnZVm"
export IMAGE2_BASE_URL="https://api.apimart.ai"
```

---

## 使用示例

### 示例 1: 明星代言活动

**用户**：`"茅台文旅代言人张艺兴到黄果树大瀑布下参加黄小西音乐节"`

**AI 分析**：
- 场景类型：代言活动 + 音乐节
- 主要主体：张艺兴
- 场景元素：黄果树大瀑布、黄小西音乐节、茅台文旅
- 需要参考图：是（张艺兴）
- 参考图搜索词：`"张艺兴 照片"`

**工具调用**：
1. Serper 搜索 `"张艺兴 照片"` → 下载参考图
2. qwen-vl-plus 验证 → 确认是本人
3. 博查搜索 `"黄果树大瀑布 实景"`、`"黄小西音乐节 舞台"`
4. `image2_tool.py` 生成

---

### 示例 2: 通用场景（无需参考图）

**用户**：`"一个穿白大褂的医生在医院走廊"`

**AI 分析**：
- 场景类型：肖像
- 主要主体：通用形象（医生）
- 需要参考图：否

**直接生成**：无需搜索参考图

---

## 尺寸选项

| 尺寸 | 像素 | 用途 |
|------|------|------|
| 1024x1024 | 1:1 | 社交媒体方图 |
| 1024x1792 | 9:16 | 竖版海报/手机壁纸 |
| 1792x1024 | 16:9 | 横版海报/横幅 |
| 1536x1024 | 3:2 | 风景照 |
| 1024x1536 | 2:3 | 人像照 |

---

## 使用方式

**由 OpenClaw 直接读取 SKILL.md 执行**，不是运行 Python 脚本。

### 触发方式

用户在飞书输入：
```
帮我生成一张张艺兴在黄果树音乐节的图片
```

OpenClaw（锥锥虾）响应：
1. 读取本 SKILL.md
2. 调用大模型理解需求（Step 1）
3. 调用工具（Step 2）
4. 输出图片

---

## 相关文件

| 文件 | 用途 | 何时使用 |
|------|------|----------|
| `scripts/serper_tool.py` | Serper 图片搜索 + 下载 | 需要参考图时 |
| `scripts/vision_tool.py` | qwen-vl-plus 视觉验证 | 验证图片内容/质量 |
| `scripts/image2_tool.py` | GPT-Image-2 API 封装 | 图像生成 |
| `references/product-db.md` | 搜索日志（非缓存） | 参考 |

---

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 参考图搜索失败 | 检查网络连接，或改用文生图模式 |
| 生成失败 | 检查提示词是否违规，或重试 |
| 临时文件未清理 | `rm -rf ~/.openclaw/agents/zhuizhuixia/workspace/scratchpad/ref_*.png` |
