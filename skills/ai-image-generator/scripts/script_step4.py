# -*- coding: utf-8 -*-
"""Step 4: 生成九宫格分镜图"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

with open(f'{dst}/script_result.json', 'r', encoding='utf-8') as f:
    script = json.load(f)

so = script['script_outline']
protagonist = script['protagonist']
panels = script['storyboard']

print('=== Step 4: 生成九宫格分镜图 ===\n')
print(f'片名: {so["title"]}')
print(f'主角: {protagonist["name"]} ({protagonist["rank"]})')
print(f'分镜: {len(panels)} 格\n')

# 构建 Prompt
prompt = """9-panel movie storyboard illustration, cinematic comic art style, for a Chinese historical war film.

## Film Info
Title: 平壤 (The Fall of Pyongyang)
Setting: 1593, Ming Dynasty military campaign, Imjin War
Main character (appears in ALL panels): A heroic Ming Dynasty general in his 40s, stern handsome face with sharp jawline, high cheekbones, a short beard, wearing Ming military armor with iron helmet. Resembles Andy Lau (刘德华).

## 9 Panels (3x3 grid, numbered 1-9, read left to right, top to bottom)

### Panel 1 - PRELUDE: Night Reconnaissance
Night scene. A group of Ming soldiers in dark armor creeping through snowy forest outside Pyongyang city walls. The general leads, holding a lantern, studying the enemy fortress through binoculars (Ming-era telescope). Blue moonlight, cold breath visible. Mood: tense silence before storm.

### Panel 2 - STRATEGY: War Council
Top-down view. The general stands over a tactical sand table model of Pyongyang, pointing at the north wall. Ten officers lean in. Candlelight illuminates their serious faces and the detailed fortress model. Papers and maps scattered. Mood: focused determination.

### Panel 3 - PREPARATION: Artillery Positioning
Wide dynamic shot. Twelve "大将军炮" (Great General Cannon) cannons being dragged into snowy positions by teams of soldiers at dawn. Steam rises from the cannons. A flag bearing "戚" (Qi) flaps in the wind. Soldiers leap over muddy ground. Mood: explosive energy building.

### Panel 4 - ESCALADE: Scaling the Walls
Low angle dramatic shot. Wooden siege ladders leaning against dark stone walls. The general climbs the first ladder, using his teeth to grip his sword, one hand pulling up. Arrows and stones rain down. Soldiers behind him charge upward. Mood: desperate courage, brute force.

### Panel 5 - MELEE: Spear Combat in Streets
Extreme close-up. A narrow street inside the city. The general leads a Qi Family Army spear formation (鸳鸯阵 duck-duck formation). Japanese samurai charge from the other end, katanas raised. General's spear stabs forward. Blood spray, sparks from clashing weapons. Mood: savage chaos, precision violence.

### Panel 6 - CLIMAX: Enemy Commander's Last Stand
Dramatic interior shot. The Japanese commander KONISHI YUKINAGA (小西行长) in red armor, trembling, holds his wakizashi. Blood-red light through shattered window illuminates him. The general in the doorway, sword raised, silhouetted. Smoke and flames in background. Mood: epic triumph, dramatic reckoning.

### Panel 7 - TWILIGHT: Wounded Warrior
Warm sunset colors. The general sits on the ruined fortress wall, armor dented and bloodied, gazing at the battlefield below. A small wound on his forehead bleeds. His sword rests across his knees. Setting sun paints everything gold and red. Mood: solemn dignity, the cost of victory.

### Panel 8 - REFLECTION: War Letters
Interior night scene. The general kneels at a low table, writing a letter by candlelight. His helmet sits beside him. An ink painting scroll shows the battle scene. A portrait of Qi Jiguang (戚继光, his teacher) hangs on the wall behind him. Candlelight warmly illuminates his thoughtful face. Mood: quiet contemplation, human depth.

### Panel 9 - EPILOGUE: Geese over Snowy Dawn
Ultra wide landscape shot. A vast snowy plain at dawn. A line of wild geese flies across the pink sky. A lone supply cart leaves the ruined city in the distance. The general on horseback rides toward camera, his cloak flowing. Faint sunlight breaks through clouds. Title "平壤" in calligraphy at bottom. Mood: epic farewell, new beginning.

## Art Style
- Cinematic film storyboard art
- Ink wash and watercolor blended style
- Rich color palette: deep reds, cold blues, warm golds
- Each panel has a small Chinese title label at top
- Film grain texture overlay
- Aspect ratio: wide cinematic frames"""

print(f'Prompt: {len(prompt)} 字')
print('调用 GPT-Image-2...\n')

urls = generate_image(prompt, size="1792x1024")

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'pingnan_storyboard_{i}.png')
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f'已保存: {size/1024:.0f} KB')
else:
    print('图片生成失败')
