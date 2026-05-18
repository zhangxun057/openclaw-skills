#!/usr/bin/env python3
"""
私聊模型分析结果落库工具 v2
功能：从 stdin 读取切分结果 + 模型分析结果，写入 L1/L2/checkpoint。
用法：
  segment_sessions.py <raw> | Agent 抽取 → 传给本脚本
  python apply_chat_analysis.py --date 2026050810 < combined.json
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone


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


def format_time(ts):
    """毫秒时间戳 → YYYY-MM-DD HH:MM:SS"""
    if ts in (None, 0, ""):
        return ""
    try:
        ts = float(ts)
        if ts > 100000000000:
            ts = ts / 1000
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)[:19]


def normalize_date(value):
    text = str(value or "").strip()
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 8:
        if digits.startswith("20"):
            return "%s-%s-%s" % (digits[:4], digits[4:6], digits[6:8])
        return "20%s-%s-%s" % (digits[:2], digits[2:4], digits[4:6])
    if len(digits) == 6 and digits.startswith("20"):
        return "%s-%s" % (digits[:4], digits[4:6])
    if len(digits) == 6:
        return "20%s-%s-%s" % (digits[:2], digits[2:4], digits[4:6])
    return text[:10]


def normalize_list(value, limit=20, item_len=60):
    if not isinstance(value, list):
        return []
    return [str(item)[:item_len] for item in value if item][:limit]


BAD_EVENT_PREFIXES = ("[文件]", "[音乐]", "[链接]", "[小程序]", "[视频号]", "[图片]", "[视频]", "[语音消息]")
BAD_EVENT_PATTERNS = (
    "quote:",
    "| quote",
    "邀请你加入飞书视频会议",
    "邀请您参加腾讯会议",
    "会议链接",
    "会议 ID",
    "http://",
    "https://",
)
BAD_EVENT_STARTS = (
    "unknown",
    "洵总",
    "您看",
    "你看看",
    "麻烦",
    "好的",
    "收到",
    "默认",
    "我觉得",
    "我感觉",
    "我问的是",
    "只是",
)
QUESTION_PATTERNS = ("是不是", "能不能", "要不要", "需不需要", "有没有", "怎么", "什么")


def is_bad_event(text):
    text = str(text or "").strip()
    if not text:
        return True
    if text.startswith(BAD_EVENT_PREFIXES):
        return True
    if text.startswith(BAD_EVENT_STARTS):
        return True
    if any(pattern in text for pattern in BAD_EVENT_PATTERNS):
        return True
    if any(pattern in text for pattern in QUESTION_PATTERNS):
        return True
    stripped = text.rstrip()
    if stripped.endswith(("?", "？", "吗", "么", "呢", "吧")):
        return True
    if len(stripped) > 60:
        return True
    return False


def normalize_events(value, limit=3):
    if not isinstance(value, list):
        return []
    result = []
    seen = set()
    for item in value:
        text = str(item or "").strip()
        if is_bad_event(text):
            continue
        if text in seen:
            continue
        seen.add(text)
        result.append(text)
        if len(result) >= limit:
            break
    return result


def normalize_traits(value):
    if not isinstance(value, dict):
        return {}
    return {str(k): str(v)[:30] for k, v in value.items() if v}


def normalize_rels(value):
    items = value if isinstance(value, list) else [value]
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        relation = item.get("relation") or item.get("relationship_type") or ""
        confidence = item.get("confidence") or ""
        evidence = item.get("evidence") or ""
        status = item.get("status") or item.get("attitude") or ""
        relation = str(relation)[:30]
        confidence = str(confidence)[:10]
        evidence = str(evidence)[:80]
        status = str(status)[:20]
        if relation:
            rel = {
                "relation": relation,
                "confidence": confidence,
                "evidence": evidence,
            }
            if status:
                rel["status"] = status
            result.append(rel)
    return result[:5]


def normalize_todos(value):
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if isinstance(item, dict):
            result.append({
                "content": str(item.get("content", ""))[:200],
                "deadline": str(item.get("deadline", ""))[:20],
            })
    return result


def build_record(seg, item):
    item = item if isinstance(item, dict) else {}
    msgs = seg.get("messages", [])

    overview = item.get("session_overview", {}) or {}
    time_start = overview.get("time_start") or format_time(msgs[0]["create_time"] if msgs else 0)
    time_end = overview.get("time_end") or format_time(msgs[-1]["create_time"] if msgs else 0)

    return {
        "segment_id": seg.get("segment_id") or "",
        "talker": seg.get("talker") or "",
        "nickname": seg.get("nickname") or "",
        "session_overview": {
            "time_start": time_start,
            "time_end": time_end,
            "rounds": overview.get("rounds", 0),
            "initiator": str(overview.get("initiator", "")),
            "volume": str(overview.get("volume", "")),
        },
        "events": normalize_events(item.get("events"), limit=3),
        "traits": normalize_traits(item.get("traits")),
        "signals": normalize_list(item.get("signals"), limit=6, item_len=60),
        "topics": normalize_list(item.get("topics"), limit=10, item_len=40),
        "rels": normalize_rels(item.get("rels")),
        "todos": normalize_todos(item.get("todos")),
    }


def load_existing_ids(path):
    ids = set()
    if not os.path.exists(path):
        return ids
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                if record.get("segment_id"):
                    ids.add(record["segment_id"])
            except Exception:
                pass
    return ids


def append_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing_ids = load_existing_ids(path)
    written = 0
    with open(path, "a", encoding="utf-8") as f:
        for record in records:
            sid = record.get("segment_id")
            if not sid or sid in existing_ids:
                continue
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            existing_ids.add(sid)
            written += 1
    return written


def relation_key(edge):
    return "|".join([
        str(edge.get("from_id") or edge.get("from_name") or ""),
        str(edge.get("relation") or ""),
        str(edge.get("to_id") or edge.get("to_name") or ""),
        str(edge.get("source_type") or ""),
        str(edge.get("source_id") or ""),
    ])


def load_existing_relation_keys(path):
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                keys.add(relation_key(record))
            except Exception:
                pass
    return keys


def append_relation_jsonl(path, edges):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = load_existing_relation_keys(path)
    written = 0
    with open(path, "a", encoding="utf-8") as f:
        for edge in edges:
            key = relation_key(edge)
            if not key or key in existing:
                continue
            f.write(json.dumps(edge, ensure_ascii=False) + "\n")
            existing.add(key)
            written += 1
    return written


def write_customers(base, records):
    written = 0
    users = set()
    for record in records:
        talker = record.get("talker")
        if not talker:
            continue
        users.add(talker)
        profile_path = os.path.join(
            base, "customers", talker, "wechat-analysis",
            talker + "_chat_extracted.jsonl"
        )
        written += append_jsonl(profile_path, [record])
    return written, len(users)


def append_relations(base, records):
    """追加关系边到 customers/{talker}/wechat-analysis/{talker}_relations.jsonl"""
    written = 0
    for record in records:
        talker = record.get("talker")
        rels = record.get("rels") or []
        if not talker or not rels:
            continue

        rel_dir = os.path.join(base, "customers", talker, "wechat-analysis")
        rel_path = os.path.join(rel_dir, talker + "_relations.jsonl")
        date = normalize_date((record.get("session_overview", {}) or {}).get("time_start", ""))
        edges = []
        for rel in rels:
            if not isinstance(rel, dict) or not rel.get("relation"):
                continue
            edges.append({
                "from_id": talker,
                "from_name": record.get("nickname") or talker,
                "relation": rel.get("relation", ""),
                "to_id": "me",
                "to_name": "我",
                "status": rel.get("status", ""),
                "confidence": rel.get("confidence", ""),
                "evidence": rel.get("evidence", ""),
                "source_type": "chat",
                "source_id": record.get("segment_id") or "",
                "date": date,
            })
        written += append_relation_jsonl(rel_path, edges)
    return written


def save_checkpoint(path, existing_ids, records):
    ids = set(str(x) for x in existing_ids)
    for record in records:
        if record.get("segment_id"):
            ids.add(record["segment_id"])
    payload = {
        "analyzed_ids": sorted(ids),
        "total_analyzed": len(ids),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return len(ids)


def align_analysis(segments, analysis):
    if not isinstance(analysis, list):
        raise ValueError("analysis 必须是 JSON 数组")
    if len(analysis) != len(segments):
        raise ValueError("analysis 数量不匹配：segments=%d, analysis=%d" % (len(segments), len(analysis)))
    return analysis


def main():
    parser = argparse.ArgumentParser(description="写入私聊模型分析结果")
    parser.add_argument(
        "--base-dir",
        default=os.path.join(os.path.expanduser("~"), ".openclaw", "projects"),
        help="数据根目录，默认为 ~/.openclaw/projects"
    )
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d%H"), help="日志标识，格式 YYYYMMDDHH")
    args = parser.parse_args()

    base = args.base_dir
    extracted_dir = os.path.join(base, "raw", "extracted_chat")
    checkpoint_path = os.path.join(extracted_dir, "checkpoint.json")

    # 从 stdin 读取：segments + analysis
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')
    input_data = json.load(sys.stdin)

    segments = input_data.get("segments", [])
    analysis = input_data.get("analysis", [])

    if not segments:
        print("NO_SEGMENTS", file=sys.stderr)
        return
    if not analysis:
        print("NO_ANALYSIS", file=sys.stderr)
        return

    items = align_analysis(segments, analysis)
    records = [build_record(seg, item) for seg, item in zip(segments, items)]

    extracted_filename = "chat_extracted_%s.jsonl" % args.date
    log_path = os.path.join(extracted_dir, extracted_filename)
    l1_written = append_jsonl(log_path, records)

    l2_written, l2_users = write_customers(base, records)
    rel_written = append_relations(base, records)

    checkpoint = load_json(checkpoint_path, default={}) or {}
    total = save_checkpoint(checkpoint_path, checkpoint.get("analyzed_ids", []), records)

    print("OK: %d analyzed records" % len(records), file=sys.stderr)
    print("L1: %d records -> %s" % (l1_written, log_path), file=sys.stderr)
    print("L2: %d records, %d customers" % (l2_written, l2_users), file=sys.stderr)
    print("RELATIONS: %d records updated" % rel_written, file=sys.stderr)
    print("CHECKPOINT: %d analyzed ids -> %s" % (total, checkpoint_path), file=sys.stderr)


if __name__ == "__main__":
    main()
