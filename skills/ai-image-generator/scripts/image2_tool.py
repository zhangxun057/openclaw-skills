# -*- coding: utf-8 -*-
"""
Image2 (GPT-Image-2) API 脚本 — 图片生成主路径
通过 APIMart 调用 GPT-Image-2 模型生成图片
支持文生图、图生图（Base64 本地方案）
"""

import sys, io
# 编码已在主脚本设置，此处跳过

import requests
import json
import time
import os
import argparse
import hashlib

# ==================== 配置 ====================
IMAGE2_API_KEY = os.environ.get("IMAGE2_API_KEY", "sk-C4fVi6uZ78vS0Ip4F0fr8ySnCP5KOwGbCqfWZfiRUfGwnZVm")
IMAGE2_BASE_URL = os.environ.get("IMAGE2_BASE_URL", "https://api.apimart.ai")
IMAGE2_MODEL = "gpt-image-2"

# 文件服务器配置
FILE_SERVER_URL = os.environ.get("FILE_SERVER_URL", "https://mjy.gzlex.com:8095/api/sse/file/upload")
FILE_SERVER_TOKEN = os.environ.get("FILE_SERVER_TOKEN", "ampzOmhjenFAMTIz")


def generate_image(prompt, size="1024x1024", image=None, quality="high"):
    """
    调用 GPT-Image-2 生成图片（异步）
    
    Args:
        prompt: 图片描述（英文效果更佳）
        size: 尺寸 "1024x1024" / "1536x1024" / "1024x1536" / "1792x1024" / "1024x1792"
        image: 参考图（URL 或 Base64）
        quality: 画质 "standard" / "high"
    
    Returns:
        图片 URL 列表 或 None
    """
    url = f"{IMAGE2_BASE_URL}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {IMAGE2_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": IMAGE2_MODEL,
        "prompt": prompt,
        "size": size,
        "quality": quality
    }
    
    # 如果有参考图，添加到 payload
    if image:
        if image.startswith("data:"):
            # Base64 格式
            payload["image"] = image
            print(f"[Image2] Using Base64 reference image ({len(image)} chars)")
        else:
            # URL 格式
            payload["image"] = image
            print(f"[Image2] Using reference image URL: {image[:80]}...")
    
    print(f"[Image2] Submitting: {prompt[:80]}...")
    print(f"[Image2] Model: {IMAGE2_MODEL}, Size: {size}")
    
    # Step 1: 提交生成任务
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        data = r.json()
        
        if data.get("code") != 200 or not data.get("data"):
            print(f"[Image2] Failed: {json.dumps(data, ensure_ascii=False)[:300]}")
            return None
        
        task_id = data["data"][0].get("task_id")
        if not task_id:
            print(f"[Image2] No task_id in response")
            return None
        
        print(f"[Image2] Task submitted: {task_id}")
        
    except Exception as e:
        print(f"[Image2] Submit error: {e}")
        return None
    
    # Step 2: 轮询任务状态
    poll_url = f"{IMAGE2_BASE_URL}/v1/tasks/{task_id}"
    max_polls = 60  # 最多等 3 分钟
    
    for i in range(max_polls):
        try:
            time.sleep(3)  # 每 3 秒轮询一次
            r = requests.get(poll_url, headers=headers, timeout=15)
            data = r.json()
            
            task_data = data.get("data", {})
            status = task_data.get("status", "unknown")
            progress = task_data.get("progress", 0)
            
            if status == "completed":
                # 提取图片 URL
                images = task_data.get("result", {}).get("images", [])
                urls = []
                for img in images:
                    url_list = img.get("url", [])
                    if isinstance(url_list, list):
                        urls.extend(url_list)
                    elif isinstance(url_list, str):
                        urls.append(url_list)
                
                if urls:
                    elapsed = task_data.get("actual_time", "?")
                    print(f"[Image2] Done! {len(urls)} image(s) in {elapsed}s")
                    return urls
                else:
                    print(f"[Image2] Completed but no URLs found")
                    return None
            
            elif status == "failed":
                print(f"[Image2] Task failed: {task_data}")
                return None
            
            else:
                print(f"[Image2] Poll {i+1}: {status} ({progress}%)")
                
        except Exception as e:
            print(f"[Image2] Poll error: {e}")
    
    print(f"[Image2] Timeout after {max_polls * 3}s")
    return None


def upload_to_file_server(file_path, filename=None):
    """上传文件到文件服务器，返回永久链接"""
    if not filename:
        filename = os.path.basename(file_path)
    
    headers = {
        "Authorization": f"Bearer {FILE_SERVER_TOKEN}",
        "User-Agent": "Apifox/1.0.0"
    }
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            r = requests.post(FILE_SERVER_URL, headers=headers, files=files, timeout=60)
        
        if r.status_code == 200:
            result = r.json()
            if result.get('code') == '0':
                file_url = result.get('data', {}).get('fileUrl', '')
                print(f"[Upload] OK: {file_url}")
                return file_url
        
        print(f"[Upload] Failed: {r.text[:200]}")
        return None
    except Exception as e:
        print(f"[Upload] Error: {e}")
        return None


