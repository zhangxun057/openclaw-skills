#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
[已废弃] 朋友圈图片深度分析

⚠️ 本脚本已废弃，请使用 analyze_media.py
触发逻辑已迁移到 run_batch.py 的 image_trigger 字段

旧逻辑：基于 extract_media_urls.py 的规则筛选值得分析的帖子
新逻辑：run_batch.py 提取时直接输出 image_trigger=0/1

功能：
1. 读取值得分析的帖子列表（extract_media_urls.py 输出）
2. 调用视觉 API（Seedream）分析图片
3. 提取：人物、产品、场景、事件信息
4. 输出结构化分析结果

输入：analyze_images_work/valuable_posts.json
输出：analyze_images_work/image_analysis_results.json
"""

import json
import sys
import os
import time
import base64
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
REQUEST_INTERVAL = 60 / MAX_REQUESTS_PER_MINUTE  # 每条间隔


def load_valuable_posts():
    """加载值得分析的帖子列表"""
    input_file = WORK_DIR / "valuable_posts.json"
    if not input_file.exists():
        print(f"❌ 文件不存在：{input_file}")
        print("  请先运行 extract_media_urls.py")
        return []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


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
        base_dir = RAW_DIR = PROJECT_DIR / "raw" / html_file.replace('.html', '')
        
        for post in entry.get('posts', []):
            media_files = post.get('media_files', [])
            # 提取 post_id
            for mf in media_files:
                match = mf.split('/')[-1]  # e.g. "14903304369418605071_0.jpg"
                if '_' in match:
                    post_id = match.rsplit('_', 1)[0]
                    full_path = str(base_dir / mf)
                    if post_id not in mapping:
                        mapping[post_id] = {
                            'nickname': post.get('nickname', ''),
                            'tm_str': post.get('tm_str', ''),
                            'content': post.get('contentDesc', ''),
                            'media_files': [
                                str(base_dir / f) for f in media_files
                                if not f.startswith('media/avatar_')
                            ]
                        }
                    else:
                        # 多条媒体追加
                        mapping[post_id]['media_files'].extend([
                            str(base_dir / f) for f in media_files
                            if not f.startswith('media/avatar_')
                        ])
    
    return mapping


def encode_image_base64(image_path):
    """将图片转为 base64"""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"  ⚠️ 读取图片失败 {image_path}: {e}")
        return None


def call_seedream_vision(image_path, context_info=None):
    """
    调用 Seedream 视觉理解 API 分析单张图片
    
    参数：
    - image_path: 本地图片路径
    - context_info: 帖子上下文（nickname, content, events 等）
    
    返回：分析结果 dict
    """
    # 编码图片
    image_base64 = encode_image_base64(image_path)
    if not image_base64:
        return None
    
    # 构建提示词
    system_prompt = """你是朋友圈图片分析专家，专门从白酒销售视角分析图片。

分析维度：
1. 人物识别：人数、身份（商务/私人）、互动关系
2. 产品信息：是否有白酒产品、展示形式（酒柜/酒桌/产品照）
3. 场景判断：宴会/商务接待/家庭聚会/户外/其他
4. 事件推断：从图片推断可能的人生节点（婚礼/生日/开业/其他）
5. 销售信号：是否适合作为销售谈资

输出 JSON 格式：
{
  "人物": "描述",
  "产品": "是否有白酒，描述",
  "场景": "场景类型",
  "事件": "推断的事件类型或空",
  "销售价值": "高/中/低",
  "备注": "其他有价值信息"
}

