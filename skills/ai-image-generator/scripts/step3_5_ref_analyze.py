# -*- coding: utf-8 -*-
"""Step 3.5: 参考图详细评估"""
import requests
import json
import base64
import os

DASHSCOPE_API_KEY = "sk-c3b3d0d532ac408090f1ef09063171da"

def analyze_reference_image(image_path, index):
    """
    用 qwen-vl-plus 详细分析参考图的适用性
    """
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    prompt = """
你是一个专业图像创意总监，正在评估这张图片是否适合作为 AI 图像生成的参考图。

## 评估维度

### 1. 基础质量
- 分辨率是否足够（建议 512x512 以上）
- 清晰度是否足够（面部/服装细节可见）
- 光线条件（是否过曝/过暗）

### 2. 人物特征
- 面部是否清晰可见
- 发型是否可辨认
- 表情是否自然/有表现力

### 3. 服装造型
- 服装款式是否清晰
- 颜色是否准确
- 是否适合舞台场景

### 4. 姿势动作
- 姿势是否适合演唱会场景
- 动作是否有张力/表现力
- 是否适合作为生成参考

### 5. 背景环境
- 背景是否杂乱
- 是否有舞台元素（灯光、观众、乐器等）
- 背景是否会影响主体识别

## 输出格式（严格 JSON）

{
    "index": 图片编号，
    "resolution": {"width": 数字，"height": 数字},
    "scores": {
        "basic_quality": 1-10 分，
        "face_clarity": 1-10 分，
        "outfit_detail": 1-10 分，
        "pose_suitability": 1-10 分，
        "background_cleanliness": 1-10 分
    },
    "strengths": ["优点 1", "优点 2", ...],
    "weaknesses": ["缺点 1", "缺点 2", ...],
    "suitable_for": ["适合的场景类型 1", "适合的场景类型 2"],
    "overall_score": 1-10 分，
    "recommendation": "推荐/备选/不推荐",
    "reasoning": "详细评估理由（100-200 字）"
}

直接输出 JSON，不要有任何额外文字。
"""
    
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'qwen-vl-plus',
        'input': {
            'messages': [
                {'role': 'system', 'content': '你是图像创意总监。输出严格 JSON。'},
                {'role': 'user', 'content': [
                    {'image': f'data:image/jpeg;base64,{b64}'},
                    {'text': prompt}
                ]}
            ]
        }
    }
    
    print(f"[{index}] 分析中...")
    
    resp = requests.post(
        'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation',
        headers=headers,
        json=payload,
        timeout=90
    )
    
    result = resp.json()
    
    if 'output' not in result:
        print(f"  API 错误：{json.dumps(result, ensure_ascii=False)[:200]}")
        return None
    
    content = result['output']['choices'][0]['message']['content'][0]['text']
    
    # 提取 JSON
    import re
    match = re.search(r'\{[\s\S]*\}', content)
    if match:
        analysis = json.loads(match.group())
        print(f"  综合评分：{analysis.get('overall_score', '?')}/10")
        print(f"  推荐度：{analysis.get('recommendation', '?')}")
        return analysis
    else:
        print(f"  无法解析 JSON: {content[:200]}")
        return None


# 主程序
print("=== Step 3.5: 参考图详细评估 ===\n")
print("使用 qwen-vl-plus 分析每张参考图的适用性\n")

# 读取已验证的参考图列表
with open('scratchpad/verified_images.json', 'r', encoding='utf-8') as f:
    verified_images = json.load(f)

# 分析每张图
analyses = []
for img in verified_images:
    idx = img['index']
    path = img['path']
    
    if os.path.exists(path):
        analysis = analyze_reference_image(path, idx)
        if analysis:
            analysis['path'] = path
            analysis['url'] = img['url']
            analysis['title'] = img['title']
            analyses.append(analysis)

# 排序（按综合评分）
analyses.sort(key=lambda x: x.get('overall_score', 0), reverse=True)

# 保存结果
with open('scratchpad/image_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analyses, f, ensure_ascii=False, indent=2)

print("\n=== 评估完成 ===\n")

# 输出排名
print("📊 参考图评分排名:\n")
for i, a in enumerate(analyses):
    badge = "🏆" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else f"{i+1}."))
    print(f"{badge} #{a['index']} - {a.get('overall_score', '?')}/10 - {a.get('recommendation', '?')}")
    print(f"   优点：{', '.join(a.get('strengths', [])[:3])}")
    if a.get('weaknesses'):
        print(f"   缺点：{', '.join(a.get('weaknesses', [])[:2])}")
    print()

# 推荐最佳
if analyses:
    best = analyses[0]
    print("=" * 60)
    print(f"🎯 推荐使用：#{best['index']}")
    print(f"   综合评分：{best.get('overall_score', '?')}/10")
    print(f"   推荐度：{best.get('recommendation', '?')}")
    print(f"   路径：{best['path']}")
    print(f"   标题：{best['title']}")
    print(f"   适合场景：{', '.join(best.get('suitable_for', []))}")
    print(f"\n   评估理由：{best.get('reasoning', '')[:200]}...")
