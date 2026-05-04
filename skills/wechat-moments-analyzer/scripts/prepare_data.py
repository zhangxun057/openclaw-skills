#!/usr/bin/env python3
"""
朋友圈分析数据准备工具
功能：读取 raw/ 目录最新 JSON，比对 checkpoint，输出新帖子列表
用法：python prepare_data.py
"""
import os
import sys
import json
import glob
import subprocess
from datetime import datetime, timedelta


def main():
    # 所有路径基于项目根目录，通过 ~ 解析
    base = os.path.expanduser("~/.openclaw/projects/moments-analysis")
    raw_dir = os.path.join(base, "raw")
    state_dir = os.path.join(base, "state")
    cp_path = os.path.join(base, "checkpoint.json")

    # 1. 找最新 JSON
    if not os.path.isdir(raw_dir):
        print("NO_RAW_DIR")
        return

    json_files = glob.glob(os.path.join(raw_dir, "**", "*.json"), recursive=True)
    if not json_files:
        print("NO_DATA")
        return

    # 过滤掉测试/衍生文件
    skip_keywords = ["test", "result", "checkpoint", "analyzed", "status"]
    raw_files = [f for f in json_files if not any(k in os.path.basename(f).lower() for k in skip_keywords)]
    if not raw_files:
        print("NO_DATA")
        return

    latest = max(raw_files, key=os.path.getmtime)

    # 2. 读 checkpoint
    analyzed = set()
    if os.path.exists(cp_path):
        try:
            with open(cp_path, "r", encoding="utf-8") as f:
                cp = json.load(f)
            analyzed = set(cp.get("analyzed_ids", []))
        except Exception:
            pass

    # 3. 读最新 JSON
    try:
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("READ_ERROR: " + str(e))
        return

    if isinstance(data, list):
        timeline = data
    else:
        timeline = data.get("timeline", [])

    # 4. 过滤新帖子
    new_posts = []
    for post in timeline:
        pid = post.get("id") or post.get("tid")
        if pid and pid not in analyzed:
            new_posts.append(post)

    # 5. 输出到 state/new_posts.json
    os.makedirs(state_dir, exist_ok=True)
    out_path = os.path.join(state_dir, "new_posts.json")
    output = {
        "data_source": latest,
        "total_in_file": len(timeline),
        "checkpoint_count": len(analyzed),
        "new_count": len(new_posts),
        "posts": new_posts
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 6. 构建媒体索引
    match_media_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "match_media.py")
    if os.path.exists(match_media_script):
        subprocess.run([
            sys.executable, match_media_script,
            "--build", "--base-dir", base
        ], capture_output=True, text=True)

    print("OK: %d new posts from %d total (checkpoint: %d)" % (
        len(new_posts), len(timeline), len(analyzed)))


if __name__ == "__main__":
    main()
