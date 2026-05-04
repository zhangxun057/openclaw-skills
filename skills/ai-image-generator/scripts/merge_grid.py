# -*- coding: utf-8 -*-
"""拼接九宫格"""
from PIL import Image
import os, glob

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

# 加载9张图
panels = []
for i in range(1, 10):
    path = os.path.join(dst, f'panel_{i}_0.png')
    if os.path.exists(path):
        img = Image.open(path)
        # 统一尺寸
        img = img.resize((512, 768), Image.LANCZOS)
        panels.append(img)
        print(f'  加载: panel_{i} ({img.size})')

if len(panels) != 9:
    print(f'只有 {len(panels)} 张图，需要 9 张')
    exit(1)

# 3x3 拼接
gap = 6  # 间距
w, h = 512, 768
grid_w = w * 3 + gap * 4
grid_h = h * 3 + gap * 4
canvas = Image.new('RGB', (grid_w, grid_h), (15, 15, 15))  # 深色背景

for idx, img in enumerate(panels):
    row = idx // 3
    col = idx % 3
    x = gap + col * (w + gap)
    y = gap + row * (h + gap)
    canvas.paste(img, (x, y))

out_path = os.path.join(dst, 'storyboard_9grid_final.png')
canvas.save(out_path, quality=95)
print(f'\n九宫格已保存: {out_path} ({os.path.getsize(out_path)/1024:.0f} KB)')
print(f'尺寸: {canvas.size}')
