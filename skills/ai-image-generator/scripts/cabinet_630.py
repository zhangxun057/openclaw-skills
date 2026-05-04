# -*- coding: utf-8 -*-
"""餐边柜 630 大促海报"""
import sys, os, base64
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

# 读取产品图
src = r'C:\Users\44452\.openclaw\media\inbound\44326b73-4c4a-4b6d-a6b3-50df796422eb.jpg'
with open(src, 'rb') as f:
    ref_b64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"

prompt = """Based on the cabinet/sideboard in the reference photo, create a stunning e-commerce promotional poster for a "630 Grand Sale" event.

PRODUCT: Keep the exact same cabinet from the reference photo - same warm wood finish, same sliding doors with reeded glass, same tapered legs, same brass knobs. Place it in a beautiful staged room setting.

ROOM SETTING: A bright, modern minimalist living room with large floor-to-ceiling windows. Soft natural light from the left. Light oak wooden floors. A few decorative items on the cabinet: a small green plant, a ceramic vase, a stack of books, a coffee machine.

PROMOTIONAL DESIGN ELEMENTS:
- Big bold "630" text in large red/yellow gradient numbers at the TOP of the image
- Below "630": "年中大促" (Mid-Year Grand Sale) in elegant Chinese calligraphy
- Price tag badge in red circle: "限时特惠" (Limited Time Offer)
- A small banner strip at the bottom: "品质生活 从家开始" (Quality life starts at home)
- Red and gold festive accent decorations (ribbons, sparkle effects)

COMPOSITION: The cabinet is the HERO product, centered in the frame, slightly tilted 3/4 angle to show both the glass doors and the drawers. The promotional text and festive elements are above and around it without obscuring the product.

Style: Professional e-commerce product photography like Tmall or JD.com premium furniture listings. Clean, bright, aspirational. The product looks premium and desirable. Photorealistic, soft shadows, warm tones."""

print('调用 GPT-Image-2...\n')
urls = generate_image(prompt, size="1024x1536", image=ref_b64, quality="high")

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'cabinet_630_{i}.png')
        result = download_image(url, save_path)
        if result:
            print(f'已保存: {os.path.getsize(result)/1024:.0f} KB')
else:
    print('生成失败')
