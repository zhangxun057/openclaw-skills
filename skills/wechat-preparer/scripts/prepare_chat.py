#!/usr/bin/env python3
"""
私聊数据准备工具
功能：扫描 raw/chat-analysis/ 下所有 JSONL 文件，切分会话段，比对 checkpoint，输出待分析的新段。
用法：
  python prepare_chat.py
  python prepare_chat.py --base-dir ~/.openclaw/projects
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

SILENCE_THRESHOLD_SECONDS = 1800  # 30 分钟


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def load_jsonl(path):
    records = []
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    return records


def is_same_day(ts1, ts2):
    tz = timezone(timedelta(hours=8))
    d1 = datetime.fromtimestamp(ts1 / 1000, tz).date()
    d2 = datetime.fromtimestamp(ts2 / 1000, tz).date()
    return d1 == d2


def parse_messages(session):
    """解析 chat JSONL 行中的 messages 数组，提取发消息的时间。
    推送格式：messages 是字符串数组 ["me: xxx", "peer: xxx"]，无时间戳。
    退而求其次：使用 session 级别的 createTime（如果存在），否则用消息序号。
    """
    msgs = session.get("messages", [])
    if not isinstance(msgs, list):
        return []

    # 尝试从 session 获取时间
    create_time = session.get("createTime", session.get("create_time", 0))
    parsed = []
    for i, m in enumerate(msgs):
        if not isinstance(m, str):
            continue
        m = m.strip()
        if not m:
            continue
        # 确定发送方
        if m.startswith("me:"):
            sender = "me"
            content = m[3:].strip()
        elif m.startswith("peer:"):
            sender = "peer"
            content = m[5:].strip()
        else:
            sender = "unknown"
            content = m

        parsed.append({
            "content": content,
            "sender": sender,
            "create_time": create_time + i * 1000 if create_time else i * 1000,
        })
    return parsed


def segment_messages(messages):
    """三层切分：日期边界 + 静默间隔"""
    if not messages:
        return []

    segments = []
    current = [messages[0]]

    for i in range(1, len(messages)):
        prev = messages[i - 1]
        curr = messages[i]

        prev_ts = prev.get("create_time", 0)
        curr_ts = curr.get("create_time", 0)
        gap = (curr_ts - prev_ts) / 1000

        cross_day = not is_same_day(prev_ts, curr_ts)
        silent = gap > SILENCE_THRESHOLD_SECONDS

        if cross_day or silent:
            if current:
                segments.append(current)
            current = [curr]
        else:
            current.append(curr)

    if current:
        segments.append(current)

    return segments


def make_segment_id(talker, segment_index, messages):
    """生成切分段的唯一 ID"""
    ts_start = messages[0]["create_time"] if messages else 0
    ts_end = messages[-1]["create_time"] if messages else 0
    return "%s_%d_%d" % (talker, ts_start, ts_end)


def main():
    parser = argparse.ArgumentParser(description="私聊数据准备")
    parser.add_argument(
        "--base-dir",
        default=os.path.join(os.path.expanduser("~"), ".openclaw", "projects"),
        help="数据根目录，默认为 ~/.openclaw/projects"
    )
    args = parser.parse_args()

    base = os.path.expanduser(args.base_dir)
    raw_dir = os.path.join(base, "raw", "chat-analysis")
    state_dir = os.path.join(base, "state")
    cp_path = os.path.join(base, "raw", "extracted_chat", "checkpoint.json")

    if not os.path.isdir(raw_dir):
        print("NO_RAW_DIR")
        return

    # 扫描所有 chat JSONL 文件
    jsonl_files = sorted([
        f for f in os.listdir(raw_dir)
        if f.startswith("chat_") and f.endswith(".jsonl")
    ])
    if not jsonl_files:
        print("NO_DATA")
        return

    checkpoint = load_json(cp_path, default={}) or {}
    analyzed = set(str(x) for x in checkpoint.get("analyzed_ids", []))

    all_segments = []
    data_sources = []
    total_sessions = 0

    for fname in jsonl_files:
        fpath = os.path.join(raw_dir, fname)
        sessions = load_jsonl(fpath)
        if not sessions:
            continue

        total_sessions += len(sessions)
        file_contrib = 0

        for session in sessions:
            talker = session.get("sessionId") or session.get("wxid") or ""
            if not talker or talker == "me":
                continue

            nick = session.get("sessionName", "")
            messages = parse_messages(session)
            if not messages:
                continue

            segments = segment_messages(messages)
            for seg_idx, seg in enumerate(segments):
                seg_id = make_segment_id(talker, seg_idx, seg)
                if seg_id in analyzed:
                    continue

                all_segments.append({
                    "talker": talker,
                    "nickname": nick,
                    "segment_index": seg_idx,
                    "segment_id": seg_id,
                    "source_file": fname,
                    "messages": seg,
                })
                file_contrib += 1

        if file_contrib > 0:
            data_sources.append(fname)

    os.makedirs(state_dir, exist_ok=True)
    out_path = os.path.join(state_dir, "chat_segments.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for seg in all_segments:
            f.write(json.dumps(seg, ensure_ascii=False) + "\n")

    print("OK: %d new segments from %d sessions (%d files contributed, checkpoint: %d)" % (
        len(all_segments), total_sessions, len(data_sources), len(analyzed)))
    print("CHAT_SEGMENTS: " + out_path)


if __name__ == "__main__":
    main()
