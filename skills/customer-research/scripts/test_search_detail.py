# -*- coding: utf-8 -*-
"""
查看 Serper 搜索结果的详细信息
"""

import sys
import os
import json

# 设置编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)

from search import search_with_serper

company_name = "北京清格科技有限公司"

print("=" * 80)
print(f"搜索：{company_name}")
print("=" * 80)

queries = [
    f"{company_name} 上市 纳税 规模 员工",
    f"{company_name} 官网 主营业务 产品",
]

for query in queries:
    print(f"\n【搜索】{query}")
    print("-" * 80)
    
    result = search_with_serper(query)
    
    for i, item in enumerate(result.get('results', []), 1):
        print(f"\n{i}. {item.get('title', 'N/A')}")
        print(f"   链接：{item.get('link', 'N/A')}")
        print(f"   摘要：{item.get('snippet', 'N/A')}")
        if item.get('date'):
            print(f"   日期：{item.get('date')}")
