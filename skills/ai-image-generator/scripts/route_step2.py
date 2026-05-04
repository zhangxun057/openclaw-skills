# -*- coding: utf-8 -*-
"""Step 2: 地理信息搜索 - 确保路线准确"""
import requests, json, os

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')
bocha_key = 'sk-130edef213334cdb8f9ae08a09a5b106'

# 核心地理命题 - 确保位置准确
geo_queries = [
    "贵阳到重庆自驾路线 G75兰海高速 经过城市",
    "重庆到大足石刻 自驾距离 多少公里 方位",
    "重庆到武隆 自驾路线 方位 距离",
    "武隆仙女山国家公园 天生三桥 相对位置",
    "武隆到贵州湄潭 自驾路线 经过哪些地方",
    "湄潭到贵阳 自驾距离 G69银百高速",
    "贵阳重庆武隆大足湄潭 地理位置关系 相对方位"
]

def search_bocha(query, count=3):
    headers = {'Authorization': f'Bearer {bocha_key}', 'Content-Type': 'application/json'}
    payload = {'query': query, 'count': count, 'search_lang': 'zh'}
    try:
        resp = requests.post('https://api.bochaai.com/v1/web-search',
            headers=headers, json=payload, timeout=30)
        result = resp.json()
        if result.get('data') and result['data'].get('webPages'):
            return [{'title': i.get('name',''), 'snippet': i.get('snippet','')[:300]}
                    for i in result['data']['webPages']['value']]
    except Exception as e:
        print(f'  搜索异常: {e}')
    return []

print('=== Step 2: 地理信息搜索 ===\n')

all_results = {}
for i, q in enumerate(geo_queries):
    results = search_bocha(q, count=3)
    all_results[q] = results
    print(f'  [{i+1}/{len(geo_queries)}] {q}')
    for r in results:
        print(f'    - {r["title"][:40]}')

# 整合上下文
context = ''
for q, results in all_results.items():
    context += f'\n### {q}\n'
    for r in results:
        context += f'- {r["title"]}: {r["snippet"]}\n'

# AI 提炼地理关键信息
key = 'sk-c3b3d0d532ac408090f1ef09063171da'

extract_prompt = f"""你是一位地图设计师。请从以下搜索结果中提取**精确的地理信息**，用于绘制手绘路线图。

## 路线概览
贵阳 → 重庆市区 → 大足石刻 → 重庆市区 → 武隆(仙女山+天生三桥) → 贵州湄潭 → 贵阳

## 搜索结果
{context}

## 提取要求

请提取以下精确信息：
1. **各城市相对方位**：每个城市在图上的大致方向（东/南/西/北/东南/西北等）
2. **城市间距离**：主要路段的大致距离（公里）
3. **高速公路/主要道路**：连接各城市的主要高速名称和编号
4. **沿途关键地标**：画在地图上的标志性建筑/景点
5. **地形特征**：山地/河流/平原等影响路线走向的地理特征

## 输出严格 JSON
{{
    "cities_relative_position": {{
        "贵阳": "图中位置描述",
        "重庆": "相对于贵阳的方向",
        "大足石刻": "相对于重庆的方向和距离",
        "武隆": "相对于重庆的方向和距离",
        "仙女山": "相对于武隆的位置",
        "天生三桥": "相对于武隆/仙女山的位置",
        "湄潭": "相对于武隆的方向和距离"
    }},
    "routes": [
        {{"from": "...", "to": "...", "road": "G75兰海高速", "distance_km": 350, "direction": "东北"}},
        ...
    ],
    "landmarks": ["...", "..."],
    "terrain": "地形描述",
    "map_layout_suggestion": "在图上如何排列这些城市和路线"
}}

直接输出 JSON。"""

headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
payload = {'model': 'qwen-plus', 'input': {'messages': [
    {'role': 'system', 'content': '你是地图设计师。输出严格 JSON。'},
    {'role': 'user', 'content': extract_prompt}
]}}

print('\n提炼地理信息...')
resp = requests.post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
    headers=headers, json=payload, timeout=60)
result = resp.json()
content = result.get('output', {}).get('text', '')

import re
match = re.search(r'\{[\s\S]*\}', content)
if match:
    geo_info = json.loads(match.group())
    
    output = {
        'search_results': all_results,
        'geo_info': geo_info
    }
    with open(f'{dst}/info_search_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print('\n地理信息提炼完成:\n')
    print('=== 城市相对方位 ===')
    for city, pos in geo_info.get('cities_relative_position', {}).items():
        print(f'  {city}: {pos}')
    print('\n=== 路线 ===')
    for route in geo_info.get('routes', []):
        print(f'  {route.get("from")} → {route.get("to")}: {route.get("road")} ({route.get("distance_km")}km, {route.get("direction")})')
    print(f'\n=== 地形 ===')
    print(f'  {geo_info.get("terrain", "")}')
    print(f'\n=== 布局建议 ===')
    print(f'  {geo_info.get("map_layout_suggestion", "")}')
    print(f'\n地标: {", ".join(geo_info.get("landmarks", []))}')
else:
    print('地理信息提炼失败')
    print(content[:500])
