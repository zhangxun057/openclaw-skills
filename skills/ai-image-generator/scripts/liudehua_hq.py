# -*- coding: utf-8 -*-
"""图生图 - quality=high"""
import sys, os, base64
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

# 读取参考图
ref_path = os.path.join(dst, 'liudehua_ref_0.jpg')
with open(ref_path, 'rb') as f:
    ref_bytes = f.read()
ref_b64 = f"data:image/jpeg;base64,{base64.b64encode(ref_bytes).decode()}"

prompt = """Keep this person's exact face and facial features from the reference photo. This is now a still from a Chinese historical war film.

The person is dressed as a Ming Dynasty general. He wears detailed iron armor with leather straps, a round iron helmet with red tassels. His blue cloak flows behind him. Double-sword at waist.

Scene: Dawn, snowy battlefield outside a fortress city. Smoke rises from burning walls. Golden hour sunrise lighting. Cinematic 35mm film grain. Real skin texture, real fabric, real metal.

Must look like a real movie still, photorealistic, not illustration."""

print(f'参考图: {len(ref_b64)} chars')
print(f'质量: high')
print(f'尺寸: 1024x1536')

urls = generate_image(prompt, size="1024x1536", image=ref_b64, quality="high")

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'liudehua_high_q_{i}.png')
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f'已保存: {size/1024:.0f} KB')
else:
    print('生成失败')
