"""
会话切分模块 v2
从 raw/chat/*.jsonl 按 talker 分组 → 仅按日期边界切段 → stdout 输出
"""
import json
import os
import sys
from typing import List, Dict
from datetime import datetime, timezone, timedelta


def load_raw_chat(input_path: str) -> List[Dict]:
    messages = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return messages


def group_by_talker(messages: List[Dict]) -> Dict[str, List[Dict]]:
    groups = {}
    for msg in messages:
        talker = msg.get('talker', msg.get('wxid', 'unknown'))
        if talker not in groups:
            groups[talker] = []
        groups[talker].append(msg)
    return groups


def is_same_day(ts1: int, ts2: int) -> bool:
    tz = timezone(timedelta(hours=8))
    d1 = datetime.fromtimestamp(ts1 / 1000, tz).date()
    d2 = datetime.fromtimestamp(ts2 / 1000, tz).date()
    return d1 == d2


def segment_by_talker(messages: List[Dict]) -> List[List[Dict]]:
    """仅按日期边界切段"""
    if not messages:
        return []

    segments = []
    current_segment = [messages[0]]

    for i in range(1, len(messages)):
        prev = messages[i - 1]
        curr = messages[i]

        prev_ts = prev.get('create_time', prev.get('createTime', 0))
        curr_ts = curr.get('create_time', curr.get('createTime', 0))

        if not is_same_day(prev_ts, curr_ts):
            if current_segment:
                segments.append(current_segment)
            current_segment = [curr]
        else:
            current_segment.append(curr)

    if current_segment:
        segments.append(current_segment)

    return segments


def run_segmentation(input_path: str):
    """主入口：读 raw chat → 分组 → 切段 → stdout 输出"""
    messages = load_raw_chat(input_path)
    groups = group_by_talker(messages)

    all_segments = []
    for talker, msgs in groups.items():
        msgs.sort(key=lambda m: m.get('create_time', m.get('createTime', 0)))
        segments = segment_by_talker(msgs)
        for idx, seg in enumerate(segments):
            all_segments.append({
                'talker': talker,
                'segment_index': idx,
                'messages': seg
            })

    # stdout 输出，Agent 直接读取
    sys.stdout.reconfigure(encoding='utf-8')
    json.dump(all_segments, sys.stdout, ensure_ascii=False)

    return all_segments


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python segment_sessions.py <raw_chat.jsonl>", file=sys.stderr)
        sys.exit(1)

    inp = sys.argv[1]
    run_segmentation(inp)
