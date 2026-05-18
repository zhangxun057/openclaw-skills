#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定制个人早报生成器
根据用户选择的领域和关键词，生成个性化每日简报
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import json
import sys
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re

# Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 早报类型配置
BRIEFING_TYPES = {
    "general": {
        "name": "综合早报",
        "sources": ["hackernews", "36kr", "weibo", "github"],
        "keywords": []
    },
    "tech": {
        "name": "科技早报",
        "sources": ["hackernews", "github", "36kr", "producthunt"],
        "keywords": ["科技", "互联网", "AI", "产品"]
    },
    "finance": {
        "name": "财经早报",
        "sources": ["wallstreetcn", "weibo"],
        "keywords": ["财经", "股市", "经济", "投资"]
    },
    "ai": {
        "name": "AI早报",
        "sources": ["hackernews", "github", "huggingface"],
        "keywords": ["AI", "LLM", "GPT", "Claude", "Agent", "大模型", "深度学习"]
    },
    "headline": {
        "name": "今日要闻",
        "sources": ["hackernews", "36kr", "weibo"],
        "keywords": []
    }
}

def fetch_hackernews(limit=10, keyword=None):
    """获取Hacker News热点"""
    items = []
    try:
        timestamp_24h = int(time.time() - 24 * 3600)
        query = keyword if keyword else "tech"
        api_url = f"http://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=created_at_i>{timestamp_24h}&hitsPerPage={limit*2}&query={requests.utils.quote(query)}"
        
        data = requests.get(api_url, timeout=10).json()
        hits = data.get('hits', [])
        
        for hit in hits[:limit]:
            items.append({
                "source": "Hacker News",
                "title": hit.get('title'),
                "url": hit.get('url') or f"https://news.ycombinator.com/item?id={hit['objectID']}",
                "points": hit.get('points', 0)
            })
    except Exception as e:
        print(f"HN fetch error: {e}", file=sys.stderr)
    
    return items

def fetch_36kr(limit=10, keyword=None):
    """获取36氪科技资讯"""
    items = []
    try:
        url = "https://www.36kr.com/information/web/news_flash_hot"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.select('.article-item a, .news-item a')[:limit]
        for article in articles:
            title = article.get_text(strip=True)
            if title and len(title) > 5:
                items.append({
                    "source": "36氪",
                    "title": title,
                    "url": "https://www.36kr.com" + article.get('href', ''),
                    "points": 0
                })
    except Exception as e:
        print(f"36kr fetch error: {e}", file=sys.stderr)
    
    return items

def fetch_weibo(limit=10, keyword=None):
    """获取微博热搜"""
    items = []
    try:
        url = "https://weibo.com/ajax/side/hotSearch"
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        realtime = data.get('data', {}).get('realtime', [])
        
        for item in realtime[:limit]:
            title = item.get('note', '') or item.get('word', '')
            if title:
                items.append({
                    "source": "微博热搜",
                    "title": title,
                    "url": f"https://s.weibo.com/weibo?q={requests.utils.quote(title)}",
                    "points": item.get('num', 0)
                })
    except Exception as e:
        print(f"Weibo fetch error: {e}", file=sys.stderr)
    
    return items

def fetch_github(limit=10, keyword=None):
    """获取GitHubTrending"""
    items = []
    try:
        url = "https://github.com/trending?since=daily"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.select('.Box-row article')[:limit]
        for article in articles:
            title_elem = article.select_one('h2 a')
            if title_elem:
                title = title_elem.get_text(strip=True)
                stars_elem = article.select_one('.octicon-star')
                stars = stars_elem.parent.get_text(strip=True) if stars_elem else "0"
                items.append({
                    "source": "GitHub Trending",
                    "title": title,
                    "url": "https://github.com" + title_elem.get('href', ''),
                    "points": stars
                })
    except Exception as e:
        print(f"GitHub fetch error: {e}", file=sys.stderr)
    
    return items

def fetch_wallstreetcn(limit=10, keyword=None):
    """获取华尔街见闻"""
    items = []
    try:
        url = "https://wallstreetcn.com/articles/live"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.select('.article-item, .news-item')[:limit]
        for article in articles:
            title_elem = article.select_one('a')
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 5:
                    items.append({
                        "source": "华尔街见闻",
                        "title": title,
                        "url": title_elem.get('href', ''),
                        "points": 0
                    })
    except Exception as e:
        print(f"WallStreetCN fetch error: {e}", file=sys.stderr)
    
    return items

def fetch_source(source_name, limit=10, keyword=None):
    """根据源名获取数据"""
    fetchers = {
        "hackernews": fetch_hackernews,
        "36kr": fetch_36kr,
        "weibo": fetch_weibo,
        "github": fetch_github,
        "wallstreetcn": fetch_wallstreetcn
    }
    
    fetcher = fetchers.get(source_name)
    if fetcher:
        return fetcher(limit, keyword)
    return []

def generate_briefing(briefing_type="general", keyword=None, deep=False, limit=10, custom_title=None):
    """生成早报"""
    
    # 获取配置
    config = BRIEFING_TYPES.get(briefing_type, BRIEFING_TYPES["general"])
    name = config["name"]
    sources = config["sources"]
    keywords = keyword.split(",") if keyword else config["keywords"]
    
    # 收集新闻
    all_news = []
    for source in sources:
        news = fetch_source(source, limit, ",".join(keywords) if keywords else None)
        all_news.extend(news)
    
    # 去重
    seen = set()
    unique_news = []
    for item in all_news:
        if item["title"] not in seen:
            seen.add(item["title"])
            unique_news.append(item)
    
    unique_news = unique_news[:limit * 2]
    
    # 生成标题
    title = custom_title or f"📰 {name} | {datetime.now().strftime('%Y年%m月%d日')}"
    
    # 生成内容
    content = [f"# {title}\n"]
    content.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    content.append(f"**数据来源**: {', '.join(sources)}")
    content.append("")
    content.append("---")
    content.append("")
    
    if deep:
        content.append("## 🔥 深度热点\n")
    else:
        content.append("## 📊 热门新闻\n")
    
    for i, item in enumerate(unique_news, 1):
        content.append(f"### {i}. {item['title']}")
        content.append(f"- **来源**: {item['source']}")
        if item.get('points'):
            content.append(f"- **热度**: {item['points']}")
        content.append(f"- **链接**: [查看]({item['url']})")
        content.append("")
    
    content.append("---")
    content.append(f"*本早报由AI生成，共收集{len(unique_news)}条资讯*")
    
    return "\n".join(content)

def main():
    parser = argparse.ArgumentParser(description="定制个人早报生成器")
    parser.add_argument("--type", default="general", choices=["general", "tech", "finance", "ai", "headline", "custom"],
                        help="早报类型")
    parser.add_argument("--keyword", help="关键词筛选，逗号分隔")
    parser.add_argument("--deep", action="store_true", help="深度阅读模式")
    parser.add_argument("--limit", type=int, default=10, help="每源条目数")
    parser.add_argument("--title", help="自定义标题")
    parser.add_argument("--save", action="store_true", default=True, help="保存到文件")
    
    args = parser.parse_args()
    
    # 生成早报
    briefing = generate_briefing(
        briefing_type=args.type,
        keyword=args.keyword,
        deep=args.deep,
        limit=args.limit,
        custom_title=args.title
    )
    
    # 输出
    print(briefing)
    
    # 保存
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"reports/{date_str}_{args.type}_briefing.md"
        os.makedirs("reports", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(briefing)
        print(f"\n✅ 已保存到: {filename}")

if __name__ == "__main__":
    main()
