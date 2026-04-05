#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙虾日记封面生成脚本
使用 Seedream 4.5 模型生成 9:16 竖屏手绘风格封面图
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime

# 读取环境变量
env_file = os.path.expanduser('~/.openclaw/.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

ARK_API_KEY = os.getenv('ARK_API_KEY')

# 固定提示词模板
COVER_PROMPT_TEMPLATE = """手绘线稿风格，{theme}，简洁线条，淡蓝色点缀，
9:16 竖屏比例，专业插画，高对比度，龙虾日记本封面"""

# 默认主题（可根据日期动态生成）
DEFAULT_THEMES = [
    "一只可爱的龙虾坐在电脑前写代码",
    "一只龙虾在分析数据和图表",
    "一只龙虾在开会讨论",
    "一只龙虾在阅读飞书文档",
    "一只龙虾在调试代码",
    "一只龙虾在思考 AI 问题",
    "一只龙虾在整理文件",
    "一只龙虾在学习新知识",
]

def get_theme_for_date(date_str):
    """根据日期获取主题（保证同一天的主题一致）"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    day_of_year = date_obj.timetuple().tm_yday
    return DEFAULT_THEMES[day_of_year % len(DEFAULT_THEMES)]

def generate_cover(prompt, model="doubao-seedream-4-5-251128", 
                   size="1440x2560", output_format="png"):
    """生成封面图"""
    
    if not ARK_API_KEY:
        raise ValueError("ARK_API_KEY not found in environment")
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
        "watermark": False
    }
    
    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"正在生成封面图：{prompt[:50]}...")
    
    response = requests.post(
        "https://ark.cn-beijing.volces.com/api/v3/images/generations",
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code != 200:
        raise Exception(f"API 请求失败：{response.status_code} - {response.text}")
    
    result = response.json()
    
    if "data" not in result:
        raise Exception(f"API 返回异常：{result}")
    
    image_url = result["data"][0]["url"]
    print(f"生成成功：{image_url[:80]}...")
    
    return image_url

def download_image(image_url, output_path):
    """下载图片到本地"""
    
    print(f"正在下载图片：{image_url[:80]}...")
    
    response = requests.get(image_url, timeout=60)
    if response.status_code != 200:
        raise Exception(f"下载失败：{response.status_code}")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"下载成功：{output_path}")
    return output_path

def generate_and_save(date_str=None, theme=None, output_dir=None):
    """生成并保存封面图"""
    
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    if theme is None:
        theme = get_theme_for_date(date_str)
    
    if output_dir is None:
        output_dir = os.path.expanduser(
            '~/.openclaw/agents/guaiguaixia/workspace/scratchpad'
        )
    
    # 构建提示词
    prompt = COVER_PROMPT_TEMPLATE.format(theme=theme)
    
    # 生成图片
    image_url = generate_cover(prompt)
    
    # 保存路径
    output_path = os.path.join(
        output_dir, 
        f"diary-{date_str}-cover.png"
    )
    
    # 下载图片
    download_image(image_url, output_path)
    
    print(f"\n[OK] 封面图已保存：{output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='龙虾日记封面生成')
    parser.add_argument('--date', help='日期 (YYYY-MM-DD)', 
                        default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument('--theme', help='主题描述（可选）')
    parser.add_argument('--output', help='输出目录')
    
    args = parser.parse_args()
    
    try:
        output_path = generate_and_save(
            date_str=args.date,
            theme=args.theme,
            output_dir=args.output
        )
        print(f"\n✅ 完成：{output_path}")
    except Exception as e:
        print(f"\n❌ 错误：{e}", file=sys.stderr)
        sys.exit(1)
