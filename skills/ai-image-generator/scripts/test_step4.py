# -*- coding: utf-8 -*-
"""Step 4 测试: 图像生成 - 马斯克卖习酒1988"""
import requests
import json
import base64
import os
import time

dst = os.path.expanduser("~/.openclaw/skills/ai-image-generator/scratchpad")

# 读取分析结果
with open(f'{dst}/analysis_result.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

# 读取信息搜索结果
info_search = None
if os.path.exists(f'{dst}/info_search_result.json'):
    with open(f'{dst}/info_search_result.json', 'r', encoding='utf-8') as f:
        info_search = json.load(f)

# 使用推荐的创意方向
rec_idx = analysis.get('recommended_direction_index', 0)
creative_dir = analysis['creative_directions'][rec_idx]

print("=== Step 4: 图像生成 ===\n")
print(f"创意方向: {creative_dir['name']}")
print(f"核心概念: {creative_dir['concept']}\n")

# 构建 Prompt
prompt_lines = [creative_dir['visual'], "", "关键元素："]

# 注入 Step 2 的视觉细节
if info_search and info_search.get('visual_details'):
    vd = info_search['visual_details']
    prompt_lines.append("")
    prompt_lines.append("【真实场景细节】")
    for category in ['space', 'color_light', 'texture', 'signatures', 'atmosphere']:
        details = vd.get(category, [])
        for d in details:
            prompt_lines.append(f"- {d}")

if info_search and info_search.get('prompt_enrichment'):
    pe = info_search['prompt_enrichment']
    for key in ['location_specifics', 'brand_elements', 'scene_mood']:
        if pe.get(key):
            prompt_lines.append(f"- {pe[key]}")

prompt_lines.extend(["", "风格：专业商业摄影，高清晰度，色彩鲜明，构图平衡，16:9横幅"])
prompt = "\n".join(prompt_lines)

print(f"生成 Prompt ({len(prompt)} 字):\n")
print(prompt[:500])
print("...\n")

# 调用 GPT-Image-2 API
api_key = os.environ.get("IMAGE2_API_KEY", "sk-C4fVi6uZ78vS0Ip4F0fr8ySnCP5KOwGbCqfWZfiRUfGwnZVm")
base_url = "https://api.apimart.ai"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "gpt-image-2",
    "prompt": prompt,
    "n": 1,
    "size": "1536x1024",
    "quality": "high"
}

print("正在调用 GPT-Image-2 生成图片...")
start = time.time()

resp = requests.post(
    f"{base_url}/v1/images/generations",
    headers=headers,
    json=payload,
    timeout=120
)

elapsed = time.time() - start
result = resp.json()

if resp.status_code == 200 and result.get("data"):
    img_data = result["data"][0]
    
    if img_data.get("b64_json"):
        img_bytes = base64.b64decode(img_data["b64_json"])
        filename = f"muskill_xijiu_douyin.png"
        filepath = f"{dst}/{filename}"
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
        print(f"\n生成完成! ({elapsed:.1f}s)")
        print(f"文件: {filepath}")
        print(f"大小: {len(img_bytes)/1024:.0f} KB")
    elif img_data.get("url"):
        print(f"\n生成完成! ({elapsed:.1f}s)")
        print(f"URL: {img_data['url']}")
        # 下载
        img_resp = requests.get(img_data["url"], timeout=30)
        if img_resp.status_code == 200:
            filename = f"muskill_xijiu_douyin.png"
            filepath = f"{dst}/{filename}"
            with open(filepath, 'wb') as f:
                f.write(img_resp.content)
            print(f"已下载到: {filepath}")
            print(f"大小: {len(img_resp.content)/1024:.0f} KB")
else:
    print(f"\n生成失败:")
    print(f"HTTP {resp.status_code}")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
