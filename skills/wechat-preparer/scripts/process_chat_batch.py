#!/usr/bin/env python3
"""
Process recent chat segments - batch extraction and save to L1/L2.
"""
import json
import os
import sys
import time

BASE = os.path.join(os.path.expanduser("~"), ".openclaw", "projects")
SEGMENT_FILE = os.path.join(BASE, "state", "chat_segments.jsonl")

def load_segments(filepath, start=0, count=20):
    segments = []
    if not os.path.exists(filepath):
        return segments
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i < start:
                continue
            if i >= start + count:
                break
            try:
                segments.append(json.loads(line))
            except:
                pass
    return segments

def analyze_chat_segment(seg):
    """Analyze a single chat segment."""
    msgs = seg.get("messages", [])
    if not msgs:
        return None
    
    talker = seg.get("talker", "") or seg.get("contact_wxid", "")
    contact_name = seg.get("contact_name", "") or seg.get("sessionName", "")
    seg_id = seg.get("seg_id", "") or seg.get("sessionId", "")
    
    # Find me/peer
    me_msgs = [m for m in msgs if m.get("is_self", False) or m.get("sender") == "me"]
    peer_msgs = [m for m in msgs if not m.get("is_self", False) and m.get("sender") != "me"]
    
    # Get timestamps
    timestamps = []
    for m in msgs:
        t = m.get("CreateTime") or m.get("create_time") or m.get("timestamp")
        if t:
            timestamps.append(int(t))
    
    time_start = min(timestamps) if timestamps else 0
    time_end = max(timestamps) if timestamps else 0
    
    # Convert to YYMMDDTHHmm
    def fmt_ts(ts):
        if not ts:
            return ""
        import datetime
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone(datetime.timedelta(hours=8)))
        return dt.strftime("%y%m%dT%H%M")
    
    # Count rounds
    rounds = 0
    last_sender = None
    for m in msgs:
        sender = m.get("sender", "") or ("me" if m.get("is_self") else "peer")
        if sender != last_sender:
            rounds += 1
            last_sender = sender
    
    # Volume analysis
    me_chars = sum(len(str(m.get("content", ""))) for m in me_msgs)
    peer_chars = sum(len(str(m.get("content", ""))) for m in peer_msgs)
    if me_chars > peer_chars * 2:
        volume = "me_dominant"
    elif peer_chars > me_chars * 2:
        volume = "them_dominant"
    else:
        volume = "balanced"
    
    # Initiator
    first_sender = msgs[0].get("sender", "") if msgs else ""
    initiator = "me" if first_sender == "me" else "them"
    
    # Collect all content for analysis
    all_content = []
    for m in msgs:
        content = m.get("content", "")
        if content and content.strip() and content.strip() != "[图片]" and content.strip() != "[视频]":
            sender = m.get("sender", "") or ("me" if m.get("is_self") else "peer")
            all_content.append((sender, content[:200]))
    
    # Simple rule-based analysis
    events, traits, signals, topics, rels, todos = [], [], [], [], [], []
    
    # Join content for analysis
    joined_content = " ".join([c[1] for c in all_content])
    
    # Extract topics
    topic_keywords = {
        "白酒": ["白酒", "酱香", "茅台", "习酒", "珍酒", "国台"],
        "工作": ["工作", "项目", "会议", "安排", "任务"],
        "生活": ["吃饭", "周末", "休息", "旅游"],
    }
    for topic, keywords in topic_keywords.items():
        if any(kw in joined_content for kw in keywords):
            topics.append(topic)
    
    # Check for image/video heavy chats
    img_count = sum(1 for m in msgs if "[图片]" in str(m.get("content", "")))
    video_count = sum(1 for m in msgs if "[视频]" in str(m.get("content", "")))
    
    return {
        "session_overview": {
            "time_start": fmt_ts(time_start),
            "time_end": fmt_ts(time_end),
            "rounds": rounds,
            "initiator": initiator,
            "volume": volume
        },
        "events": events,
        "traits": traits,
        "signals": signals,
        "topics": topics,
        "rels": rels,
        "todos": todos,
        "_meta": {
            "talker": talker,
            "contact_name": contact_name,
            "msg_count": len(msgs),
            "img_count": img_count,
            "video_count": video_count
        }
    }

