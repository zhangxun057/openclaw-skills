#!/usr/bin/env python3
"""
群聊模型分析结果落库工具
功能：从 stdin 读取群聊切分结果 + 模型分析结果，写入 L1/checkpoint。
用法：
  python apply_group_chat_analysis.py --date 2026050917 < combined.json
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone


BAD_EVENT_PREFIXES = ("[文件]", "[音乐]", "[链接]", "[小程序]", "[视频号]", "[图片]", "[视频]", "[语音消息]")
BAD_EVENT_PATTERNS = ("quote:", "| quote", "会议链接", "会议 ID", "http://", "https://")
QUESTION_PATTERNS = ("是不是", "能不能", "要不要", "需不需要", "有没有", "怎么", "什么")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def load_existing_ids(path):
    ids = set()
    if not os.path.exists(path):
        return ids
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                if record.get("record_id"):
                    ids.add(record["record_id"])
            except Exception:
                pass
    return ids


def normalize_list(value, limit=12, item_len=60):
    if not isinstance(value, list):
        return []
    result = []
    seen = set()
    for item in value:
        text = str(item or "").strip()[:item_len]
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
        if len(result) >= limit:
            break
    return result


def is_bad_event(text):
    text = str(text or "").strip()
    if not text:
        return True
    if text.startswith(BAD_EVENT_PREFIXES):
        return True
    if any(pattern in text for pattern in BAD_EVENT_PATTERNS):
        return True
    if any(pattern in text for pattern in QUESTION_PATTERNS):
        return True
    if text.rstrip().endswith(("?", "？", "吗", "么", "呢", "吧")):
        return True
    if len(text) > 60:
        return True
    return False


def normalize_events(value, limit=3):
    if not isinstance(value, list):
        return []
    result = []
    seen = set()
    for item in value:
        text = str(item or "").strip()
        if is_bad_event(text) or text in seen:
            continue
        seen.add(text)
        result.append(text)
        if len(result) >= limit:
            break
    return result


def normalize_traits(value):
    if not isinstance(value, dict):
        return {}
    return {str(k)[:30]: str(v)[:40] for k, v in value.items() if v}


def normalize_rels(value):
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if not isinstance(item, dict):
            continue
        from_name = str(item.get("from") or "").strip()[:40]
        relation = str(item.get("relation") or "").strip()[:30]
        to_name = str(item.get("to") or "").strip()[:40]
        status = str(item.get("status") or "").strip()[:30]
        if not from_name or not relation or not to_name:
            continue
        result.append({
            "from": from_name,
            "relation": relation,
            "to": to_name,
            "status": status,
        })
        if len(result) >= 10:
            break
    return result


def build_record(segment, item):
    item = item if isinstance(item, dict) else {}
    overview = item.get("session_overview") if isinstance(item.get("session_overview"), dict) else {}
    messages = segment.get("messages") or []
    return {
        "record_id": segment.get("record_id") or "",
        "source": "group_chat",
        "chat_id": segment.get("chat_id") or "",
        "chat_name": segment.get("chat_name") or "",
        "source_file": segment.get("source_file") or "",
        "session_overview": {
            "time_start": overview.get("time_start", ""),
            "time_end": overview.get("time_end", ""),
            "rounds": overview.get("rounds", len(messages)),
            "message_count": segment.get("message_count", len(messages)),
        },
        "topics": normalize_list(item.get("topics"), limit=12, item_len=40),
        "events": normalize_events(item.get("events"), limit=3),
        "traits": normalize_traits(item.get("traits")),
        "signals": normalize_list(item.get("signals"), limit=6, item_len=30),
        "rels": normalize_rels(item.get("rels")),
    }


def append_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = load_existing_ids(path)
    written = 0
    with open(path, "a", encoding="utf-8") as f:
        for record in records:
            rid = record.get("record_id")
            if not rid or rid in existing:
                continue
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            existing.add(rid)
            written += 1
    return written


def save_checkpoint(path, existing_ids, records):
    ids = set(str(x) for x in existing_ids)
    for record in records:
        if record.get("record_id"):
            ids.add(record["record_id"])
    payload = {
        "analyzed_ids": sorted(ids),
        "total_analyzed": len(ids),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return len(ids)


def main():
    parser = argparse.ArgumentParser(description="写入群聊模型分析结果")
    parser.add_argument(
        "--base-dir",
        default=os.path.join(os.path.expanduser("~"), ".openclaw", "projects"),
        help="数据根目录，默认为 ~/.openclaw/projects"
    )
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d%H"), help="日志标识，格式 YYYYMMDDHH")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    input_data = json.load(sys.stdin)
    segments = input_data.get("segments", [])
    analysis = input_data.get("analysis", [])

    if not segments:
        print("NO_SEGMENTS", file=sys.stderr)
        return
    if not analysis:
        print("NO_ANALYSIS", file=sys.stderr)
        return
    if not isinstance(analysis, list) or len(analysis) != len(segments):
        raise ValueError("analysis 数量不匹配：segments=%d, analysis=%d" % (
            len(segments), len(analysis) if isinstance(analysis, list) else -1
        ))

    records = [build_record(seg, item) for seg, item in zip(segments, analysis)]
    extracted_dir = os.path.join(args.base_dir, "raw", "extracted_group_chat")
    checkpoint_path = os.path.join(extracted_dir, "checkpoint.json")
    log_path = os.path.join(extracted_dir, "group_chat_extracted_%s.jsonl" % args.date)
    written = append_jsonl(log_path, records)
    checkpoint = load_json(checkpoint_path, default={}) or {}
    total = save_checkpoint(checkpoint_path, checkpoint.get("analyzed_ids", []), records)

    print("OK: %d analyzed group records" % len(records), file=sys.stderr)
    print("L1: %d records -> %s" % (written, log_path), file=sys.stderr)
    print("CHECKPOINT: %d analyzed ids -> %s" % (total, checkpoint_path), file=sys.stderr)


if __name__ == "__main__":
    main()
