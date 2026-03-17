#!/usr/bin/env python3
"""
skill.sh 网站爬虫 - 优化版
功能：精准抓取 skills.sh 的 Trending 和 All Time 榜单
作者: 锥锥虾
日期: 2026-03-16
优化: 针对实际页面结构调整选择器
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
from urllib.parse import urljoin

# 配置
BASE_URL = "https://skills.sh"
TRENDING_URL = "https://skills.sh/trending"
OUTPUT_DIR = os.path.expanduser("~/.openclaw/workspace/skill-logs/skill-radar/daily-scan")

# 请求头（模拟浏览器）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def ensure_output_dir():
    """确保输出目录存在"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR


def fetch_page(url: str) -> str:
    """获取网页 HTML 内容"""
    try:
        print(f"[INFO] 正在抓取: {url}")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        print(f"[OK] 抓取成功: {response.status_code}")
        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] 抓取失败: {e}")
        return None


def parse_skill_row(row: BeautifulSoup) -> dict:
    """
    解析单行 skill 数据
    
    页面结构:
    <a href="/owner/repo/skill-name">
        <div>排名</div>
        <div>
            <h3>skill名称</h3>
            <p>owner/repo</p>
        </div>
        <div>安装量</div>
    </a>
    """
    skill = {}
    
    # 获取 URL
    skill["url"] = urljoin(BASE_URL, row.get("href", ""))
    
    # 获取所有子 div
    divs = row.find_all("div", recursive=False)
    if len(divs) < 3:
        return None
    
    # 排名 (第一个 div)
    rank_text = divs[0].get_text(strip=True)
    skill["rank"] = int(rank_text) if rank_text.isdigit() else 0
    
    # 名称和来源 (第二个 div 包含 h3 和 p)
    info_div = divs[1]
    name_elem = info_div.find("h3")
    skill["name"] = name_elem.get_text(strip=True) if name_elem else "未知"
    
    source_elem = info_div.find("p")
    skill["source"] = source_elem.get_text(strip=True) if source_elem else ""
    
    # 安装量 (第三个 div)
    installs_text = divs[2].get_text(strip=True)
    skill["installs"] = installs_text
    
    # 计算数值（用于排序）
    skill["installs_num"] = parse_installs(installs_text)
    
    return skill


def parse_installs(text: str) -> int:
    """解析安装量字符串为数值"""
    if not text:
        return 0
    
    # 移除逗号
    text = text.replace(",", "")
    
    # 处理 K/M 后缀
    match = re.match(r"([\d.]+)\s*([KM]?)", text.upper())
    if match:
        num, suffix = match.groups()
        num = float(num)
        if suffix == "K":
            num *= 1000
        elif suffix == "M":
            num *= 1000000
        return int(num)
    
    return 0


