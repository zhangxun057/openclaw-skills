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
    with open(fpath, 'r', encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            if not line: continue
            obj = json.loads(line)
            if obj.get('type') == 'message':
                all_msgs.append(obj['message'])

# sort by time
all_msgs.sort(key=lambda m: m.get('time',''))

user_msgs = [m for m in all_msgs if m.get('role') == 'user']
ai_msgs = [m for m in all_msgs if m.get('role') == 'assistant']

user_chars = sum(len(m.get('text','').replace('\n',' ')) for m in user_msgs)

print(f'Total messages: {len(all_msgs)}')
print(f'User messages: {len(user_msgs)}, chars: ~{user_chars}')
print(f'AI messages: {len(ai_msgs)}')
if all_msgs:
    print(f'Time span: {all_msgs[0].get("time","")[11:16]} ~ {all_msgs[-1].get("time","")[11:16]}')
print()

for i, m in enumerate(all_msgs):
    role = m.get('role','?')
    text = m.get('text','')[:120].replace('\n',' ')
    t = m.get('time','')
    print(f'[{t}] [{role}] {text}')