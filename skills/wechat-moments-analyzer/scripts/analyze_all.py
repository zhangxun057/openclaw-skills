#!/usr/bin/env python3
"""
朋友圈全量分析调度脚本

读取 state/new_posts.json，按 50 条/批切割，输出每批帖子数据到 state/batch_N.json。
供主 Agent 循环 spawn SubAgent 使用。

用法：
  python analyze_all.py              # 切割所有批次，输出批次文件
  python analyze_all.py --verify     # 校验当前 checkpoint 进度
  python analyze_all.py --batch 3    # 只输出第3批数据
  python analyze_all.py --status     # 输出当前分析状态摘要

每批输出到 state/batch_N.json（N从1开始）
SubAgent 分析后自行写入 logs/ 和 checkpoint.json
本脚本通过校验 checkpoint 确认每批完成情况
"""

import os
import sys
import json
import io
import glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 所有路径基于项目根目录
BASE = os.path.expanduser("~/.openclaw/projects/moments-analysis")
NEW_POSTS = os.path.join(BASE, "state", "new_posts.json")
CHECKPOINT = os.path.join(BASE, "checkpoint.json")
BATCH_DIR = os.path.join(BASE, "state", "batches")
LOGS_DIR = os.path.join(BASE, "logs")

BATCH_SIZE = 50


def load_json(path):
    """安全读取 JSON 文件"""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("READ_ERROR: %s - %s" % (path, e))
        return None


def save_json(path, data):
    """安全写入 JSON 文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_analyzed_count():
    """获取当前已分析的帖子数量"""
    ckpt = load_json(CHECKPOINT)
    if ckpt:
        ids = ckpt.get("analyzed_ids", [])
        return len(ids)
    return 0


def get_analyzed_ids():
    """获取已分析的帖子 ID 集合"""
    ckpt = load_json(CHECKPOINT)
    if ckpt:
        return set(ckpt.get("analyzed_ids", []))
    return set()


def split_batches(posts, batch_size=BATCH_SIZE):
    """将帖子列表切割为批次"""
    batches = []
    for i in range(0, len(posts), batch_size):
        batch = posts[i:i + batch_size]
        batches.append(batch)
    return batches


def main():
    import argparse
    parser = argparse.ArgumentParser(description="朋友圈全量分析调度脚本")
    parser.add_argument("--batch", type=int, help="只输出指定批次（从1开始）")
    parser.add_argument("--verify", action="store_true", help="校验 checkpoint 进度")
    parser.add_argument("--status", action="store_true", help="输出当前状态摘要")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="每批条数")
    args = parser.parse_args()

    # 读取新帖子
    data = load_json(NEW_POSTS)
    if data is None:
        print("ERROR: new_posts.json 不存在，请先运行 prepare_data.py")
        sys.exit(1)

    posts = data.get("posts", [])
    if not posts:
        print("NO_DATA: 没有待分析的帖子")
        sys.exit(0)

    analyzed_ids = get_analyzed_ids()

    # 过滤未分析的帖子
    pending = []
    for p in posts:
        pid = p.get("id") or p.get("tid")
        if pid and pid not in analyzed_ids:
            pending.append(p)

    if not pending:
        print("DONE: 所有帖子已分析完毕")
        sys.exit(0)

    # 切割批次
    batches = split_batches(pending, args.batch_size)
    total_batches = len(batches)

    if args.status:
        # 输出状态摘要
        total_in_file = data.get("total_in_file", len(posts))
        checkpoint_count = data.get("checkpoint_count", 0)
        already_analyzed = len(analyzed_ids) - checkpoint_count if len(analyzed_ids) > checkpoint_count else 0

        # 统计已有日志
        log_files = glob.glob(os.path.join(LOGS_DIR, "*.jsonl"))
        total_valuable = 0
        total_signals = 0
        for lf in log_files:
            with open(lf, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        rec = json.loads(line.strip())
                        if rec:
                            total_valuable += 1
                            if rec.get("signals"):
                                total_signals += len(rec["signals"])
                    except:
                        pass

        print("STATUS: total=%d | analyzed=%d | pending=%d | batches=%d | valuable=%d | signals=%d" % (
            total_in_file,
            len(analyzed_ids),
            len(pending),
            total_batches,
            total_valuable,
            total_signals
        ))
        sys.exit(0)

    if args.verify:
        # 校验当前进度
        completed = 0
        for i, batch in enumerate(batches, 1):
            batch_ids = set()
            for p in batch:
                pid = p.get("id") or p.get("tid")
                if pid:
                    batch_ids.add(pid)
            if batch_ids.issubset(analyzed_ids):
                completed += 1

        print("VERIFY: %d/%d batches completed | %d posts remaining" % (
            completed, total_batches, len(pending) - completed * args.batch_size
        ))

        # 找出未完成的批次
        for i, batch in enumerate(batches, 1):
            batch_ids = set()
            for p in batch:
                pid = p.get("id") or p.get("tid")
                if pid:
                    batch_ids.add(pid)
            if not batch_ids.issubset(analyzed_ids):
                print("PENDING: batch %d (%d posts)" % (i, len(batch)))

        sys.exit(0)

    if args.batch:
        # 输出指定批次
        if args.batch < 1 or args.batch > total_batches:
            print("ERROR: batch %d out of range (1-%d)" % (args.batch, total_batches))
            sys.exit(1)

        batch_posts = batches[args.batch - 1]
        batch_data = {
            "batch_num": args.batch,
            "total_batches": total_batches,
            "batch_size": len(batch_posts),
            "posts": batch_posts
        }

        # 写入批次文件
        batch_file = os.path.join(BATCH_DIR, "batch_%d.json" % args.batch)
        save_json(batch_file, batch_data)
        print("BATCH %d/%d: %d posts -> %s" % (
            args.batch, total_batches, len(batch_posts), batch_file
        ))
        sys.exit(0)

    # 默认：切割所有批次
    os.makedirs(BATCH_DIR, exist_ok=True)
    for i, batch in enumerate(batches, 1):
        batch_data = {
            "batch_num": i,
            "total_batches": total_batches,
            "batch_size": len(batch),
            "posts": batch
        }
        batch_file = os.path.join(BATCH_DIR, "batch_%d.json" % i)
        save_json(batch_file, batch_data)

    print("SPLIT: %d posts -> %d batches (size=%d)" % (
        len(pending), total_batches, args.batch_size
    ))
    print("BATCH_DIR: %s" % BATCH_DIR)

    # 输出每批概要
    for i, batch in enumerate(batches, 1):
        nicks = [p.get("nickname", "?")[:10] for p in batch[:3]]
        more = "..." if len(batch) > 3 else ""
        print("  batch %2d: %d posts [%s%s]" % (i, len(batch), ", ".join(nicks), more))


if __name__ == "__main__":
    main()
