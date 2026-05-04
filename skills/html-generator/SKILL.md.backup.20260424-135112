---
name: html-generator
description: Generate modern, mobile-responsive HTML pages with AI-generated images for a premium look. Activated when user asks to generate/create/build a webpage, website, or HTML file with images or illustrations. Automatically plans image needs, generates prompts, calls Seedream API, uploads to file server, and produces the final HTML with embedded image links.
---

# HTML Generator（图文增强版）

自动为网页内容规划配图，生成高质量提示词，调用 AI 生图，并嵌入最终网页。

## 完整工作流

```
1. 内容分析 → 规划配图需求
2. 生成提示词（英文，Seedream 优化）
3. 调用 Seedream API 生成图片
4. 上传图片到文件服务器
5. 生成带图片链接的 HTML
6. 上传 HTML → 返回永久链接
```

---

## 第一步：规划配图

根据网页内容分析需要哪些图片，填写「配图规划表」：

| 图片角色 | 数量 | 用途描述 | 风格关键词 |
|---------|:----:|---------|-----------|
| hero | 1 | 全屏封面背景 | 深色典雅、金色光泽、高端 |
| section | N | 内容区配图 | 根据内容主题设定 |
| card | N | 卡片背景装饰 | 根据卡片主题设定 |
| guide | 1 | 指南/场景配图 | 综合、温馨 |

**规划原则：**
- 首屏 Hero 必须有配图，作为第一印象
- 每个主要章节至少一张配图
- 避免纯文字堆砌，用图片提升视觉层次
- 估算图片数量，向用户确认后再生成（可省成本）

---

## 第二步：生成提示词

### 英文 Prompt 公式

```
[画面主体] + [环境/背景] + [光线/氛围] + [色彩] + [构图/视角] + [避免项] + , high quality, 4K, professional photography, no text
```

### 示例

**Hero 封面（酱香白酒）：**
```
A premium Chinese Moutai-style baijiu bottle on a dark mahogany table, golden liquid pouring in slow motion, warm amber light, rich wooden background with subtle gold accents, cinematic lighting, shallow depth of field, luxurious and elegant atmosphere, high quality, 4K, professional photography, no text, no words
```

**传统酱香（古法酿造）：**
```
Traditional Chinese baijiu brewing scene, large clay jars in ancient cellars, workers using wooden poles for fermentation, warm torch lighting, rustic stone walls, amber and copper tones, heritage and craftsmanship atmosphere, high quality, 4K, professional photography, no text
```

**典雅酱香（高端商务）：**
```
Elegant Chinese baijiu gift box on marble surface, golden packaging with silk ribbon, soft studio lighting, minimalist luxury background with subtle gold patterns, refined and sophisticated atmosphere, high quality, 4K, professional photography, no text
```

**馥郁酱香（层次丰富）：**
```
Multiple layers of aroma rising from a baijiu glass, visualized as colorful swirling mist (amber, floral, fruity notes), dark elegant background, dramatic lighting, artistic and abstract representation of complex flavors, high quality, 4K, professional photography, no text
```

**清雅酱香（清新明亮）：**
```
Fresh green fields with ripe sorghum wheat, morning mist, sunlight filtering through, a glass of clear baijiu with green reflections, clean and refreshing atmosphere, natural daylight, airy and light mood, high quality, 4K, professional photography, no text
```

---

## 第三步：调用 Seedream API 生成图片

### API 参数

```
URL: https://ark.cn-beijing.volces.com/api/v3/images/generations
Method: POST
Authorization: Bearer d155ace0-ee4d-42b1-936e-4a16d2623c89
Content-Type: application/json
模型: doubao-seedream-5-0-260128
response_format: url
watermark: false
```

### 单张生成

```bash
curl -X POST https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer d155ace0-ee4d-42b1-936e-4a16d2623c89" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "英文提示词",
    "sequential_image_generation": "disabled",
    "response_format": "url",
    "size": "2048x2048",
    "watermark": false
  }'
```

