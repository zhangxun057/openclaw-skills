#!/usr/bin/env python3
"""HTML Generator - 调用 Seedream API 生成图片"""

import requests
import json
import sys
import os

# 配置 - 使用稳定版模型
SEEDREAM_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
SEEDREAM_KEY = "d155ace0-ee4d-42b1-936e-4a16d2623c89"
MODEL = "doubao-seedream-4-5-251128"

FILE_SERVER = "https://mjy.gzlex.com:8095/api/sse/file/upload"
FILE_TOKEN = "ampzOmhjenFAMTIz"

def generate_and_upload(prompt):
    """生成图片并上传到文件服务器，返回永久链接"""
    print(f"[Gen] {prompt[:50]}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SEEDREAM_KEY}"
    }
    
    data = {
        "model": MODEL,
        "prompt": prompt,
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "watermark": False
    }
    
    resp = requests.post(SEEDREAM_URL, headers=headers, json=data, timeout=120)
    
    if resp.status_code != 200:
        print(f"[Err] HTTP {resp.status_code}: {resp.text[:100]}")
        return None
    
    result = resp.json()
    
    if "error" in result:
        print(f"[Err] API Error: {result.get('error', result)[:100]}")
        return None
    
    image_url = result["data"][0]["url"]
    print(f"[OK] Seedream URL: {image_url[:80]}...")
    
    # 下载到临时文件
    import tempfile
    import shutil
    
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_path = temp_file.name
    temp_file.close()
    
    print(f"[Download] Saving to {temp_path}")
    
    # 使用 session 处理重定向
    session = requests.Session()
    img_resp = session.get(image_url, timeout=60)
    
    with open(temp_path, 'wb') as f:
        f.write(img_resp.content)
    
    print(f"[OK] Downloaded, size: {os.path.getsize(temp_path)} bytes")
    
    # 上传到文件服务器
    print(f"[Upload] Uploading to file server...")
    with open(temp_path, "rb") as f:
        files = {"file": f}
        upload_resp = requests.post(FILE_SERVER, headers={"Authorization": f"Bearer {FILE_TOKEN}", "User-Agent": "Apifox/1.0.0"}, files=files, timeout=60)
    
    # 清理临时文件
    os.remove(temp_path)
    
    result = upload_resp.json()
    
    if result.get("code") != "0":
        print(f"[Err] Upload failed: {result}")
        return None
    
    return result["data"]["fileUrl"]

def upload_file(file_path):
    """上传文件到文件服务器"""
    print(f"[Upload] {file_path}")
    
    headers = {
        "Authorization": f"Bearer {FILE_TOKEN}",
        "User-Agent": "Apifox/1.0.0"
    }
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(FILE_SERVER, headers=headers, files=files, timeout=60)
    
    result = resp.json()
    
    if result.get("code") != "0":
        print(f"[Err] Upload failed: {result}")
        return None
    
    return result["data"]["fileUrl"]

def main():
    args = sys.argv[1:]
    
    if not args:
        print("""
HTML Generator - AI 生图脚本

Usage:
  python html-gen.py generate "prompt"     生成图片
  python html-gen.py upload /path/to/file  上传文件

Examples:
  python html-gen.py generate "A premium Chinese baijiu bottle"
  python html-gen.py upload /tmp/image.jpg
""")
        return
    
    cmd = args[0]
    
    if cmd == "generate":
        if len(args) < 2:
            print("Usage: python html-gen.py generate 'prompt'")
            return
            
        prompt = args[1]
        url = generate_and_upload(prompt)
        
        if url:
            print(f"[OK] Permanent URL: {url}")
            
    elif cmd == "upload":
        if len(args) < 2:
            print("Usage: python html-gen.py upload /path/to/file")
            return
            
        file_path = args[1]
        if not os.path.exists(file_path):
            print(f"[Err] File not found: {file_path}")
            return
            
        url = upload_file(file_path)
        
        if url:
            print(f"[OK] File URL: {url}")
            
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
