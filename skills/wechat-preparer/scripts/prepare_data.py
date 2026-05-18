#!/usr/bin/env python3
"""
朋友圈数据准备工具 v2
功能：扫描 raw/moments-analysis/ 下所有 JSON，比对 extracted_moment/checkpoint.json 去重，
      新帖子通过 stdout 输出，Agent 直接读取。
用法：python prepare_data.py
"""
import argparse
import glob
import json
import os
import sys


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def get_post_id(post):
    pid = post.get("id") or post.get("tid")
    if pid:
        return str(pid)
    username = post.get("username") or post.get("wxid") or ""
    create_time = post.get("createTime") or ""
    if username or create_time:
        return "%s_%s" % (username, create_time)
    return ""


def main():
    parser = argparse.ArgumentParser(description="朋友圈数据准备")
    parser.add_argument(
        "--base-dir",
        default=os.path.join(os.path.expanduser("~"), ".openclaw", "projects"),
        help="数据根目录，默认为 ~/.openclaw/projects"
    )
    args = parser.parse_args()

    base = args.base_dir
    raw_dir = os.path.join(base, "raw", "moments-analysis")
    cp_path = os.path.join(base, "raw", "extracted_moment", "checkpoint.json")

    if not os.path.isdir(raw_dir):
        print("NO_RAW_DIR", file=sys.stderr)
        sys.exit(1)

    json_files = sorted(glob.glob(os.path.join(raw_dir, "**", "*.json"), recursive=True))
    if not json_files:
        print("NO_DATA", file=sys.stderr)
        sys.exit(1)

    checkpoint = load_json(cp_path, default={}) or {}
    analyzed = set(str(x) for x in checkpoint.get("analyzed_ids", []))

    all_new = []
    data_sources = []
    total_scanned = 0

    for fpath in json_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        posts = data.get("posts", []) if isinstance(data, dict) else data
        if not posts:
            continue

        total_scanned += len(posts)
        file_contrib = 0
        for post in posts:
            pid = get_post_id(post)
            if pid and pid not in analyzed:
                post["_post_id"] = pid
                all_new.append(post)
                file_contrib += 1

        if file_contrib > 0:
            data_sources.append(os.path.basename(fpath))

    output = {
        "data_sources": data_sources,
        "total_scanned": total_scanned,
        "checkpoint_count": len(analyzed),
        "new_count": len(all_new),
        "posts": all_new
    }

    sys.stdout.reconfigure(encoding='utf-8')
    json.dump(output, sys.stdout, ensure_ascii=False)
    sys.stdout.write('\n')

    sys.stderr.write("OK: %d new / %d total / %d files / checkpoint=%d\n" % (
        len(all_new), total_scanned, len(data_sources), len(analyzed)))
    sys.stderr.flush()


if __name__ == "__main__":
    main()
