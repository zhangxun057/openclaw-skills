# -*- coding: utf-8 -*-
"""电影海报 - 图生图"""
import sys, os, base64
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

ref_path = os.path.join(dst, 'liudehua_ref_0.jpg')
with open(ref_path, 'rb') as f:
    ref_bytes = f.read()
ref_b64 = f"data:image/jpeg;base64,{base64.b64encode(ref_bytes).decode()}"

prompt = """Based on the person in the reference photo, create an epic Chinese war film movie poster.

The person is a Ming Dynasty general in full battle-worn iron armor, standing heroically on the ruins of a burning fortress wall. His blue Qi Army cloak billows dramatically behind him. In his right hand he holds a double-sword raised high. His left hand grips a blood-stained Qi Army banner.

BACKGROUND: Behind him, the city of Pyongyang burns - massive flames, smoke columns rising into a dramatic dark sky. Dozens of cannons line the wall below. An army of Ming soldiers charges through the gates. Wild geese fly across a blood-red sunset sky.

COMPOSITION: He is CENTER-FRAME, full body, looking directly at the camera with fierce determination. Low angle shot makes him look heroic and towering. The burning city and army create depth behind him.

TEXT PLACEMENT: Title "平壤" in large bold Chinese calligraphy at the TOP CENTER of the image. Subtitle "THE FALL OF PYONGYANG" in English below the Chinese title. Cast name area at the bottom.

Style: Epic Hollywood blockbuster movie poster like Red Cliff or The Great Wall. Dramatic contrast, warm orange fire tones against cool blue sky. Photorealistic, 35mm cinematic grain. Ultra detailed armor textures. Grand and heroic atmosphere."""

print('调用 GPT-Image-2 (海报)...\n')
urls = generate_image(prompt, size="1024x1536", image=ref_b64, quality="high")

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'movie_poster_{i}.png')
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f'已保存: {size/1024:.0f} KB')
else:
    print('生成失败')
