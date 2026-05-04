# -*- coding: utf-8 -*-
"""九宫格 v2 - 无参考图，文字描述面部，每个镜头角度不同"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

# 统一角色描述 + 每格不同镜头
ROLE = """A Chinese male actor, age 50, handsome face with high cheekbones, defined jawline, thin mustache, short beard, short black hair pulled back into a bun, stern determined eyes. He is a Ming Dynasty military general."""

panels = [
    {
        "num": 1, "title": "雪夜潜行",
        "prompt": f"""{ROLE}
SIDE PROFILE VIEW. Night scene. He crouches low in a snowy pine forest, viewing enemy fortress through a brass telescope. CAMERA: from his left side, showing his sharp profile silhouette against moonlight. Only his left ear, jawline, and telescope visible. Soldiers crawl behind him. Blue moonlight, cold breath. Cinematic 35mm film grain, shallow depth of field, photorealistic movie still."""
    },
    {
        "num": 2, "title": "统帅推演",
        "prompt": f"""{ROLE}
OVERHEAD BIRD'S EYE VIEW, looking straight down. He stands over a wooden sand table model of Pyongyang fortress, pointing at the north wall. His face is seen from above - top of his iron helmet with red tassels visible. Ten officers surround him, all seen from above. Warm candlelight from below creates dramatic shadows. Photorealistic movie still, overhead cinematography like in Hero."""
    },
    {
        "num": 3, "title": "火器就位",
        "prompt": f"""{ROLE}
WIDE ESTABLISHING SHOT, he is small in frame, standing on a hill overlooking snowy battlefield. Twelve massive Ming cannons being positioned below. CAMERA: very far away, he is a tiny figure silhouetted against dawn sky, back turned to camera, looking out at the vast army. Epic scale. His blue cloak flows. Photorealistic war epic, Lawrence of Arabia style wide shot."""
    },
    {
        "num": 4, "title": "首登城墙",
        "prompt": f"""{ROLE}
LOW ANGLE from below, looking UP. He climbs a siege ladder, seen from below. His face is turned upward toward the top of the wall - we see his jaw, his teeth clenched on a sword blade, his neck straining, one hand pulling the ladder. Arrows rain down around him. Extreme low angle like a ground soldier's POV. Real stone wall texture above. Photorealistic war action."""
    },
    {
        "num": 5, "title": "鸳鸯阵巷战",
        "prompt": f"""{ROLE}
EXTREME CLOSE-UP on his face, FULL FACE FRONT VIEW. He is mid-battle, teeth gritted, veins on forehead, sweat and blood splattered. He thrusts a long spear forward (off-camera). His eyes are fierce, focused. The background is blurred chaos of a narrow stone street with Japanese samurai armor visible. Real blood spatter on his armor. Action movie close-up, like Saving Private Ryan D-Day beach scene. Photorealistic."""
    },
    {
        "num": 6, "title": "敌将末路",
        "prompt": f"""{ROLE}
THREE-QUARTER VIEW from his RIGHT SIDE. He stands with his back partially turned, sword raised behind a kneeling defeated Japanese commander in red samurai armor. We see mostly the Japanese commander's terrified face and the general's back/shoulder/sword arm. Dramatic side lighting through broken window. Fire and smoke. The general's face is partially hidden, mysterious. Photorealistic dramatic movie still."""
    },
    {
        "num": 7, "title": "夕照沉思",
        "prompt": f"""{ROLE}
CLOSE-UP SIDE VIEW, his LEFT FACE. He sits on ruined fortress wall at sunset. We see his left profile - left ear, left eye gazing down at battlefield, jawline. Golden sunset light hits the right side of his face. A wound bleeds on his left temple. His double-sword rests across his knees. Poetic, melancholic. Shot like Terrence Malick films. Photorealistic natural light."""
    },
    {
        "num": 8, "title": "烽火家书",
        "prompt": f"""{ROLE}
TOP-DOWN SLIGHT ANGLE. He kneels at a low writing desk, face seen from above and slightly in front - we see the top of his head, his eyebrows, his nose tip, and the brush in his hand writing a letter. Candlelight from the left casts warm shadow across half his face (Rembrandt lighting). A letter, ink, and a scroll on the desk. Intimate, human. Ang Lee style cinematography. Photorealistic."""
    },
    {
        "num": 9, "title": "雁过雪原",
        "prompt": f"""{ROLE}
BACK VIEW, FROM BEHIND. He rides a horse away from camera across a vast snowy plain at dawn. We see the BACK of his blue cloak, the back of his head, his helmet. Wild geese fly in V-formation ahead of him in the pink sky. The burning Pyongyang city is a smudge of smoke on the far horizon. He is riding INTO the distance, away from us. No face visible at all. Epic farewell, like the ending of a Western. Photorealistic wide landscape."""
    }
]

print('=== 九宫格 v2 (无参考图，多角度) ===')
print(f'分镜数: {len(panels)}\n')

for panel in panels:
    print(f'--- [{panel["num"]}/9] {panel["title"]} ---')
    urls = generate_image(panel["prompt"], size="1024x1536", quality="high")
    
    if urls:
        for i, url in enumerate(urls):
            save_path = os.path.join(dst, f'panel_v2_{panel["num"]}.png')
            result = download_image(url, save_path)
            if result:
                size = os.path.getsize(result)
                print(f'  保存: panel_v2_{panel["num"]}.png ({size/1024:.0f} KB)')
    else:
        print(f'  [FAIL]')
    print()
    time.sleep(2)

print('=== 全部完成 ===')
import glob
panels_files = sorted(glob.glob(f'{dst}/panel_v2_*.png'))
for pf in panels_files:
    print(f'  {os.path.basename(pf)}: {os.path.getsize(pf)/1024:.0f} KB')