def download_image(url, save_path=None):
    """下载图片到本地"""
    if not save_path:
        name = f"image2_{int(time.time())}_{hashlib.md5(url.encode()).hexdigest()[:8]}"
        save_path = f"/tmp/{name}.png"
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(r.content)
        print(f"[Download] OK: {save_path} ({len(r.content)} bytes)")
        return save_path
    except Exception as e:
        print(f"[Download] Failed: {e}")
        return None


def generate_and_save(prompt, size="1024x1024", image=None, save_dir=None):
    """
    完整流程：生成图片 → 下载到本地 → 返回本地路径
    
    Args:
        prompt: 图片描述
        size: 尺寸
        image: 参考图（URL 或 Base64）
        save_dir: 保存目录（默认 workspace/scratchpad）
    
    Returns:
        本地文件路径列表
    """
    if not save_dir:
        save_dir = "C:/Users/44452/.openclaw/agents/zhuizhuixia/workspace/scratchpad"
    
    # Step 1: 生成
    urls = generate_image(prompt, size=size, image=image)
    if not urls:
        print("[Error] Image generation failed")
        return []
    
    local_paths = []
    for i, url in enumerate(urls):
        # Step 2: 下载
        filename = f"image_{int(time.time())}_{i}.png"
        save_path = os.path.join(save_dir, filename)
        
        local_path = download_image(url, save_path)
        if local_path:
            local_paths.append(local_path)
        else:
            print(f"[Error] Failed to download: {url}")
    
    return local_paths


def generate_and_upload(prompt, size="1024x1024", image=None):
    """
    完整流程：生成图片 → 下载 → 上传文件服务器 → 返回永久链接
    
    Args:
        prompt: 图片描述
        size: 尺寸
        image: 参考图（URL 或 Base64）
    
    Returns:
        永久图片 URL 列表
    """
    # Step 1: 生成
    urls = generate_image(prompt, size=size, image=image)
    if not urls:
        print("[Error] Image generation failed")
        return []
    
    permanent_urls = []
    for i, url in enumerate(urls):
        # Step 2: 下载
        local_path = download_image(url)
        if not local_path:
            print(f"[Fallback] Using API URL: {url}")
            permanent_urls.append(url)
            continue
        
        # Step 3: 上传
        file_url = upload_to_file_server(local_path, f"image2_{int(time.time())}_{i}.png")
        if file_url:
            permanent_urls.append(file_url)
        else:
            permanent_urls.append(url)  # Fallback
        
        # Cleanup
        try:
            os.remove(local_path)
        except:
            pass
    
    return permanent_urls


# ==================== CLI 入口 ====================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image2 (GPT-Image-2) image generation')
    sub = parser.add_subparsers(dest='command')
    
    # generate 命令
    gen = sub.add_parser('generate', help='Generate image')
    gen.add_argument('prompt', help='Image description')
    gen.add_argument('--size', default='1024x1024', help='Size')
    
    # generate-upload 命令
    gu = sub.add_parser('generate-upload', help='Generate and upload')
    gu.add_argument('prompt', help='Image description')
    gu.add_argument('--size', default='1024x1024', help='Size')
    gu.add_argument('--image', '-i', default=None, help='Reference image URL or Base64')
    
    # generate-save 命令（本地保存）
    gs = sub.add_parser('generate-save', help='Generate and save locally')
    gs.add_argument('prompt', help='Image description')
    gs.add_argument('--size', default='1024x1024', help='Size')
    gs.add_argument('--image', '-i', default=None, help='Reference image URL or Base64')
    gs.add_argument('--save-dir', default=None, help='Save directory')
    
    # image-to-image 命令
    i2i = sub.add_parser('image-to-image', help='Generate with reference image')
    i2i.add_argument('prompt', help='Image description')
    i2i.add_argument('--image', '-i', required=True, help='Reference image URL or Base64')
    i2i.add_argument('--size', default='1024x1024', help='Size')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        urls = generate_image(args.prompt, size=args.size)
        if urls:
            for u in urls:
                print(u)
    
    elif args.command == 'generate-upload':
        urls = generate_and_upload(args.prompt, size=args.size, image=args.image)
        if urls:
            print("\nPermanent URLs:")
            for u in urls:
                print(u)
    
    elif args.command == 'generate-save':
        paths = generate_and_save(args.prompt, size=args.size, image=args.image, save_dir=args.save_dir)
        if paths:
            print("\nLocal paths:")
            for p in paths:
                print(p)
    
    elif args.command == 'image-to-image':
        if not args.image:
            print("[Error] --image is required for image-to-image command")
            sys.exit(1)
        urls = generate_and_upload(args.prompt, size=args.size, image=args.image)
        if urls:
            print("\nPermanent URLs:")
            for u in urls:
                print(u)
    
    else:
        parser.print_help()
