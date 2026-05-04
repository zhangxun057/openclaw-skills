# -*- coding: utf-8 -*-
"""
视觉验证工具
使用阿里云百炼 qwen-vl-plus 验证图片内容
"""
import os
import sys
import requests
import base64
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    print("错误：需要安装 Pillow。运行：pip install Pillow")
    sys.exit(1)

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-c3b3d0d532ac408090f1ef09063171da")
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

HEADERS = {
    "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
    "Content-Type": "application/json"
}


def check_resolution(image_bytes):
    """
    检查图片分辨率
    
    Returns:
        {width, height, level, file_size_kb, pass}
        level: good(≥512) / low(256-511) / too_low(<256)
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        w, h = img.size
        file_size_kb = len(image_bytes) / 1024
        
        if w >= 512 and h >= 512:
            level = "good"
        elif w >= 256 and h >= 256:
            level = "low"
        else:
            level = "too_low"
        
        return {
            "width": w,
            "height": h,
            "file_size_kb": round(file_size_kb, 1),
            "level": level,
            "pass": level != "too_low"
        }
    except Exception as e:
        return {"error": str(e), "pass": False}


def verify_content(image_bytes, expected_type="person"):
    """
    使用视觉模型验证图片内容
    
    Args:
        image_bytes: 图片 bytes
        expected_type: 期望类型 (person/product/scene/animal)
    
    Returns:
        {
            "pass": bool,
            "main_subject": "person/animal/product/scene/unknown",
            "clarity_ok": bool,
            "resolution_ok": bool,
            "raw": "模型原始回复"
        }
    """
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    prompt = """请严格判断这张图片：
1. 主体是什么？（人物/动物/物品/风景）
2. 清晰度是否足够作为参考图？
3. 分辨率是否足够（建议 512x512 以上）？

回答格式：
主体：[xxx]
清晰度：[够/不够]
分辨率：[够/不够]"""
    
    payload = {
        "model": "qwen-vl-plus",
        "input": {
            "messages": [{
                "role": "user",
                "content": [
                    {"image": f"data:image/jpeg;base64,{b64}"},
                    {"text": prompt}
                ]
            }]
        }
    }
    
    try:
        resp = requests.post(DASHSCOPE_URL, headers=HEADERS, json=payload, timeout=60)
        result = resp.json()
        
        if "output" not in result:
            return {"pass": False, "error": str(result), "main_subject": "unknown"}
        
        text = result["output"]["choices"][0]["message"]["content"][0]["text"]
        text_lower = text.lower()
        
        # 判断主体
        main_subject = "unknown"
        if any(kw in text_lower for kw in ["人物", "人", "woman", "man", "person", "girl", "boy", "女性", "男性"]):
            main_subject = "person"
        elif any(kw in text_lower for kw in ["动物", "animal", "dog", "cat", "panda", "熊", "熊猫"]):
            main_subject = "animal"
        elif any(kw in text_lower for kw in ["物品", "商品", "product", "item", "物体"]):
            main_subject = "product"
        elif any(kw in text_lower for kw in ["风景", "场景", "landscape", "scene", "建筑"]):
            main_subject = "scene"
        
        # 判断清晰度
        clarity_ok = not any(kw in text_lower for kw in ["模糊", "马赛克", "blur", "blurry", "不够", "无法辨认"])
        
        # 判断分辨率
        resolution_bad = any(kw in text_lower for kw in ["分辨率太低", "太小", "不够", "太低"])
        resolution_ok = not resolution_bad
        
        # 综合判断
        subject_match = (main_subject == expected_type) if expected_type else True
        pass_check = subject_match and clarity_ok and resolution_ok
        
        return {
            "pass": pass_check,
            "main_subject": main_subject,
            "clarity_ok": clarity_ok,
            "resolution_ok": resolution_ok,
            "raw": text
        }
    except Exception as e:
        return {"pass": False, "error": str(e), "main_subject": "unknown"}


def full_verify(image_bytes, expected_type="person"):
    """
    完整验证：分辨率 + 内容
    
    Returns:
        {
            "pass": bool,
            "overall": "pass/fail",
            "resolution": {...},
            "content": {...}
        }
    """
    res = check_resolution(image_bytes)
    content = verify_content(image_bytes, expected_type)
    
    overall_pass = res.get("pass", False) and content.get("pass", False)
    
    return {
        "pass": overall_pass,
        "overall": "pass" if overall_pass else "fail",
        "resolution": res,
        "content": content
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python vision_tool.py <图片路径> [期望类型]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    expected_type = sys.argv[2] if len(sys.argv) > 2 else "person"
    
    if not os.path.exists(image_path):
        print(f"错误：文件不存在 {image_path}")
        sys.exit(1)
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    result = full_verify(image_bytes, expected_type)
    
    print(f"分辨率：{result['resolution'].get('width')}x{result['resolution'].get('height')} [{result['resolution'].get('level')}]")
    print(f"主体识别：{result['content'].get('main_subject')}")
    print(f"清晰度：{'✅' if result['content'].get('clarity_ok') else '❌'}")
    print(f"分辨率判定：{'✅' if result['content'].get('resolution_ok') else '❌'}")
    print(f"\n综合结果：{'✅ PASS' if result['pass'] else '❌ FAIL'}")
