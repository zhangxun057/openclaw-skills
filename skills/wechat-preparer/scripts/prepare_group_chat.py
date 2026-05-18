#!/usr/bin/env python3
"""
群聊数据准备工具
功能：扫描 raw/group-chat-analysis/ 下所有 JSONL 文件，过滤低价值消息，按群和消息数量切段，
      比对 extracted_group_chat/checkpoint.json，输出待分析的新段。
用法：
  python prepare_group_chat.py
  python prepare_group_chat.py --base-dir ~/.openclaw/projects --max-messages 120
"""
import argparse
import hashlib
import json
import os
import re
import sys


DEFAULT_MAX_MESSAGES = 120
DROP_EXACT = {"收到", "好的", "好", "嗯", "嗯嗯", "ok", "OK", "1", "是", "对"}
SYSTEM_PATTERNS = (
    "邀请你和",
    "加入了群聊",
    "撤回了一条消息",
    "拍了拍",
)


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


def parse_message(raw, index):
    if isinstance(raw, str):
        text = raw.strip()
        sender = "unknown"
        content = text
        if ":" in text:
            left, right = text.split(":", 1)
            if left.strip():
                sender = left.strip()
                content = right.strip()
        return {
            "sender": sender,
            "content": content,
            "create_time": index * 1000,
            "raw_index": index,
        }
    if isinstance(raw, dict):
        return {
            "sender": str(raw.get("sender") or raw.get("senderName") or raw.get("nickname") or "unknown"),
            "content": str(raw.get("content") or raw.get("text") or raw.get("message") or "").strip(),
            "create_time": raw.get("create_time") or raw.get("createTime") or raw.get("timestamp") or index * 1000,
            "raw_index": index,
        }
    return {
        "sender": "unknown",
        "content": str(raw).strip(),
        "create_time": index * 1000,
        "raw_index": index,
    }


def is_noise_message(message):
    content = re.sub(r"\s+", " ", str(message.get("content") or "")).strip()
    if not content:
        return True
    if content in DROP_EXACT:
        return True
    if any(pattern in content for pattern in SYSTEM_PATTERNS):
        return True
    if re.fullmatch(r"[\W_]{1,4}", content):
        return True
    return False


def segment_id(chat_id, source_file, messages):
    start = messages[0].get("raw_index", 0) if messages else 0
    end = messages[-1].get("raw_index", 0) if messages else 0
    fingerprint_src = "\n".join(
        "%s:%s" % (m.get("sender", ""), m.get("content", "")[:80])
        for m in (messages[:3] + messages[-3:])
    )
    digest = hashlib.sha1(fingerprint_src.encode("utf-8", errors="ignore")).hexdigest()[:10]
    return "%s_%s_%s_%s_%s" % (chat_id, source_file.replace(".", "_"), start, end, digest)


def split_messages(messages, max_messages):
    return [messages[i:i + max_messages] for i in range(0, len(messages), max_messages)]


def main():
    parser = argparse.ArgumentParser(description="群聊数据准备")
    parser.add_argument(
        "--base-dir",
        default=os.path.join(os.path.expanduser("~"), ".openclaw", "projects"),
        help="数据根目录，默认为 ~/.openclaw/projects"
    )
    parser.add_argument("--max-messages", type=int, default=DEFAULT_MAX_MESSAGES, help="每段最多保留的有效消息数")
    args = parser.parse_args()

    base = os.path.expanduser(args.base_dir)
    raw_dir = os.path.join(base, "raw", "group-chat-analysis")
    cp_path = os.path.join(base, "raw", "extracted_group_chat", "checkpoint.json")
    state_dir = os.path.join(base, "state")

    if not os.path.isdir(raw_dir):
        print("NO_RAW_DIR", file=sys.stderr)
        sys.exit(1)

    jsonl_files = sorted([
        f for f in os.listdir(raw_dir)
        if f.startswith("group_chat_") and f.endswith(".jsonl")
    ])
    if not jsonl_files:
        print("NO_DATA", file=sys.stderr)
        sys.exit(1)

    checkpoint = load_json(cp_path, default={}) or {}
    analyzed = set(str(x) for x in checkpoint.get("analyzed_ids", []))

    all_segments = []
    total_sessions = 0
    total_messages = 0
    kept_messages = 0
    data_sources = []

    for fname in jsonl_files:
        sessions = load_jsonl(os.path.join(raw_dir, fname))
        if not sessions:
            continue
        file_contrib = 0
        total_sessions += len(sessions)
        for session in sessions:
            chat_id = session.get("sessionId") or session.get("chat_id") or session.get("id") or ""
            chat_name = session.get("sessionName") or session.get("chat_name") or chat_id
            if not chat_id:
                continue
            raw_messages = session.get("messages") or []
            parsed = [parse_message(m, i) for i, m in enumerate(raw_messages)]
            total_messages += len(parsed)
            filtered = [m for m in parsed if not is_noise_message(m)]
            kept_messages += len(filtered)
            if not filtered:
                continue
            for chunk in split_messages(filtered, max(20, args.max_messages)):
                sid = segment_id(chat_id, fname, chunk)
                if sid in analyzed:
                    continue
                all_segments.append({
                    "record_id": sid,
                    "chat_id": chat_id,
                    "chat_name": chat_name,
                    "source_file": fname,
                    "message_count": len(chunk),
                    "messages": chunk,
                })
                file_contrib += 1
        if file_contrib:
            data_sources.append(fname)

    os.makedirs(state_dir, exist_ok=True)
    out_path = os.path.join(state_dir, "group_chat_segments.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for seg in all_segments:
            f.write(json.dumps(seg, ensure_ascii=False) + "\n")

    print("OK: %d new group segments from %d sessions (%d/%d messages kept, %d files contributed, checkpoint: %d)" % (
        len(all_segments), total_sessions, kept_messages, total_messages, len(data_sources), len(analyzed)
    ), file=sys.stderr)
    print("GROUP_CHAT_SEGMENTS: " + out_path)


if __name__ == "__main__":
    main()
