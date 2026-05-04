# -*- coding: utf-8 -*-
"""
龙虾体检 - Step 1：全身扫描
扫描 sessions + chat-logs，输出可疑文件列表 + 原始片段
不做任何判断，只负责"找可疑"
"""
import os
import re
import json
import glob
from datetime import datetime, timezone, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
EVOLUTION_DIR = SKILL_DIR.parent.parent / "evolution"
SESSIONS_DIR = SKILL_DIR.parent.parent / "agents" / "main" / "sessions"
CHATLOGS_DIR = SKILL_DIR.parent.parent / "chat-logs" / "main"

# 可疑信号（开放宽泛，不绑定坑编号）
SUSPICIOUS_SIGNALS = [
    # 工具失败类
    "error", "failed", "fail", "timeout", "exception",
    "Command failed", "Command exited with code 1",
    "LLM idle timeout", "no response from model",
    # 执行异常类
    "unexpected token", "terminatorexpected", "pathnotfound",
    "namedparameter", "access denied", "encoding error",
    # 网络类
    "fetch failed", "connection refused", "connection timeout",
    # 进程/服务类
    "abnormal closure", "gateway closed", "1006",
    # 中文报错
    "失败", "错误", "超时", "异常", "连接失败",
]


def get_session_files(target_date_str, days=1):
    """获取目标日期范围内的 session 文件"""
    target = datetime.strptime(target_date_str, "%Y-%m-%d")
    start_ts = (target - timedelta(days=days)).timestamp()
    end_ts = (target + timedelta(days=1)).timestamp()
    
    files = []
    if not SESSIONS_DIR.exists():
        return files
    
    for fname in os.listdir(SESSIONS_DIR):
        if not fname.endswith('.jsonl'):
            continue
        if '.reset.' in fname or '.deleted.' in fname or '.lock' in fname:
            continue
        fpath = SESSIONS_DIR / fname
        mtime = os.path.getmtime(fpath)
        if mtime >= start_ts and mtime < end_ts:
            files.append({
                "path": str(fpath),
                "name": fname,
                "mtime": datetime.fromtimestamp(mtime, tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
            })
    return files


def get_chatlog_files(target_date_str, days=1):
    """获取目标日期范围内的 chatlog 文件"""
    target = datetime.strptime(target_date_str, "%Y-%m-%d")
    start_ts = (target - timedelta(days=days)).timestamp()
    end_ts = (target + timedelta(days=1)).timestamp()
    
    files = []
    if not CHATLOGS_DIR.exists():
        return files
    
    for fname in os.listdir(CHATLOGS_DIR):
        if not fname.startswith(target_date_str.replace('-', '-')):
            continue
        if not fname.endswith('.jsonl'):
            continue
        fpath = CHATLOGS_DIR / fname
        mtime = os.path.getmtime(fpath)
        if mtime >= start_ts and mtime < end_ts:
            files.append({
                "path": str(fpath),
                "name": fname,
                "mtime": datetime.fromtimestamp(mtime, tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
            })
    return files


def extract_snippets(file_info, max_snippets=3):
    """从文件提取可疑片段（只提取，不判断）"""
    snippets = []
    try:
        content = open(file_info["path"], encoding="utf-8", errors="ignore").read()
    except Exception:
        return snippets
    
    lines = content.split('\n')
    found_lines = set()
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for signal in SUSPICIOUS_SIGNALS:
            if signal.lower() in line_lower:
                if i not in found_lines:
                    # 取上下文前后各2行
                    context = []
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    for j in range(start, end):
                        try:
                            context.append(lines[j].strip()[:300])
                        except:
                            pass
                    snippets.append({
                        "line": i + 1,
                        "signal": signal,
                        "context": context
                    })
                    found_lines.add(i)
                    break
        if len(snippets) >= max_snippets:
            break
    
    return snippets


def main():
    import argparse
    parser = argparse.ArgumentParser(description="龙虾体检 - Step 1：全身扫描")
    parser.add_argument("--days", type=int, default=1, help="扫描最近N天")
    parser.add_argument("--date", type=str, default=None, help="目标日期 YYYY-MM-DD，默认昨天")
    parser.add_argument("--output", type=str, default=None, help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
    else:
        yesterday = datetime.now(timezone(timedelta(hours=8))) - timedelta(days=1)
        target_date = yesterday.strftime("%Y-%m-%d")
    
    # Step 1：全身扫描
    session_files = get_session_files(target_date, args.days)
    chatlog_files = get_chatlog_files(target_date, args.days)
    
    # 对每个文件提取可疑片段
    suspicious_files = []
    
    for f in session_files:
        snippets = extract_snippets(f)
        suspicious_files.append({
            "source": "session",
            "path": f["path"],
            "name": f["name"],
            "mtime": f["mtime"],
            "has_snippets": len(snippets) > 0,
            "snippet_count": len(snippets),
            "snippets": snippets
        })
    
    chatlog_snapshots = []
    for f in chatlog_files:
        snippets = extract_snippets(f)
        chatlog_snapshots.append({
            "source": "chatlog",
            "path": f["path"],
            "name": f["name"],
            "mtime": f["mtime"],
            "has_snippets": len(snippets) > 0,
            "snippet_count": len(snippets),
            "snippets": snippets
        })
    
    # 有可疑片段的文件排在前面
    suspicious_files.sort(key=lambda x: (0 if x["has_snippets"] else 1, -x["snippet_count"]))
    chatlog_snapshots.sort(key=lambda x: (0 if x["has_snippets"] else 1, -x["snippet_count"]))
    
    result = {
        "target_date": target_date,
        "scanned_days": args.days,
        "scan_summary": {
            "session_files_found": len(session_files),
            "chatlog_files_found": len(chatlog_files),
            "session_with_snippets": sum(1 for f in suspicious_files if f["has_snippets"]),
            "chatlog_with_snippets": sum(1 for f in chatlog_snapshots if f["has_snippets"]),
        },
        "session_files": session_files,
        "chatlog_files": chatlog_snapshots,
        "suspicious_files": suspicious_files,  # 有片段的文件（未判断）
    }
    
    output = args.output or str(SKILL_DIR / "scripts" / "scan_result.json")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"扫描日期: {target_date}")
    print(f"扫描范围: 最近{args.days}天")
    print(f"Session文件: {len(session_files)}个")
    print(f"  - 含可疑片段: {sum(1 for f in suspicious_files if f['has_snippets'])}个")
    print(f"Chatlog文件: {len(chatlog_files)}个")
    print(f"  - 含可疑片段: {sum(1 for f in chatlog_snapshots if f['has_snippets'])}个")
    print(f"输出文件: {output}")
    print(f"✅ Step 1 完成，等待 Step 2 精准诊断")


if __name__ == "__main__":
    main()
