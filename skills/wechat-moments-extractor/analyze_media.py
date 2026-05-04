#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
朋友圈图片深度分析

输入：JSONL 文件（只处理 image_trigger=1 的帖子）
输出：图片分析结果（产品/场景/人物/消费信号）

触发条件：
- whitelist 用户（强制）
- 点赞或评论 >= 3
- 内容含饮酒场景关键词
- signals 结果中有 image_prompt
"""

import json
import sys
import os
import time
import base64
import re
from pathlib import Path
from datetime import datetime

# 路径配置
SKILL_DIR = Path(__file__).parent
PROJECT_DIR = SKILL_DIR.parent.parent / "projects" / "moments-analysis"
WORK_DIR = PROJECT_DIR / "analyze_images_work"
STATE_DIR = PROJECT_DIR / "state"
OUTPUT_DIR = WORK_DIR / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Seedream API 配置
SEEDREAM_API_KEY = "d155ace0-ee4d-42b1-936e-4a16d2623c89"
SEEDREAM_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# 限速配置
MAX_REQUESTS_PER_MINUTE = 30
REQUEST_INTERVAL = 60 / MAX_REQUESTS_PER_MINUTE

# 保底 prompt2（白名单/点赞触发时用）
PROMPT_FALLBACK = "描述图中场景和人物及其行为动作，重点关注：1) 是否有白酒产品（品牌、包装、规格）；2) 饮用场景（商务/宴请/聚会/家庭）；3) 消费实力线索（穿着配饰、车辆、餐厅档次）"

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def load_jsonl(filepath):
    """加载 JSONL 文件"""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records

def load_media_index():
    """加载 media_index 构建 post_id -> 实际路径映射"""
    media_index_path = STATE_DIR / "media_index.json"
    if not media_index_path.exists():
        return {}
    
    with open(media_index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mapping = {}
    for entry in data.get('entries', []):
        html_file = entry.get('html_file', '')
        base_dir = PROJECT_DIR / "raw" / html_file.replace('.html', '')
        
        for post in entry.get('posts', []):
            media_files = post.get('media_files', [])
            non_avatar = [mf for mf in media_files if not mf.startswith('media/avatar_')]
            
            for mf in non_avatar:
                fname = mf.split('/')[-1]
                if '_' in fname:
                    post_id = fname.rsplit('_', 1)[0]
                    if post_id not in mapping:
                        mapping[post_id] = {
                            'nickname': post.get('nickname', ''),
                            'tm_str': post.get('tm_str', ''),
                            'content': post.get('contentDesc', ''),
                            'media_files': [str(base_dir / f) for f in non_avatar]
                        }
                    break
    
    return mapping

def find_media_for_post(post_id, media_index):
    """根据 post_id 查找对应的媒体文件"""
    if post_id in media_index:
        return media_index[post_id]
    for key, value in media_index.items():
        if post_id.startswith(key) or key.startswith(post_id):
            return value
    return None

def encode_image_base64(image_path):
    """将图片转为 base64"""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"  [!] 读取图片失败 {image_path}: {e}")
        return None

# ---------------------------------------------------------------------------
# API 调用
# ---------------------------------------------------------------------------

def call_seedream_vision(image_path, prompt, context_info=None):
    """
    调用 Seedream 视觉理解 API 分析单张图片
    """
    image_base64 = encode_image_base64(image_path)
    if not image_base64:
        return None
    
    system_prompt = """你是朋友圈图片分析专家，专门从白酒销售视角分析图片。

分析维度：
1. 人物识别：人数、身份（商务/私人）、互动关系
2. 产品信息：是否有白酒产品、品牌、包装、规格
3. 场景判断：宴会/商务接待/家庭聚会/户外/其他
4. 事件推断：从图片推断可能的人生节点
5. 消费实力：从穿着、车辆、餐厅档次等判断消费水平

