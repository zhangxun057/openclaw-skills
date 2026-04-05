# -*- coding: utf-8 -*-
"""
customer-research 主入口
支持企业客户和个人客户调研

Phase 5: 客户画像关联（已实现）
- 检测客户是否存在
- 新客户 → 询问创建，自动填充基本信息
- 老客户 → 询问更新，对比变化维度
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# 添加脚本目录到路径
script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)

# 导入搜索和报告模块
from search import (
    search_company, 
    search_person, 
    check_secondary_digging,
    execute_secondary_digging,
    judge_search_result,
    request_qcc_authorization
)
from report import generate_company_report, generate_person_report, save_report

# 导入 customer-mgr 模块（Phase 5 联动）
try:
    customer_mgr_dir = Path.home() / ".openclaw/skills/customer-mgr/scripts"
    sys.path.insert(0, str(customer_mgr_dir))
    from customer_db import CustomerDB
    from linker import ResultLinker
    from profile_updater import ProfileUpdater
    CUSTOMER_MGR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  警告：customer-mgr 模块不可用 - {e}")
    CUSTOMER_MGR_AVAILABLE = False

# 配置常量
STORAGE_BASE = Path.home() / ".openclaw/agents/guaiguaixia/workspace/storage"
CUSTOMERS_DIR = STORAGE_BASE / "customers"


def extract_profile_updates(research_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    从调研数据中提取画像更新信息
    """
    updates = {"企业基本信息": {}, "行业地位": {}}
    
    # 从企查查数据提取
    if research_data.get('data', {}).get('detail'):
        detail = research_data['data']['detail']
        updates["企业基本信息"] = {
            "企业全称": detail.get('Name'),
            "法人": detail.get('OperName'),
            "成立日期": detail.get('StartDate'),
            "注册资本": detail.get('RegistCapi'),
            "经营状态": detail.get('Status'),
            "统一社会信用代码": detail.get('CreditCode'),
        }
        updates["行业地位"] = {
            "行业分类": detail.get('Industry', {}).get('SmallCategory'),
            "企业规模": detail.get('PersonScope'),
        }
    
    # 从 Serper 数据提取
    if research_data.get('info'):
        info = research_data['info']
        if info.get('industry_status', {}).get('上市情况'):
            updates["行业地位"]["上市情况"] = info['industry_status']['上市情况']
        if info.get('key_tags'):
            updates["行业地位"]["关键标签"] = ', '.join(info['key_tags'])
    
    return updates


