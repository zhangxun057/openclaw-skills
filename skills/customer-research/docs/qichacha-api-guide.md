# 企查查 API 调用指南

**更新时间**: 2026-04-24  
**状态**: ✅ 已验证可用

---

## 一、凭证

| 名称 | 值 |
|------|-----|
| API Key | `56ffd2c150294cb4ad6fbe9fc21a62ab` |
| Secret Key | `F6899B72B4E3EB76C00CA73C96E51D53` |

---

## 二、认证机制（每次请求都必须）

每次调用 API 需要在 **Headers** 中携带 Token 和 Timespan：

```
Token = MD5(API_KEY + Timespan + SECRET_KEY).upper()
Timespan = 当前时间戳（秒，10位整数）
```

### 生成示例（Python）

```python
import hashlib
import time

api_key = "56ffd2c150294cb4ad6fbe9fc21a62ab"
secret_key = "F6899B72B4E3EB76C00CA73C96E51D53"

timespan = str(int(time.time()))  # e.g. "1745472883"
raw = f"{api_key}{timespan}{secret_key}"
token = hashlib.md5(raw.encode()).hexdigest().upper()
```

### 生成示例（curl）

```bash
# Linux/Mac
TIMESPAN=$(date +%s)
TOKEN=$(echo -n "56ffd2c150294cb4ad6fbe9fc21a62ab${TIMESPAN}F6899B72B4E3EB76C00CA73C96E51D53" | md5sum | awk '{print toupper($1)}')
```

```powershell
# Windows PowerShell
$TIMESPAN = [int](Get-Date -UFormat %s)
$RAW = "56ffd2c150294cb4ad6fbe9fc21a62ab${TIMESPAN}F6899B72B4E3EB76C00CA73C96E51D53"
$TOKEN = ([System.BitConverter]::ToString([System.Security.Cryptography.MD5]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($RAW))) -replace '-','').ToUpper()
```

---

## 三、接口详情

### 接口 886 — 企业模糊搜索（¥0.10/次）

**用途**: 搜索企业，确认是否存在，获取准确全称

**请求**:
```
GET https://api.qichacha.com/FuzzySearch/GetList
```

**Headers**:
```
Token: <生成的Token>
Timespan: <时间戳>
```

**Query 参数**:
| 参数 | 必填 | 说明 |
|------|------|------|
| key | ✅ | API Key |
| searchKey | ✅ | 搜索关键词（企业名/人名/信用代码） |

**curl 示例**:
```bash
TIMESPAN=$(date +%s)
TOKEN=$(echo -n "56ffd2c150294cb4ad6fbe9fc21a62ab${TIMESPAN}F6899B72B4E3EB76C00CA73C96E51D53" | md5sum | awk '{print toupper($1)}')

curl -s "https://api.qichacha.com/FuzzySearch/GetList?key=56ffd2c150294cb4ad6fbe9fc21a62ab&searchKey=华创云信" \
  -H "Token: $TOKEN" \
  -H "Timespan: $TIMESPAN"
```

**返回**:
```json
{
  "Status": "200",
  "Message": "成功",
  "Paging": {...},
  "Result": [
    {
      "KeyNo": "fhr5mys5...",
      "Name": "华创云信数字技术股份有限公司",
      "CreditCode": "91130605700838787Q",
      "StartDate": "1998-07-21",
      "OperName": "陶永泽",
      "Status": "存续",
      "No": "110102026476139",
      "Address": "北京市西城区锦什坊街26号楼3层301-2"
    }
  ]
}
```

---

### 接口 2001 — 企业身份核验（¥1.00/次）

**用途**: 获取详细工商信息（注册资本、员工规模、联系方式等）

**请求**:
```
GET https://api.qichacha.com/EnterpriseInfo/Verify
```

**Headers**: 同上

**Query 参数**:
| 参数 | 必填 | 说明 |
|------|------|------|
| key | ✅ | API Key |
| searchKey | ✅ | **企业全称**（建议用886返回的准确名称） |

**curl 示例**:
```bash
TIMESPAN=$(date +%s)
TOKEN=$(echo -n "56ffd2c150294cb4ad6fbe9fc21a62ab${TIMESPAN}F6899B72B4E3EB76C00CA73C96E51D53" | md5sum | awk '{print toupper($1)}')

curl -s "https://api.qichacha.com/EnterpriseInfo/Verify?key=56ffd2c150294cb4ad6fbe9fc21a62ab&searchKey=华创云信数字技术股份有限公司" \
  -H "Token: $TOKEN" \
  -H "Timespan: $TIMESPAN"
```

