#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增量分析决策主程序

功能：
1. 读取最后分析时间（从 logs/ 目录）
2. 扫描 raw/ 目录下所有可用数据
3. 计算待分析时间段（去重）
4. 决策调用策略（逐天/批量/告警）
5. 驱动多次调用 run_pipeline.py
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
SKILL_DIR = Path(__file__).parent
PROJECT_DIR = SKILL_DIR.parent.parent / "projects" / "moments-analysis"
RAW_DIR = PROJECT_DIR / "raw"
LOGS_DIR = PROJECT_DIR / "logs"
PROFILES_DIR = PROJECT_DIR / "profiles"

# 告警阈值：超过 N 天未分析则告警
ALERT_THRESHOLD_DAYS = 3


def get_last_analyzed_date():
    """
    从 logs/ 目录读取最后分析的日期
    
    返回：YYYY-MM-DD 格式字符串，如果没有则返回 None
    """
    if not LOGS_DIR.exists():
        return None
    
    # 扫描所有 JSONL 文件
    jsonl_files = list(LOGS_DIR.glob("*.jsonl"))
    if not jsonl_files:
        return None
    
    # 提取日期并排序
    dates = []
    for f in jsonl_files:
        # 文件名格式：YYYY-MM-DD.jsonl 或 4 月 23 日 V2 版本.jsonl
        match = re.match(r'(\d{4}-\d{2}-\d{2})', f.name)
        if match:
            dates.append(match.group(1))
    
    if not dates:
        return None
    
    # 返回最近的日期
    return max(dates)


def get_available_raw_dates():
    """
    扫描 raw/ 目录，获取所有可用的数据文件日期
    
    返回：日期列表 ['2026-04-23', '2026-04-24', ...]
    """
    if not RAW_DIR.exists():
        return []
    
    dates = set()
    
    # 扫描所有 JSON 文件
    for f in RAW_DIR.glob("*.json"):
        # 跳过 analyzed 和 checkpoint 文件
        if '_analyzed' in f.name or '_checkpoint' in f.name:
            continue
        if f.name == 'status.json':
            continue
        
        # 尝试从文件名提取日期
        # 格式 1: 20260423_220920.json → 2026-04-23
        match = re.match(r'(\d{4})(\d{2})(\d{2})', f.name)
        if match:
            date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            dates.add(date_str)
            continue
        
        # 格式 2: 2026-04-23.json → 2026-04-23
        match = re.match(r'(\d{4}-\d{2}-\d{2})', f.name)
        if match:
            dates.add(match.group(1))
    
    return sorted(list(dates))


def get_unanalyzed_dates(last_date, available_dates):
    """
    计算需要分析的日期（未分析的日期）
    
    参数：
    - last_date: 最后分析的日期（YYYY-MM-DD）
    - available_dates: 所有可用数据的日期列表
    
    返回：需要分析的日期列表
    """
    if not last_date:
        # 没有分析记录，返回所有日期
        return available_dates
    
    # 过滤出晚于 last_date 的日期
    unanalyzed = [d for d in available_dates if d > last_date]
    return unanalyzed


def decide_strategy(unanalyzed_dates):
    """
    决策调用策略
    
    参数：
    - unanalyzed_dates: 需要分析的日期列表
    
    返回：策略字典
    {
        'mode': 'normal' | 'catchup' | 'alert',
        'dates': 需要处理的日期列表,
        'message': 策略说明
    }
    """
    count = len(unanalyzed_dates)
    
    if count == 0:
        return {
            'mode': 'skip',
            'dates': [],
            'message': '无新增数据，跳过分析'
        }
    elif count <= 3:
        return {
            'mode': 'normal',
            'dates': unanalyzed_dates,
            'message': f'发现 {count} 天新增数据，逐天分析'
        }
    elif count <= ALERT_THRESHOLD_DAYS:
        return {
            'mode': 'catchup',
            'dates': unanalyzed_dates,
            'message': f'发现 {count} 天未分析，批量补跑'
        }
    else:
        return {
            'mode': 'alert',
            'dates': unanalyzed_dates,
            'message': f'⚠️ 已积累 {count} 天未分析（超过阈值{ALERT_THRESHOLD_DAYS}天），请确认是否继续'
        }


