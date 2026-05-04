# -*- coding: utf-8 -*-
"""
run_scan.py - 包装扫描+写文件两步流程
"""
import subprocess
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent
OUTPUT_FILE = SKILL_DIR / "scan_result.json"

if __name__ == "__main__":
    # 确保 stdout 可以输出 emoji
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    
    # Step 1: 运行 health_scan
    r1 = subprocess.run(
        [sys.executable, str(SKILL_DIR / "health_scan.py"), "--days", "2", "--date", "2026-04-20"],
        capture_output=True, encoding="utf-8", errors="replace"
    )
    
    if r1.returncode != 0:
        print("health_scan 失败")
        print(r1.stderr[:500] if r1.stderr else "")
        sys.exit(1)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(r1.stdout)
    
    print("[Step 1 OK] health_scan done")
    
    # Step 2: 运行 write_evolution
    r2 = subprocess.run(
        [sys.executable, str(SKILL_DIR / "write_evolution.py"), "--date", "2026-04-20", "--input", str(OUTPUT_FILE)],
        capture_output=True, encoding="utf-8", errors="replace"
    )
    
    if r2.returncode != 0:
        print("write_evolution 失败")
        print(r2.stderr[:500] if r2.stderr else "")
        sys.exit(1)
    
    print("[Step 2 OK] write_evolution done")
    # 只打印纯文字部分，避免 emoji 编码错误
    lines = [l for l in r2.stdout.split('\n') if l and not any('\ufffd' in c for c in l)]
    for l in lines[:10]:
        print(l)