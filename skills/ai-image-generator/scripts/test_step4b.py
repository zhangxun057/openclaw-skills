# -*- coding: utf-8 -*-
"""Step 4 测试: 图像生成 - 直接调用 image2_tool"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from image2_tool import generate_image, download_image

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

print(f"Prompt ({len(prompt)} 字):\n")
print(prompt[:800])
print("...\n")

# 生成图片
print("调用 GPT-Image-2...")
urls = generate_image(prompt, size="1536x1024")

if urls:
    print(f"\n获得 {len(urls)} 个 URL")
    for i, url in enumerate(urls):
        print(f"  URL {i}: {url[:80]}...")
        save_path = os.path.join(dst, f"muskill_xijiu_douyin_{i}.png")
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f"  已保存: {result} ({size/1024:.0f} KB)")
else:
    print("图片生成失败")
