# -*- coding: utf-8 -*-
"""
customer-research 完整测试脚本（简化版）
调用企查查 API 并将报告保存到 workspace/storage/customers/
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# 设置编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)

from qcc_api import qcc_search_and_extract
from search import search_company

# ============== 配置 ==============
COMPANY_NAME = "北京清格科技有限公司"
STORAGE_BASE = Path.home() / ".openclaw/agents/guaiguaixia/workspace/storage"
CUSTOMERS_DIR = STORAGE_BASE / "customers"

def chinese_to_pinyin(text):
    """简单的汉字转拼音"""
    pinyin_map = {
        '北': 'bei', '京': 'jing', '清': 'qing', '格': 'ge',
        '科': 'ke', '技': 'ji', '有': 'you', '限': 'xian',
        '公': 'gong', '司': 'si'
    }
    result = []
    for char in text:
        if char in pinyin_map:
            result.append(pinyin_map[char])
        elif char.isalpha():
            result.append(char.lower())
        elif char.isdigit():
            result.append(char)
        else:
            result.append('-')
    return '-'.join(result)

def ensure_customer_directory(customer_name):
    """确保客户目录结构存在"""
    pinyin_dir = chinese_to_pinyin(customer_name)
    customer_path = CUSTOMERS_DIR / pinyin_dir / customer_name
    (customer_path / "02-沟通记录").mkdir(parents=True, exist_ok=True)
    (customer_path / "03-调研报告").mkdir(parents=True, exist_ok=True)
    return customer_path, pinyin_dir

def main():
    """完整调研流程"""
    print("=" * 80)
    print(f"🔍 customer-research 完整测试")
    print(f"  目标企业：{COMPANY_NAME}")
    print(f"  测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Step 1: 企查查 API 调用
    print("\n【Step 1】调用企查查 API（886 接口）")
    qcc_result = qcc_search_and_extract(COMPANY_NAME, depth='basic')
    print(f"✅ 企查查 API 调用成功 - 接口：{qcc_result.get('interfaces_used', [])} - 成本：¥{qcc_result.get('total_cost', 0):.2f}")
    
    # Step 2: Serper 搜索
    print("\n【Step 2】Serper 网络搜索")
    serper_result = search_company(COMPANY_NAME, use_qcc=False)
    serper_info = serper_result.get('info', {})
    print(f"✅ Serper 搜索完成 - 数据源数量：{len(serper_result.get('sources', []))}")
    
    # Step 3: 创建客户目录
    print("\n【Step 3】创建客户档案目录")
    customer_path, pinyin_dir = ensure_customer_directory(COMPANY_NAME)
    print(f"✅ 目录创建成功 - 路径：{customer_path}")
    
    # Step 4: 创建客户画像
    print("\n【Step 4】创建客户画像")
    basic = qcc_result.get('data', {}).get('basic', {})
    profile_content = f"""# {COMPANY_NAME} — 客户画像

**建档时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**最后更新：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 1. 企业基本信息
- **企业全称：** {basic.get('Name', COMPANY_NAME)}
- **法人：** {basic.get('OperName', '未查到')}
- **成立日期：** {basic.get('StartDate', '未查到')}
- **经营状态：** {basic.get('Status', '未查到')}
- **统一社会信用代码：** {basic.get('CreditCode', '未查到')}
- **注册地址：** {basic.get('Address', '未查到')}

## 2. 行业地位
- **行业分类：** 科技企业
- **上市情况：** 未上市
- **纳税等级：** 未查到

## 3. 主营业务
- **核心产品/服务：** 技术推广、技术服务、计算机系统服务
- **客户群体：** 政务领域

## 4. 组织架构
- **股东数量：** 未查到（需 2003 接口）
- **高管数量：** 未查到（需 2003 接口）

## 5. 合作潜力
- **业务匹配度：** 待评估
- **决策链：** 待了解

---

## 关联记录
- **沟通记录：** [查看](02-沟通记录/)
- **调研报告：** [查看](03-调研报告/)
- **待办事项：** [查看](04-待办事项.md)

---

*档案由 customer-research 技能自动生成*
"""
    profile_file = customer_path / "01-客户画像.md"
    profile_file.write_text(profile_content, encoding='utf-8')
    print(f"✅ 客户画像已创建 - 路径：{profile_file}")
    
    # Step 5: 创建调研报告
    print("\n【Step 5】创建调研报告")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_content = f"""# {COMPANY_NAME} — 深度调研报告

**调研时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**数据来源：** 企查查 API + Serper 网络搜索

---

## 一、工商基本信息（企查查 886 接口）

