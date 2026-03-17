#!/usr/bin/env python3
"""
skill-radar 主控脚本
整合多个数据源：skills.sh (Browser) / GitHub (CLI) / ClawHub (Browser) / Coze (Browser)
作者: 锥锥虾
日期: 2026-03-16
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import List, Dict

# 修复 Windows 终端编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

OUTPUT_DIR = os.path.expanduser("~/.openclaw/workspace/skill-logs/skill-radar/daily-scan")

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def fetch_github_skills() -> Dict:
    """使用 GitHub CLI 抓取热门仓库"""
    log("开始抓取 GitHub...")
    try:
        result = subprocess.run(
            ["gh", "search", "repos", "openclaw skill", "--sort", "stars", "--limit", "30", "--json", "name,description,stargazersCount,url,owner"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        if result.returncode != 0:
            log(f"GitHub CLI 错误: {result.stderr}")
            return {"source": "github", "category": "stars", "count": 0, "skills": [], "error": result.stderr}
        
        repos = json.loads(result.stdout)
        
        skills = []
        for repo in repos:
            skills.append({
                "name": repo.get("name", ""),
                "description": repo.get("description", ""),
                "stars": repo.get("stargazersCount", 0),
                "url": repo.get("url", ""),
                "owner": repo.get("owner", {}).get("login", ""),
                "source": "github"
            })
        
        log(f"GitHub 抓取完成: {len(skills)} 个")
        return {
            "source": "github",
            "category": "stars",
            "count": len(skills),
            "skills": skills
        }
    except Exception as e:
        log(f"GitHub 抓取失败: {e}")
        return {"source": "github", "category": "stars", "count": 0, "skills": [], "error": str(e)}

def load_skills_sh_browser_result() -> Dict:
    """加载 Browser 抓取的 skills.sh 结果（由外部 Browser 脚本生成）"""
    browser_output = os.path.join(OUTPUT_DIR, "skills_sh_browser.json")
    if os.path.exists(browser_output):
        with open(browser_output, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"source": "skills.sh", "category": "trending+alltime", "count": 0, "skills": []}

def load_clawhub_browser_result() -> Dict:
    """加载 Browser 抓取的 ClawHub 结果"""
    browser_output = os.path.join(OUTPUT_DIR, "clawhub_browser.json")
    if os.path.exists(browser_output):
        with open(browser_output, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"source": "clawhub", "category": "popular", "count": 0, "skills": []}

def merge_and_deduplicate(sources: List[Dict]) -> List[Dict]:
    """合并多个数据源并去重"""
    seen = {}
    all_skills = []
    
    for source in sources:
        for skill in source.get("skills", []):
            name = skill.get("name", "").lower().replace("-", "").replace("_", "")
            if not name:
                continue
            
            # 去重：同名 skill 保留 star 最高的
            if name not in seen:
                seen[name] = skill
                all_skills.append(skill)
            else:
                # 比较热度，保留更高的
                existing = seen[name]
                existing_stars = existing.get("stars", 0) or existing.get("installs_num", 0)
                new_stars = skill.get("stars", 0) or skill.get("installs_num", 0)
                if new_stars > existing_stars:
                    all_skills.remove(existing)
                    seen[name] = skill
                    all_skills.append(skill)
    
    # 按热度排序
    all_skills.sort(key=lambda x: x.get("stars", 0) or x.get("installs_num", 0), reverse=True)
    return all_skills

def generate_report(sources: List[Dict], merged: List[Dict]) -> str:
    """生成日报"""
    report = []
    report.append("=" * 50)
    report.append("【龙虾 Skill Radar 日报】")
    report.append(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    # 各源统计
    report.append("【数据源统计】")
    for source in sources:
        report.append(f"  {source['source']}: {source['count']} 个")
    report.append(f"  去重后: {len(merged)} 个")
    report.append("")
    
    # Top 10 推荐
    report.append("【Top 10 热门 Skill】")
    for i, skill in enumerate(merged[:10], 1):
        name = skill.get("name", "未知")
        stars = skill.get("stars", 0) or skill.get("installs_num", 0)
        source = skill.get("source", "")
        desc = skill.get("description", "")[:50]
        report.append(f"{i}. {name} ({stars}⭐/{source})")
        if desc:
            report.append(f"   {desc}...")
    
    report.append("")
    report.append("=" * 50)
    
    return "\n".join(report)

def save_results(data: Dict, filename: str = None):
    """保存结果"""
    ensure_output_dir()
    if filename is None:
        filename = f"{datetime.now().strftime('%Y-%m-%d')}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath

def main():
    log("Skill Radar 启动")
    
    # 收集各数据源结果
    sources = []
    
    # 1. GitHub (CLI)
    github_data = fetch_github_skills()
    sources.append(github_data)
    
    # 2. skills.sh (Browser 预抓取结果)
    skills_sh_data = load_skills_sh_browser_result()
    if skills_sh_data["count"] > 0:
        sources.append(skills_sh_data)
        log(f"skills.sh (Browser): {skills_sh_data['count']} 个")
    else:
        log("skills.sh (Browser): 暂无数据，请先运行 browser 抓取")
    
    # 3. ClawHub (Browser 预抓取结果)
    clawhub_data = load_clawhub_browser_result()
    if clawhub_data["count"] > 0:
        sources.append(clawhub_data)
        log(f"ClawHub (Browser): {clawhub_data['count']} 个")
    else:
        log("ClawHub (Browser): 暂无数据，请先运行 browser 抓取")
    
    # 合并去重
    log("合并去重...")
    merged = merge_and_deduplicate(sources)
    
    # 生成报告
    report = generate_report(sources, merged)
    print("\n" + report)
    
    # 保存结果
    result = {
        "date": datetime.now().isoformat(),
        "sources": sources,
        "merged_count": len(merged),
        "top_skills": merged[:30]
    }
    
    output_file = save_results(result)
    log(f"结果已保存: {output_file}")
    
    # 保存文本报告
    report_file = os.path.join(OUTPUT_DIR, f"{datetime.now().strftime('%Y-%m-%d')}_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    log(f"报告已保存: {report_file}")

if __name__ == "__main__":
    main()
