# -*- coding: utf-8 -*-
"""Step 1: 理解需求 - 贵阳自驾重庆手绘地图"""
import requests, json, re, os

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')
os.makedirs(dst, exist_ok=True)
key = 'sk-c3b3d0d532ac408090f1ef09063171da'

user_input = '生成一张贵阳自驾重庆的旅游路线手绘地图。路线：贵阳出发->重庆市区->大足石刻->返回重庆->武隆（仙女山国家公园、天生三桥）->途经贵州湄潭->返回贵阳。时间4月30日-5月5日。用于成团宣传。要求地理位置准确。'

prompt = f"""你是一个图像创意策划总监。用户想要生成一张图片，请理解他的需求。

用户输入："{user_input}"

分析任务：
1. 场景类型
2. 主要主体
3. 场景元素
4. 参考图需求
5. 背景复杂度评估
6. 生成 2-3 个创意方向
7. 为每个创意方向提取搜索命题（关键地理信息、手绘风格参考）

输出严格 JSON：{{
    "scene_type": "...",
    "main_subject": ["..."],
    "scene_elements": ["..."],
    "needs_reference": true/false,
    "reference_query": "...",
    "reference_reason": "...",
    "background_cluttered": true/false,
    "creative_directions": [
        {{
            "name": "方向名称",
            "concept": "核心概念",
            "visual": "视觉描述",
            "search_needed": ["搜索命题1", "搜索命题2"]
        }}
    ],
    "recommended_direction_index": 0,
    "reasoning": "分析逻辑"
}}"""

headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
payload = {'model': 'qwen-plus', 'input': {'messages': [
    {'role': 'system', 'content': '你是图像创意策划。输出严格 JSON。'},
    {'role': 'user', 'content': prompt}
]}}

resp = requests.post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
    headers=headers, json=payload, timeout=60)
result = resp.json()
content = result.get('output', {}).get('text', '')

match = re.search(r'\{[\s\S]*\}', content)
if match:
    analysis = json.loads(match.group())
    with open(f'{dst}/analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print('Step 1 OK')
    print(f'场景: {analysis.get("scene_type")}')
    print(f'主体: {analysis.get("main_subject")}')
    print(f'创意方向: {len(analysis.get("creative_directions", []))} 个')
    for d in analysis.get('creative_directions', []):
        print(f'  [{d["name"]}] {d["concept"][:50]}')
        for s in d.get('search_needed', []):
            print(f'    搜索: {s}')
else:
    print('Step 1 failed')
    print(content[:500])
