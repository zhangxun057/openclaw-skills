# -*- coding: utf-8 -*-
"""
测试企查查 2003 接口（客户身份识别 KYC）
"""

import sys
import os
import json

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)

from qcc_api import qcc_search_and_extract

COMPANY_NAME = "北京清格科技有限公司"

print("=" * 80)
print(f"测试 2003 接口（客户身份识别 KYC）")
print(f"目标企业：{COMPANY_NAME}")
print(f"成本：¥3.00")
print("=" * 80)

result = qcc_search_and_extract(COMPANY_NAME, depth='deep')

print(f"\n接口调用结果：")
print(f"  - 使用接口：{result.get('interfaces_used', [])}")
print(f"  - 总成本：¥{result.get('total_cost', 0):.2f}")

if result.get('error'):
    print(f"\n❌ 错误：{result['error']}")
else:
    print(f"\n✅ 调用成功！")
    
    # 显示数据结构
    if result.get('data'):
        print(f"\n返回数据结构：")
        if result['data'].get('basic'):
            print(f"  - basic: {len(result['data']['basic'])} 个字段")
        if result['data'].get('detail'):
            detail = result['data']['detail']
            print(f"  - detail: {len(detail)} 个字段")
            print(f"\n关键字段：")
            for key in ['Name', 'RegistCapi', 'StartDate', 'OperName', 'Status']:
                if key in detail:
                    print(f"    - {key}: {detail[key]}")
    
    # 保存完整结果
    output_file = os.path.join(script_dir, "qcc_2003_result.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n📁 完整结果已保存：{output_file}")

print("=" * 80)
