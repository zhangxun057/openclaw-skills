# -*- coding: utf-8 -*-
"""
企查查 API 调用方式完整示例
用于验证和演示每个接口的正确调用方法
"""

import requests
import hashlib
import time
import json

# ============================================================
# 凭证
# ============================================================
API_KEY = "56ffd2c150294cb4ad6fbe9fc21a62ab"
SECRET_KEY = "F6899B72B4E3EB76C00CA73C96E51D53"

# ============================================================
# Token 生成（每次请求都需要重新生成）
# ============================================================
def make_token():
    """
    生成认证 Token
    
    规则: MD5(API_KEY + Timespan + SECRET_KEY).upper()
    
    示例:
      API_KEY = "56ffd2c..."
      Timespan = "1745472883"  (当前时间戳, 10位)
      SECRET_KEY = "F6899B72..."
      
      拼接: "56ffd2c...1745472883F6899B72..."
      MD5 后转大写
    """
    timespan = str(int(time.time()))
    raw = f"{API_KEY}{timespan}{SECRET_KEY}"
    token = hashlib.md5(raw.encode('utf-8')).hexdigest().upper()
    return token, timespan


# ============================================================
# 接口 886 - 企业模糊搜索 (¥0.10/次)
# ============================================================
def call_886(search_key):
    """
    GET https://api.qichacha.com/FuzzySearch/GetList
    
    Headers:
      Token: xxx       (由 make_token 生成)
      Timespan: xxx    (由 make_token 生成)
    
    Query Params:
      key: API_KEY
      searchKey: 搜索关键词 (企业名称/人名/信用代码)
    
    返回:
      Status: "200" 表示成功
      Result: [{KeyNo, Name, CreditCode, StartDate, OperName, Status, No, Address}]
    """
    token, ts = make_token()
    url = "https://api.qichacha.com/FuzzySearch/GetList"
    params = {"key": API_KEY, "searchKey": search_key}
    headers = {"Token": token, "Timespan": ts}
    
    print(f"[886] GET {url}")
    print(f"  Params: key=***&searchKey={search_key}")
    print(f"  Headers: Token={token[:16]}..., Timespan={ts}")
    
    r = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"  HTTP {r.status_code}")
    
    if r.status_code != 200:
        print(f"  Response: {r.text[:500]}")
        return None
    
    data = r.json()
    print(f"  Status: {data.get('Status')}")
    print(f"  找到企业数: {len(data.get('Result', []))}")
    for c in data.get('Result', [])[:3]:
        print(f"    - {c.get('Name')} ({c.get('Status')})")
    return data


# ============================================================
# 接口 2001 - 企业身份核验 (¥1.00/次)
# ============================================================
def call_2001(exact_name):
    """
    GET https://api.qichacha.com/EnterpriseInfo/Verify
    
    Headers:
      Token: xxx
      Timespan: xxx
    
    Query Params:
      key: API_KEY
      searchKey: 企业全称 (必须是准确全称，建议先用886获取)
    
    返回:
      Status: "200" 表示成功
      Result.Data: {Name, OperName, RegistCapi, StartDate, Status, ...}
    """
    token, ts = make_token()
    url = "https://api.qichacha.com/EnterpriseInfo/Verify"
    params = {"key": API_KEY, "searchKey": exact_name}
    headers = {"Token": token, "Timespan": ts}
    
    print(f"\n[2001] GET {url}")
    print(f"  Params: key=***&searchKey={exact_name}")
    
    r = requests.get(url, params=params, headers=headers, timeout=15)
    print(f"  HTTP {r.status_code}")
    
    if r.status_code != 200:
        print(f"  Response: {r.text[:500]}")
        return None
    
    data = r.json()
    print(f"  Status: {data.get('Status')}")
    detail = data.get('Result', {}).get('Data', {})
    if detail:
        print(f"  企业: {detail.get('Name')}")
        print(f"  法人: {detail.get('OperName')}")
        print(f"  注册资本: {detail.get('RegistCapi')}")
    return data


# ============================================================
# 接口 2003 - KYC 深度尽调 (¥3.00/次)
# ============================================================
def call_2003(exact_name):
    """
    GET https://api.qichacha.com/CustomerDueDiligence/KYC
    
    Headers:
      Token: xxx
      Timespan: xxx
    
    Query Params:
      key: API_KEY
      searchKey: 企业全称
    
    返回:
      Status: "200" 表示成功
      Result.Data: {
        股东(PubPartnerList), 高管(PubEmployeeList), 
        对外投资(InvestmentList), 分支机构(BranchList),
        风险信息, 财务数据, ...
      }
    """
    token, ts = make_token()
    url = "https://api.qichacha.com/CustomerDueDiligence/KYC"
    params = {"key": API_KEY, "searchKey": exact_name}
    headers = {"Token": token, "Timespan": ts}
    
    print(f"\n[2003] GET {url}")
    print(f"  Params: key=***&searchKey={exact_name}")
    
    r = requests.get(url, params=params, headers=headers, timeout=15)
    print(f"  HTTP {r.status_code}")
    
    if r.status_code != 200:
        print(f"  Response: {r.text[:500]}")
        return None
    
    data = r.json()
    print(f"  Status: {data.get('Status')}")
    detail = data.get('Result', {}).get('Data', {})
    if detail:
        print(f"  企业: {detail.get('Name')}")
        print(f"  注册资本: {detail.get('RegistCapi')}")
        partners = detail.get('PubPartnerList', [])
        print(f"  股东数: {len(partners)}")
        for p in partners[:5]:
            print(f"    - {p.get('StockName')} {p.get('StockPercent')}")
    return data


# ============================================================
# 运行测试
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("企查查 API 调用测试")
    print("=" * 60)
    
    # Step 1: 886 搜索
    result = call_886("华创云信")
    
    # Step 2: 用搜索结果中的准确名称调 2003
    if result and result.get('Result'):
        exact_name = result['Result'][0]['Name']
        print(f"\n精确名称: {exact_name}")
        call_2003(exact_name)
    
    print("\n" + "=" * 60)
    print("测试完成")