### 多张并行生成（sequential_image_generation: auto）

```bash
curl -X POST https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer d155ace0-ee4d-42b1-936e-4a16d2623c89" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "英文提示词",
    "sequential_image_generation": "auto",
    "sequential_image_generation_options": {"max_images": 4},
    "response_format": "url",
    "size": "2048x2048",
    "watermark": false
  }'
```

### 从响应中提取 URL

```bash
# 生成成功后，URL 在 data[0].url 字段
echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data'][0]['url'])"
```

---

## 第四步：上传图片到文件服务器

### 上传图片（用于 CDN 持久化）

```bash
# 上传单张
curl -s -X POST "https://mjy.gzlex.com:8095/api/sse/file/upload" \
  -H "Authorization: Bearer ampzOmhjenFAMTIz" \
  -H "User-Agent: Apifox/1.0.0" \
  -F "file=@/tmp/image.jpg"

# 响应格式: {"code":"0","data":{"fileUrl":"https://..."}}
```

> **注意：** Seedream 返回的 URL 是有时效的 CDN 链接，建议上传到文件服务器获得永久链接后再嵌入 HTML。

---

## 第五步：生成 HTML 并嵌入图片

### 设计规范

- **Mobile-first**：响应式设计，适配手机端阅读
- **配色方案**（传递给 AI 生图的参考）：
  - 深色主题：背景 #0a0a0f，主色 #c9a66b（金色），辅色 #8b6914
  - 浅色主题：背景 #fafafa，主色 #3b82f6（蓝），辅色 #f59e0b
- **字体**：Google Fonts Noto Sans SC（400/500/700/900）
- **布局**：卡片圆角 16-24px，微阴影，平滑动画

### HTML 图片嵌入方式

```css
/* Hero 全屏背景 */
.hero {
  background-image: url('https://永久链接.jpg');
  background-size: cover;
  background-position: center;
  height: 100vh;
}

/* 卡片背景装饰 */
.card-bg {
  background-image: linear-gradient(rgba(10,10,15,0.7), rgba(10,10,15,0.85)), url('https://永久链接.jpg');
  background-size: cover;
  background-position: center;
  border-radius: 24px;
}

/* 内容配图 */
.section-img {
  width: 100%;
  border-radius: 16px;
  margin: 20px 0;
}
```

---

## 第六步：上传最终 HTML

```bash
curl -s -X POST "https://mjy.gzlex.com:8095/api/sse/file/upload" \
  -H "Authorization: Bearer ampzOmhjenFAMTIz" \
  -H "User-Agent: Apifox/1.0.0" \
  -F "file=@/tmp/output.html"
```

---

## 输出格式

```
✅ 网页生成并上传成功！

📐 配图规划：
   - Hero 大图 × 1
   - 风格卡片图 × 4
   - 指南场景图 × 1

🎨 生成的图片链接：
   - Hero: https://...
   - 传统酱香: https://...
   - 典雅酱香: https://...
   - 馥郁酱香: https://...
   - 清雅酱香: https://...
   - 选酒指南: https://...

🔗 您的网页链接：https://mjy.gzlex.com/xxx.html
```

---

## 成本控制原则

- 生成前**先确认配图数量**，告知用户预计消耗
- 简单文字网页（无配图需求）直接生成，不调用 API
- 图片数量建议不超过 6 张/次
- 如果图片 URL 已有永久链接，跳过上传步骤

---

## 快速参考卡

| 操作 | 命令/方法 |
|-----|---------|
| 生图 | `curl -X POST Seedream API + prompt` |
| 提 URL | `data[0].url` 字段 |
| 上传 | `curl POST file server` |
| 查上传 URL | `data.fileUrl` 字段 |
| 保存临时文件 | `/tmp/xxx.jpg` 或 `/tmp/xxx.html` |
