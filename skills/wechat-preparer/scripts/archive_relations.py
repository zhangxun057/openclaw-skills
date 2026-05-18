#!/usr/bin/env python3
"""Archive L1 rels into customer relation-edge jsonl files."""
import argparse
import glob
import json
import os
from datetime import datetime


def iter_jsonl(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def relation_key(edge):
    return "|".join([
        str(edge.get("from_id") or edge.get("from_name") or ""),
        str(edge.get("relation") or ""),
        str(edge.get("to_id") or edge.get("to_name") or ""),
        str(edge.get("source_type") or ""),
        str(edge.get("source_id") or ""),
    ])


def relation_label(action):
    return {"like": "点赞", "comment": "评论"}.get(action, "朋友圈互动")


def customer_exists(base, customer_id):
    if not customer_id or customer_id == "me":
        return False
    return os.path.isdir(os.path.join(base, "customers", customer_id))


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


def write_edge(base, customer_id, edge, dry_run=False):
    path = os.path.join(base, "customers", customer_id, "wechat-analysis", customer_id + "_relations.jsonl")
    if dry_run:
        return 1, path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    key = relation_key(edge)
    existing = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    existing.add(relation_key(json.loads(line)))
                except Exception:
                    pass
    if key in existing:
        return 0, path
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(edge, ensure_ascii=False) + "\n")
    return 1, path


def archive_edge(base, edge, dry_run=False):
    targets = []
    for side in ("from_id", "to_id"):
        cid = edge.get(side) or ""
        if customer_exists(base, cid):
            targets.append(cid)
    written = 0
    paths = []
    for cid in dict.fromkeys(targets):
        count, path = write_edge(base, cid, edge, dry_run=dry_run)
        written += count
        paths.append(path)
    return written, paths


def moment_edges(record):
    source_id = record.get("post_id") or ""
    to_id = record.get("wxid") or ""
    to_name = record.get("nickname") or to_id
    date = normalize_date(record.get("post_time") or "")
    if not source_id or not to_id:
        return []
    edges = []
    for rel in record.get("rels") or []:
        if isinstance(rel, str):
            person_id, person_name, action = "", rel, "interaction"
        elif isinstance(rel, dict):
            person_id = rel.get("person_id") or ""
            person_name = rel.get("person") or person_id
            action = rel.get("action") or "interaction"
        else:
            continue
        if not person_id and not person_name:
            continue
        edges.append({
            "from_id": person_id,
            "from_name": person_name,
            "relation": relation_label(action),
            "to_id": to_id,
            "to_name": to_name,
            "status": "",
            "source_type": "moment",
            "source_id": source_id,
            "date": date,
        })
    return edges


def chat_edges(record):
    source_id = record.get("segment_id") or ""
    from_id = record.get("talker") or ""
    from_name = record.get("nickname") or from_id
    date = normalize_date((record.get("session_overview") or {}).get("time_start") or "")
    rels = record.get("rels") or []
    if isinstance(rels, dict):
        rels = [rels]
    edges = []
    for rel in rels:
        if not isinstance(rel, dict):
            continue
        relation = rel.get("relation") or rel.get("relationship_type") or ""
        status = rel.get("status") or rel.get("attitude") or ""
        confidence = rel.get("confidence") or ""
        evidence = rel.get("evidence") or ""
        if not from_id or not relation:
            continue
        edges.append({
            "from_id": from_id,
            "from_name": from_name,
            "relation": relation,
            "to_id": "me",
            "to_name": "我",
            "status": status,
            "confidence": confidence,
            "evidence": evidence,
            "source_type": "chat",
            "source_id": source_id,
            "date": date,
        })
    return edges


def group_edges(base, record):
    source_id = record.get("record_id") or record.get("chat_id") or ""
    date = normalize_date((record.get("session_overview") or {}).get("time_start") or record.get("create_time") or "")
    edges = []
    for rel in record.get("rels") or []:
        if not isinstance(rel, dict):
            continue
        from_name = str(rel.get("from") or "")
        to_name = str(rel.get("to") or "")
        relation = str(rel.get("relation") or "")
        if not from_name or not to_name or not relation:
            continue
        edges.append({
            "from_id": from_name if customer_exists(base, from_name) else "",
            "from_name": from_name,
            "relation": relation,
            "to_id": to_name if customer_exists(base, to_name) else "",
            "to_name": to_name,
            "status": str(rel.get("status") or ""),
            "source_type": "group_chat",
            "source_id": source_id,
            "date": date,
        })
    return edges


def source_files(base, source):
    patterns = {
        "moment": os.path.join(base, "raw", "extracted_moment", "moment_extracted_*.jsonl"),
        "chat": os.path.join(base, "raw", "extracted_chat", "chat_extracted_*.jsonl"),
        "group_chat": os.path.join(base, "raw", "extracted_group_chat", "group_chat_extracted_*.jsonl"),
    }
    return sorted(glob.glob(patterns[source]))


def main():
    parser = argparse.ArgumentParser(description="Archive extracted rels into customer relation edges")
    parser.add_argument(
        "--base-dir",
        default=os.path.join(os.path.expanduser("~"), ".openclaw", "projects")
    )
    parser.add_argument("--source", choices=["moment", "chat", "group_chat", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    sources = ["moment", "chat", "group_chat"] if args.source == "all" else [args.source]
    scanned = edges = written = 0
    examples = []
    for source in sources:
        for path in source_files(args.base_dir, source):
            for record in iter_jsonl(path):
                scanned += 1
                if source == "moment":
                    new_edges = moment_edges(record)
                elif source == "chat":
                    new_edges = chat_edges(record)
                else:
                    new_edges = group_edges(args.base_dir, record)
                for edge in new_edges:
                    edges += 1
                    count, paths = archive_edge(args.base_dir, edge, dry_run=args.dry_run)
                    written += count
                    if len(examples) < 5:
                        examples.append({"edge": edge, "paths": paths})
                if args.limit and scanned >= args.limit:
                    break
            if args.limit and scanned >= args.limit:
                break

    print(json.dumps({
        "scanned_records": scanned,
        "relation_edges": edges,
        "written_or_would_write": written,
        "dry_run": args.dry_run,
        "examples": examples,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