def run_pipeline(date_str, posts_file=None):
    """
    调用 run_pipeline.py 处理指定日期的数据
    
    参数：
    - date_str: 日期（YYYY-MM-DD）
    - posts_file: 自定义输入文件路径（可选）
    
    返回：是否成功
    """
    cmd = [
        sys.executable,
        str(SKILL_DIR / "run_pipeline.py"),
        "--date", date_str
    ]
    
    if posts_file:
        cmd.extend(["--posts-file", posts_file])
    
    print(f"\n{'='*60}")
    print(f"执行：{' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True, encoding='utf-8')
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 执行失败：{e}")
        return False
    except Exception as e:
        print(f"\n❌ 异常：{e}")
        return False


def find_posts_file_for_date(date_str):
    """
    根据日期查找对应的 raw 数据文件
    
    参数：
    - date_str: 日期（YYYY-MM-DD）
    
    返回：文件路径（如果找到）
    """
    # 尝试匹配多种命名格式
    patterns = [
        f"{date_str.replace('-', '')}_*.json",  # 20260423_220920.json
        f"{date_str}.json",  # 2026-04-23.json
    ]
    
    for pattern in patterns:
        matches = list(RAW_DIR.glob(pattern))
        if matches:
            # 返回第一个匹配的文件
            return str(matches[0])
    
    return None


def main():
    print("=" * 60)
    print("朋友圈增量分析决策")
    print("=" * 60)
    
    # 1. 读取最后分析时间
    print("\n[1/5] 读取最后分析时间...")
    last_date = get_last_analyzed_date()
    if last_date:
        print(f"  最后分析日期：{last_date}")
    else:
        print(f"  无历史分析记录")
    
    # 2. 扫描可用数据
    print("\n[2/5] 扫描 raw/ 目录...")
    available_dates = get_available_raw_dates()
    print(f"  发现 {len(available_dates)} 个数据文件")
    if available_dates:
        print(f"  日期范围：{available_dates[0]} ~ {available_dates[-1]}")
    
    # 3. 计算待分析日期
    print("\n[3/5] 计算待分析日期...")
    unanalyzed = get_unanalyzed_dates(last_date, available_dates)
    print(f"  需要分析：{len(unanalyzed)} 天")
    if unanalyzed:
        print(f"  日期列表：{', '.join(unanalyzed)}")
    
    # 4. 决策调用策略
    print("\n[4/5] 决策调用策略...")
    strategy = decide_strategy(unanalyzed)
    print(f"  模式：{strategy['mode']}")
    print(f"  说明：{strategy['message']}")
    
    # 5. 执行分析
    print("\n[5/5] 执行分析...")
    
    if strategy['mode'] == 'skip':
        print("  [OK] 无新增数据，跳过")
        return 0
    
    if strategy['mode'] == 'alert':
        # 告警模式，需要人工确认
        print("\n[ALERT] " + "=" * 50)
        print("[ALERT] 告警：积累数据过多，建议人工确认")
        print("[ALERT] " + "=" * 50)
        print("\n建议操作：")
        print("  1. 检查 raw/ 目录是否有异常数据积累")
        print("  2. 确认是否需要全量分析")
        print("  3. 如需继续，手动运行：python run_pipeline.py --date YYYY-MM-DD")
        return 1
    
    # 正常模式或补跑模式：逐天处理
    success_count = 0
    fail_count = 0
    
    for date_str in strategy['dates']:
        # 查找对应的数据文件
        posts_file = find_posts_file_for_date(date_str)
        
        if not posts_file:
            print(f"\n[WARN] 未找到 {date_str} 的数据文件，跳过")
            fail_count += 1
            continue
        
        # 调用 run_pipeline.py
        success = run_pipeline(date_str, posts_file)
        
        if success:
            print(f"  [OK] {date_str} 分析完成")
            success_count += 1
        else:
            print(f"  [FAIL] {date_str} 分析失败")
            fail_count += 1
    
    # 汇总报告
    print("\n" + "=" * 60)
    print("增量分析完成")
    print("=" * 60)
    print(f"  成功：{success_count} 天")
    print(f"  失败：{fail_count} 天")
    
    if fail_count > 0:
        print(f"\n[WARN] 有 {fail_count} 天分析失败，请检查日志")
        return 1
    else:
        print(f"\n[OK] 全部成功")
        return 0


if __name__ == '__main__':
    sys.exit(main())
