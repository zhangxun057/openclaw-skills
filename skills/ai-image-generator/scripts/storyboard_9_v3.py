# -*- coding: utf-8 -*-
"""九宫格 v3 - 参考图+自然镜头语言"""
import sys, os, json, base64, time
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

# 读取参考图
ref_path = os.path.join(dst, 'liudehua_ref_0.jpg')
with open(ref_path, 'rb') as f:
    ref_bytes = f.read()
ref_b64 = f"data:image/jpeg;base64,{base64.b64encode(ref_bytes).decode()}"

# 关键技巧：不写"keep face"，而是用角色身份引导
panels = [
    {
        "num": 1, "title": "雪夜潜行",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: A snowy forest at night near Pyongyang. The Ming Dynasty general crouches low among pine trees, holding a brass telescope, scouting enemy fortress walls in the distance. Moonlight filters through branches. His soldiers crawl silently behind him.

CINEMATOGRAPHY: Medium shot from the LEFT SIDE. We see his left profile - left ear, jawline, telescope raised to his left eye. Blue moonlight on his iron helmet. Shallow depth of field, foreground branches blurred.

Style: Cinematic film still, 35mm, cold blue tones, photorealistic. Like a scene from Red Cliff or The Last Samurai."""
    },
    {
        "num": 2, "title": "统帅推演",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: Inside a military tent. The Ming Dynasty general stands at a wooden sand table model of Pyongyang, pointing at the north wall with a bamboo rod. Ten officers surround the table, studying the plan.

CINEMATOGRAPHY: High angle shot from ABOVE, looking straight down at the sand table. We see the top of his iron helmet with red tassels, his hand pointing, the officers' heads around the table. Warm candlelight from oil lamps creates dramatic shadows.

Style: Cinematic overhead shot like in Game of Thrones or Hero. Warm amber tones. Photorealistic film still."""
    },
    {
        "num": 3, "title": "火器就位",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: Dawn battlefield. Twelve large Ming Dynasty cannons being dragged into snowy positions by teams of soldiers. The general rides on horseback at the top of a ridge, overseeing the deployment.

CINEMATOGRAPHY: Ultra WIDE shot, the general is a TINY figure on horseback at the top of frame, silhouetted against the pink dawn sky. The vast army and cannons spread across the lower two-thirds of the frame. His blue cloak is visible but his face is too far away to see clearly.

Style: Epic wide shot like Lawrence of Arabia. Vast scale. Cold dawn light. Photorealistic."""
    },
    {
        "num": 4, "title": "首登城墙",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: The general is first up the siege ladder against Pyongyang's stone fortress wall. He grips the top of the wall with one hand, pulling himself up, sword in the other hand.

CINEMATOGRAPHY: LOW ANGLE from the ground, looking UP along the wall. We see him from BELOW - his hand gripping the wall top, his iron helmet appearing over the edge, arrows flying past. The sky is above him. Dramatic upward perspective.

Style: Ground-level POV shot like Saving Private Ryan. Gritty, intense. Real stone texture. Photorealistic war cinematography."""
    },
    {
        "num": 5, "title": "鸳鸯阵巷战",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: Inside the fortress, a narrow stone street. The general leads a duck-formation spear squad (鸳鸯阵) fighting Japanese samurai warriors in red armor. He thrusts a long spear forward.

CINEMATOGRAPHY: HANDHELD camera, MEDIUM CLOSE-UP shot from FRONT, slightly off-center. He is charging toward the camera with his spear. His face is intense, teeth gritted, sweat flying. Blurred motion of samurai behind him. Chaotic energy.

Style: Handheld combat shot like in Gladiator or 1917. Urgent, kinetic. Blood and sparks. Photorealistic action."""
    },
    {
        "num": 6, "title": "敌将末路",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: Inside a burning building in the fortress. The Japanese commander KONISHI YUKINAGA kneels in red samurai armor, defeated, holding a wakizashi sword pointing at his own belly. The general stands over him.

CINEMATOGRAPHY: TWO-SHOT, medium distance. The camera is at the Japanese commander's eye level, looking UP at the general who looms over him. The general is seen from a LOW BACK angle - we see the back of his armor and his raised sword, but his face is turned slightly, profile visible from the commander's perspective.

Style: Dramatic Rembrandt lighting. Warm fire glow, deep shadows. Like a Kurosawa film. Photorealistic."""
    },
    {
        "num": 7, "title": "夕照沉思",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: The general sits alone on the ruined fortress wall at golden hour sunset. The battlefield is quiet below. His armor is dented and blood-stained.

CINEMATOGRAPHY: WIDE shot, he sits on the LEFT THIRD of frame. We see his RIGHT SIDE and RIGHT ARM - his right hand resting on his sword. The vast sunset landscape fills the right two-thirds. His face is in profile from the right, golden light illuminating the right side of his face.

Style: Poetic wide shot like Terrence Malick. Golden hour, warm natural light. Melancholic beauty. Photorealistic."""
    },
    {
        "num": 8, "title": "烽火家书",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: Night interior. The general kneels at a low writing desk, brush in hand, writing a letter. His iron helmet sits beside an oil lamp. A scroll of his teacher Qi Jiguang hangs on the wall.

CINEMATOGRAPHY: MEDIUM shot from the FRONT, slightly elevated angle. He looks DOWN at the paper, so we see his face from ABOVE - his eyebrows, his nose, his focused eyes looking down. Candlelight from the left creates Rembrandt lighting on his face. Intimate and quiet.

Style: Ang Lee intimate cinematography. Warm amber candlelight. Real ink and paper textures. Photorealistic close-up portrait."""
    },
    {
        "num": 9, "title": "雁过雪原",
        "prompt": """Based on the person in the reference photo, place them in this film scene.

Scene: Dawn. A vast snowy plain. Wild geese fly in V-formation across the pink sky. The ruined Pyongyang smokes in the far distance.

CINEMATOGRAPHY: ULTRA WIDE landscape shot. The general on horseback rides AWAY from the camera, into the distance. We see ONLY his BACK - the back of his blue cloak, the back of his iron helmet, his silhouette against the sunrise. He is small in frame. No face visible.

Style: Epic farewell shot like the ending of a Western or Lawrence of Arabia. Pink and gold sky. Lonely, beautiful. Photorealistic landscape."""
    }
]

print('=== 九宫格 v3 (参考图+自然镜头) ===')
print(f'参考图: 已加载')
print(f'分镜数: {len(panels)}\n')

for panel in panels:
    print(f'--- [{panel["num"]}/9] {panel["title"]} ---')
    urls = generate_image(panel["prompt"], size="1024x1536", image=ref_b64, quality="high")
    
    if urls:
        for i, url in enumerate(urls):
            save_path = os.path.join(dst, f'panel_v3_{panel["num"]}.png')
            result = download_image(url, save_path)
            if result:
                size = os.path.getsize(result)
                print(f'  保存: panel_v3_{panel["num"]}.png ({size/1024:.0f} KB)')
    else:
        print(f'  [FAIL]')
    print()
    time.sleep(2)

print('=== 全部完成 ===')
import glob
panels_files = sorted(glob.glob(f'{dst}/panel_v3_*.png'))
for pf in panels_files:
    print(f'  {os.path.basename(pf)}: {os.path.getsize(pf)/1024:.0f} KB')