注意：
- 只输出 JSON，不要其他内容
- 无法判断时标注"无法确定"
- 重点关注白酒相关内容"""
    
    user_prompt = f"分析这张朋友圈图片"
    if context_info:
        if context_info.get('content'):
            user_prompt += f"\n\n朋友圈内容：{context_info['content']}"
        if context_info.get('events'):
            user_prompt += f"\n已有事件标签：{context_info['events']}"
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
                # 尝试解析 JSON
                try:
                    # 提取 JSON（可能在 ```json ... ``` 中）
                    if '```json' in content:
                        content = content.split('```json')[1].split('```')[0]
                    elif '```' in content:
                        content = content.split('```')[1].split('```')[0]
                    return json.loads(content.strip())
                except json.JSONDecodeError:
                    return {'raw_response': content}
            
            return None
    
    except Exception as e:
        print(f"  ⚠️ API 调用失败：{e}")
        return None


def analyze_posts(posts, media_index):
    """
    批量分析帖子中的图片
    
    策略：
    - 每个帖子最多分析 2 张图片（避免重复）
    - 优先分析有事件/信号的帖子
    """
    results = []
    
    print(f"\n开始分析 {len(posts)} 条帖子...")
    
    for i, post in enumerate(posts, 1):
        post_id = post.get('post_id', '')
        nickname = post.get('nickname', '未知')
        reason = post.get('reason', '')
        
        print(f"\n[{i}/{len(posts)}] {nickname} | {reason[:30]}")
        
        # 获取该 post 的媒体文件
        media_info = media_index.get(post_id, {})
        media_files = media_info.get('media_files', [])
        
        if not media_files:
            # 尝试从 post 中获取 media
            media_files = post.get('media_files', [])
        
        if not media_files:
            print(f"  ⚠️ 无媒体文件，跳过")
            continue
        
        # 限制每 post 分析数量
        files_to_analyze = media_files[:2]
        
        post_results = []
        for media_path in files_to_analyze:
            if not os.path.exists(media_path):
                print(f"  ⚠️ 文件不存在：{media_path}")
                continue
            
            # 调用 API
            context = {
                'nickname': nickname,
                'content': post.get('content', ''),
                'events': post.get('events', []),
                'signals': post.get('signals', []),
                'traits': post.get('traits', {})
            }
            
            result = call_seedream_vision(media_path, context)
            
            if result:
                post_results.append({
                    'media_path': media_path,
                    'analysis': result,
                    'post_id': post_id,
                    'nickname': nickname
                })
                print(f"  ✓ {os.path.basename(media_path)}: 销售价值={result.get('销售价值', 'N/A')}")
            else:
                print(f"  ✗ 分析失败")
            
            # 限速
            time.sleep(REQUEST_INTERVAL)
        
        if post_results:
            results.append({
                'post_id': post_id,
                'nickname': nickname,
                'date': post.get('date', ''),
                'reason': reason,
                'content': post.get('content', ''),
                'events': post.get('events', []),
                'signals': post.get('signals', []),
                'image_results': post_results
            })
    
    return results


def save_results(results, summary_file):
    """保存分析结果"""
    output_file = OUTPUT_DIR / f"image_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 同步保存一份到工作目录根目录（方便查看）
    latest = WORK_DIR / "latest_analysis.json"
    with open(latest, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return output_file


def print_summary(results):
    """打印分析汇总"""
    if not results:
        print("\n无分析结果")
        return
    
    total_posts = len(results)
    total_images = sum(len(r.get('image_results', [])) for r in results)
    
    # 按销售价值统计
    value_stats = {'高': 0, '中': 0, '低': 0}
    high_value_posts = []
    
    for r in results:
        for img in r.get('image_results', []):
            analysis = img.get('analysis', {})
            value = analysis.get('销售价值', '低')
            if value in value_stats:
                value_stats[value] += 1
            if value == '高':
                high_value_posts.append(r)
    
    print("\n" + "=" * 60)
    print("图片分析汇总")
    print("=" * 60)
    print(f"  分析帖子数：{total_posts}")
    print(f"  分析图片数：{total_images}")
    print(f"\n销售价值分布：")
    print(f"  高：{value_stats['高']} 张")
    print(f"  中：{value_stats['中']} 张")
    print(f"  低：{value_stats['低']} 张")
    
    if high_value_posts:
        print(f"\n高价值帖子（建议优先跟进）：")
        for r in high_value_posts[:5]:
            print(f"  - {r['nickname']}: {r['reason']}")


def main():
    print("=" * 60)
    print("朋友圈图片深度分析")
    print("=" * 60)
    
    # 1. 加载值得分析的帖子
    print("\n[1/3] 加载待分析帖子...")
    posts = load_valuable_posts()
    if not posts:
        print("  ❌ 没有待分析帖子，请先运行 extract_media_urls.py")
        return 1
    print(f"  待分析帖子：{len(posts)} 条")
    
    # 2. 加载 media_index
    print("\n[2/3] 加载媒体索引...")
    media_index = load_media_index()
    print(f"  媒体映射：{len(media_index)} 条")
    
    # 3. 分析图片
    print("\n[3/3] 开始分析图片...")
    results = analyze_posts(posts, media_index)
    
    # 4. 保存结果
    output_file = save_results(results, WORK_DIR / "summary.json")
    print(f"\n✓ 结果保存到：{output_file}")
    
    # 5. 打印汇总
    print_summary(results)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
