#!/usr/bin/env python3
"""
Process recent group chat segments - batch extraction and save to L1.
"""
import json
import os
import sys
import time

BASE = os.path.join(os.path.expanduser("~"), ".openclaw", "projects")
SEGMENT_FILE = os.path.join(BASE, "state", "group_chat_segments.jsonl")

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

def analyze_group_segment(seg):
    """Analyze a single group chat segment."""
    msgs = seg.get("messages", [])
    if not msgs:
        return None
    
    group_id = seg.get("groupId", "") or seg.get("group_id", "")
    group_name = seg.get("groupName", "") or seg.get("group_name", "") or "未知群"
    
    # Find timestamps
    timestamps = []
    for m in msgs:
        t = m.get("CreateTime") or m.get("create_time") or m.get("timestamp")
        if t:
            timestamps.append(int(t))
    
    time_start = min(timestamps) if timestamps else 0
    time_end = max(timestamps) if timestamps else 0
    
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
        sender = m.get("senderName", "") or m.get("sender", "") or m.get("nickname", "")
        if sender != last_sender:
            rounds += 1
            last_sender = sender
    
    # Get unique speakers
    speakers = set()
    for m in msgs:
        sender = m.get("senderName", "") or m.get("sender", "") or m.get("nickname", "")
        if sender:
            speakers.add(sender)
    
    # Collect content for topic analysis
    all_content = []
    for m in msgs:
        content = m.get("content", "") or m.get("msgContent", "")
        if content and content.strip() and content.strip() not in ("[图片]", "[视频]", "[语音]"):
            all_content.append(content[:200])
    
    joined = " ".join(all_content)
    
    # Topics
    topics = []
    topic_keywords = {
        "白酒": ["白酒", "酱香", "茅台", "习酒", "珍酒", "国台", "青酒"],
        "工作": ["工作", "项目", "会议", "安排", "需求", "开发", "测试"],
        "生活": ["吃饭", "周末", "休息", "旅游"],
        "活动": ["活动", "会议", "论坛", "展会", "招商"],
    }
    for topic, keywords in topic_keywords.items():
        if any(kw in joined for kw in keywords):
            topics.append(topic)
    
    # Events and traits (rule-based initial)
    events = []
    traits = {}
    signals = []
    rels = []
    
    # Save meta
    return {
        "session_overview": {
            "time_start": fmt_ts(time_start),
            "time_end": fmt_ts(time_end),
            "rounds": rounds
        },
        "topics": topics,
        "events": events,
        "traits": traits,
        "signals": signals,
        "rels": rels,
        "_meta": {
            "group_id": group_id,
            "group_name": group_name,
            "msg_count": len(msgs),
            "speaker_count": len(speakers)
        }
    }

def save_group_results(segments, analyses):
    """Save to L1."""
    l1_dir = os.path.join(BASE, "raw", "extracted_group_chat")
    os.makedirs(l1_dir, exist_ok=True)
    
    date_label = "20260508"
    l1_path = os.path.join(l1_dir, "group_chat_extracted_%s09.jsonl" % date_label)
    
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
        
        seg_id = seg.get("seg_id", "") or "gseg_%d_%d" % (hash(str(seg)), len(analysis["_meta"]["group_name"]))
        if seg_id in existing_ids:
            continue
        
        record = {
            "seg_id": seg_id,
            "group_id": analysis["_meta"]["group_id"],
            "group_name": analysis["_meta"]["group_name"],
            "msg_count": analysis["_meta"]["msg_count"],
            "speaker_count": analysis["_meta"]["speaker_count"],
            "analysis": {
                "session_overview": analysis["session_overview"],
                "topics": analysis["topics"],
                "events": analysis["events"],
                "traits": analysis["traits"],
                "signals": analysis["signals"],
                "rels": analysis["rels"]
            },
            "raw_date": date_label
        }
        
        with open(l1_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
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
        seg_id = seg.get("seg_id", "")
        if seg_id:
            analyzed_ids.add(seg_id)
    
    checkpoint["analyzed_ids"] = sorted(list(analyzed_ids))
    checkpoint["last_updated"] = date_label
    checkpoint["last_run"] = int(time.time())
    
    with open(cp_path, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    return saved

def main():
    segments = load_segments(SEGMENT_FILE, start=0, count=50)
    
    if not segments:
        print("NO_SEGMENTS", file=sys.stderr)
        return
    
    print("Processing %d group chat segments..." % len(segments), file=sys.stderr)
    
    analyses = []
    for seg in segments:
        analysis = analyze_group_segment(seg)
        analyses.append(analysis)
    
    saved = save_group_results(segments, analyses)
    
    total_topics = sum(len(a["topics"]) for a in analyses if a)
    print("L1 saved: %d segments" % saved, file=sys.stderr)
    print("Total topics detected: %d" % total_topics, file=sys.stderr)
    
    for i, (seg, analysis) in enumerate(zip(segments, analyses)):
        if analysis is None:
            continue
        name = analysis["_meta"]["group_name"][:20]
        msgs = analysis["_meta"]["msg_count"]
        speakers = analysis["_meta"]["speaker_count"]
        overview = analysis["session_overview"]
        topics = analysis["topics"]
        print("[%d] %s: %d msgs, %d speakers, rounds=%d, topics=%s" % (
            i+1, name, msgs, speakers, overview["rounds"], topics
        ), file=sys.stderr)
    
    sys.stderr.flush()

if __name__ == "__main__":
    main()
