#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seedream 4.5 API 调用脚本
统一调用 Seedream 4.5 生成高质量信息图

使用方法:
    python seedream_api.py generate "<中文Prompt>" --output infographic.png
    python seedream_api.py generate-upload "<中文Prompt>"

API Key 自动从 ~/.openclaw/apis/ark.json 读取
"""

import argparse
import json
import os
import sys
from typing import Optional

# Seedream API 端点
SEEDREAM_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"


def load_api_key() -> str:
    """
    从 ~/.openclaw/apis.md 读取 Seedream API Key
    
    Returns:
        API Key 字符串
        
    Raises:
        FileNotFoundError: 如果配置文件不存在
        ValueError: 如果找不到 Seedream API Key
    """
    import re
    
    config_path = os.path.expanduser("~/.openclaw/apis.md")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"API 配置文件不存在: {config_path}\n"
            "请确保 apis.md 文件存在并包含 Seedream API Key"
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 Seedream (ARK) 部分的 API Key
    # 匹配模式: | API Key | `xxx` | 图片生成 |
    pattern = r'##\s*5\.\s*Seedream.*?\|\s*API Key\s*\|\s*`([^`]+)`'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # 备选：直接搜索 Seedream 附近的 API Key
    seedream_section = re.search(r'##\s*5\.\s*Seedream.*?(?=##|$)', content, re.DOTALL | re.IGNORECASE)
    if seedream_section:
        section = seedream_section.group(0)
        key_match = re.search(r'`([a-f0-9-]{36})`', section)
        if key_match:
            return key_match.group(1)
    
    raise ValueError(
        f"在 {config_path} 中找不到 Seedream API Key\n"
        "请确保文件包含 '## 5. Seedream' 部分及 API Key"
    )


def generate_image(
    prompt: str,
    model: str = "doubao-seedream-4-5-251128",
    size: str = "4K",
    format: str = "png",
    api_key: Optional[str] = None
) -> dict:
    """
    调用 Seedream API 生成图像
    
    Args:
        prompt: 图像生成提示词（中文）
        model: 模型名称
        size: 图像尺寸 (4K/2K/1080p等)
        format: 输出格式 (png/jpg)
        api_key: API Key（如不提供则自动从配置文件读取）
        
    Returns:
        API 响应字典
    """
    import requests
    
    if api_key is None:
        api_key = load_api_key()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "format": format
    }
    
    try:
        response = requests.post(SEEDREAM_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 调用失败: {e}", file=sys.stderr)
        if hasattr(e.response, 'text'):
            print(f"响应内容: {e.response.text}", file=sys.stderr)
        raise


def download_image(url: str, output_path: str) -> str:
    """
    下载生成的图像
    
    Args:
        url: 图像 URL
        output_path: 保存路径
        
    Returns:
        保存的文件路径
    """
    import requests
    
    response = requests.get(url)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    return output_path


def upload_to_server(file_path: str) -> str:
    """
    上传文件到文件服务器
    
    从 ~/.openclaw/apis.md 读取文件服务器配置
    
    Args:
        file_path: 本地文件路径
        
    Returns:
        文件服务器永久链接
        
    Raises:
        FileNotFoundError: 如果配置文件不存在
        ValueError: 如果找不到文件服务器配置
        requests.RequestException: 如果上传失败
    """
    import re
    
    config_path = os.path.expanduser("~/.openclaw/apis.md")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"API 配置文件不存在: {config_path}\n"
            "请确保 apis.md 文件存在并包含文件服务器配置"
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找文件服务器配置
    # 匹配 ## 6. 文件服务器 部分
    section_match = re.search(r'##\s*6\.\s*文件服务器.*?(?=##|$)', content, re.DOTALL)
    if not section_match:
        raise ValueError("在 apis.md 中找不到文件服务器配置 (## 6. 文件服务器)")
    
    section = section_match.group(0)
    
    # 提取 URL
    url_match = re.search(r'\|\s*URL\s*\|\s*`([^`]+)`', section)
    if not url_match:
        raise ValueError("找不到文件服务器 URL")
    upload_url = url_match.group(1).strip()
    
    # 提取 Token
    token_match = re.search(r'\|\s*Token\s*\|\s*`([^`]+)`', section)
    if not token_match:
        raise ValueError("找不到文件服务器 Token")
    token = token_match.group(1).strip()
    
    # 准备上传
    file_name = os.path.basename(file_path)
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # 构建 multipart/form-data 请求
    import requests
    
    headers = {
        'Authorization': f'Basic {token}'
    }
    
    files = {
        'file': (file_name, file_content, f'image/{os.path.splitext(file_name)[1][1:]}')
    }
    
    try:
        response = requests.post(upload_url, headers=headers, files=files)
        response.raise_for_status()
        
        result = response.json()
        
        # 根据响应格式提取 URL
        # 假设响应格式: {"success": true, "data": {"url": "..."}}
        if result.get('success') and 'data' in result:
            data = result['data']
            if isinstance(data, dict) and 'url' in data:
                return data['url']
            elif isinstance(data, str):
                return data
        elif 'url' in result:
            return result['url']
        else:
            # 返回完整响应用于调试
            return str(result)
            
    except requests.exceptions.RequestException as e:
        print(f"上传失败: {e}", file=sys.stderr)
        if hasattr(e.response, 'text'):
            print(f"响应: {e.response.text}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Seedream 4.5 信息图生成工具"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # generate 命令
    gen_parser = subparsers.add_parser('generate', help='生成图像并保存到本地')
    gen_parser.add_argument('prompt', help='图像生成提示词（中文）')
    gen_parser.add_argument('--model', default='doubao-seedream-4-5-251128',
                          help='模型名称 (默认: doubao-seedream-4-5-251128)')
    gen_parser.add_argument('--size', default='4K',
                          help='图像尺寸 (默认: 4K)')
    gen_parser.add_argument('--format', default='png',
                          help='输出格式 (默认: png)')
    gen_parser.add_argument('--output', '-o', default='infographic.png',
                          help='输出文件路径 (默认: infographic.png)')
    
    # generate-upload 命令
    upload_parser = subparsers.add_parser('generate-upload', 
                                         help='生成图像并上传到文件服务器')
    upload_parser.add_argument('prompt', help='图像生成提示词（中文）')
    upload_parser.add_argument('--model', default='doubao-seedream-4-5-251128',
                             help='模型名称 (默认: doubao-seedream-4-5-251128)')
    upload_parser.add_argument('--size', default='4K',
                             help='图像尺寸 (默认: 4K)')
    upload_parser.add_argument('--format', default='png',
                             help='输出格式 (默认: png)')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    try:
        print(f"正在生成图像...")
        print(f"提示词: {args.prompt[:100]}...")
        
        result = generate_image(
            prompt=args.prompt,
            model=args.model,
            size=args.size,
            format=args.format
        )
        
        if 'data' in result and len(result['data']) > 0:
            image_url = result['data'][0].get('url')
            
            if args.command == 'generate':
                # 下载到本地
                output_path = download_image(image_url, args.output)
                print(f"✅ 图像已保存: {output_path}")
                
            elif args.command == 'generate-upload':
                # 下载临时文件后上传
                temp_path = "/tmp/temp_infographic.png"
                download_image(image_url, temp_path)
                permanent_url = upload_to_server(temp_path)
                print(f"✅ 图像已上传: {permanent_url}")
                
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            print(f"⚠️ API 响应异常: {result}", file=sys.stderr)
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        print("请确保 ~/.openclaw/apis.md 文件存在且包含 Seedream API Key", 
              file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        print("请确保 ~/.openclaw/apis.md 包含 ## 5. Seedream 部分及 API Key", 
              file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
