#!/usr/bin/env python3
"""
朋友圈分析数据准备工具（Test 版本）
功能：读取 raw/ 目录最新 JSON，比对 checkpoint，输出新帖子列表
输出到 test/ 目录，便于对比测试
用法：python prepare_data_test.py
"""
import os
import sys
import json
import glob
from datetime import datetime, timedelta


def main():
    # 所有路径基于项目根目录，通过 ~ 解析
    base = os.path.expanduser("~/.openclaw/projects/moments-analysis")
    raw_dir = os.path.join(base, "raw")
    test_dir = os.path.join(base, "test")
    cp_path = os.path.join(base, "checkpoint.json")

    # 1. 找最新 JSON
    if not os.path.isdir(raw_dir):
        print("NO_RAW_DIR")
        return

    json_files = glob.glob(os.path.join(raw_dir, "**", "*.json"), recursive=True)
    if not json_files:
        print("NO_DATA")
        return

    latest = max(json_files, key=os.path.getmtime)

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

    timeline = data.get("timeline", [])
    if not timeline:
        timeline = data if isinstance(data, list) else []

    # 4. 过滤新帖子
    new_posts = []
    for post in timeline:
        pid = post.get("id") or post.get("tid")
        if pid and pid not in analyzed:
            # 只保留分析需要的字段，压缩体积
            new_posts.append({
                "id": post.get("id"),
                "tid": post.get("tid"),
                "username": post.get("username"),
                "nickname": post.get("nickname"),
                "createTime": post.get("createTime"),
                "contentDesc": post.get("contentDesc", ""),
                "type": post.get("type"),
                "likes": post.get("likes", []),
                "comments": post.get("comments", []),
                "location": post.get("location"),
                "avatarUrl": post.get("avatarUrl"),
                "media_count": len(post.get("media", []))
            })

    # 5. 输出到 test/new_posts.json
    os.makedirs(test_dir, exist_ok=True)
    out_path = os.path.join(test_dir, "new_posts.json")
    output = {
        "data_source": latest,
        "total_in_file": len(timeline),
        "checkpoint_count": len(analyzed),
        "new_count": len(new_posts),
        "posts": new_posts
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("OK: %d new posts from %d total (checkpoint: %d)" % (len(new_posts), len(timeline), len(analyzed)))


if __name__ == "__main__":
    main()