def parse_skills_page(html: str) -> list:
    """解析 skills 列表页面"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    skills = []
    
    # 查找主内容区域
    main = soup.find("main") or soup
    
    # 查找所有 skill 链接 (href 包含 / 且包含文字结构)
    # skills.sh 的结构是 <a> 包含排名、名称、安装量
    links = main.find_all("a", href=re.compile(r"^/[^/]+/[^/]+/"))
    
    print(f"[INFO] 找到 {len(links)} 个潜在 skill 链接")
    
    for link in links:
        # 过滤掉 "+X more from owner/repo" 这种展开按钮
        text = link.get_text(strip=True)
        if "more from" in text.lower():
            continue
        
        # 过滤掉非 skill 链接（通过检查是否有排名数字）
        divs = link.find_all("div", recursive=False)
        if len(divs) < 3:
            continue
        
        rank_text = divs[0].get_text(strip=True) if divs else ""
        if not rank_text.isdigit():
            continue
        
        # 解析 skill
        skill = parse_skill_row(link)
        if skill and skill["name"] and skill["name"] != "未知":
            skills.append(skill)
    
    # 按排名排序
    skills.sort(key=lambda x: x.get("rank", 999))
    
    return skills


def remove_duplicates(skills: list) -> list:
    """去重：同名 skill 只保留排名最高的"""
    seen = {}
    for skill in skills:
        name = skill.get("name", "").lower()
        if name not in seen or skill.get("rank", 999) < seen[name].get("rank", 999):
            seen[name] = skill
    
    # 转回列表并按排名排序
    result = list(seen.values())
    result.sort(key=lambda x: x.get("rank", 999))
    return result


def save_results(data: dict, filename: str = None):
    """保存抓取结果到 JSON 文件"""
    ensure_output_dir()
    
    if filename is None:
        filename = f"{datetime.now().strftime('%Y-%m-%d')}.json"
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 结果已保存: {filepath}")
    return filepath


def fetch_skills_sh_trending() -> dict:
    """抓取 skills.sh Trending 榜单"""
    html = fetch_page(TRENDING_URL)
    skills = parse_skills_page(html)
    skills = remove_duplicates(skills)
    
    return {
        "source": "skills.sh",
        "category": "trending",
        "url": TRENDING_URL,
        "scraped_at": datetime.now().isoformat(),
        "count": len(skills),
        "skills": skills
    }


def fetch_skills_sh_alltime() -> dict:
    """抓取 skills.sh All Time 榜单"""
    html = fetch_page(BASE_URL)
    skills = parse_skills_page(html)
    skills = remove_duplicates(skills)
    
    return {
        "source": "skills.sh",
        "category": "all_time",
        "url": BASE_URL,
        "scraped_at": datetime.now().isoformat(),
        "count": len(skills),
        "skills": skills
    }


def validate_results(trending: dict, alltime: dict) -> bool:
    """验证抓取结果质量"""
    print("\n" + "=" * 50)
    print("数据质量验证")
    print("=" * 50)
    
    # 检查数量
    trending_count = trending.get("count", 0)
    alltime_count = alltime.get("count", 0)
    
    print(f"Trending: {trending_count} 个 skills")
    print(f"All Time: {alltime_count} 个 skills")
    
    # 检查是否有空数据
    if trending_count == 0 and alltime_count == 0:
        print("[ERROR] 未抓取到任何数据")
        return False
    
    # 检查样本数据
    if trending.get("skills"):
        sample = trending["skills"][0]
        print(f"\n样本数据 (Trending #1):")
        print(f"  名称: {sample.get('name')}")
        print(f"  排名: {sample.get('rank')}")
        print(f"  来源: {sample.get('source')}")
        print(f"  安装量: {sample.get('installs')}")
        print(f"  URL: {sample.get('url')}")
    
    # 质量判断
    if trending_count < 10 and alltime_count < 10:
        print("[WARN] 抓取数量偏少，可能页面结构有变化")
        return False
    
    print("[OK] 数据质量通过")
    return True


def main():
    """主函数：抓取所有数据源"""
    print("=" * 50)
    print("Skill.sh 爬虫启动 (优化版)")
    print("=" * 50)
    
    results = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sources": []
    }
    
    # 抓取 Trending
    print("\n[1/2] 抓取 Trending 榜单...")
    trending_data = fetch_skills_sh_trending()
    results["sources"].append(trending_data)
    print(f"[OK] Trending: {trending_data['count']} 个 skills (去重后)")
    
    # 抓取 All Time
    print("\n[2/2] 抓取 All Time 榜单...")
    alltime_data = fetch_skills_sh_alltime()
    results["sources"].append(alltime_data)
    print(f"[OK] All Time: {alltime_data['count']} 个 skills (去重后)")
    
    # 验证数据质量
    is_valid = validate_results(trending_data, alltime_data)
    
    # 保存结果
    print("\n" + "=" * 50)
    output_file = save_results(results)
    
    # 输出统计
    total = trending_data['count'] + alltime_data['count']
    print(f"\n[完成] 共抓取 {total} 个 skills")
    print(f"[输出] {output_file}")
    
    if not is_valid:
        print("\n[WARN] 数据质量未达标，请检查页面结构是否变化")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