输出 JSON 格式：
{
  "场景描述": "描述",
  "产品": "白酒品牌和规格或'无'",
  "人物": "人数和关系",
  "消费实力": "高/中/低/无法判断",
  "事件推断": "推断的事件类型或'无法判断'",
  "详细描述": "更多细节（可选）"
}"""
    
    user_prompt = prompt
    if context_info:
        if context_info.get('content'):
            user_prompt = f"朋友圈内容：{context_info['content']}\n\n{prompt}"
        if context_info.get('signals'):
            user_prompt += f"\n已有销售信号：{context_info['signals']}"
    
    payload = {
        "model": "doubao-seedream-250312",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                {"type": "text", "text": user_prompt}
            ]}
        ],
        "max_tokens": 500
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SEEDREAM_API_KEY}"
    }
    
    try:
        import urllib.request
        req = urllib.request.Request(
            SEEDREAM_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                try:
                    if '```json' in content:
                        content = content.split('```json')[1].split('```')[0]
                    elif '```' in content:
                        content = content.split('```')[1].split('```')[0]
                    return json.loads(content.strip())
                except json.JSONDecodeError:
                    return {'raw_response': content}
            return None
    
    except Exception as e:
        print(f"  [!] API 调用失败：{e}")
        return None

# ---------------------------------------------------------------------------
# 主逻辑
# ---------------------------------------------------------------------------

def filter_trigger_posts(records):
    """筛选 image_trigger=1 的帖子"""
    trigger_posts = []
    for r in records:
        if r.get('image_trigger') == 1:
            trigger_posts.append(r)
    return trigger_posts

def analyze_posts(posts, media_index):
    """批量分析图片"""
    results = []
    
    print(f"\n开始分析 {len(posts)} 条图片...")
    
    for i, post in enumerate(posts, 1):
        post_id = post.get('post_id', '')
        nickname = post.get('nickname', '未知')
        image_prompt = post.get('image_prompt', PROMPT_FALLBACK)
        content = post.get('content', '')
        signals = post.get('signals', [])
        
        print(f"\n[{i}/{len(posts)}] {nickname}")
        
        # 获取媒体文件路径
        media_info = media_index.get(post_id, {})
        if not media_info:
            media_info = find_media_for_post(post_id, media_index)
        
        media_files = media_info.get('media_files', post.get('media_files', []))
        
        if not media_files:
            print(f"  [!] 无媒体文件，跳过")
            continue
        
        # 限制每 post 分析数量（最多 2 张）
        files_to_analyze = media_files[:2]
        
        post_results = []
        for media_path in files_to_analyze:
            if not os.path.exists(media_path):
                print(f"  [!] 文件不存在：{media_path}")
                continue
            
            context = {
                'content': content,
                'signals': signals,
                'nickname': nickname
            }
            
            result = call_seedream_vision(media_path, image_prompt, context)
            
            if result:
                post_results.append({
                    'media_path': media_path,
                    'analysis': result,
                    'post_id': post_id,
                    'nickname': nickname
                })
                print(f"  [OK] {os.path.basename(media_path)}: {result.get('产品', 'N/A')}")
            else:
                print(f"  [!] 分析失败")
            
            time.sleep(REQUEST_INTERVAL)
        
        if post_results:
            results.append({
                'post_id': post_id,
                'nickname': nickname,
                'content': content,
                'signals': signals,
                'image_prompt': image_prompt,
                'image_results': post_results
            })
    
    return results

def save_results(results, output_file):
    """保存分析结果"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    latest = WORK_DIR / "latest_media_analysis.json"
    with open(latest, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return output_file

def print_summary(results):
    """打印汇总"""
    if not results:
        print("\n无分析结果")
        return
    
    total_posts = len(results)
    total_images = sum(len(r.get('image_results', [])) for r in results)
    
    # 统计有白酒产品的
    has_liquor = 0
    for r in results:
        for img in r.get('image_results', []):
            product = img.get('analysis', {}).get('产品', '')
            if product and product != '无':
                has_liquor += 1
                break
    
    print("\n" + "=" * 60)
    print("图片分析汇总")
    print("=" * 60)
    print(f"  分析帖子数：{total_posts}")
    print(f"  分析图片数：{total_images}")
    print(f"  有白酒产品：{has_liquor} 条")
    
    if has_liquor > 0:
        print(f"\n有白酒产品的帖子：")
        for r in results:
            for img in r.get('image_results', []):
                product = img.get('analysis', {}).get('产品', '')
                if product and product != '无':
                    print(f"  - {r['nickname']}: {product}")

# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("朋友圈图片深度分析")
    print("=" * 60)
    
    # 默认使用最新的分析结果
    input_file = WORK_DIR / "latest_media_analysis_input.jsonl"
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        # 尝试从 analyze_images_work 目录找
        input_file = WORK_DIR / "valuable_posts.json"
        if not input_file.exists():
            print(f"[ERROR] 未找到输入文件：{input_file}")
            print("用法: python analyze_media.py <输入JSONL文件>")
            return 1
    
    print(f"\n[1/4] 加载数据...")
    if input_file.suffix == '.jsonl':
        records = load_jsonl(input_file)
    else:
        # JSON 文件
        with open(input_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
    
    print(f"  共 {len(records)} 条记录")
    
    # 筛选 trigger=1 的帖子
    trigger_posts = filter_trigger_posts(records)
    print(f"  image_trigger=1: {len(trigger_posts)} 条")
    
    if not trigger_posts:
        print("[INFO] 无需要分析的帖子")
        return 0
    
    # 加载 media_index
    print("\n[2/4] 加载媒体索引...")
    media_index = load_media_index()
    print(f"  媒体映射：{len(media_index)} 条")
    
    # 分析图片
    print("\n[3/4] 开始分析图片...")
    results = analyze_posts(trigger_posts, media_index)
    
    # 保存结果
    output_file = OUTPUT_DIR / f"media_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_results(results, output_file)
    print(f"\n[4/4] 结果已保存到：{output_file}")
    
    # 打印汇总
    print_summary(results)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())