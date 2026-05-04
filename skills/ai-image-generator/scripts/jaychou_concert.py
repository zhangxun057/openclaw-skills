# -*- coding: utf-8 -*-
"""周杰伦演唱会 - 搜参考图 → 图生图"""
import sys, os, base64
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))

import serper_tool
serper_tool.SERPER_API_KEY = "a1b5573c9dae9041939d841fd602d1abba333ee7"
serper_tool.HEADERS["X-API-KEY"] = serper_tool.SERPER_API_KEY

from serper_tool import search_and_download
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

print('=== Step 3: 搜索周杰伦参考图 ===\n')
ref_images = search_and_download("周杰伦 演唱会 高清 正面", max_images=3)

if not ref_images:
    print('参考图搜索失败')
    exit(1)

ref_path = os.path.join(dst, 'jaychou_ref_0.jpg')
with open(ref_path, 'wb') as f:
    f.write(ref_images[0]['content'])
print(f'参考图已保存: {len(ref_images[0]["content"])/1024:.0f} KB')

ref_b64 = ref_images[0]['base64']

print('\n=== Step 4: 生成演唱会现场照 ===\n')

prompt = """Based on the person in the reference photo, create a concert live photo at Qianling Mountain Park (黔灵山公园) in Guiyang, Guizhou.

The person is performing on a large outdoor concert stage set up at the famous lakeside pavilion area in Qianling Mountain Park. He is wearing a cool black leather jacket with silver details, holding a microphone, singing passionately to the audience.

SETTING: Qianling Mountain Park, Guiyang. The iconic lakeside pavilion (麒麟阁) and lush green mountains visible in the background. The stage is set up near the lake with the park's beautiful landscape around it - tall trees, the lake reflecting lights, misty mountains in the distance.

LIGHTING: Dramatic concert lighting - purple, blue, and white stage lights. Laser beams cutting through misty mountain air. LED screens on stage showing visual effects. The natural park scenery contrasts with the electric concert atmosphere.

AUDIENCE: Thousands of fans in the foreground, waving light sticks in blue glow. Camera phones raised capturing the moment. The crowd extends into the park area.

CINEMATOGRAPHY: Medium close-up from slightly below, the performer looks powerful and larger-than-life. Concert photography style with slight motion blur on background. Real skin texture, real fabric of jacket.

Style: Professional concert photography, like a real Getty Images concert photo. Photorealistic, 35mm, vivid colors, high energy atmosphere."""

print('调用 GPT-Image-2...\n')
urls = generate_image(prompt, size="1024x1536", image=ref_b64, quality="high")

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'jaychou_concert_{i}.png')
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f'已保存: {size/1024:.0f} KB')
else:
    print('生成失败')
