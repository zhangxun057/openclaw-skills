# -*- coding: utf-8 -*-
"""
customer-research 测试脚本
测试对象：北京清格科技有限公司
"""

import sys
import os
from datetime import datetime

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加脚本目录到路径
script_dir = os.path.dirname(__file__)
sys.path.insert(0, script_dir)

from search import search_company, judge_search_result
from report import generate_company_report, save_report


def test_beijing_qinge():
    """测试北京清格科技有限公司调研"""
    
    company_name = "北京清格科技有限公司"
    
    print("=" * 80)
    print(f"🔍 customer-research 技能测试")
    print(f"  目标企业：{company_name}")
    print(f"  测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Phase 1: 基础调研
    print("\n【Phase 1】基础调研（自动执行）")
    print("-" * 80)
    
    result = search_company(company_name, use_qcc=False)
    
    print(f"\n搜索完成：")
    print(f"  - 数据源数量：{len(result.get('sources', []))}")
    print(f"  - 置信度：{judge_search_result(result)}")
    
    # 打印结果摘要
    if result.get('info'):
        print(f"\n获取到的信息：")
        for key, value in result['info'].items():
            if value:
                print(f"  - {key}: {value}")
    
    # Phase 2: 生成基础报告
    print("\n【Phase 2】生成基础报告")
    print("-" * 80)
    
    report_content = generate_company_report(result)
    filepath = save_report(report_content, company_name)
    
    print(f"\n✅ 报告已保存：{filepath}")
    
    # Phase 3: 输出报告预览
    print("\n【Phase 3】报告预览")
    print("-" * 80)
    print(report_content[:2000])  # 预览前 2000 字
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)
    
    return filepath


if __name__ == '__main__':
    test_beijing_qinge()
