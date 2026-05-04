#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

fpath = r"C:\Users\44452\.openclaw\projects\moments-analysis\raw\20260423_v2_test.json"
print(f"File size: {os.path.getsize(fpath)} bytes")

with open(fpath, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Type: {type(data).__name__}")
if isinstance(data, list):
    print(f"Record count: {len(data)}")
    if data:
        r = data[0]
        print(f"\nFirst record keys: {list(r.keys())}")
        print(f"Has rels: {'rels' in r}")
        print(f"Has image_trigger: {'image_trigger' in r}")
        print(f"Has post_id: {'post_id' in r}")
        print(f"Sample rels: {r.get('rels', 'MISSING')}")
        print(f"Sample image_trigger: {r.get('image_trigger', 'MISSING')}")
        print(f"\nFirst record:")
        for k, v in r.items():
            print(f"  {k}: {str(v)[:80]}")
elif isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
