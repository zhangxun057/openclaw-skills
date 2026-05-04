# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\44452\.openclaw\skills\customer-research\scripts')
from qcc_api import qcc_search_and_extract
import json

company = "华创云信数字技术股份有限公司"

# Phase 1: 886 搜索
result = qcc_search_and_extract(company, depth='basic')
print("=== 886 基础搜索 ===")
print(json.dumps(result, ensure_ascii=False, indent=2))

# 2003 KYC 深度尽调
print("\n=== 2003 KYC 深度尽调 ===")
result_deep = qcc_search_and_extract(company, depth='deep')
print(json.dumps(result_deep, ensure_ascii=False, indent=2))
