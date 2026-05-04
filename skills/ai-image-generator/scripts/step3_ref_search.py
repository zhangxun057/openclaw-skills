# -*- coding: utf-8 -*-
"""Step 2: 搜索参考图并下载"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from serper_tool import search_and_download

# 从分析结果读取搜索词
import json
with open('scratchpad/analysis_result.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

reference_query = analysis.get('reference_query', '张艺兴 演唱会')
needs_reference = analysis.get('needs_reference', False)

print(f"=== Step 2: 参考图搜索 ===\n")
print(f"需要参考图：{needs_reference}")
print(f"搜索词：{reference_query}")
print()

if not needs_reference:
    print("无需参考图，跳过此步骤。")
    sys.exit(0)

# 搜索并下载
results = search_and_download(reference_query, max_images=5)

if not results:
    print("\n❌ 未找到参考图")
    sys.exit(1)

# 保存结果
import json
output = []
for i, r in enumerate(results):
    output.append({
        "index": i,
        "url": r['url'],
        "title": r['title'],
        "base64_length": len(r['base64']),
        "file_size_kb": len(r['content']) / 1024
    })
    # 保存图片到本地
    save_path = f"scratchpad/ref_image_{i}.jpg"
    with open(save_path, 'wb') as f:
        f.write(r['content'])
    print(f"  已保存：{save_path}")

with open('scratchpad/reference_images.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 找到 {len(results)} 张参考图")
print("结果已保存到 scratchpad/reference_images.json")
