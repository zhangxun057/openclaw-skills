# -*- coding: utf-8 -*-
"""Step 1+2: 剧本设计 + 历史信息搜索"""
import requests, json, re, os

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')
os.makedirs(dst, exist_ok=True)
bocha_key = 'sk-130edef213334cdb8f9ae08a09a5b106'
dash_key = 'sk-c3b3d0d532ac408090f1ef09063171da'

def search_bocha(query, count=3):
    headers = {'Authorization': f'Bearer {bocha_key}', 'Content-Type': 'application/json'}
    payload = {'query': query, 'count': count, 'search_lang': 'zh'}
    try:
        resp = requests.post('https://api.bochaai.com/v1/web-search',
            headers=headers, json=payload, timeout=30)
        r = resp.json()
        if r.get('data') and r['data'].get('webPages'):
            return [{'title': i.get('name',''), 'snippet': i.get('snippet','')[:300]}
                    for i in r['data']['webPages']['value']]
    except: pass
    return []

# 搜索关键历史信息
queries = [
    "万历朝鲜战争 戚继光 戚家军 平壤之战 历史",
    "平壤之战 1593 李如松 刘綎 碧蹄馆",
    "明朝军队 攻城战 朝鲜 万历 战术 武器",
    "戚家军 鸳鸯阵 藤牌 鸟铳 编制",
    "万历朝鲜之役 日军 小西行长 平壤城防"
]

print('=== 搜索历史信息 ===\n')
all_results = {}
for i, q in enumerate(queries):
    results = search_bocha(q, count=3)
    all_results[q] = results
    print(f'  [{i+1}/{len(queries)}] {q}')
    for r in results[:1]:
        print(f'    - {r["title"][:50]}')

# 整合
context = ''
for q, results in all_results.items():
    context += f'\n### {q}\n'
    for r in results:
        context += f'- {r["title"]}: {r["snippet"]}\n'

# AI 设计剧本
prompt = f"""你是一位资深编剧和军事历史顾问。请基于以下历史资料，设计一个以万历朝鲜战争为背景的古装战争剧本，并输出9格分镜图的详细描述。

## 历史背景
- 万历朝鲜战争（1592-1598），明朝派军援朝抗倭
- 戚家军：戚继光创建的精锐部队，以鸳鸯阵闻名
- 平壤之战（1593年1月）：明军收复平壤的关键战役
- 主角由刘德华饰演，应是戚家军中的核心将领

## 搜索结果
{context}

## 要求

### 1. 剧本大纲（200字以内）
围绕"戚家军攻打平壤城"展开，刘德华饰演主角

### 2. 九宫格分镜设计
为9个关键场景设计分镜，每个分镜包含：
- 画面描述（50-100字，详细到构图、人物、光影、动作）
- 情绪/氛围
- 时序位置（故事中的哪个阶段）

### 3. 角色设计
刘德华饰演的角色信息

## 输出严格 JSON
{{
    "script_outline": {{
        "title": "电影名称",
        "genre": "古装战争",
        "logline": "一句话概括（30字）",
        "synopsis": "剧本大纲（200字）"
    }},
    "protagonist": {{
        "name": "角色名",
        "rank": "职位",
        "personality": "性格特点",
        "appearance": "刘德华在这个角色中的造型描述"
    }},
    "storyboard": [
        {{
            "panel": 1,
            "title": "场景名称",
            "phase": "故事阶段",
            "visual": "详细画面描述（构图、人物动作、光影、氛围）",
            "emotion": "情绪基调"
        }}
    ]
}}"""

headers = {'Authorization': f'Bearer {dash_key}', 'Content-Type': 'application/json'}
payload = {'model': 'qwen-plus', 'input': {'messages': [
    {'role': 'system', 'content': '你是资深编剧+军事历史顾问。输出严格 JSON。'},
    {'role': 'user', 'content': prompt}
]}}

print('\n设计剧本和分镜...')
resp = requests.post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
    headers=headers, json=payload, timeout=120)
result = resp.json()
content = result.get('output', {}).get('text', '')

match = re.search(r'\{[\s\S]*\}', content)
if match:
    script = json.loads(match.group())
    with open(f'{dst}/script_result.json', 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    
    print('\n=== 剧本设计完成 ===\n')
    so = script.get('script_outline', {})
    print(f'片名: {so.get("title")}')
    print(f'类型: {so.get("genre")}')
    print(f'Logline: {so.get("logline")}')
    print(f'\n大纲: {so.get("synopsis", "")[:150]}...')
    
    p = script.get('protagonist', {})
    print(f'\n主角: {p.get("name")} - {p.get("rank")}')
    print(f'性格: {p.get("personality")}')
    print(f'造型: {p.get("appearance", "")[:80]}...')
    
    print(f'\n=== 九宫格分镜 ===\n')
    for panel in script.get('storyboard', []):
        print(f'  {panel["panel"]}. [{panel["title"]}] {panel["phase"]}')
        print(f'     {panel["visual"][:80]}...')
        print(f'     情绪: {panel["emotion"]}')
    
    print(f'\n已保存到 scratchpad/script_result.json')
else:
    print('剧本设计失败')
    print(content[:500])
