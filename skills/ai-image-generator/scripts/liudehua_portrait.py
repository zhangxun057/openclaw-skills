# -*- coding: utf-8 -*-
"""先生成 1 张写实主角定妆照确认风格"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

prompt = """Photorealistic movie still from a Chinese historical war epic film. 

The main character: A man who strongly resembles Andy Lau (刘德华), age around 50, with a handsome face, defined jawline, thin mustache, serious determined expression. He is a Ming Dynasty general.

He wears detailed Ming Dynasty iron armor with leather straps, a round iron helmet with red tassels, and carries a double-sword at his waist. His armor shows battle wear - dents, scratches, dried blood.

The scene: He stands at dawn in a snowy battlefield outside a fortress city (Pyongyang). His blue cloak flows in the cold wind behind him. In the background, smoke rises from the burning city walls. Cannon positions visible.

Lighting: Golden hour sunrise, warm and cold contrast. Cinematic film quality, 35mm grain. Real skin texture, real fabric, real iron metal. Shot like a Ridley Scott historical epic.

Must look like a REAL PHOTOGRAPH, not a painting or illustration. Real actor on a real film set. Photorealistic."""

print('调用 GPT-Image-2...')
urls = generate_image(prompt, size="1024x1536")

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'liudehua_general_{i}.png')
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f'已保存: {result} ({size/1024:.0f} KB)')
else:
    print('生成失败')
