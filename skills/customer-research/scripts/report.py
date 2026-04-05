# -*- coding: utf-8 -*-
"""
customer-research 报告生成模块
支持企业客户和个人客户的报告生成
"""

import os
from datetime import datetime
from typing import Dict, List, Optional


def generate_deep_clues(search_result: Dict) -> str:
    """
    生成深度线索建议（AI 自主思考）
    
    Args:
        search_result: 调研数据
    
    Returns:
        深度线索 Markdown
    """
    clues = []
    info = search_result.get('info', {})
    
    # 示例：AI 应根据实际数据自主判断
    if info.get('scale', {}).get('企业规模') == '大型/集团':
        clues.append('企业规模较大，可能有较强采购能力和多主体需求')
    if info.get('industry_status', {}).get('上市情况') == '未上市':
        clues.append('未上市企业，决策流程可能较短，适合快速推进')
    
    # 如有股东搜索数据，分析股东背景
    if search_result.get('shareholder_searches'):
        for sh in search_result['shareholder_searches']:
            findings = sh.get('key_findings', {})
            if findings.get('has_gov_background'):
                clues.append(f"股东{sh.get('shareholder')}可能有政府背景，可关注政务资源协同")
    
    # 输出线索（最多 3 个）
    if clues:
        return '\n'.join([f"- {clue}" for clue in clues[:3]])
    else:
        return '暂无明显深度调查线索，建议按标准流程跟进'


def generate_company_report(search_result: Dict) -> str:
    """生成企业客户调研报告"""
    company_name = search_result.get('company_name', '未知企业')
    info = search_result.get('info', {})
    sources = search_result.get('sources', [])
    
    scale = info.get('scale', {})
    industry_status = info.get('industry_status', {})
    business = info.get('business', {})
    key_tags = info.get('key_tags', [])
    
    report = f"""# {company_name} — 背景调研报告

**调研时间：** {search_result.get('search_time', datetime.now().strftime('%Y-%m-%d %H:%M'))}

---

## 基本信息
- **法人：** {scale.get('法人') or '未查到'}
- **成立日期：** {scale.get('成立日期') or '未查到'}
- **注册地：** {scale.get('注册地') or '未查到'}
- **企业规模：** {scale.get('企业规模') or scale.get('员工数') or '未查到'}

## 行业地位
- **上市情况：** {industry_status.get('上市情况') or '未上市/未查到'}
- **纳税等级：** {industry_status.get('纳税等级') or '未查到'}
- **行业排名：** {industry_status.get('行业排名') or '未查到'}

## 主营业务
- **主营业务：** {business.get('主营业务') or business.get('描述') or '未查到'}
- **官网：** {business.get('官网') or '未查到'}
- **核心产品/服务：** {business.get('核心产品/服务') or '未查到'}

## 关键标签
{', '.join(key_tags) if key_tags else '暂无关键标签'}

---

## 深度调查建议

**AI 自主思考：** 基于以上信息，以下线索值得深挖：

{generate_deep_clues(search_result)}

---

## 信息来源
"""
    
    if sources:
        for i, source in enumerate(sources, 1):
            title = source.get('title', '未知来源')
            link = source.get('link', '#')
            report += f"\n{i}. [{title}]({link})"
    else:
        report += "\n暂无可靠信息来源"
    
    # 二阶挖掘结果
    secondary = search_result.get('secondary_digging', [])
    if secondary:
        report += "\n\n## 关联挖掘\n\n"
        for dig in secondary:
            report += f"- **{dig.get('type')}**: {dig.get('target')} - {dig.get('finding')}\n"
    
    # 置信度提示
    confidence = search_result.get('confidence', 'unknown')
    if confidence == 'low':
        report += """

---

## ⚠️ 信息不足提示

本次调研未查到足够的公开信息，建议：
- 在拜访时询问企业基本信息
- 查看企业官网或公众号
- 通过企查查/天眼查等工具补充
"""
    
    report += """

---

*报告由 customer-research 技能自动生成*
"""
    
    return report


def generate_person_report(search_result: Dict) -> str:
    """生成个人客户调研报告"""
    person_info = search_result.get('person_info', '未知人士')
    companies = search_result.get('associated_companies', [])
    sources = search_result.get('sources', [])
    
    report = f"""# {person_info} — 背景调研报告

**调研时间：** {search_result.get('search_time', datetime.now().strftime('%Y-%m-%d %H:%M'))}

---

## 个人身份
- **姓名：** {search_result.get('name', '未查到')}
- **职务：** {search_result.get('position', '未查到')}
- **关联商会/协会：** {search_result.get('associations', '未查到')}

---

## 关联企业
"""
    
    if companies:
        for i, company in enumerate(companies, 1):
            report += f"\n### {i}. {company.get('name', '未知企业')}\n"
            report += f"- **职务：** {company.get('position', '未查到')}\n"
            report += f"- **持股：** {company.get('holding', '未查到')}\n"
            report += f"- **企业状态：** {company.get('status', '未查到')}\n"
    else:
        report += "\n未查到关联企业\n"
    
    report += f"""
---

## 信息来源
"""
    
    if sources:
        for i, source in enumerate(sources, 1):
            title = source.get('title', '未知来源')
            link = source.get('link', '#')
            report += f"\n{i}. [{title}]({link})"
    else:
        report += "\n暂无可靠信息来源"
    
    report += """

---

*报告由 customer-research 技能自动生成*
"""
    
    return report


def save_report(report_content: str, name: str, output_dir: str = None) -> str:
    """保存调研报告到文件"""
    if output_dir is None:
        output_dir = os.path.expanduser("~/.openclaw/skills/customer-research/output")
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = name.replace('/', '_').replace('\\', '_')[:50]
    filename = f"{timestamp}_{safe_name}_调研报告.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return filepath


if __name__ == '__main__':
    # 测试
    print("报告生成模块已加载")
