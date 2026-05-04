# -*- coding: utf-8 -*-
"""九宫格分镜 - 图生图 high quality, 逐格生成"""
import sys, os, json, base64, time
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

# 读取参考图
ref_path = os.path.join(dst, 'liudehua_ref_0.jpg')
with open(ref_path, 'rb') as f:
    ref_bytes = f.read()
ref_b64 = f"data:image/jpeg;base64,{base64.b64encode(ref_bytes).decode()}"

panels = [
    {
        "num": 1,
        "title": "雪夜潜行",
        "prompt": "Keep the person's exact face from the reference photo. Night scene. This Ming Dynasty general in dark iron armor leads soldiers through a snowy pine forest outside Pyongyang fortress walls. He holds a brass telescope, studying enemy positions. Blue moonlight, breath visible in cold air. Photorealistic movie still, 35mm film grain, shallow depth of field."
    },
    {
        "num": 2,
        "title": "统帅推演",
        "prompt": "Keep the person's exact face from the reference photo. Top-down dramatic shot. This Ming Dynasty general in full armor stands over a wooden sand table model of Pyongyang fortress, pointing at the north wall with a bamboo rod. Ten officers surround him. Warm candlelight illuminates his serious handsome face. Real wood grain, real fabric banners. Photorealistic movie still."
    },
    {
        "num": 3,
        "title": "火器就位",
        "prompt": "Keep the person's exact face from the reference photo. Dawn, epic wide shot. Twelve massive Ming Dynasty cannons positioned in snowy field. Soldiers drag cannons on wooden sleds. This general supervises on horseback, his blue Qi Army banner flapping in wind. Steam from horses, muddy ground. Photorealistic war film still."
    },
    {
        "num": 4,
        "title": "首登城墙",
        "prompt": "Keep the person's exact face from the reference photo. Low angle dramatic shot. This Ming Dynasty general climbs a wooden siege ladder against dark stone fortress wall, sword clenched in teeth, one hand gripping the ladder. Arrows fly past. Real stone texture, real iron arrowheads, sweat on his face. Photorealistic war documentary style."
    },
    {
        "num": 5,
        "title": "鸳鸯阵巷战",
        "prompt": "Keep the person's exact face from the reference photo. Extreme close-up action. This general leads a spear formation in a narrow stone street inside the fortress, fighting Japanese samurai in red armor. Blood splatter, sparks from clashing metal weapons. His blue-and-iron Ming armor dented and bloodied. Photorealistic battle scene, motion blur on weapons."
    },
    {
        "num": 6,
        "title": "敌将末路",
        "prompt": "Keep the person's exact face from the reference photo. Dramatic interior shot. A Japanese commander in ornate red samurai armor kneels, defeated. This Ming Dynasty general stands over him, sword raised. Dramatic side lighting through broken window. Real flame and smoke. Cinematic teal-and-orange color grading. Photorealistic movie still."
    },
    {
        "num": 7,
        "title": "夕照沉思",
        "prompt": "Keep the person's exact face from the reference photo. Golden hour sunset. This general sits on ruined fortress wall, armor damaged and blood-stained, gazing at battlefield below. His double-sword rests across his knees. Warm golden sunlight on his face. Real crumbling stone texture, cloak blowing in wind. Photorealistic, poetic naturalism."
    },
    {
        "num": 8,
        "title": "烽火家书",
        "prompt": "Keep the person's exact face from the reference photo. Intimate night interior. This Ming Dynasty general kneels at a low wooden desk, writing a letter with calligraphy brush by candlelight. His helmet sits beside an oil lamp. Real ink and paper texture, warm candlelight on his thoughtful face. A portrait scroll on the wall. Photorealistic close-up."
    },
    {
        "num": 9,
        "title": "雁过雪原",
        "prompt": "Keep the person's exact face from the reference photo. Ultra-wide landscape. This general on horseback rides across vast snowy plain at dawn. Pink and gold sunrise. Wild geese fly overhead. Burning Pyongyang city smokes in distant background. Blue cloak billows behind him. Real snow, real sky. Epic cinematography. Photorealistic movie ending shot."
    }
]

print(f'=== 九宫格分镜生成 ===')
print(f'参考图: {len(ref_b64)} chars')
print(f'质量: high')
print(f'尺寸: 1024x1536')
print(f'分镜数: {len(panels)}\n')

for panel in panels:
    print(f'--- [{panel["num"]}/9] {panel["title"]} ---')
    urls = generate_image(panel["prompt"], size="1024x1536", image=ref_b64, quality="high")
    
    if urls:
        for i, url in enumerate(urls):
            save_path = os.path.join(dst, f'panel_{panel["num"]}_{i}.png')
            result = download_image(url, save_path)
            if result:
                size = os.path.getsize(result)
                print(f'  保存: panel_{panel["num"]}.png ({size/1024:.0f} KB)')
    else:
        print(f'  [FAIL] 生成失败')
    
    print()
    time.sleep(2)  # 间隔避免限速

print('=== 全部完成 ===')

# 列出所有面板文件
import glob
panels_files = sorted(glob.glob(f'{dst}/panel_*.png'))
for pf in panels_files:
    size = os.path.getsize(pf)/1024
    print(f'  {os.path.basename(pf)}: {size:.0f} KB')