def phase5_customer_profile_linkage(company_name: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 5: 客户画像关联
    """
    if not CUSTOMER_MGR_AVAILABLE:
        return {"success": False, "message": "customer-mgr 模块不可用", "action": "skip"}
    
    print("\n【Phase 5】客户画像关联")
    print("-" * 60)
    
    db = CustomerDB(CUSTOMERS_DIR)
    customer = db.find_customer(company_name)
    
    if customer:
        print(f"检测到已有客户档案")
        print(f"路径：{customer['path']}")
        print(f"\n自动执行更新...")
        
        profile_updates = extract_profile_updates(research_data)
        updater = ProfileUpdater()
        update_result = updater.update_profile(customer["path"], profile_updates)
        
        linker = ResultLinker()
        link_result = linker.link_research(customer["path"], research_data)
        
        print(f"✅ 客户画像已更新")
        print(f"✅ 调研报告已关联")
        
        return {"success": True, "action": "updated", "customer": customer}
    else:
        print(f"检测到新客户（首次调研）")
        print(f"\n自动创建客户档案...")
        
        create_result = db.create_customer(company_name)
        
        if create_result["success"]:
            profile_updates = extract_profile_updates(research_data)
            updater = ProfileUpdater()
            update_result = updater.update_profile(create_result["path"], profile_updates)
            
            linker = ResultLinker()
            link_result = linker.link_research(create_result["path"], research_data)
            
            print(f"✅ 客户画像已创建")
            print(f"✅ 调研报告已关联")
            print(f"路径：{create_result['path']}")
            
            return {"success": True, "action": "created", "customer": create_result}
        else:
            return {"success": False, "message": create_result.get("message"), "action": "failed"}


def detect_input_type(input_text: str) -> str:
    """
    判断输入类型（企业 or 个人）
    
    Returns:
        'company' | 'person' | 'unknown'
    """
    # 个人特征词
    person_keywords = ['会长', '秘书长', '董事长', '总经理', '总裁', 'CEO', '总', '先生', '女士']
    
    # 检查是否包含个人特征词
    for keyword in person_keywords:
        if keyword in input_text:
            return 'person'
    
    # 检查是否包含企业特征词
    company_keywords = ['公司', '集团', '企业', '厂', '所', '交易所']
    for keyword in company_keywords:
        if keyword in input_text:
            return 'company'
    
    # 默认按企业处理
    return 'company'


def main(input_text: str, use_qcc: bool = False, enable_secondary: bool = True, auto_phase5: bool = True):
    """
    客户调研主函数（包含 Phase 5）
    
    Args:
        input_text: 输入文本（企业名 或 个人身份）
        use_qcc: 是否使用企查查 API
        enable_secondary: 是否启用二阶挖掘
        auto_phase5: 是否自动执行 Phase 5（默认 True）
    """
    print(f"\n🔍 开始调研：{input_text}")
    print("=" * 60)
    
    # 第一步：判断输入类型
    input_type = detect_input_type(input_text)
    print(f"\n【步骤 1/5】判断输入类型：{input_type}")
    
    # 第二步：一级信息收集
    print("\n【步骤 2/5】一级信息收集...")
    
    if input_type == 'company':
        result = search_company(input_text, use_qcc=use_qcc)
    else:
        result = search_person(input_text)
    
    # 第三步：判断是否触发二阶挖掘
    print("\n【步骤 3/5】判断二阶挖掘...")
    
    if enable_secondary and input_type == 'company':
        digging_directions = check_secondary_digging(result)
        
        if digging_directions:
            print(f"  触发 {len(digging_directions)} 个挖掘方向：")
            for d in digging_directions:
                print(f"    - {d['type']}: {d['target']}（{d['reason']}）")
            
            print("\n  执行二阶挖掘...")
            secondary_results = execute_secondary_digging(digging_directions)
            result['secondary_digging'] = secondary_results
        else:
            print("  无需二阶挖掘")
    else:
        print("  跳过二阶挖掘")
    
    # 第四步：生成报告
    print("\n【步骤 4/5】生成调研报告...")
    
    if input_type == 'company':
        report_content = generate_company_report(result)
    else:
        report_content = generate_person_report(result)
    
    filepath = save_report(report_content, input_text)
    print(f"✅ 报告已保存：{filepath}")
    
    # 【新增】标准输出：深度调查询问
    print(f"\n📋 初步调研完成，是否执行深度调查？")
    print(f"  - 深度调查可能调用付费接口或花费较多时间")
    print(f"  - 回复'确认'继续，'跳过'继续普通流程")
    
    # 第五步：客户画像关联（Phase 5）
    if auto_phase5 and input_type == 'company':
        phase5_result = phase5_customer_profile_linkage(input_text, result)
        if phase5_result.get('success'):
            print(f"\n✅ Phase 5 完成：{phase5_result['action']}")
        else:
            print(f"\n⚠️  Phase 5 跳过：{phase5_result.get('message', '未知原因')}")
    else:
        print(f"\n⚠️  Phase 5 跳过（auto_phase5=False 或个人客户）")
    
    # 输出结果
    confidence = judge_search_result(result)
    print(f"\n{'=' * 60}")
    print(f"✅ 调研完成！")
    print(f"报告已保存：{filepath}")
    print(f"置信度：{confidence}")
    print(f"信息来源：{len(result.get('sources', []))}个")
    
    if result.get('secondary_digging'):
        print(f"二阶挖掘：{len(result['secondary_digging'])}条")
    
    return filepath


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python main.py \"企业名称/个人身份\" [--qcc] [--no-secondary]")
        print()
        print("示例:")
        print("  python main.py \"北京清格科技\"           # 企业调研")
        print("  python main.py \"黄开枢 贵阳福建商会会长\" # 个人客户挖掘")
        print("  python main.py \"北京清格科技\" --qcc     # 使用企查查")
        print("  python main.py \"北京清格科技\" --no-secondary  # 禁用二阶挖掘")
        sys.exit(1)
    
    input_text = sys.argv[1]
    use_qcc = '--qcc' in sys.argv
    enable_secondary = '--no-secondary' not in sys.argv
    
    main(input_text, use_qcc=use_qcc, enable_secondary=enable_secondary)