**返回**:
```json
{
  "Status": "200",
  "Result": {
    "Data": {
      "Name": "华创云信数字技术股份有限公司",
      "OperName": "陶永泽",
      "RegistCapi": "221354.2477万元",
      "StartDate": "1998-07-21",
      "Status": "存续",
      "PersonScope": "少于50人",
      "ContactInfo": {"Tel": "010-83063199"}
    }
  }
}
```

---

### 接口 2003 — KYC 深度尽调（¥3.00/次）⭐

**用途**: 获取股东、高管、对外投资、风险等完整信息

**请求**:
```
GET https://api.qichacha.com/CustomerDueDiligence/KYC
```

**Headers**: 同上

**Query 参数**:
| 参数 | 必填 | 说明 |
|------|------|------|
| key | ✅ | API Key |
| searchKey | ✅ | **企业全称** |

**curl 示例**:
```bash
TIMESPAN=$(date +%s)
TOKEN=$(echo -n "56ffd2c150294cb4ad6fbe9fc21a62ab${TIMESPAN}F6899B72B4E3EB76C00CA73C96E51D53" | md5sum | awk '{print toupper($1)}')

curl -s "https://api.qichacha.com/CustomerDueDiligence/KYC?key=56ffd2c150294cb4ad6fbe9fc21a62ab&searchKey=华创云信数字技术股份有限公司" \
  -H "Token: $TOKEN" \
  -H "Timespan: $TIMESPAN"
```

**返回字段** (Result.Data 内):
| 字段 | 说明 |
|------|------|
| PubPartnerList | 前十大股东 |
| PubEmployeeList | 核心高管 |
| InvestmentList | 对外投资 |
| BranchList | 分支机构 |
| TagList | 企业标签 |
| FinancialInformation | 营收等财务数据 |
| StockInfo | 股票信息 |
| OriginalName | 曾用名 |
| ChangeList | 工商变更记录 |

---

## 四、Python 完整调用代码

```python
import requests, hashlib, time, json

API_KEY = "56ffd2c150294cb4ad6fbe9fc21a62ab"
SECRET_KEY = "F6899B72B4E3EB76C00CA73C96E51D53"

def qcc_call(interface, search_key):
    """通用调用封装"""
    endpoints = {
        "886":  "https://api.qichacha.com/FuzzySearch/GetList",
        "2001": "https://api.qichacha.com/EnterpriseInfo/Verify",
        "2003": "https://api.qichacha.com/CustomerDueDiligence/KYC",
    }
    
    # 生成认证
    ts = str(int(time.time()))
    token = hashlib.md5(f"{API_KEY}{ts}{SECRET_KEY}".encode()).hexdigest().upper()
    
    # 发请求
    r = requests.get(
        endpoints[interface],
        params={"key": API_KEY, "searchKey": search_key},
        headers={"Token": token, "Timespan": ts},
        timeout=15
    )
    r.raise_for_status()
    return r.json()

# 用法
result = qcc_call("886", "华创云信")           # 搜索
result = qcc_call("2001", "华创云信数字技术股份有限公司")  # 核验
result = qcc_call("2003", "华创云信数字技术股份有限公司")  # 深度尽调
```

---

## 五、常见问题

### 404 错误排查

| 原因 | 解决 |
|------|------|
| URL 拼写错误 | 确认完整路径如 `/FuzzySearch/GetList` |
| 缺少 Headers | 必须带 `Token` 和 `Timespan` 两个 header |
| Token 过期 | Token 每次请求需重新生成，不能复用 |
| searchKey 编码 | URL 中中文需要 UTF-8 编码 |
| key 参数遗漏 | key 必须在 Query Params 中，不能放 header |

### 2001/2003 返回空

- searchKey 必须是**企业全称**，不能是简称
- 建议先调 886 获取准确名称，再用返回的 `Name` 字段调 2001/2003

---

## 六、成本汇总

| 接口 | 单价 | 用途 |
|------|------|------|
| 886 | ¥0.10 | 搜索确认 |
| 2001 | ¥1.00 | 详细工商 |
| 2003 | ¥3.00 | 深度尽调 |
| **完整流程** | **¥3.10** | 886 + 2003 |
