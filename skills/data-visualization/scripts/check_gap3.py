import json, os

# Check what fields are in the raw data
raw = os.path.expanduser('~/.openclaw/projects/moments-analysis/raw/20260419_205048.json')
with open(raw, 'r', encoding='utf-8') as f:
    data = json.load(f)

tl = data.get('timeline', [])
print('First entry full keys:', list(tl[0].keys()))
print()
# Show first 3 entries
for i, entry in enumerate(tl[:3]):
    print(f'Entry {i}:')
    print(f'  tid: {entry.get("tid")}')
    print(f'  id: {entry.get("id")}')
    print(f'  username: {entry.get("username")}')
    print(f'  nickname: {entry.get("nickname")}')
    print(f'  createTime: {entry.get("createTime")}')
    print(f'  contentDesc: {(entry.get("contentDesc") or "")[:60]}')
    print()

# Check checkpoint against id field
cp = os.path.expanduser('~/.openclaw/projects/moments-analysis/checkpoint.json')
with open(cp, 'r', encoding='utf-8') as f:
    cp_data = json.load(f)
analyzed_ids = set(cp_data.get('analyzed_ids', []))
print('Checkpoint sample IDs:', list(analyzed_ids)[:5])

# Check if any raw entry has id matching checkpoint
raw_ids_from_field = set(entry.get('id') for entry in tl if entry.get('id'))
print('Raw id field values sample:', list(raw_ids_from_field)[:5])
print('Overlap with checkpoint:', len(analyzed_ids & raw_ids_from_field))
