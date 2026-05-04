# -*- coding: utf-8 -*-
"""Step 2 测试: 信息搜索与创意酝酿"""
import requests
import json
import re
import os

dst = os.path.expanduser("~/.openclaw/skills/ai-image-generator/scratchpad")
bocha_key = os.environ.get("BOCHA_API_KEY", "sk-130edef213334cdb8f9ae08a09a5b106")
dashscope_key = os.environ.get("DASHSCOPE_API_KEY", "sk-c3b3d0d532ac408090f1ef09063171da")

# 读取 Step 1 分析结果
with open(f'{dst}/analysis_result.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

# 提取所有 search_needed
search_queries = []
for direction in analysis.get('creative_directions', []):
    for q in direction.get('search_needed', []):
        if q not in search_queries:
            search_queries.append(q)

print("=== Step 2: 信息搜索与创意酝酿 ===\n")
print(f"搜索命题: {len(search_queries)} 个\n")

# 1. 博查批量搜索
def search_bocha(query, count=3):
    headers = {
        "Authorization": f"Bearer {bocha_key}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "count": count, "search_lang": "zh"}
    try:
        resp = requests.post(
            "https://api.bochaai.com/v1/web-search",
            headers=headers, json=payload, timeout=30
        )
        result = resp.json()
        if result.get("data") and result["data"].get("webPages"):
            return [{"title": i.get("name",""), "snippet": i.get("snippet","")[:200]}
                    for i in result["data"]["webPages"]["value"]]
    except Exception as e:
        print(f"  搜索异常: {e}")
    return []

all_results = {}
for i, query in enumerate(search_queries):
    results = search_bocha(query, count=3)
    all_results[query] = results
    print(f"  [{i+1}/{len(search_queries)}] '{query}' -> {len(results)} 条")

# 2. 整合上下文
context_text = ""
for query, results in all_results.items():
    context_text += f"\n### {query}\n"
    for r in results:
        context_text += f"- {r['title']}: {r['snippet']}\n"

print(f"\n搜索结果共 {sum(len(v) for v in all_results.values())} 条")

# 3. AI 提炼视觉细节
extract_prompt = f"""
你是一位资深视觉创意总监。以下是从搜索引擎获取的背景信息，请从中提取**关键视觉细节**，用于指导 AI 图像生成。

## 搜索结果
{context_text}

## 提取要求

请从搜索结果中提炼以下维度的视觉信息：
1. **空间与构图**：场地大小、布局、建筑结构、地标特征
2. **色彩与光影**：主色调、光线特征、阴影效果
3. **材质与纹理**：石头、水面、植被、织物、金属等
4. **标志性元素**：必须出现的符号、logo、品牌特征
5. **氛围与情绪**：场景的情绪基调

## 输出格式（严格 JSON）

{{
    "visual_details": {{
        "space": ["空间细节1", "空间细节2"],
        "color_light": ["色彩/光影细节1", "色彩/光影细节2"],
        "texture": ["材质细节1", "材质细节2"],
        "signatures": ["标志性元素1", "标志性元素2"],
        "atmosphere": ["氛围描述1"]
    }},
    "prompt_enrichment": {{
        "location_specifics": "将地点描述转化为具体的视觉语言",
        "brand_elements": "将品牌/产品描述转化为可视觉化的细节",
        "scene_mood": "场景情绪的精确描述"
    }},
    "confidence": "high/medium/low"
}}

直接输出 JSON。
"""

print("\n正在提炼视觉细节...")

headers = {
    "Authorization": f"Bearer {dashscope_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "qwen-plus",
    "input": {
        "messages": [
            {"role": "system", "content": "你是视觉创意提炼专家。输出严格 JSON。"},
            {"role": "user", "content": extract_prompt}
        ]
    }
}

resp = requests.post(
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
    headers=headers, json=payload, timeout=60
)

result = resp.json()
content = result.get("output", {}).get("text", "")

match = re.search(r'\{[\s\S]*\}', content)
if match:
    visual_details = json.loads(match.group())
    
    output = {
        "search_queries": search_queries,
        "search_results": all_results,
        "visual_details": visual_details
    }
    
    with open(f'{dst}/info_search_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nStep 2 完成")
    print(f"  置信度: {visual_details.get('confidence', 'unknown')}")
    
    vd = visual_details.get('visual_details', {})
    print(f"\n=== 提炼的视觉细节 ===\n")
    for cat, items in vd.items():
        if items:
            print(f"  {cat}:")
            for item in items:
                print(f"    - {item}")
    
    pe = visual_details.get('prompt_enrichment', {})
    if pe:
        print(f"\n  === Prompt 注入素材 ===")
        for key, val in pe.items():
            if val:
                print(f"  {key}: {val}")
    
    print(f"\n已保存到 scratchpad/info_search_result.json")
else:
    print(f"视觉细节提炼失败")
    print(content[:500])
    exit(1)
