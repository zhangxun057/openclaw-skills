# -*- coding: utf-8 -*-
"""拼接九宫格 v2"""
from PIL import Image
import os
dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

panels = []
for i in range(1, 10):
    path = os.path.join(dst, f'panel_v2_{i}.png')
    if os.path.exists(path):
        img = Image.open(path).resize((512, 768), Image.LANCZOS)
        panels.append(img)

gap = 6
w, h = 512, 768
canvas = Image.new('RGB', (w*3+gap*4, h*3+gap*4), (15, 15, 15))
for idx, img in enumerate(panels):
    row, col = idx // 3, idx % 3
    canvas.paste(img, (gap+col*(w+gap), gap+row*(h+gap)))

out = os.path.join(dst, 'storyboard_v2_9grid.png')
canvas.save(out, quality=95)
print(f'九宫格已保存: {out} ({os.path.getsize(out)/1024:.0f} KB)')
