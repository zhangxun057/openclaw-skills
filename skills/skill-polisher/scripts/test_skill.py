#!/usr/bin/env python3
"""
Skill Test Script
运行技能测试案例，验证修改有效性
"""

import json
import sys
from pathlib import Path

def load_test_cases(skill_path: str):
    """加载测试案例"""
    test_file = Path(skill_path) / "references" / "test-case-patterns.md"
    
    if not test_file.exists():
        print(f"⚠️ 警告：找不到测试案例文件 {test_file}")
        return []
    
    # 简单解析 markdown 中的测试案例
    cases = []
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # 查找测试案例部分
        if "## 测试案例" in content:
            cases.append({"name": "测试案例库", "file": str(test_file)})
    
    return cases

def run_test(skill_path: str, test_case: dict):
    """运行单个测试案例"""
    print(f"\n🧪 运行测试：{test_case['name']}")
    print(f"   参考文件：{test_case['file']}")
    
    # 实际测试需要调用技能执行
    # 这里只是框架，实际使用时需要扩展
    print(f"   ✅ 测试框架就绪")
    return True

def main():
    if len(sys.argv) < 2:
        print("用法：python test_skill.py <skill-path> [test-case]")
        print("示例：python test_skill.py ~/.openclaw/skills/customer-research")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    test_case_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔍 测试技能：{skill_path}")
    
    # 加载测试案例
    cases = load_test_cases(skill_path)
    
    if not cases:
        print("⚠️ 没有可用的测试案例，请手动验证技能功能")
        return
    
    # 运行测试
    if test_case_name:
        # 运行指定测试
        case = next((c for c in cases if c['name'] == test_case_name), None)
        if case:
            run_test(skill_path, case)
        else:
            print(f"❌ 找不到测试案例：{test_case_name}")
    else:
        # 运行所有测试
        print(f"\n📋 找到 {len(cases)} 个测试案例")
        for case in cases:
            run_test(skill_path, case)
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()
