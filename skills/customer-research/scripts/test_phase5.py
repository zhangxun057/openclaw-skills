# -*- coding: utf-8 -*-
"""
测试 Phase 5 客户画像关联功能
"""

import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)

from main import main

# 测试一个新客户（应该触发创建）
print("=" * 80)
print("测试 Phase 5 - 新客户创建")
print("=" * 80)

result = main("北京清格科技有限公司", use_qcc=True, enable_secondary=False, auto_phase5=True)

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
