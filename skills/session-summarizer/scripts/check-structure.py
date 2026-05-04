import json
from pathlib import Path

# Read first few lines of largest file to understand structure
f = Path(r"C:\Users\44452\.openclaw\chat-logs\main\2026-04-22_a86ef80e.jsonl")
lines = f.read_text(encoding="utf-8").strip().split('\n')[:3]
for i, line in enumerate(lines):
    obj = json.loads(line)
    print(f"=== Line {i} ===")
    print(f"type: {obj.get('type')}")
    if obj.get('type') == 'message':
        m = obj['message']
        print(f"role: {m.get('role')}, time: {m.get('time')}")
        print(f"text (first 300): {m.get('text','')[:300]}")