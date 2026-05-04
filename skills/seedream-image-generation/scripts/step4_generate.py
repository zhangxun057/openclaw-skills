# -*- coding: utf-8 -*-
"""Step 4: 图像生成"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import base64

# 读取分析结果
with open('scratchpad/analysis_result.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

# 读取参考图
with open('scratchpad/verified_images.json', 'r', encoding='utf-8') as f:
    verified = json.load(f)

# 使用推荐的 #2 参考图
ref_img = verified[2]  # #2 是评分最高的
ref_path = ref_img['path']

print("=== Step 4: 图像生成 ===\n")
print(f"使用参考图：#{ref_img['index']}")
print(f"路径：{ref_path}")
print(f"标题：{ref_img['title'][:60]}...")

# 读取参考图为 base64
with open(ref_path, 'rb') as f:
    ref_bytes = f.read()
ref_base64 = base64.b64encode(ref_bytes).decode('utf-8')
print(f"参考图大小：{len(ref_bytes)/1024:.1f}KB")

# 构建 Prompt（基于 AI 分析的创意方向）
creative_dir = analysis['creative_directions'][analysis['recommended_direction_index']]

# 深化 Prompt（加入参考图信息）
prompt = f"""
{creative_dir['visual']}

关键元素：
- 主体：张艺兴（参考图中的人物形象、发型、服装风格）
- 场景：黄果树大瀑布前的户外音乐节舞台
- 时间：白天，阳光明媚
- 活动：黄小西音乐节现场演唱
- 氛围：激情、动感、自然与音乐交融
- 细节：瀑布水流、水雾彩虹、观众剪影、舞台灯光

风格：专业商业摄影，高清晰度，色彩鲜明，构图平衡
"""

print(f"\n生成 Prompt:\n{prompt[:300]}...\n")

# 调用 Image2 API
from image2_tool import generate_and_save

print("正在调用 GPT-Image-2 生成图片...")
print("这可能需要 1-3 分钟，请耐心等待...\n")

paths = generate_and_save(
    prompt=prompt.strip(),
    size="1024x1792",  # 竖版海报比例
    image=f"data:image/jpeg;base64,{ref_base64}",
    save_dir="scratchpad"
)

if paths:
    print(f"\n生成成功！")
    for p in paths:
        print(f"  保存路径：{p}")
    
    # 保存生成记录
    record = {
        "prompt": prompt,
        "reference_image": ref_img,
        "output_paths": paths,
        "creative_direction": creative_dir
    }
    with open('scratchpad/generation_record.json', 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    
    print("\n生成记录已保存到 scratchpad/generation_record.json")
else:
    print("\n生成失败，请检查 API 响应")
