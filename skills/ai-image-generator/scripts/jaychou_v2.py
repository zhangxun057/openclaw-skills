# -*- coding: utf-8 -*-
"""周杰伦演唱会 v2 - 修正镜头逻辑"""
import sys, os, base64
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/ai-image-generator/scripts'))
from image2_tool import generate_image, download_image

dst = os.path.expanduser('~/.openclaw/skills/ai-image-generator/scratchpad')

ref_path = os.path.join(dst, 'jaychou_ref_0.jpg')
with open(ref_path, 'rb') as f:
    ref_b64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"

prompt = """Based on the person in the reference photo, create a concert live photo at Qianling Mountain Park (黔灵山公园) in Guiyang.

SCENE: An outdoor concert at night in the famous lakeside area of Qianling Mountain Park. The person is the singer on stage.

CAMERA POSITION: Shot FROM THE AUDIENCE, looking UP at the stage. The singer is in the CENTER-UPPER portion of the frame, standing on the elevated stage, facing TOWARD the camera/audience. He holds a microphone, singing to the crowd.

LAYOUT (from bottom to top of frame):
- BOTTOM: The tops of thousands of audience heads, hands raised with blue light sticks
- MIDDLE: The stage edge and the singer performing, facing the audience
- UPPER: The stage backdrop with LED screens, and behind that, the dark green mountains and lake of Qianling Mountain Park at night. The park's pavilion (麒麟阁) is lit up in the distance.

LIGHTING: Stage lights from behind the singer illuminate his silhouette and the audience. Purple and blue laser beams shoot from the stage over the audience's heads toward the mountains. LED screens on stage show visual effects.

Style: Real concert photography from audience perspective, like a music magazine cover photo. Photorealistic, vivid colors, shallow depth of field with the audience slightly blurred and the singer sharp."""

print('调用 GPT-Image-2 v2...\n')
urls = generate_image(prompt, size="1024x1536", image=ref_b64, quality="high")

if urls:
    for i, url in enumerate(urls):
        save_path = os.path.join(dst, f'jaychou_concert_v2_{i}.png')
        result = download_image(url, save_path)
        if result:
            print(f'已保存: {os.path.getsize(result)/1024:.0f} KB')
else:
    print('生成失败')
