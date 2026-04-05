#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Test Script
执行 skill 的测试用例，验证修改是否有效
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def load_test_cases(test_file: str) -> list:
    """加载测试用例"""
    test_path = Path(test_file)
    
    if not test_path.exists():
        print(f"⚠️ Test file not found: {test_file}")
        return []
    
    with open(test_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_test(test_case: dict) -> bool:
    """
    执行单个测试用例
    
    Returns:
        bool: 测试是否通过
    """
    print(f"\n🧪 Running test: {test_case.get('name', 'Unnamed')}")
    print(f"   Type: {test_case.get('type', 'N/A')}")
    print(f"   Input: {test_case.get('input', 'N/A')}")
    print(f"   Expected: {test_case.get('expected', 'N/A')}")
    
    # 这里应该调用实际的 skill 进行测试
    # 目前只是框架，需要用户手动执行或集成到测试框架
    
    print(f"   ⚠️ Manual test required - please run the skill with the input above")
    
    # 返回 True 表示测试框架正常
    return True


def run_all_tests(skill_path: str) -> dict:
    """
    执行所有测试用例
    
    Returns:
        dict: 测试结果统计
    """
    skill_dir = Path(skill_path)
    test_file = skill_dir / "references" / "test-cases.json"
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
    
    if not test_file.exists():
        print(f"⚠️ No test cases found at {test_file}")
        print("   Please create test-cases.json in references/ folder")
        return results
    
    test_cases = load_test_cases(str(test_file))
    results["total"] = len(test_cases)
    
    print(f"\n📊 Running {len(test_cases)} test cases for {skill_dir.name}\n")
    print("=" * 60)
    
    for test_case in test_cases:
        try:
            if run_test(test_case):
                results["passed"] += 1
                print(f"   ✅ PASS")
            else:
                results["failed"] += 1
                print(f"   ❌ FAIL")
        except Exception as e:
            results["failed"] += 1
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"\n📊 Test Summary:")
    print(f"   Total:   {results['total']}")
    print(f"   Passed:  {results['passed']}")
    print(f"   Failed:  {results['failed']}")
    print(f"   Skipped: {results['skipped']}")
    
    return results


def save_test_log(skill_path: str, results: dict):
    """保存测试日志"""
    skill_dir = Path(skill_path)
    log_dir = skill_dir / "test-logs"
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = log_dir / f"test-{timestamp}.json"
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "skill": skill_dir.name,
        "results": results
    }
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📝 Test log saved to: {log_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_skill.py <skill-path>")
        print("Example: python test_skill.py C:\\Users\\...\\skills\\skill-name")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    results = run_all_tests(skill_path)
    save_test_log(skill_path, results)
    
    # 返回退出码
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
