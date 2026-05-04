#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从已分析的 JSONL 数据中筛选值得分析图片的帖子

输入：logs/YYYY-MM-DD.jsonl（已分析的提取结果）
输出：待分析图片列表 JSON（post_id, wxid, nickname, media_path, reason）
"""

import json
import sys
import re
from pathlib import Path

# 路径配置
SKILL_DIR = Path(__file__).parent
PROJECT_DIR = SKILL_DIR.parent.parent / "projects" / "moments-analysis"
RAW_DIR = PROJECT_DIR / "raw"
LOGS_DIR = PROJECT_DIR / "logs"
OUTPUT_DIR = PROJECT_DIR / "analyze_images_work"
STATE_DIR = PROJECT_DIR / "state"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_media_index():
    """加载 media_index.json，构建 post_id -> media_path 的映射"""
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
                fname = mf.split('/')[-1]  # e.g. "14903304369418605071_0.jpg"
                if '_' in fname:
                    post_id = fname.rsplit('_', 1)[0]
                    full_path = str(base_dir / mf)
                    if post_id not in mapping:
                        mapping[post_id] = {
                            'nickname': post.get('nickname', ''),
                            'tm_str': post.get('tm_str', ''),
                            'content': post.get('contentDesc', ''),
                            'media_files': [str(base_dir / f) for f in non_avatar]
                        }
                    break
    
    return mapping


def is_valuable_for_image_analysis(post, media_count):
    """
    判断帖子是否值得分析图片
    """
    post_type = post.get('post_type', '')
    if post_type == 'noise':
        return False, ''
    
    if media_count == 0:
        return False, ''
    
    events = post.get('events', [])
    signals = post.get('signals', [])
    content_desc = post.get('contentDesc', post.get('content', ''))
    location = post.get('location', '')
    
    reasons = []
    
    # 人生节点事件
    life_events = ['婚礼', '开业', '生日', '周年', '乔迁', '升学', '订婚', '满月', '周岁', '封坛', '奠基', '发布', '峰会', '庆典', '展会', '宴请']
    for event in events:
        for keyword in life_events:
            if keyword in event:
                reasons.append(f'人生节点: {event}')
                break
    
    # 销售信号
    if signals:
        reasons.append(f'销售信号')
    
    # 多图+有内容
    if media_count >= 3 and content_desc.strip():
        reasons.append(f'多图({media_count}张)')
    
    # 有地理位置
    if location and content_desc.strip():
        reasons.append(f'场景地点')
    
    # 白酒相关
    liquor_keywords = ['酒', '茅台', '酱香', '酱酒', '董酒', '习酒', '国台', '珍酒', '青酒', '丹泉', '龍國宴', '开瓶', '封坛', '酒窖', '品鉴']
    for kw in liquor_keywords:
        if kw in content_desc:
            reasons.append(f'白酒相关')
            break
    
    # 商业活动
    product_keywords = ['发布', '新品', '上市', '活动', '招商', '代理', '团购', '定制']
    for kw in product_keywords:
        if kw in content_desc:
            reasons.append(f'商业活动')
            break
    
    if reasons:
        return True, '; '.join(reasons[:2])
    
    if content_desc and len(content_desc) > 50:
        return True, f'内容丰富({len(content_desc)}字)'
    
    return False, ''


def find_media_for_post(post_id, media_index):
    """根据 post_id 查找对应的媒体文件"""
    if post_id in media_index:
        return media_index[post_id]
    for key, value in media_index.items():
        if post_id.startswith(key) or key.startswith(post_id):
            return value
    return None


def process_log_file(log_file, media_index):
    """处理单个日志文件"""
    valuable_posts = []
    
    # 尝试多种编码
    content = None
    for encoding in ['utf-8', 'gbk', 'utf-8-sig']:
        try:
            with open(log_file, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print(f"  [!] 无法解码文件，跳过")
        return valuable_posts
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            post = json.loads(line)
        except json.JSONDecodeError:
            continue
        
        post_id = post.get('post_id', '')
        wxid = post.get('wxid', '')
        nickname = post.get('nickname', '未知')
        
        # 从 media_index 获取媒体信息
        media_info = find_media_for_post(post_id, media_index)
        media_count = len(media_info.get('media_files', [])) if media_info else 0
        
        is_valuable, reason = is_valuable_for_image_analysis(post, media_count)
        
        if is_valuable:
            item = {
                'post_id': post_id,
                'wxid': wxid,
                'nickname': nickname,
                'reason': reason,
                'media_count': media_count,
                'events': post.get('events', []),
                'signals': post.get('signals', []),
                'traits': post.get('traits', {}),
                'content': post.get('contentDesc', post.get('content', '')),
            }
            if media_info:
                item['media_files'] = media_info.get('media_files', [])
                item['tm_str'] = media_info.get('tm_str', '')
            valuable_posts.append(item)
    
    return valuable_posts


def main():
    print("=" * 60)
    print("朋友圈图片价值筛选")
    print("=" * 60)
    
    print("\n[1/3] 加载 media_index...")
    media_index = load_media_index()
    print(f"  加载了 {len(media_index)} 条媒体映射")
    
    print("\n[2/3] 扫描 logs/ 目录...")
    log_files = sorted(LOGS_DIR.glob("*.jsonl"))
    print(f"  发现 {len(log_files)} 个日志文件")
    
    print("\n[3/3] 筛选值得分析的帖子...")
    all_valuable = []
    
    for log_file in log_files:
        date_str = log_file.stem
        print(f"\n  处理 {date_str}...")
        valuable = process_log_file(log_file, media_index)
        print(f"    发现 {len(valuable)} 条值得分析")
        for item in valuable:
            item['date'] = date_str
            all_valuable.append(item)
    
    output_file = OUTPUT_DIR / "valuable_posts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_valuable, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"筛选完成！共 {len(all_valuable)} 条值得分析")
    print(f"结果保存到：{output_file}")
    print("=" * 60)
    
    if all_valuable:
        print("\n按日期统计：")
        by_date = {}
        for item in all_valuable:
            d = item.get('date', 'unknown')
            by_date[d] = by_date.get(d, 0) + 1
        for d in sorted(by_date.keys()):
            print(f"  {d}: {by_date[d]} 条")


if __name__ == '__main__':
    main()
