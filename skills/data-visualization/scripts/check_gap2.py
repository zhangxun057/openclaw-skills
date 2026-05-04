import json, os, glob

cp = os.path.expanduser('~/.openclaw/projects/moments-analysis/checkpoint.json')
with open(cp, 'r', encoding='utf-8') as f:
    data = json.load(f)

analyzed_ids = set(data.get('analyzed_ids', []))
print('Analyzed IDs in checkpoint:', len(analyzed_ids))

# Check all raw JSON files
raw_dir = os.path.expanduser('~/.openclaw/projects/moments-analysis/raw')
for jf in sorted(glob.glob(os.path.join(raw_dir, '*.json'))):
    basename = os.path.basename(jf)
    if basename == 'status.json':
        continue
    with open(jf, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    timeline = raw.get('timeline', [])
    raw_ids = set(t.get('tid') for t in timeline)
    overlap = analyzed_ids & raw_ids
    in_raw_not_analyzed = raw_ids - analyzed_ids
    print(f'{basename}: {len(timeline)} entries, overlap={len(overlap)}, not_analyzed={len(in_raw_not_analyzed)}')
    if timeline:
        ct = timeline[0].get('createTime', 'N/A')
        cl = timeline[-1].get('createTime', 'N/A')
        print(f'  Time range: {cl} -> {ct}')
        print(f'  ID range: {timeline[-1].get("tid")} -> {timeline[0].get("tid")}')
