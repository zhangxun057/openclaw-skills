import json
from pathlib import Path

date = '2026-04-25'
agent = 'main'
base = Path(f'C:/Users/44452/.openclaw/chat-logs/{agent}')

files = [
    '2026-04-25_2233331d.jsonl',
    '2026-04-25_7cf628d9.jsonl',
    '2026-04-25_c5beb18e.jsonl'
]

all_msgs = []
for fname in files:
    fpath = base / fname
    try:
        with open(fpath, 'rb') as fp:
            raw = fp.read()
        text = raw.decode('utf-8', errors='replace')
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                # Direct message format: {"time":"...", "role":"user", "text":"..."}
                if 'time' in obj and 'role' in obj and 'text' in obj:
                    all_msgs.append(obj)
            except Exception:
                pass
    except Exception as e:
        print(f'Error reading {fname}: {e}')

# sort by time
all_msgs.sort(key=lambda m: m.get('time',''))

user_msgs = [m for m in all_msgs if m.get('role') == 'user']
ai_msgs = [m for m in all_msgs if m.get('role') == 'assistant']
user_chars = sum(len(m.get('text','')) for m in user_msgs)

print(f'Total messages: {len(all_msgs)}')
print(f'User messages: {len(user_msgs)}, chars: ~{user_chars}')
print(f'AI messages: {len(ai_msgs)}')
if all_msgs:
    print(f'Time span: {all_msgs[0].get("time","")[11:16]} ~ {all_msgs[-1].get("time","")[11:16]}')

# Write to temp file for analysis
out_path = Path('C:/Users/44452/.openclaw/chat-logs/summaries/_temp_msgs.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    for m in all_msgs:
        role = m.get('role','?')
        text = m.get('text','')
        t = m.get('time','')
        f.write(f'=== [{t}] [{role}] ===\n{text}\n\n')

print(f'Wrote {len(all_msgs)} messages to {out_path}')
print('Done')