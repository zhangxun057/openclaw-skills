# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import json
import os

WEFLOW_API = "http://127.0.0.1:5032/api/v1"
OUTPUT_DIR = r"C:\Users\44452\.openclaw\agents\guaiguaixia\workspace\scratchpad\moments_test"

os.makedirs(OUTPUT_DIR, exist_ok=True)

log_lines = []

def log(msg):
    log_lines.append(msg)
    print(msg)

log("Step 1: Check WeFlow service...")
try:
    base = WEFLOW_API.replace("/api/v1", "")
    r = requests.get(f"{base}/health", timeout=5)
    log(f"  Status: {r.status_code}")
except Exception as e:
    log(f"  WeFlow unavailable: {e}")
    sys.exit(1)

log("\nStep 2: Get friend list...")
r = requests.get(f"{WEFLOW_API}/sessions", params={"limit": 5})
data = r.json()
sessions = data.get("sessions", [])
individuals = [s for s in sessions if "@chatroom" not in s.get("username", "")]
log(f"  Total: {len(sessions)} sessions, {len(individuals)} individual friends")
for s in individuals[:3]:
    name = s.get("displayName", "?")
    wxid = s.get("username", "?")
    log(f"    - {name} ({wxid})")

log("\nStep 3: Try /sns/export to get timeline...")
payload = {
    "outputDir": OUTPUT_DIR,
    "format": "html",
    "exportMedia": False,
    "exportImages": False,
    "exportLivePhotos": False,
    "exportVideos": False,
    "start": "20260410",
    "end": "20260411"
}
try:
    r = requests.post(f"{WEFLOW_API}/sns/export", json=payload, timeout=120)
    log(f"  Response status: {r.status_code}")
    resp_data = r.json()
    log(f"  Response keys: {list(resp_data.keys())}")
    
    timeline = resp_data.get("timeline") or resp_data.get("data", {}).get("timeline")
    if timeline and isinstance(timeline, list):
        log(f"  Got timeline: {len(timeline)} posts")
        
        output_file = os.path.join(OUTPUT_DIR, "test_export.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "success": True,
                "count": len(timeline),
                "timeline": timeline
            }, f, ensure_ascii=False, indent=2)
        log(f"  Saved to: {output_file}")
        
        if timeline:
            first = timeline[0]
            log(f"\n  First post:")
            log(f"    tid: {first.get('tid', 'N/A')}")
            log(f"    username: {first.get('username', 'N/A')}")
            log(f"    nickname: {first.get('nickname', 'N/A')}")
            log(f"    createTime: {first.get('createTime', 'N/A')}")
            content = (first.get('contentDesc', '') or '')[:50]
            log(f"    content: {content}")
            log(f"    media: {len(first.get('media', []))}")
            log(f"    likes: {len(first.get('likes', []))}")
            log(f"    comments: {len(first.get('comments', []))}")
    else:
        log(f"  No timeline in response. Trying /sns/timeline per friend...")
        
        all_posts = []
        for s in individuals[:10]:
            wxid = s.get("username", "")
            if not wxid:
                continue
            try:
                r2 = requests.get(f"{WEFLOW_API}/sns/timeline", params={"usernames": wxid}, timeout=15)
                tl_data = r2.json()
                posts = tl_data.get("data", {}).get("timeline", [])
                all_posts.extend(posts)
            except Exception:
                pass
        
        log(f"  Got {len(all_posts)} posts from 10 friends")
        if all_posts:
            first = all_posts[0]
            log(f"    tid: {first.get('tid', 'N/A')}")
            log(f"    username: {first.get('username', 'N/A')}")
            log(f"    nickname: {first.get('nickname', 'N/A')}")
            log(f"    createTime: {first.get('createTime', 'N/A')}")
            content = (first.get('contentDesc', '') or '')[:50]
            log(f"    content: {content}")
            
            output_file = os.path.join(OUTPUT_DIR, "test_timeline.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "success": True,
                    "count": len(all_posts),
                    "timeline": all_posts
                }, f, ensure_ascii=False, indent=2)
            log(f"  Saved to: {output_file}")

except Exception as e:
    log(f"  Error: {e}")

log("\nDone!")

with open(os.path.join(OUTPUT_DIR, "test_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
