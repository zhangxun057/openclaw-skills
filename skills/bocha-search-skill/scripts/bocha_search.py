# -*- coding: utf-8 -*-
"""
博查 AI 搜索脚本
通过博查 API 进行网络搜索，返回 URLs + 摘要
"""

import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
import argparse

# ==================== 配置 ====================
BOCHA_API_KEY = "sk-130edef213334cdb8f9ae08a09a5b106"
BOCHA_SEARCH_URL = "https://api.bochaai.com/v1/web-search"


def search(query, count=5, summary=True, freshness="pw"):
    """
    调用博查 API 搜索
    
    Args:
        query: 搜索关键词
        count: 返回结果数量 (默认 5)
        summary: 是否返回摘要 (默认 True)
        freshness: 时间范围: pd=今天, pw=本周, pm=本月, py=今年, 无=不限
    
    Returns:
        list[dict]: 搜索结果列表，每项包含 title, url, snippet, summary
    """
    headers = {
        "Authorization": f"Bearer {BOCHA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "count": count,
        "summary": summary
    }
    if freshness:
        payload["freshness"] = freshness
    
    try:
        r = requests.post(BOCHA_SEARCH_URL, headers=headers, json=payload, timeout=15)
        data = r.json()
        
        if data.get("code") != 200:
            print(f"[Bocha] Error: {data.get('msg', 'Unknown error')}")
            return []
        
        web_pages = data.get("data", {}).get("webPages", {}).get("value", [])
        results = []
        for page in web_pages:
            results.append({
                "title": page.get("name", ""),
                "url": page.get("url", ""),
                "snippet": page.get("snippet", ""),
                "summary": page.get("summary", ""),
                "siteName": page.get("siteName", ""),
                "datePublished": page.get("datePublished", ""),
                "dateLastCrawled": page.get("dateLastCrawled", "")
            })
        
        return results
        
    except Exception as e:
        print(f"[Bocha] Request failed: {e}")
        return []


def visit_page(url, timeout=10):
    """
    访问网页并提取内容
    
    Args:
        url: 网页 URL
        timeout: 超时时间
    
    Returns:
        str: 网页内容（markdown 格式）或 None
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, headers=headers, timeout=timeout)
        
        # 简单提取：返回原始 HTML 的前 3000 字符
        # 实际项目中可以用 readability / trafilatura 做更好的提取
        text = r.text
        return text[:3000]
        
    except Exception as e:
        print(f"[Bocha] Visit failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="博查 AI 搜索")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("-n", "--count", type=int, default=5, help="返回结果数量")
    parser.add_argument("--no-visit", action="store_true", help="只搜索不访问内容")
    parser.add_argument("--visit-first", action="store_true", help="搜索并自动访问第一个结果")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--freshness", default="", help="时间范围: pd/pw/pm/py")
    
    args = parser.parse_args()
    
    # 搜索
    results = search(args.query, count=args.count, freshness=args.freshness)
    
    if not results:
        print("[Bocha] No results found")
        return
    
    # 如果需要访问第一个结果
    if args.visit_first and results:
        content = visit_page(results[0]["url"])
        if content:
            results[0]["full_content"] = content
    
    # 输出
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n[博查搜索] \"{args.query}\" - 找到 {len(results)} 条结果\n")
        print("=" * 60)
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['title']}")
            print(f"   URL: {r['url']}")
            if r.get('summary'):
                print(f"   摘要: {r['summary'][:200]}")
            elif r.get('snippet'):
                print(f"   摘要: {r['snippet'][:200]}")
            if r.get('siteName'):
                print(f"   来源: {r['siteName']}")
            if r.get('datePublished'):
                print(f"   发布: {r['datePublished']}")
            print()
        
        # 如果访问了第一个结果
        if args.visit_first and results and results[0].get('full_content'):
            print("=" * 60)
            print(f"\n[全文内容] {results[0]['title']}\n")
            print(results[0]['full_content'][:1500])


if __name__ == "__main__":
    main()
