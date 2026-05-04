# -*- coding: utf-8 -*-
"""完整流程: 搜索刘德华参考图 → 图生图"""
import sys, os, json, base64
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))

# 设置正确的 Serper Key
import serper_tool
serper_tool.SERPER_API_KEY = "a1b5573c9dae9041939d841fd602d1abba333ee7"
serper_tool.HEADERS["X-API-KEY"] = serper_tool.SERPER_API_KEY

from serper_tool import search_and_download
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

print('=== Step 3: 搜索参考图 ===\n')

# 搜索刘德华高清照片
ref_images = search_and_download("刘德华 帅气 高清 正面 全身照", max_images=3)

if not ref_images:
    print('参考图搜索失败')
    exit(1)

# 保存第一张参考图
ref_path = os.path.join(dst, 'liudehua_ref_0.jpg')
with open(ref_path, 'wb') as f:
    f.write(ref_images[0]['content'])
print(f'\n参考图已保存: {ref_path} ({len(ref_images[0]["content"])/1024:.0f} KB)')

# 用参考图进行图生图
print('\n=== Step 4: 图生图（基于参考图）===\n')

ref_b64 = ref_images[0]['base64']

prompt = """This person is now in a Ming Dynasty historical war film scene. Keep the person's exact face and facial features from the reference photo.

The person is dressed as a Ming Dynasty general. He wears detailed iron Ming armor with leather straps, a round iron helmet with red tassels, and carries a double-sword. His blue cloak flows behind him.

Scene: He stands at dawn in a snowy battlefield outside Pyongyang fortress. Smoke rises from burning walls in the background. Golden hour sunrise lighting. Cinematic 35mm film quality.

Must keep the person's face exactly as in the reference photo. Photorealistic movie still."""

print(f'调用 GPT-Image-2 (带参考图, {len(ref_b64)} 字符 base64)...')

# 使用图生图模式
urls = generate_image(prompt, size="1024x1536", image=ref_b64)

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'liudehua_i2i_{i}.png')
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f'\n图生图完成: {result} ({size/1024:.0f} KB)')
else:
    print('图生图失败')
