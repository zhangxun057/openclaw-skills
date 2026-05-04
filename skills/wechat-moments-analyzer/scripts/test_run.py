#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""小批量测试 run_batch"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_batch

input_file = r"C:\Users\44452\.openclaw\projects\moments-analysis\raw\20260423_220920.json"

print(f"\n=== 测试 run_batch ===")
print(f"输入文件: {input_file}")

try:
    result = run_batch.run_full_analysis(
        posts_file=input_file,
        batch_size=10,
        output_file=r"C:\Users\44452\.openclaw\projects\moments-analysis\raw\20260423_v2_test.json",
        max_workers=5,
        max_concurrent_batches=10
    )
    print(f"\n[OK] 分析完成，返回 {len(result)} 条记录")
except Exception as e:
    print(f"\n[FAIL] 运行出错: {e}")
    import traceback
    traceback.print_exc()