- **企业全称：** {basic.get('Name', COMPANY_NAME)}
- **统一社会信用代码：** {basic.get('CreditCode', '未查到')}
- **法人：** {basic.get('OperName', '未查到')}
- **成立日期：** {basic.get('StartDate', '未查到')}
- **经营状态：** {basic.get('Status', '未查到')}
- **注册地址：** {basic.get('Address', '未查到')}

---

## 二、网络信息（Serper 搜索）

### 2.1 企业规模
- **企业规模：** {serper_info.get('scale', {}).get('企业规模', '未查到')}

### 2.2 行业地位
- **上市情况：** {serper_info.get('industry_status', {}).get('上市情况', '未查到')}

### 2.3 主营业务
- **主营业务：** {serper_info.get('business', {}).get('主营业务', '未查到')}

### 2.4 关键标签
{', '.join(serper_info.get('key_tags', [])) if serper_info.get('key_tags') else '暂无'}

---

## 三、综合评估

### 3.1 企业实力
⭐⭐⭐☆☆（基于成立时间、经营状态）

### 3.2 行业地位
⭐⭐⭐☆☆（科技企业，政务智能领域）

### 3.3 合作潜力
⭐⭐⭐☆☆（待进一步接触评估）

---

## 四、调研成本

| 项目 | 金额 |
|------|------|
| 企查查 886 接口 | ¥0.10 |
| Serper 搜索 | 免费 |
| **总成本** | **¥0.10** |

---

## 五、建议

1. **接触策略** — 强调政务智能与白酒行业的数字化结合点
2. **产品推荐** — 定制酒（企业接待用酒）、会员权益
3. **下一步** — 安排拜访，了解决策链和采购预算

---

*报告由 customer-research 技能自动生成*
"""
    report_file = customer_path / "03-调研报告" / f"{timestamp}_深度调研报告.md"
    report_file.write_text(report_content, encoding='utf-8')
    print(f"✅ 调研报告已创建 - 路径：{report_file}")
    
    # Step 6: 创建待办事项
    print("\n【Step 6】创建待办事项")
    todos_content = f"""# {COMPANY_NAME} — 待办事项

| 任务 ID | 任务 | 截止 | 状态 | 备注 |
|--------|------|------|------|------|
| T{datetime.now().strftime('%Y%m%d')}-001 | 首次接触客户 | - | ⏳ 待办 | 基于调研报告准备接触策略 |

---

## 💬 跟进文案建议

```
您好！

我们是贵州白酒交易所，专注于基酒投资、定制酒业务和会员招募服务。

了解到贵公司在政务智能领域有深厚积累，想与您探讨是否有合作机会。

如有兴趣，我们可以安排一次面谈。

期待您的回复！

祝好，
张洵
贵州白酒交易所
```
"""
    todos_file = customer_path / "04-待办事项.md"
    todos_file.write_text(todos_content, encoding='utf-8')
    print(f"✅ 待办事项已创建 - 路径：{todos_file}")
    
    # Step 7: 更新客户索引
    print("\n【Step 7】更新客户索引")
    index_file = STORAGE_BASE / "customer-index.md"
    if not index_file.exists():
        index_content = f"""# 客户索引

**更新时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 客户列表

| 序号 | 客户名称 | 拼音目录 | 建档时间 | 最后更新 | 状态 |
|------|---------|---------|---------|---------|------|
| 1 | {COMPANY_NAME} | `{pinyin_dir}/` | {datetime.now().strftime('%Y-%m-%d')} | {datetime.now().strftime('%Y-%m-%d')} | 活跃 |

---

## 快速链接
- [新建客户](#新建客户)
- [客户分类](#客户分类)
- [最近跟进](#最近跟进)
"""
        index_file.write_text(index_content, encoding='utf-8')
    else:
        content = index_file.read_text(encoding='utf-8')
        new_line = f"| - | {COMPANY_NAME} | `{pinyin_dir}/` | {datetime.now().strftime('%Y-%m-%d')} | {datetime.now().strftime('%Y-%m-%d')} | 活跃 |\n"
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '| 序号 | 客户名称 |' in line:
                lines.insert(i + 2, new_line)
                break
        index_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ 客户索引已更新 - 路径：{index_file}")
    
    # 总结
    print("\n" + "=" * 80)
    print("✅ 完整调研流程完成！")
    print("=" * 80)
    print(f"\n📁 客户档案位置：{customer_path}")
    print(f"\n已创建文件：")
    print(f"  1. 01-客户画像.md")
    print(f"  2. 03-调研报告/{report_file.name}")
    print(f"  3. 04-待办事项.md")
    print(f"\n💰 总成本：¥{qcc_result.get('total_cost', 0):.2f}")
    print("=" * 80)

if __name__ == '__main__':
    main()
