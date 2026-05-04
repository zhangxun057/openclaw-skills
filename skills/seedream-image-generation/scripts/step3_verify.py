# -*- coding: utf-8 -*-
"""Step 3: 视觉验证参考图"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from vision_tool import full_verify
import json

print("=== Step 3: 视觉验证参考图 ===\n")

# 读取参考图列表
with open('scratchpad/reference_images.json', 'r', encoding='utf-8') as f:
    ref_images = json.load(f)

# 读取分析结果（获取期望类型）
with open('scratchpad/analysis_result.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

main_subject = analysis.get('main_subject', 'person')
print(f"主要主体：{main_subject}")
print(f"需要验证 {len(ref_images)} 张图片\n")

# 验证每张图
valid_images = []
for i, img in enumerate(ref_images):
    img_path = f"scratchpad/ref_image_{i}.jpg"
    
    if not os.path.exists(img_path):
        print(f"[{i}] 文件不存在：{img_path}")
        continue
    
    print(f"[{i}] 验证：{img['title'][:60]}...")
    
    with open(img_path, 'rb') as f:
        image_bytes = f.read()
    
    result = full_verify(image_bytes, expected_type="person")
    
    print(f"    分辨率：{result['resolution'].get('width', '?')}x{result['resolution'].get('height', '?')} [{result['resolution'].get('level', '?')}]")
    print(f"    主体识别：{result['content'].get('main_subject', '?')}")
    print(f"    清晰度：{'OK' if result['content'].get('clarity_ok') else 'FAIL'}")
    print(f"    分辨率判定：{'OK' if result['content'].get('resolution_ok') else 'FAIL'}")
    print(f"    综合结果：{'PASS' if result['pass'] else 'FAIL'}")
    
    if result['pass']:
        valid_images.append({
            "index": i,
            "path": img_path,
            "url": img['url'],
            "title": img['title'],
            "verification": result
        })
        print(f"    -> 通过，加入候选列表")
    print()

print(f"=== 验证完成 ===")
print(f"通过：{len(valid_images)}/{len(ref_images)} 张")

# 保存结果
with open('scratchpad/verified_images.json', 'w', encoding='utf-8') as f:
    json.dump(valid_images, f, ensure_ascii=False, indent=2)

if valid_images:
    # 推荐最佳图片（第一个通过的）
    best = valid_images[0]
    print(f"\n推荐参考图：#{best['index']}")
    print(f"  路径：{best['path']}")
    print(f"  URL: {best['url']}")
    print(f"  标题：{best['title']}")
else:
    print("\n没有图片通过验证，需要重新搜索或手动指定。")
