# -*- coding: utf-8 -*-
"""Step 4 v2: 重新生成 - 实景电影感分镜图"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

prompt = """Photorealistic cinematic movie storyboard, 9-panel grid layout, live-action film still style.

This is for a real historical war movie starring Andy Lau (刘德华). Every panel must look like an actual film screenshot - photorealistic, not illustrated, not comic, not cartoon.

## Film Info
Title: 平壤 (The Fall of Pyongyang)
Genre: Historical war epic, like Red Cliff or The Battle at Lake Changjin
Main actor: Andy Lau (刘德华) as a Ming Dynasty general - must strongly resemble him in every panel. He is 60 years old, handsome face, defined jawline, thin mustache, serious expression, natural skin texture, real hair.

## 9 Panels (3x3 grid, numbered 1-9, left to right, top to bottom)
Each panel must look like a REAL MOVIE STILL captured on a real film set with real actors, real costumes, real lighting.

### Panel 1 - PRELUDE: Snow Night Reconnaissance
PHOTOREALISTIC. Andy Lau in Ming Dynasty iron armor and helmet, leading soldiers through a snowy pine forest at night. Blue moonlight. He holds a brass telescope, peering at distant Pyongyang fortress walls. Breath visible in cold air. Shallow depth of field. Shot like a Ridley Scott film. Real skin pores visible. Real snow falling.

### Panel 2 - STRATEGY: War Council
PHOTOREALISTIC. Andy Lau in full Ming armor, standing over a wooden sand table model of Pyongyang fortress, pointing at the north wall with a bamboo rod. Ten officers surround him. Warm candlelight illuminates his weathered handsome face. Real wood grain on table. Real fabric textures on banners. Shot like a Zhang Yimou film.

### Panel 3 - PREPARATION: Cannon Positioning
PHOTOREALISTIC. Dawn. Twelve massive Ming Dynasty cannons (大将军炮) positioned in snowy field. Soldiers pull cannons on wooden sleds. Andy Lau supervises on horseback. His "戚" (Qi Army) banner flaps in wind. Real iron cannon textures. Real mud and snow. Real horses breathing steam. Wide epic shot.

### Panel 4 - ESCALADE: Scaling Walls
PHOTOREALISTIC. Low angle. Andy Lau climbing a wooden siege ladder against dark stone fortress wall. Sword clenched in teeth. One hand grips the ladder. Arrows fly past. Real stone texture on wall. Real iron arrowheads. Sweat on his face. Dust and debris falling. Shot like a war documentary. 35mm film grain.

### Panel 5 - MELEE: Street Battle
PHOTOREALISTIC. Close-up action shot. Andy Lau leading a spear formation in a narrow stone street inside the fortress. Fighting Japanese samurai in red armor. Real blood splatter. Real metal sparks from clashing weapons. His Ming blue-and-iron armor dented and bloody. Real face showing determination. Motion blur on weapons.

### Panel 6 - CLIMAX: Enemy Commander's Fall
PHOTOREALISTIC. Dramatic interior. Japanese commander (小西行长) in ornate red samurai armor, kneeling, defeated. Andy Lau stands over him, sword raised. Dramatic side lighting through broken window. Real flame and smoke from burning building. Real wooden beams and straw floor. Cinematic color grading - teal and orange.

### Panel 7 - SUNSET: Victory Reflection
PHOTOREALISTIC. Andy Lau sitting on the ruined fortress wall at golden hour sunset. Armor damaged, blood-stained. Gazing at the battlefield below. His double-sword rests across his knees. Real golden sunlight hitting his face. Real texture of crumbling stone wall. Real fabric of his cloak blowing in wind. Shot like Terrence Malick - poetic naturalism.

### Panel 8 - LETTER HOME: Night Writing
PHOTOREALISTIC. Andy Lau kneeling at a low wooden writing desk in a candlelit room. Writing a letter with a calligraphy brush. His Ming helmet sits beside an oil lamp. Real ink and paper texture. Real warm candlelight on his thoughtful face. A scroll painting of his teacher Qi Jiguang on the wall. Intimate close-up. Shot like Ang Lee.

### Panel 9 - EPILOGUE: Dawn Departure
PHOTOREALISTIC. Ultra-wide landscape. Andy Lau on horseback riding across a vast snowy plain at dawn. Pink and gold sunrise. Wild geese fly overhead. The ruined city of Pyongyang smokes in the distance. His blue cloak billows behind him. Real snow, real sky, real horse. Epic cinematography like Lawrence of Arabia.

## Critical Requirements
- MUST look like REAL PHOTOGRAPHS of a real film set with real actors
- NO illustration, NO comic, NO cartoon, NO painting style
- Real human faces with realistic skin texture
- Real lighting from practical sources (candles, sun, moonlight)
- Real costumes with fabric texture and wear
- Cinematic 35mm film grain
- Each panel has a small title label in Chinese calligraphy at the bottom
- The main actor MUST resemble Andy Lau (刘德华) - specific facial features"""

print(f'Prompt: {len(prompt)} 字')
print('调用 GPT-Image-2 (写实风格)...\n')

urls = generate_image(prompt, size="1792x1024")

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'pingnan_storyboard_v2_{i}.png')
        result = download_image(url, save_path)
        if result:
            size = os.path.getsize(result)
            print(f'已保存: {size/1024:.0f} KB')
else:
    print('图片生成失败')
