# -*- coding: utf-8 -*-
"""Step 1: AI 理解需求"""
import requests
import json
import re

user_input = "张艺兴在黄果树瀑布下的黄小西音乐节（白天）的现场演唱照片"

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
   - 不需要：通用形象、抽象创意、全球知名 IP

### 第二步：生成创意方向
基于分析，生成 2-3 个创意方向。

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
    'Authorization': 'Bearer sk-c3b3d0d532ac408090f1ef09063171da',
    'Content-Type': 'application/json'
}

payload = {
    'model': 'qwen-plus',
    'input': {
        'messages': [
            {'role': 'system', 'content': '你是图像创意策划。输出严格 JSON。'},
            {'role': 'user', 'content': prompt}
        ]
    }
}

print(f"用户输入：{user_input}\n")
print("调用 qwen-plus 分析需求...")

resp = requests.post(
    'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
    headers=headers,
    json=payload,
    timeout=60
)

result = resp.json()
print(f"API 返回：{json.dumps(result, ensure_ascii=False)[:500]}")

# 兼容不同返回格式
if "output" in result and "choices" in result["output"]:
    content = result["output"]["choices"][0]["message"]["content"]
elif "output" in result and "text" in result["output"]:
    content = result["output"]["text"]
elif "choices" in result:
    content = result["choices"][0]["message"]["content"]
else:
    print(f"无法解析返回：{json.dumps(result, ensure_ascii=False)}")
    exit(1)

# 提取 JSON
match = re.search(r'\{[\s\S]*\}', content)
if match:
    analysis = json.loads(match.group())
    print("\n=== AI 分析结果 ===\n")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    
    # 保存结果
    with open('scratchpad/analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print("\n✅ 结果已保存到 scratchpad/analysis_result.json")
else:
    print(f"无法解析 JSON，原始输出：\n{content}")
