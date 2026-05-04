# -*- coding: utf-8 -*-
"""
Serper 图片搜索工具
搜索参考图并下载
"""
import os
import requests
import base64

SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "YOUR_SERPER_API_KEY_HERE")
SERPER_URL = "https://google.serper.dev/images"

HEADERS = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def search_images(query, num=5):
    """
    Serper 图片搜索
    
    Args:
        query: 搜索词
        num: 返回数量
    
    Returns:
        图片列表，每项包含 imageUrl、title 等
    """
    payload = {"q": query, "num": num}
    
    try:
        resp = requests.post(SERPER_URL, headers=HEADERS, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("images", [])
        else:
            print(f"[Serper] 失败：{resp.status_code} {resp.text[:100]}")
            return []
    except Exception as e:
        print(f"[Serper] 异常：{e}")
        return []


def download_image(url):
    """
    下载图片
    
    Args:
        url: 图片 URL
    
    Returns:
        图片 bytes，失败返回 None
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        if resp.status_code == 200 and len(resp.content) > 10000:
            return resp.content
        return None
    except Exception as e:
        return None


def search_and_download(query, max_images=3):
    """
    搜索并下载参考图
    
    Args:
        query: 搜索词
        max_images: 最多下载几张
    
    Returns:
        图片列表，每项包含：
        {
            "url": str,
            "title": str,
            "content": bytes,
            "base64": str (data:image/jpeg;base64,xxx)
        }
    """
    print(f"[Serper] 搜索：{query}")
    
    images = search_images(query, num=max_images * 2)
    if not images:
        print("[Serper] 无结果")
        return []
    
    results = []
    for img in images[:max_images * 2]:
        if len(results) >= max_images:
            break
        
        url = img.get("imageUrl") or img.get("link", "")
        if not url:
            continue
        
        print(f"  下载：{url[:70]}")
        content = download_image(url)
        if content:
            b64 = base64.b64encode(content).decode('utf-8')
            results.append({
                "url": url,
                "title": img.get("title", ""),
                "content": content,
                "base64": f"data:image/jpeg;base64,{b64}"
            })
            print(f"    {len(content)/1024:.1f}KB [OK]")
        else:
            print(f"    失败 [FAIL]")
    
    print(f"[Serper] 完成：{len(results)}/{max_images} 个")
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法：python serper_tool.py \"搜索词\"")
        sys.exit(1)
    
    query = sys.argv[1]
    results = search_and_download(query)
    for r in results:
        print(f"\n{r['url'][:80]}")
        print(f"Base64: {len(r['base64'])} 字符")
