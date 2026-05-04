# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import subprocess
import os

script = r"C:\Users\44452\.openclaw\skills\wechat-moments-loader\scripts\loader.py"
output_dir = r"C:\Users\44452\.openclaw\agents\guaiguaixia\workspace\scratchpad"

result = subprocess.run(
    [sys.executable, script, "--start", "5h", "--output", output_dir],
    capture_output=True,
    text=True,
    timeout=120,
    encoding='utf-8',
    errors='replace'
)

print("=== STDOUT ===")
print(result.stdout)
print("\n=== STDERR ===")
print(result.stderr)
print(f"\n=== RETURN CODE: {result.returncode} ===")
