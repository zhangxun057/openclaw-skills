# seedream-image-generation

## 触发条件
用户要求用Seedream生成图片、使用字节生图、AI生图时激活。

## 功能
调用字节Seedream图像生成API，支持文生图、图生图、多图融合、组图，生成后自动上传到文件服务器返回持久化链接。

## 接口信息
- **URL**: https://ark.cn-beijing.volces.com/api/v3/images/generations
- **API Key**: 环境变量 ARK_API_KEY

## 支持模型

| 模型 | 说明 | 支持功能 |
|------|------|----------|
| doubao-seedream-5.0-lite | 最新版本 | 联网搜索、组图、多图融合、png输出 |
| doubao-seedream-4-5-251128 | 当前使用 | 4.5版本、文生图、图生图、多图融合 |
| doubao-seedream-4.0 | 经典版 | 1K/2K/4K |
| doubao-seedream-3.0-t2i | 轻量版 | 仅文生图 |

## 使用方式

### 命令行
```bash
cd ~/.openclaw/workspace/skills/seedream-image-generation/scripts

# 文生图
python3 seedream_api.py generate-upload "一只猫"

# 单图生图（图生图）
python3 seedream_api.py generate-upload "将背景换成海边" --image "https://xxx.jpg"

# 多图融合
python3 seedream_api.py generate-upload "将图1的服装换为图2的服装" --images "URL1,URL2"

# 组图模式
python3 seedream_api.py generate-upload "生成4张不同颜色的跑车" --sequential --max-images 4

# 指定参数
python3 seedream_api.py generate-upload "提示词" --size 4K --format png
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --model | 模型版本 | doubao-seedream-4-5-251128 |
| --size | 分辨率 | 2K |
| --watermark | 加水印 | false |
| --image | 单张参考图URL | - |
| --images | 多张参考图URL（逗号分隔） | - |
| --sequential | 开启组图模式 | disabled |
| --max-images | 最大图片数 | 15 |
| --format | 输出格式 (png/jpeg) | png |

### 分辨率选项

| 分辨率 | 像素 |
|--------|------|
| 1K | 1024x1024 |
| 2K | 2048x2048 |
| 3K | 3072x3072 (仅5.0-lite) |
| 4K | 4096x4096 |

## 环境变量
```bash
export ARK_API_KEY="你的API Key"
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
> "用Seedream生成一只猫"

**图生图：**
> "用Seedream把这张图的背景换成海边"

**多图融合：**
> "用Seedream将图1的服装换为图2的服装"

**组图：**
> "用Seedream生成4张不同风格的城市风景图"

**指定分辨率和格式：**
> "用Seedream生成一张4K分辨率的白酒海报"

## 返回
生成完成后返回文件服务器链接（永久有效），可直接在消息中查看图片。
