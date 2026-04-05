# -*- coding: utf-8 -*-
import sys
import os
import json

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)

from qcc_api import qcc_search_and_extract

result = qcc_search_and_extract("北京清格科技有限公司", depth='basic')

print("企查查返回结果：")
print(json.dumps(result, ensure_ascii=False, indent=2))
