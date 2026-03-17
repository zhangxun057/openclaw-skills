---
name: jimeng-4-image-generation
description: 即梦4.0图像生成API封装。支持文生图、图生图、多图组合生成，可生成1-15张图像，输出4K超高清。生成后自动上传到文件服务器返回持久化链接。触发场景：用户要求生成图片、使用即梦4.0、AI生图、图像生成等。
---

# 即梦4.0图像生成

## 使用方法

### 方式1：命令行（推荐）

```bash
cd /Users/jjsbot/.openclaw/workspace/skills/jimeng-4-image-generation/scripts

# 一步生成并上传到文件服务器
python jimeng_api.py generate-upload "一只可爱的橘猫"

# 仅生成图片（返回即梦临时链接）
python jimeng_api.py generate "一只可爱的橘猫"

# 上传已有图片URL到文件服务器
python jimeng_api.py upload <图片URL>

# 查询任务状态
python jimeng_api.py query <task_id>
```

### 方式2：Python代码

```python
import sys
sys.path.append('/Users/jjsbot/.openclaw/workspace/skills/jimeng-4-image-generation/scripts')

from jimeng_api import generate_and_upload, generate_image, upload_to_file_server

# 方式1：一步完成生成+上传（返回文件服务器持久链接）
urls = generate_and_upload("一只可爱的橘猫")
print(urls)
# ['https://mjyp1.gzlex.com/jjspublic/agent/plugins/2026_3_13_xxx.png']

# 方式2：仅生成（返回即梦临时链接，24小时有效）
image_urls = generate_image("一只可爱的橘猫")
print(image_urls)

# 方式3：上传本地文件或已有URL
uploaded_url = upload_to_file_server("https://example.com/image.png")
print(uploaded_url)
```

## 参数说明

### 提交任务参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| req_key | string | 是 | 固定值: `jimeng_t2i_v40` |
| prompt | string | 是 | 生成提示词，最长800字符 |
| image_urls | array | 否 | 参考图URL，最多10张 |
| size | int | 否 | 生成面积，默认2048*2048=4194304 |
| width | int | 否 | 宽度，与height同时传才生效 |
| height | int | 否 | 高度，与width同时传才生效 |
| scale | float | 否 | 文本影响程度，默认0.5，范围[0,1] |
| force_single | bool | 否 | 强制生成单图，默认false |
| min_ratio | float | 否 | 最小宽高比，默认1/3 |
| max_ratio | float | 否 | 最大宽高比，默认3 |

### 推荐尺寸

| 分辨率 | 宽高比 | 尺寸 |
|--------|--------|------|
| 1K | 1:1 | 1024x1024 |
| 2K | 1:1 | 2048x2048 |
| 2K | 4:3 | 2304x1728 |
| 2K | 3:2 | 2496x1664 |
| 2K | 16:9 | 2560x1440 |
| 2K | 21:9 | 3024x1296 |
| 4K | 1:1 | 4096x4096 |

## 环境变量
```bash
export VOLCENGINE_ACCESS_KEY="你的AccessKey"
export VOLCENGINE_SECRET_KEY="你的SecretKey"
```
不设置则使用默认密钥。

## 文件服务器
生成后自动上传到：https://mjy.gzlex.com:8095

返回永久链接：
```
https://mjyp1.gzlex.com/jjspublic/agent/plugins/2026_3_17_xxx.png
```

## 使用示例

**文生图：**
> "用即梦生成一只猫"

**图生图：**
> "用即梦把这张图的背景换成海边"

**多图融合：**
> "用即梦将图1的服装换为图2的服装"

**指定分辨率：**
> "用即梦生成一张4K分辨率的白酒海报"

## 返回
生成完成后返回文件服务器链接（永久有效），可直接在消息中查看图片。
