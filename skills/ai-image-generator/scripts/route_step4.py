# -*- coding: utf-8 -*-
"""Step 4: 生成手绘路线地图"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

# 读取地理信息
with open(f'{dst}/info_search_result.json', 'r', encoding='utf-8') as f:
    info = json.load(f)

geo = info.get('geo_info', {})

print('=== Step 4: 生成手绘地图 ===\n')

# 构建精确的 Prompt
prompt = """Hand-drawn travel route map illustration, artistic watercolor and ink sketch style.

## Route (counterclockwise loop, starting and ending in Guiyang)

Starting point: GUIYANG (贵阳) - top-left area of map, capital of Guizhou province

1. Guiyang → CHONGQING (重庆): Northeast direction, ~350km via G75 Lanhai Expressway (兰海高速). Chongqing is upper-center area, a major city on the Yangtze River.

2. Chongqing → DAZU STONE CARVINGS (大足石刻): Northwest of Chongqing, ~108km via G85 Yinkun Expressway + S108. UNESCO World Heritage site with ancient Buddhist rock sculptures.

3. Dazu → back to CHONGQING: Same route back.

4. Chongqing → WULONG (武隆): Southeast of Chongqing, ~186km via G65 Baomao Expressway (包茂高速). Wulong is in a mountainous canyon area.

5. Wulong area attractions:
   - FAIRY MOUNTAIN NATIONAL PARK (仙女山国家公园): West of Wulong town, alpine grassland with forests, ~15km from town
   - THREE NATURAL BRIDGES (天生三桥): Southeast of Wulong, spectacular karst canyon formations, ~35km from town

6. Wulong → MEITAN (湄潭): Southeast direction, ~270km via G65 then G75 then G69 Yinbai Expressway (银百高速). Meitan is in northern Guizhou, famous tea-growing region.

7. Meitan → GUIYANG: Southwest, ~213km via G69 Yinbai Expressway. Back to starting point.

## Map Layout
- Skewed oblique projection: Guiyang at bottom-left, Chongqing at top-center, Wulong at right-center
- Route forms a large loop: Guiyang (start) → up to Chongqing → right to Wulong → down-left through Meitan → back to Guiyang
- Each stop marked with a numbered circle (①②③④⑤⑥)
- Show highway numbers (G75, G65, G69, G85) along routes
- Distance labels on each segment

## Visual Style
- Beautiful hand-drawn travel illustration map
- Watercolor wash with ink outlines
- Green mountains and blue rivers as background terrain
- Small illustrated icons at each stop: temple/cave for Dazu, mountain peak for Fairy Mountain, bridge arch for Three Natural Bridges, tea leaf for Meitan, clock tower for Chongqing, monkey icon for Guiyang
- Compass rose in corner
- Title banner: "贵阳-重庆自驾之旅 4.30-5.5"
- Warm color palette, inviting and adventure-feeling
- Clean white or cream background
- Chinese and English labels for cities

## Important
- Geographic accuracy matters: Wulong is SOUTHEAST of Chongqing
- Dazu is NORTHWEST of Chongqing  
- Meitan is between Wulong and Guiyang
- The route is a LOOP, not a straight line
- Show the G75/G65/G69 highway names on the routes"""

print(f'Prompt ({len(prompt)} 字)')

urls = generate_image(prompt, size="1792x1024")

if urls:
    print(f'\n获得 {len(urls)} 个 URL')
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'guiyang_chongqing_route_{i}.png')
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f'  已保存: {size/1024:.0f} KB')
else:
    print('图片生成失败')