def save_chat_results(segments, analyses):
    """Save to L1 and L2."""
    l1_dir = os.path.join(BASE, "raw", "extracted_chat")
    os.makedirs(l1_dir, exist_ok=True)
    
    customers_dir = os.path.join(BASE, "customers")
    
    date_label = "20260508"  # Most recent chat file
    l1_path = os.path.join(l1_dir, "chat_extracted_%s09.jsonl" % date_label)
    
    # Load existing IDs
    existing_ids = set()
    if os.path.exists(l1_path):
        with open(l1_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                    existing_ids.add(item.get("seg_id", ""))
                except:
                    pass
    
    saved = 0
    for seg, analysis in zip(segments, analyses):
        if analysis is None:
            continue
        
        seg_id = seg.get("seg_id", "") or seg.get("sessionId", "") or "seg_%d" % hash(str(seg))
        if seg_id in existing_ids:
            continue
        
        talker = seg.get("talker", "") or seg.get("contact_wxid", "")
        
        record = {
            "seg_id": seg_id,
            "talker": talker,
            "contact_name": analysis["_meta"]["contact_name"],
            "msg_count": analysis["_meta"]["msg_count"],
            "analysis": {
                "session_overview": analysis["session_overview"],
                "events": analysis["events"],
                "traits": analysis["traits"],
                "signals": analysis["signals"],
                "topics": analysis["topics"],
                "rels": analysis["rels"],
                "todos": analysis["todos"]
            },
            "raw_date": date_label
        }
        
        # L1
        with open(l1_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        # L2
        if talker:
            cust_dir = os.path.join(customers_dir, talker, "wechat-analysis")
            os.makedirs(cust_dir, exist_ok=True)
            l2_path = os.path.join(cust_dir, "%s_chat_extracted.jsonl" % talker)
            with open(l2_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        # Save relations
        if analysis["rels"]:
            rel_path = os.path.join(cust_dir, "%s_relations.jsonl" % talker) if talker else None
            if rel_path:
                with open(rel_path, "a", encoding="utf-8") as f:
                    for rel in analysis["rels"]:
                        f.write(json.dumps(rel, ensure_ascii=False) + "\n")
        
        saved += 1
    
    # Update checkpoint
    cp_path = os.path.join(l1_dir, "checkpoint.json")
    checkpoint = {}
    if os.path.exists(cp_path):
        try:
            with open(cp_path, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
        except:
            pass
    
    analyzed_ids = set(str(x) for x in checkpoint.get("analyzed_ids", []))
    for seg in segments:
        seg_id = seg.get("seg_id", "") or seg.get("sessionId", "")
        if seg_id:
            analyzed_ids.add(seg_id)
    
    checkpoint["analyzed_ids"] = sorted(list(analyzed_ids))
    checkpoint["last_updated"] = date_label
    checkpoint["last_run"] = int(time.time())
    
    with open(cp_path, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    return saved

def main():
    # Process first 50 chat segments (initial batch)
    segments = load_segments(SEGMENT_FILE, start=0, count=50)
    
    if not segments:
        print("NO_SEGMENTS", file=sys.stderr)
        return
    
    print("Processing %d chat segments..." % len(segments), file=sys.stderr)
    
    analyses = []
    for seg in segments:
        analysis = analyze_chat_segment(seg)
        analyses.append(analysis)
    
    saved = save_chat_results(segments, analyses)
    
    # Summary
    total_events = sum(len(a["events"]) for a in analyses if a)
    total_signals = sum(len(a["signals"]) for a in analyses if a)
    total_topics = sum(len(a["topics"]) for a in analyses if a)
    
    print("L1/L2 saved: %d segments" % saved, file=sys.stderr)
    print("Events: %d, Signals: %d, Topics: %d" % (total_events, total_signals, total_topics), file=sys.stderr)
    
    # Print segment summaries
    for i, (seg, analysis) in enumerate(zip(segments, analyses)):
        if analysis is None:
            continue
        name = analysis["_meta"]["contact_name"]
        msgs = analysis["_meta"]["msg_count"]
        overview = analysis["session_overview"]
        topics = analysis["topics"]
        print("[%d] %s: %d msgs, rounds=%d, volume=%s, topics=%s" % (
            i+1, name[:20], msgs, overview["rounds"], overview["volume"], topics
        ), file=sys.stderr)
    
    sys.stderr.flush()

if __name__ == "__main__":
    main()
