#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seedream 图像生成 API 调用脚本（增强稳定版）
支持文生图、图生图、组图、多图融合，生成后自动上传到文件服务器

稳定性保障：
- 自动重试（最多 3 次，指数退避）
- 智能超时（根据操作类型）
- 错误分类和回退
- 详细日志
"""

import os
import sys
import json
import time
import requests
import argparse
from typing import List, Optional, Dict, Any

# ============== 配置常量 ==============
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # 指数退避：1s, 2s, 4s

# 超时设置（秒）
TIMEOUT_GENERATE = 120    # 文生图
TIMEOUT_IMG2IMG = 180     # 图生图
TIMEOUT_UPLOAD = 60       # 文件上传
TIMEOUT_DOWNLOAD = 30     # 图片下载

# API 端点
ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

# ============== 环境变量 ==============
env_file = os.path.expanduser('~/.openclaw/.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

ARK_API_KEY = os.getenv('ARK_API_KEY')
FILE_SERVER_URL = os.getenv('FILE_SERVER_URL')
FILE_SERVER_TOKEN = os.getenv('FILE_SERVER_TOKEN')

# ============== 日志函数 ==============
def log_info(msg: str):
    print(f"[INFO] {msg}")

def log_warn(msg: str):
    print(f"[WARN] {msg}")

def log_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)

def log_retry(msg: str, attempt: int, max_attempts: int):
    print(f"[RETRY {attempt}/{max_attempts}] {msg}")

# ============== 核心函数 ==============

# ============== 模型支持的尺寸 ==============
MODEL_SUPPORTED_SIZES = {
    "doubao-seedream-5.0-lite": ["1K", "2K", "3K", "4K"],
    "doubao-seedream-4-5-251128": ["2K", "4K"],  # 4.5 不支持 1K 和 3K
    "doubao-seedream-4.0": ["1K", "2K", "4K"],
    "doubao-seedream-3.0-t2i": ["1K", "2K"],
}

def validate_size(model: str, size: str) -> bool:
    """验证尺寸是否被模型支持"""
    supported = MODEL_SUPPORTED_SIZES.get(model, ["2K"])
    return size in supported

def generate_image(prompt: str, 
                   model: str = "doubao-seedream-4-5-251128", 
                   size: str = "2K",
                   image_url: Optional[str] = None, 
                   image_urls: Optional[List[str]] = None, 
                   sequential: bool = False, 
                   max_images: int = 15, 
                   output_format: str = "png", 
                   watermark: bool = False,
                   timeout: Optional[int] = None) -> List[str]:
    """
    生成图像（带重试机制）
    
    Args:
        prompt: 提示词
        model: 模型版本，默认 doubao-seedream-4-5-251128
        size: 分辨率，默认 2K
        image_url: 单张参考图 URL
        image_urls: 多张参考图 URL 列表
        sequential: 是否组图模式
        max_images: 最大图片数
        output_format: 输出格式
        watermark: 是否加水印
        timeout: 超时时间（秒）
    
    Returns:
        图片 URL 列表
    
    Raises:
        ValueError: API Key 缺失或参数无效
        Exception: API 调用失败
    """
    
    if not ARK_API_KEY:
        raise ValueError("ARK_API_KEY not found in environment. Please set it in ~/.openclaw/.env")
    
    # 参数验证
    if not validate_size(model, size):
        supported = MODEL_SUPPORTED_SIZES.get(model, ["2K"])
        raise ValueError(f"模型 {model} 不支持尺寸 {size}。支持的尺寸：{', '.join(supported)}")
    
    # 自动计算超时
    if timeout is None:
        timeout = TIMEOUT_IMG2IMG if (image_url or image_urls) else TIMEOUT_GENERATE
    
    # 构建请求体
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
        "watermark": watermark
    }
    
    # 添加参考图
    if image_url:
        payload["image_url"] = image_url
    elif image_urls:
        payload["image_urls"] = image_urls
    
    # 组图模式
    if sequential:
        payload["sequential"] = True
        payload["max_images"] = max_images
    
    headers = {
        "Authorization": f"Bearer {ARK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 重试逻辑
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log_info(f"正在生成图像：{prompt[:50]}... (模型：{model}, 尺寸：{size})")
            
            response = requests.post(
                ARK_API_URL,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # HTTP 状态码检查
            if response.status_code != 200:
                raise Exception(f"API 请求失败：{response.status_code} - {response.text[:200]}")
            
            result = response.json()
            
            # 响应数据检查
            if "data" not in result:
                # 检查是否有错误信息
                error_msg = result.get("error", {}).get("message", "未知错误")
                raise Exception(f"API 返回异常：{error_msg}")
            
            image_urls = [item["url"] for item in result["data"]]
            log_info(f"生成成功，共{len(image_urls)}张图片")
            
            return image_urls
            
        except requests.exceptions.Timeout:
            last_error = f"请求超时（{timeout}秒）"
            log_retry(last_error, attempt, MAX_RETRIES)
            
        except requests.exceptions.ConnectionError as e:
            last_error = f"网络连接失败：{str(e)[:100]}"
            log_retry(last_error, attempt, MAX_RETRIES)
            
        except Exception as e:
            last_error = str(e)
            log_retry(last_error, attempt, MAX_RETRIES)
        
        # 指数退避
        if attempt < MAX_RETRIES:
            delay = RETRY_DELAYS[attempt - 1]
            log_info(f"等待 {delay}秒后重试...")
            time.sleep(delay)
    
    # 所有重试都失败
    raise Exception(f"生成图像失败，已重试{MAX_RETRIES}次。最后错误：{last_error}")


def download_image(image_url: str, timeout: int = TIMEOUT_DOWNLOAD) -> bytes:
    """下载图片内容"""
    log_info(f"正在下载图片：{image_url[:60]}...")
    
    response = requests.get(image_url, timeout=timeout)
    if response.status_code != 200:
        raise Exception(f"下载图片失败：{response.status_code}")
    
    return response.content


def upload_to_file_server(image_content: bytes, 
                          filename: str = "image.png",
                          timeout: int = TIMEOUT_UPLOAD) -> str:
    """
    上传图片到文件服务器（带重试）
    
    Args:
        image_content: 图片二进制内容
        filename: 文件名
        timeout: 超时时间
    
    Returns:
        上传后的 URL
    
    Raises:
        ValueError: 文件服务器配置缺失
        Exception: 上传失败
    """
    
    if not FILE_SERVER_URL or not FILE_SERVER_TOKEN:
        raise ValueError("FILE_SERVER_URL or FILE_SERVER_TOKEN not found in environment")
    
    # 重试逻辑
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log_info(f"正在上传到文件服务器：{filename}...")
            
            files = {'file': (filename, image_content, 'image/png')}
            headers = {'Authorization': f'Bearer {FILE_SERVER_TOKEN}'}
            
            upload_response = requests.post(
                FILE_SERVER_URL,
                files=files,
                headers=headers,
                timeout=timeout
            )
            
            if upload_response.status_code != 200:
                raise Exception(f"上传失败：{upload_response.status_code} - {upload_response.text[:200]}")
            
            result = upload_response.json()
            
            if result.get('code') not in [200, '200', 0, '0']:
                # 某些服务器返回 code=0 表示成功
                raise Exception(f"上传失败：{result}")
            
            uploaded_url = result.get('data', {}).get('url') or result.get('data', {}).get('fileUrl')
            
            if not uploaded_url:
                raise Exception(f"上传成功但未返回 URL: {result}")
            
            log_info(f"上传成功：{uploaded_url}")
            return uploaded_url
            
        except requests.exceptions.Timeout:
            last_error = f"上传超时（{timeout}秒）"
            log_retry(last_error, attempt, MAX_RETRIES)
            
        except requests.exceptions.ConnectionError as e:
            last_error = f"网络连接失败：{str(e)[:100]}"
            log_retry(last_error, attempt, MAX_RETRIES)
            
        except Exception as e:
            last_error = str(e)
            log_retry(last_error, attempt, MAX_RETRIES)
        
        # 指数退避
        if attempt < MAX_RETRIES:
            delay = RETRY_DELAYS[attempt - 1]
            log_info(f"等待 {delay}秒后重试...")
            time.sleep(delay)
    
    # 所有重试都失败
    raise Exception(f"上传文件失败，已重试{MAX_RETRIES}次。最后错误：{last_error}")


def generate_and_upload(prompt: str, **kwargs) -> List[str]:
    """
    生成图像并上传到文件服务器
    
    Returns:
        持久化 URL 列表
    """
    # 生成图像
    temp_urls = generate_image(prompt, **kwargs)
    
    # 逐个上传
    uploaded_urls = []
    for i, url in enumerate(temp_urls):
        try:
            # 下载图片
            image_content = download_image(url)
            
            # 生成文件名
            filename = f"seedream_{int(time.time())}_{i}.png"
            
            # 上传
            uploaded_url = upload_to_file_server(image_content, filename)
            uploaded_urls.append(uploaded_url)
            
        except Exception as e:
            log_warn(f"上传图片失败：{url} - {e}")
            log_info(f"使用原始临时 URL: {url}")
            uploaded_urls.append(url)  # 回退到临时 URL
    
    return uploaded_urls


# ============== 命令行入口 ==============

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Seedream 图像生成（增强稳定版）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 文生图
  python seedream_api.py generate-upload "一只猫"
  
  # 图生图
  python seedream_api.py generate-upload "将背景换成海边" --image "https://xxx.jpg"
  
  # 指定模型和参数
  python seedream_api.py generate-upload "提示词" --model doubao-seedream-4-5-251128 --size 4K
  
  # 组图模式
  python seedream_api.py generate-upload "生成 4 张跑车" --sequential --max-images 4
        """
    )
    
    parser.add_argument('command', 
                       choices=['generate', 'generate-upload', 'upload'],
                       help='命令：generate(仅生成), generate-upload(生成 + 上传), upload(仅上传)')
    parser.add_argument('prompt', nargs='?', help='生成提示词或上传的 URL')
    parser.add_argument('--model', 
                       default='doubao-seedream-4-5-251128',
                       help='模型版本 (默认：doubao-seedream-4-5-251128)')
    parser.add_argument('--size', 
                       default='2K',
                       choices=['1K', '2K', '3K', '4K'],
                       help='分辨率 (默认：2K)')
    parser.add_argument('--format', 
                       default='png',
                       choices=['png', 'jpeg'],
                       help='输出格式 (默认：png)')
    parser.add_argument('--image', help='单张参考图 URL')
    parser.add_argument('--images', help='多张参考图 URL(逗号分隔)')
    parser.add_argument('--sequential', 
                       action='store_true',
                       help='组图模式')
    parser.add_argument('--max-images', 
                       type=int, 
                       default=15,
                       help='最大图片数 (默认：15)')
    parser.add_argument('--watermark', 
                       action='store_true',
                       help='加水印')
    parser.add_argument('--timeout', 
                       type=int,
                       help='自定义超时时间 (秒)')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'generate-upload':
            kwargs = {
                'model': args.model,
                'size': args.size,
                'output_format': args.format,
                'sequential': args.sequential,
                'max_images': args.max_images,
                'watermark': args.watermark
            }
            if args.timeout:
                kwargs['timeout'] = args.timeout
            
            if args.image:
                kwargs['image_url'] = args.image
            elif args.images:
                kwargs['image_urls'] = args.images.split(',')
            
            log_info("=" * 50)
            log_info("Seedream 图像生成（增强稳定版）")
            log_info("=" * 50)
            
            urls = generate_and_upload(args.prompt, **kwargs)
            
            log_info("=" * 50)
            log_info("生成的图片链接 (永久有效):")
            log_info("=" * 50)
            for url in urls:
                print(url)
        
        elif args.command == 'generate':
            kwargs = {
                'model': args.model,
                'size': args.size,
                'output_format': args.format,
                'sequential': args.sequential,
                'max_images': args.max_images,
                'watermark': args.watermark
            }
            if args.timeout:
                kwargs['timeout'] = args.timeout
            
            if args.image:
                kwargs['image_url'] = args.image
            elif args.images:
                kwargs['image_urls'] = args.images.split(',')
            
            urls = generate_image(args.prompt, **kwargs)
            
            log_info("临时图片链接 (24 小时有效):")
            for url in urls:
                print(url)
        
        elif args.command == 'upload':
            if not args.prompt:
                raise ValueError("请提供要上传的图片 URL")
            
            image_content = download_image(args.prompt)
            filename = f"upload_{int(time.time())}.png"
            url = upload_to_file_server(image_content, filename)
            log_info(f"上传成功：{url}")
    
    except KeyboardInterrupt:
        log_error("用户中断")
        sys.exit(130)
    except Exception as e:
        log_error(str(e))
        sys.exit(1)
