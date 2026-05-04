# -*- coding: utf-8 -*-
"""Step 4.5: 重新生成 - 茅台广告海报"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import base64

# 使用 #2 参考图（张艺兴演唱会）
with open('scratchpad/verified_images.json', 'r', encoding='utf-8') as f:
    verified = json.load(f)

ref_img = verified[2]
ref_path = ref_img['path']

print("=== 重新生成：茅台广告海报 ===\n")
print(f"参考图：#{ref_img['index']}")

# 读取参考图
with open(ref_path, 'rb') as f:
    ref_bytes = f.read()
ref_base64 = base64.b64encode(ref_bytes).decode('utf-8')

# 新 Prompt：茅台广告海报风格
prompt = """
高端商业广告海报，张艺兴为贵州茅台酒代言。

【画面构图】
- 张艺兴站在黄果树大瀑布前，手持茅台酒瓶
- 低机位仰拍，凸显人物气场与瀑布气势
- 黄金分割构图，人物位于画面右侧 1/3 处

【人物造型】
- 张艺兴穿着时尚西装或潮牌服装
- 发型精致，妆容干净，面带自信微笑
- 手持茅台酒（红色包装，白色瓶身），展示产品

【背景场景】
- 黄果树大瀑布：多级跌落，水雾弥漫，气势磅礴
- 瀑布高度约 77 米，白色水流 + 灰色岩壁 + 绿色植被
- 前景水花飞溅，背景青山环绕

【海报元素】
- 顶部或左侧留白区域用于放置文案
- 整体色调：红色（茅台）+ 金色（高端）+ 蓝绿色（瀑布自然）
- 光影效果：自然光 + 柔光补光，人物面部明亮

【海报配文】（AI 生成文字）
- 主标题："茅台 × 张艺兴" 或 "国酒茅台"
- 副标题："年轻的力量" 或 "传承与创新"
- 位置：画面顶部或左侧空白处

【风格】
高端商业广告摄影，4K 超高清，色彩饱和，对比度适中，专业后期调色
"""

print(f"生成 Prompt:\n{prompt[:400]}...\n")

# 调用 Image2 API
from image2_tool import generate_and_save

print("正在调用 GPT-Image-2 生成海报...")
print("预计需要 1-3 分钟...\n")

paths = generate_and_save(
    prompt=prompt.strip(),
    size="1024x1792",  # 竖版海报
    image=f"data:image/jpeg;base64,{ref_base64}",
    save_dir="scratchpad"
)

if paths:
    print(f"\n✅ 生成成功！")
    for p in paths:
        print(f"  保存路径：{p}")
    
    # 保存记录
    record = {
        "prompt": prompt,
        "reference_image": ref_img,
        "output_paths": paths,
        "type": "茅台广告海报"
    }
    with open('scratchpad/maotai_poster_record.json', 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    
    print("\n记录已保存到 scratchpad/maotai_poster_record.json")
else:
    print("\n❌ 生成失败")
