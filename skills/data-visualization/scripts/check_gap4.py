import json, os

# Check overlap between checkpoint (id field) and raw data (id field)
cp = os.path.expanduser('~/.openclaw/projects/moments-analysis/checkpoint.json')
with open(cp, 'r', encoding='utf-8') as f:
    cp_data = json.load(f)
analyzed_ids = set(cp_data.get('analyzed_ids', []))

raw = os.path.expanduser('~/.openclaw/projects/moments-analysis/raw/20260419_205048.json')
with open(raw, 'r', encoding='utf-8') as f:
    data = json.load(f)
tl = data.get('timeline', [])

raw_id_set = set(entry.get('id') for entry in tl if entry.get('id'))
overlap = analyzed_ids & raw_id_set
not_analyzed = raw_id_set - analyzed_ids

print('Checkpoint IDs:', len(analyzed_ids))
print('Raw data entries:', len(tl))
print('Raw id field values:', len(raw_id_set))
print('Overlap (already analyzed):', len(overlap))
print('NOT analyzed in raw:', len(not_analyzed))
print()

# Time analysis
import datetime
times = [e.get('createTime', 0) for e in tl if e.get('createTime')]
times.sort()
if times:
    oldest = datetime.datetime.fromtimestamp(times[0])
    newest = datetime.datetime.fromtimestamp(times[-1])
    print(f'Raw data time range: {oldest} -> {newest}')
    print(f'Span: {(newest - oldest).total_seconds() / 3600:.1f} hours')

# Check the old data file too
old = os.path.expanduser('~/.openclaw/projects/moments-analysis/raw/20260413_000000.json')
with open(old, 'r', encoding='utf-8') as f:
    old_data = json.load(f)
old_tl = old_data.get('timeline', [])
old_id_set = set(entry.get('id') for entry in old_tl if entry.get('id'))
old_overlap = analyzed_ids & old_id_set
old_not = old_id_set - analyzed_ids
print(f'\nOld data (20260413): {len(old_tl)} entries, overlap={len(old_overlap)}, not_analyzed={len(old_not)}')

# Check the other files too
for fname in ['20260419_232751.json', '20260419_233033.json']:
    path = os.path.expanduser(f'~/.openclaw/projects/moments-analysis/raw/{fname}')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
        tl2 = d.get('timeline', [])
        id_set2 = set(entry.get('id') for entry in tl2 if entry.get('id'))
        ov = analyzed_ids & id_set2
        print(f'{fname}: {len(tl2)} entries, overlap={len(ov)}, not_analyzed={len(id_set2 - analyzed_ids)}')
