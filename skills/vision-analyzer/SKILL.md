---
name: vision-analyzer
description: |
  阿里云百炼视觉分析工具。用于分析图片内容、提取信息、识别物体和场景。
  
  **Use this skill when:**
  (1) 用户上传图片要求分析内容
  (2) 需要识别图片中的物体、文字、场景
  (3) 需要描述图片细节
  (4) 用户说"分析这张图片"、"这张图讲了什么"、"识别图片"
  
  **Supported image formats:** JPG, JPEG, PNG, GIF, WebP
  **Max image size:** 10MB
  
  **Keywords:** 图片分析, 视觉分析, 图像识别, 识别图片, 这张图, 图片内容
---

# Vision Analyzer v0.1

基于阿里云百炼 (DashScope) qwen-vl-plus 模型的视觉分析工具。

## API 配置

API Key 存储在：`~/.openclaw/Apis.md` 第 4.2 节

```markdown
### 4.2 阿里云百炼
| 名称 | 值 | 用途 |
| API Key | `sk-c3b3d0d532ac408090f1ef09063171da` | 大模型调用 |
```

## 调用方式

### 方法 1：分析本地图片文件

```python
import requests
import base64

def analyze_image_file(image_path: str, prompt: str = "描述这张图片") -> str:
    """
    分析本地图片文件
    
    Args:
        image_path: 图片文件路径
        prompt: 分析提示词
    
    Returns:
        分析结果文本
    """
    # 读取图片并转 base64
    with open(image_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # API 配置
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
    headers = {
        'Authorization': 'Bearer sk-c3b3d0d532ac408090f1ef09063171da',
        'Content-Type': 'application/json'
    }
    
    # 构建请求
    payload = {
        'model': 'qwen-vl-plus',
        'input': {
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {'image': f'data:image/jpeg;base64,{img_base64}'},
                        {'text': prompt}
                    ]
                }
            ]
        }
    }
    
    # 调用 API
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # 提取回答
    return result['output']['choices'][0]['message']['content'][0]['text']
```

### 方法 2：分析图片 URL

```python
import requests

def analyze_image_url(image_url: str, prompt: str = "描述这张图片") -> str:
    """
    分析网络图片 URL
    
    Args:
        image_url: 图片网络地址
        prompt: 分析提示词
    
    Returns:
        分析结果文本
    """
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
    headers = {
        'Authorization': 'Bearer sk-b2f26e1e60214bddb51a92cabc38d79d',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'qwen-vl-plus',
        'input': {
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {'image': image_url},
                        {'text': prompt}
                    ]
                }
            ]
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    return result['output']['choices'][0]['message']['content'][0]['text']
```

## 使用示例

### 示例 1：基础描述

```python
# 分析桌面图片
result = analyze_image_file(
    'C:\\Users\\44452\\Desktop\\photo.jpg',
    '描述这张图片的内容'
)
print(result)
```

### 示例 2：特定问题

```python
# 询问图片中的具体问题
result = analyze_image_file(
    'C:\\Users\\44452\\Desktop\\menu.jpg',
    '这张菜单上有什么推荐菜？价格是多少？'
)
print(result)
```

### 示例 3：网络图片

```python
# 分析网络图片
result = analyze_image_url(
    'https://example.com/image.jpg',
    '这张图展示的是什么场景？'
)
print(result)
```

## 提示词技巧

| 场景 | 推荐提示词 |
|------|-----------|
| **基础描述** | "描述这张图片的内容" |
| **细节识别** | "图片中有哪些物体？分别在哪里？" |
| **文字识别** | "图片中的文字是什么？" |
| **场景分析** | "这是什么地方？在什么环境下？" |
| **情感氛围** | "这张图片传达了什么氛围或情感？" |
| **比较分析** | "左右两边有什么不同？" |

## 错误处理

```python
try:
    result = analyze_image_file('path/to/image.jpg')
    print(result)
except FileNotFoundError:
    print("错误：找不到图片文件")
except KeyError:
    print("错误：API 返回异常，请检查 API Key 是否有效")
except Exception as e:
    print(f"错误：{e}")
```

## 模型能力

**qwen-vl-plus 支持：**
- ✅ 物体识别和定位
- ✅ 场景描述
- ✅ OCR 文字识别
- ✅ 情感分析
- ✅ 多图对比（需特殊构造消息）
- ✅ 中文/英文/多语言理解

**限制：**
- 单图最大 10MB
- 支持格式：JPG, JPEG, PNG, GIF, WebP
- 复杂图表可能需要专门提示词

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v0.1 | 2026-03-21 | 初始版本，基础图片分析功能 |

## 未来迭代方向

- [ ] 支持批量图片分析
- [ ] 支持图片对比分析
- [ ] 支持特定区域裁剪分析
- [ ] 集成更多视觉模型（GPT-4V, Claude Vision 等）
- [ ] 添加结果缓存机制
- [ ] 支持视频帧分析
