#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 run_batch.py 是否能正常运行"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test 1: Import all modules
try:
    import run_batch
    print("[OK] run_batch.py imports")
except Exception as e:
    print(f"[FAIL] run_batch import: {e}")

try:
    import extract_events
    print("[OK] extract_events imports")
except Exception as e:
    print(f"[FAIL] extract_events import: {e}")

try:
    import extract_signals
    print("[OK] extract_signals imports")
except Exception as e:
    print(f"[FAIL] extract_signals import: {e}")

try:
    import extract_traits
    print("[OK] extract_traits imports")
except Exception as e:
    print(f"[FAIL] extract_traits import: {e}")

try:
    import extract_post_type
    print("[OK] extract_post_type imports")
except Exception as e:
    print(f"[FAIL] extract_post_type import: {e}")

# Test 2: Check shared_api
try:
    import shared_api
    print("[OK] shared_api imports")
    if hasattr(shared_api, 'call_with_fallback'):
        print("[OK] call_with_fallback exists")
    else:
        print("[WARN] call_with_fallback not found in shared_api")
except Exception as e:
    print(f"[FAIL] shared_api import: {e}")

print("\n=== Import test done ===")
