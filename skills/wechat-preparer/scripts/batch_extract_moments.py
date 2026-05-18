#!/usr/bin/env python3
"""
Batch moments extraction helper.
Reads posts from a specific date file, applies Agent analysis, and saves to L1/L2.
"""
import json
import os
import sys
import time

def main():
    base = os.path.join(os.path.expanduser("~"), ".openclaw", "projects")
    
    # Read command line args
    if len(sys.argv) < 2:
        print("Usage: batch_extract_moments.py <YYYYMMDD>", file=sys.stderr)
        sys.exit(1)
    
    date_str = sys.argv[1]
    raw_path = os.path.join(base, "raw", "moments-analysis", f"{date_str}.json")
    
    if not os.path.exists(raw_path):
        print(f"NO_RAW: {raw_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    posts = data.get("posts", [])
    if not posts:
        print("NO_POSTS", file=sys.stderr)
        sys.exit(1)
    
    # Add _post_id if missing
    for p in posts:
        if "_post_id" not in p:
            pid = p.get("id") or p.get("tid")
            if pid:
                p["_post_id"] = str(pid)
            else:
                p["_post_id"] = "%s_%s" % (p.get("username",""), p.get("createTime",""))
    
    # Output posts as JSON for Agent to read
    sys.stdout.reconfigure(encoding='utf-8')
    json.dump(posts, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write('\n')
    
    sys.stderr.write(f"BATCH_READY: {len(posts)} posts from {date_str}\n")
    sys.stderr.flush()

if __name__ == "__main__":
    main()
