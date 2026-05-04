"""
写 Evolution 文件脚本 - write_evolution.py
读取 health_scan.py 的输出，写入 observations.md 和 treatments.md
"""

import os
import json
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 配置
SKILL_DIR = Path(__file__).parent.parent
EVOLUTION_DIR = SKILL_DIR.parent.parent / "evolution"
OBSERVATIONS_FILE = EVOLUTION_DIR / "observations.md"
TREATMENTS_FILE = EVOLUTION_DIR / "treatments.md"

def load_existing_content(filepath):
    """读取现有内容"""
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return ""

def write_observations(date_str, scan_result):
    """写 observations.md"""
    lines = []
    lines.append(f"\n## {date_str} 体检")
    lines.append(f"- 扫描session: {scan_result.get('session_scanned', 0)}个")
    
    known = scan_result.get("known_hits", [])
    unknown = scan_result.get("unknown_hits", [])
    
    if known:
        lines.append(f"- 已知坑命中: {len(known)}类 | 新异常: {len(unknown)}条")
        for item in known:
            lines.append(f"  - {item['pid']}: {item['session_count']}个session ({item['name']})")
    else:
        lines.append(f"- 已知坑命中: 0 | 新异常: {len(unknown)}条")
    
    lines.append("- 治疗结果: (待填写)")
    
    content = load_existing_content(OBSERVATIONS_FILE)
    # 追加
    content += "\n".join(lines) + "\n"
    OBSERVATIONS_FILE.write_text(content, encoding="utf-8")
    return "\n".join(lines)

def write_treatments(date_str, scan_result):
    """写 treatments.md"""
    lines = []
    lines.append(f"\n## {date_str}")
    
    known = scan_result.get("known_hits", [])
    unknown = scan_result.get("unknown_hits", [])
    
    pids = [item['pid'] for item in known]
    new_anomalies = [item['name'] for item in unknown]
    
    lines.append(f"- 体检版本: agent-retrospective v4.0.0")
    lines.append(f"- 已知坑处理: {', '.join(pids) if pids else '无'}")
    lines.append(f"- 新异常: {', '.join([f'[新] {n}' for n in new_anomalies]) if new_anomalies else '无'}")
    lines.append("- 结果: (待填写)")
    
    content = load_existing_content(TREATMENTS_FILE)
    content += "\n".join(lines) + "\n"
    TREATMENTS_FILE.write_text(content, encoding="utf-8")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="写 Evolution 文件")
    parser.add_argument("--date", type=str, required=True, help="目标日期 YYYY-MM-DD")
    parser.add_argument("--input", type=str, help="health_scan.py 的 JSON 输出文件路径")
    
    args = parser.parse_args()
    
    # 读取输入 JSON
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            scan_result = json.load(f)
    else:
        # 从 stdin 读取
        scan_result = json.load(open(os.sys.stdin.buffer, encoding="utf-8"))
    
    obs = write_observations(args.date, scan_result)
    treat = write_treatments(args.date, scan_result)
    
    print("✅ observations.md 已更新")
    print("✅ treatments.md 已更新")
    print(f"\n观测记录:\n{obs}")
    print(f"\n治疗记录:\n{treat}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()