import json
from pathlib import Path

base = Path('C:/Users/44452/.openclaw/chat-logs/main')
fpath = base / '2026-04-25_2233331d.jsonl'

with open(fpath, 'rb') as fp:
    raw = fp.read()

text = raw.decode('utf-8', errors='replace')
lines = text.split('\n')

print(f'Total lines: {len(lines)}')
for i, line in enumerate(lines):
    line = line.strip()
    if not line: continue
    try:
        obj = json.loads(line)
        print(f'Line {i}: type={obj.get("type","?")}, keys={list(obj.keys())}')
        if obj.get('type') == 'message':
            msg = obj['message']
            print(f'  -> message role={msg.get("role")}, text_len={len(msg.get("text",""))}')
    except Exception as e:
        print(f'Line {i}: JSON parse error: {e}, raw: {line[:100]}')