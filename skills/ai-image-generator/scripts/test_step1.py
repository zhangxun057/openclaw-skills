# -*- coding: utf-8 -*-
"""Step 1 测试: AI 理解需求 - 马斯克卖习酒"""
import requests
import json
import re
import os

dst = os.path.expanduser("~/.openclaw/skills/ai-image-generator/scratchpad")
os.makedirs(dst, exist_ok=True)

dashscope_key = os.environ.get("DASHSCOPE_API_KEY", "sk-c3b3d0d532ac408090f1ef09063171da")

user_input = "马斯克卖习酒1988，在抖音直播间"

prompt = f"""
你是一个图像创意策划总监。用户想要生成一张图片，请理解他的需求。

## 用户输入
"{user_input}"

## 分析任务

### 第一步：语义分析
1. **场景类型**：这是什么场景？
2. **主要主体**：有没有具体的人名/品牌名/产品名？
3. **场景元素**：有哪些关键元素？
4. **参考图需求**：
   - 需要：涉及具体人物（明星/企业家/运动员）或具体品牌/产品
   - 不需要：通用形象、抽象创意
5. **背景复杂度评估**：
   - 如果参考图中主体背景杂乱 → background_cluttered: true
   - 如果参考图中主体背景干净 → background_cluttered: false

### 第二步：生成创意方向
基于分析，生成 2-3 个创意方向。

### 第三步：提取搜索命题
为每个创意方向，列出需要搜索的背景信息（3-5 个命题）。

## 输出格式（严格 JSON）

{{
    "scene_type": "...",
    "main_subject": ["...", "..."],
    "scene_elements": ["...", "..."],
    "needs_reference": true/false,
    "reference_query": "如果需要，搜索词，否则 null",
    "reference_reason": "为什么需要/不需要参考图",
    "background_cluttered": true/false,
    "creative_directions": [
        {{
            "name": "方向名称（4-8 字）",
            "concept": "核心概念（15-30 字）",
            "visual": "视觉描述（50-100 字）",
            "search_needed": ["搜索命题 1", "搜索命题 2"]
        }}
    ],
    "recommended_direction_index": 0,
    "reasoning": "分析逻辑（100-200 字）"
}}

直接输出 JSON，不要有任何额外文字。
"""

headers = {
    "Authorization": f"Bearer {dashscope_key}",
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

print("=== Step 1: AI 理解需求 ===\n")
print(f"用户输入: {user_input}\n")

resp = requests.post(
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
    headers=headers,
    json=payload,
    timeout=60
)

result = resp.json()

# 兼容两种格式
content = None
if "output" in result:
    if "choices" in result["output"] and result["output"]["choices"]:
        content = result["output"]["choices"][0].get("message", {}).get("content")
    if not content and "text" in result["output"]:
        content = result["output"]["text"]

if not content:
    print(f"API 响应异常: {json.dumps(result, ensure_ascii=False, indent=2)}")
    exit(1)

# 提取 JSON
match = re.search(r'\{[\s\S]*\}', content)
if match:
    analysis = json.loads(match.group())
    with open(f'{dst}/analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print("Step 1 完成\n")
    print(f"场景类型: {analysis.get('scene_type')}")
    print(f"主要主体: {analysis.get('main_subject')}")
    print(f"场景元素: {', '.join(analysis.get('scene_elements', []))}")
    print(f"需要参考图: {analysis.get('needs_reference')}")
    print(f"搜索词: {analysis.get('reference_query')}")
    print(f"背景复杂: {analysis.get('background_cluttered')}")
    print(f"\n创意方向: {len(analysis.get('creative_directions', []))} 个")
    for i, d in enumerate(analysis.get('creative_directions', [])):
        print(f"  [{i+1}] {d['name']}: {d['concept']}")
        sq = d.get('search_needed', [])
        for s in sq:
            print(f"       需搜索: {s}")
    print(f"\n推荐: 方向 {analysis.get('recommended_direction_index') + 1}")
    print(f"\n已保存到 scratchpad/analysis_result.json")
else:
    print(f"无法提取 JSON\n原始输出:\n{content}")
    exit(1)
