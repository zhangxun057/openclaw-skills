# -*- coding: utf-8 -*-
"""Step 2: 信息搜索与创意酝酿"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json
import re


def search_bocha(query, count=5, api_key=None):
    """博查搜索 API，获取背景信息"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "count": count,
        "search_lang": "zh"
    }

    resp = requests.post(
        "https://api.bochaai.com/v1/web-search",
        headers=headers,
        json=payload,
        timeout=30
    )

    result = resp.json()
    if result.get("data") and result["data"].get("webPages"):
        return [
            {
                "title": item.get("name", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("url", "")
            }
            for item in result["data"]["webPages"]["value"]
        ]
    return []


def extract_visual_details(search_results_text, dashscope_key):
    """用 AI 从搜索结果中提炼视觉细节"""
    prompt = f"""
你是一位资深视觉创意总监。以下是从搜索引擎获取的背景信息，请从中提取**关键视觉细节**，用于指导 AI 图像生成。

## 搜索结果
{search_results_text}

## 提取要求

请从搜索结果中提炼以下维度的视觉信息：

1. **空间与构图**：场地大小、布局、建筑结构、地标特征
2. **色彩与光影**：主色调、光线特征、阴影效果
3. **材质与纹理**：石头、水面、植被、织物、金属等
4. **标志性元素**：必须出现的符号、logo、品牌特征
5. **氛围与情绪**：场景的情绪基调（庄严/活力/宁静/浪漫）

## 输出格式（JSON）

{{
    "visual_details": {{
        "space": ["空间细节1", "空间细节2"],
        "color_light": ["色彩/光影细节1", "色彩/光影细节2"],
        "texture": ["材质细节1", "材质细节2"],
        "signatures": ["标志性元素1", "标志性元素2"],
        "atmosphere": ["氛围描述1"]
    }},
    "prompt_enrichment": {{
        "location_specifics": "将通用地点描述转化为具体的视觉语言",
        "brand_elements": "将品牌/产品描述转化为可视觉化的细节",
        "scene_mood": "场景情绪的精确描述"
    }},
    "confidence": "high/medium/low"
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
                {"role": "system", "content": "你是视觉创意提炼专家。输出严格 JSON。"},
                {"role": "user", "content": prompt}
            ]
        }
    }

    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        headers=headers,
        json=payload,
        timeout=60
    )

    result = resp.json()
    content = result["output"]["choices"][0]["message"]["content"]

    match = re.search(r'\{[\s\S]*\}', content)
    if match:
        return json.loads(match.group())
    return None


def main():
    """主流程：读取分析结果 → 搜索 → 提炼 → 保存"""
    bocha_key = os.environ.get("BOCHA_API_KEY", "")
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY", "")

    if not bocha_key or not dashscope_key:
        print("请设置环境变量 BOCHA_API_KEY 和 DASHSCOPE_API_KEY")
        sys.exit(1)

    # 读取 Step 1 的分析结果
    with open('scratchpad/analysis_result.json', 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    search_queries = []
    for direction in analysis.get('creative_directions', []):
        for q in direction.get('search_needed', []):
            if q not in search_queries:
                search_queries.append(q)

    if not search_queries:
        print("无需信息搜索，跳过。")
        sys.exit(0)

    print(f"=== Step 2: 信息搜索与创意酝酿 ===\n")
    print(f"搜索命题：{len(search_queries)} 个\n")

    # 1. 批量搜索
    all_results = {}
    for i, query in enumerate(search_queries):
        results = search_bocha(query, count=3, api_key=bocha_key)
        all_results[query] = results
        print(f"  [{i+1}/{len(search_queries)}] '{query}' → {len(results)} 条结果")

    # 2. 整合为上下文文本
    context_text = ""
    for query, results in all_results.items():
        context_text += f"\n### 命题：{query}\n"
        for r in results:
            context_text += f"- {r['title']}: {r['snippet'][:200]}\n"

    print(f"\n正在提炼视觉细节...")

    # 3. AI 提炼
    visual_details = extract_visual_details(context_text, dashscope_key)

    if not visual_details:
        print("视觉细节提炼失败")
        sys.exit(1)

    # 4. 保存结果
    output = {
        "search_queries": search_queries,
        "search_results": all_results,
        "visual_details": visual_details
    }

    with open('scratchpad/info_search_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n信息搜索完成")
    print(f"  搜索命题：{len(search_queries)} 个")
    print(f"  搜索结果：{sum(len(v) for v in all_results.values())} 条")
    print(f"  视觉细节置信度：{visual_details.get('confidence', 'unknown')}")
    print(f"\n结果已保存到 scratchpad/info_search_result.json")

    # 5. 展示提炼的视觉细节
    print(f"\n=== 提炼的视觉细节 ===\n")
    vd = visual_details.get('visual_details', {})
    for category, items in vd.items():
        if items:
            print(f"  {category}:")
            for item in items:
                print(f"    - {item}")

    pe = visual_details.get('prompt_enrichment', {})
    if pe:
        print(f"\n  === Prompt 注入素材 ===")
        for key, val in pe.items():
            if val:
                print(f"  {key}: {val}")


if __name__ == "__main__":
    main()
