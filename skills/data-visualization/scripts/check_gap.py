import json, os

cp = os.path.expanduser('~/.openclaw/projects/moments-analysis/checkpoint.json')
with open(cp, 'r', encoding='utf-8') as f:
    data = json.load(f)

ids = data.get('analyzed_ids', [])
print('Total analyzed IDs:', len(ids))
print('First 5 IDs (oldest):', ids[-5:])
print('Last 5 IDs (newest):', ids[:5])
print('Last analyzed time:', data.get('last_analyzed_time', 'N/A'))
print('Last analyzed count:', data.get('last_analyzed_count', 'N/A'))
print()

# Now check what's in the latest raw data
raw = os.path.expanduser('~/.openclaw/projects/moments-analysis/raw/20260419_205048.json')
with open(raw, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)
    
raw_ids = [t.get('tid') for t in raw_data.get('timeline', [])]
print('Latest raw data:', len(raw_ids), 'entries')
print('First 5 raw IDs (newest):', raw_ids[:5])
print('Last 5 raw IDs (oldest):', raw_ids[-5:])

# Find gaps
analyzed_set = set(ids)
raw_set = set(raw_ids)
in_raw_not_analyzed = raw_set - analyzed_set
in_analyzed_not_raw = analyzed_set - raw_set
print('In raw but not analyzed:', len(in_raw_not_analyzed))
print('In analyzed but not raw:', len(in_analyzed_not_raw))
