#!/usr/bin/env python3
"""
一键完整流程脚本
功能：自动下载WeFlow → 启动服务 → 下载数据 → 客户盘点
"""

import os
import sys
import subprocess
import argparse
import time

def run_script(script_name, args=None):
    """运行子脚本"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    print(f"\n{'='*50}")
    print(f"执行: {script_name}")
    print('='*50)
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="微信客户分析一键流程")
    parser.add_argument("--output", default="~/.openclaw/workspace/客户档案", help="输出目录")
    parser.add_argument("--data-dir", default="~/.openclaw/workspace/微信数据", help="数据目录")
    parser.add_argument("--download-media", action="store_true", help="下载媒体文件")
    parser.add_argument("--download-moments", action="store_true", help="下载朋友圈")
    parser.add_argument("--min-messages", type=int, default=50, help="最少消息数")
    parser.add_argument("--skip-download", action="store_true", help="跳过数据下载（使用已有数据）")
    parser.add_argument("--skip-weflow", action="store_true", help="跳过WeFlow启动（已启动）")
    args = parser.parse_args()
    
    data_dir = os.path.expanduser(args.data_dir)
    output_dir = os.path.expanduser(args.output)
    
    print("="*50)
    print("微信客户分析 - 一键完整流程")
    print("="*50)
    print(f"数据目录: {data_dir}")
    print(f"输出目录: {output_dir}")
    print(f"下载媒体: {'是' if args.download_media else '否'}")
    print(f"下载朋友圈: {'是' if args.download_moments else '否'}")
    print("="*50)
    
    # 步骤1: 启动WeFlow
    if not args.skip_weflow:
        print("\n[步骤1/4] 启动WeFlow服务...")
        if not run_script("weflow_manager.py", ["--action", "start", "--wait-wechat"]):
            print("[ERROR] WeFlow启动失败，请检查:")
            print("  1. Node.js是否已安装")
            print("  2. 端口5032是否被占用")
            print("  3. 微信桌面版是否已登录")
            return
    else:
        print("\n[步骤1/4] 跳过WeFlow启动")
    
    # 步骤2: 下载全量数据
    if not args.skip_download:
        print("\n[步骤2/4] 下载全量数据...")
        download_args = [
            "--output", data_dir
        ]
        if args.download_media:
            download_args.append("--include-media")
        if args.download_moments:
            download_args.append("--include-moments")
        
        if not run_script("download_all.py", download_args):
            print("[ERROR] 数据下载失败")
            return
    else:
        print("\n[步骤2/4] 跳过数据下载（使用已有数据）")
        if not os.path.exists(data_dir):
            print(f"[ERROR] 数据目录不存在: {data_dir}")
            return
    
    # 步骤3: 客户逐一盘点
    print("\n[步骤3/4] 客户逐一盘点...")
    analyze_args = [
        "--data-dir", data_dir,
        "--output", output_dir,
        "--min-messages", str(args.min_messages)
    ]
    
    if not run_script("analyze_all.py", analyze_args):
        print("[ERROR] 客户盘点失败")
        return
    
    # 步骤4: 完成提示
    print("\n[步骤4/4] 生成完成报告...")
    print("\n" + "="*50)
    print("分析完成！")
    print("="*50)
    print(f"客户档案已保存至: {output_dir}")
    print(f"\n查看档案:")
    print(f"  核心客户: {output_dir}/核心客户/")
    print(f"  活跃客户: {output_dir}/活跃客户/")
    print(f"  普通客户: {output_dir}/普通客户/")
    print(f"  待激活客户: {output_dir}/待激活客户/")
    print(f"\n统计数据:")
    print(f"  {output_dir}/客户盘点统计.json")
    print("="*50)

if __name__ == "__main__":
    main()
