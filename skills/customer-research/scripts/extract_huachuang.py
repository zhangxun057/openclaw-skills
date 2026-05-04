# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'C:\Users\44452\.openclaw\skills\customer-research\scripts')
from qcc_api import qcc_search_and_extract

result = qcc_search_and_extract("华创云信数字技术股份有限公司", depth='deep')
data = result['data'].get('detail', result['data'].get('basic', {}))

# 提取关键信息并输出到文件
output = {
    "企业全称": data.get("Name"),
    "统一社会信用代码": data.get("CreditCode"),
    "法定代表人": data.get("OperName"),
    "经营状态": data.get("Status"),
    "成立日期": data.get("StartDate"),
    "注册资本": data.get("RegistCapi"),
    "实缴资本": data.get("RealCapi"),
    "企业类型": data.get("EconKind"),
    "行业": data.get("Industry", {}).get("Industry", "") + " > " + data.get("Industry", {}).get("SubIndustry", "") + " > " + data.get("Industry", {}).get("SmallCategory", ""),
    "员工规模": data.get("PersonScope"),
    "参保人数": data.get("InsuredCount"),
    "纳税等级": data.get("TaxpayerType"),
    "地址": data.get("Address"),
    "联系电话": data.get("ContactInfo", {}).get("Tel"),
    "邮箱": data.get("ContactInfo", {}).get("Email"),
    "股票代码": data.get("StockInfo", {}).get("StockNumber") if data.get("StockInfo") else None,
    "2024年营业收入": data.get("FinancialInformation", {}).get("Amount") if data.get("FinancialInformation") else None,
    "经营范围摘要": data.get("Scope", "")[:200],
    "曾用名": [item.get("Name") for item in data.get("OriginalName", [])],
    "集团": data.get("GroupInfo", {}).get("Name") if data.get("GroupInfo") else None,
    "标签": [tag.get("Name") for tag in data.get("TagList", [])],
}

# 股东
shareholders = data.get("PubPartnerList", [])
output["前十大股东"] = [{"名称": s.get("StockName"), "持股比例": s.get("StockPercent"), "持股数量": s.get("Amount")} for s in shareholders[:10]]

# 高管
employees = data.get("PubEmployeeList", [])
output["核心高管"] = [{"姓名": e.get("Name"), "职务": e.get("Job")} for e in employees]

# 对外投资（主要）
investments = data.get("InvestmentList", [])
output["对外投资"] = [{"企业名称": i.get("Name"), "持股比例": i.get("FundedRatio"), "注册资本": i.get("ShouldCapi"), "行业": i.get("Industry", {}).get("SmallCategory", ""), "状态": i.get("Status")} for i in investments[:15]]

# 分支机构
branches = data.get("BranchList", [])
output["分支机构"] = [{"名称": b.get("Name"), "负责人": b.get("OperName"), "状态": b.get("Status")} for b in branches]

with open(r'C:\Users\44452\.openclaw\skills\customer-research\scripts\huachuang_result.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("done")
