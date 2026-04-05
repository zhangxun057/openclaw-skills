#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
customer-mgr 主入口
处理所有客户管理请求：创建/查询/更新/关联
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List, Any

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from customer_db import CustomerDB
from profile_updater import ProfileUpdater
from linker import ResultLinker

# ============== 配置常量 ==============
STORAGE_BASE = Path.home() / ".openclaw/agents/guaiguaixia/workspace/storage"
CUSTOMERS_DIR = STORAGE_BASE / "customers"
INDEX_FILE = STORAGE_BASE / "customer-index.md"

# ============== 日志函数 ==============
def log_info(msg: str):
    print(f"[INFO] {msg}")

def log_warn(msg: str):
    print(f"[WARN] {msg}")

def log_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)

def log_success(msg: str):
    print(f"✅ {msg}")

# ============== 核心函数 ==============

def ensure_storage_structure():
    """确保存储结构存在"""
    CUSTOMERS_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        create_index_file()

def create_index_file():
    """创建客户索引文件"""
    index_content = """# 客户索引

**更新时间：** {update_time}

---

## 客户列表

| 序号 | 客户名称 | 拼音目录 | 建档时间 | 最后更新 | 状态 |
|------|---------|---------|---------|---------|------|

---

## 快速链接
- [新建客户](#新建客户)
- [客户分类](#客户分类)
- [最近跟进](#最近跟进)

""".format(update_time="待更新")
    
    INDEX_FILE.write_text(index_content, encoding='utf-8')
    log_info("客户索引文件已创建")

def create_customer(customer_name: str, auto_create: bool = True) -> Dict[str, Any]:
    """
    创建客户档案
    
    Args:
        customer_name: 客户名称
        auto_create: 是否自动创建（False 则先询问）
    
    Returns:
        创建结果字典
    """
    ensure_storage_structure()
    
    db = CustomerDB(CUSTOMERS_DIR)
    
    # 检查是否已存在
    existing = db.find_customer(customer_name)
    if existing:
        return {
            "success": False,
            "message": f"客户已存在：{existing['name']}",
            "path": existing['path'],
            "action": "exists"
        }
    
    # 创建客户档案
    result = db.create_customer(customer_name)
    
    if result["success"]:
        # 更新索引
        update_index(customer_name, result["pinyin_dir"], action="add")
        
        return {
            "success": True,
            "message": f"客户档案创建成功：{customer_name}",
            "path": result["path"],
            "pinyin_dir": result["pinyin_dir"],
            "action": "created",
            "next_steps": [
                "🔍 是否立即调研？ → 调用 customer-research",
                "📋 是否有拜访记录？ → 调用 sales-visit-summary",
                "⏸️ 先建档，稍后补充"
            ]
        }
    else:
        return result

def query_customer(customer_name: str) -> Dict[str, Any]:
    """
    查询客户档案
    
    Args:
        customer_name: 客户名称
    
    Returns:
        客户档案信息
    """
    db = CustomerDB(CUSTOMERS_DIR)
    
    # 查找客户
    customer = db.find_customer(customer_name)
    
    if not customer:
        return {
            "success": False,
            "message": f"未找到客户：{customer_name}",
            "action": "not_found"
        }
    
    # 读取档案内容
    profile = db.read_profile(customer["path"])
    communications = db.list_communications(customer["path"])
    researches = db.list_researches(customer["path"])
    todos = db.read_todos(customer["path"])
    
    # 转换 Path 为字符串
    customer["path"] = str(customer["path"])
    
    return {
        "success": True,
        "customer": customer,
        "profile": profile,
        "communications": communications,
        "researches": researches,
        "todos": todos,
        "action": "found"
    }

def update_profile(customer_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新客户画像
    
    Args:
        customer_name: 客户名称
        updates: 更新内容（6 维度框架）
    
    Returns:
        更新结果
    """
    db = CustomerDB(CUSTOMERS_DIR)
    updater = ProfileUpdater()
    
    # 查找客户
    customer = db.find_customer(customer_name)
    
    if not customer:
        return {
            "success": False,
            "message": f"未找到客户：{customer_name}",
            "action": "not_found"
        }
    
    # 更新画像
    result = updater.update_profile(customer["path"], updates)
    
    if result["success"]:
        # 更新索引中的最后更新时间
        update_index(customer["name"], customer["pinyin_dir"], action="update")
        
        return {
            "success": True,
            "message": f"客户画像已更新：{customer_name}",
            "updated_fields": result["updated_fields"],
            "action": "updated"
        }
    else:
        return result

def link_research(customer_name: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    关联调研报告到客户档案
    
    Args:
        customer_name: 客户名称
        research_data: 调研数据
    
    Returns:
        关联结果
    """
    db = CustomerDB(CUSTOMERS_DIR)
    linker = ResultLinker()
    
    # 查找客户
    customer = db.find_customer(customer_name)
    
    if not customer:
        return {
            "success": False,
            "message": f"未找到客户：{customer_name}",
            "action": "not_found",
            "suggestion": "是否创建新客户？"
        }
    
    # 关联调研报告
    result = linker.link_research(customer["path"], research_data)
    
    if result["success"]:
        # 同时更新画像
        if "profile_updates" in research_data:
            update_profile(customer_name, research_data["profile_updates"])
        
        return {
            "success": True,
            "message": f"调研报告已关联：{customer_name}",
            "research_file": result["file_path"],
            "action": "linked"
        }
    else:
        return result

def link_communication(customer_name: str, communication_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    关联沟通记录到客户档案
    
    Args:
        customer_name: 客户名称
        communication_data: 沟通数据
    
    Returns:
        关联结果
    """
    db = CustomerDB(CUSTOMERS_DIR)
    linker = ResultLinker()
    
    # 查找客户
    customer = db.find_customer(customer_name)
    
    if not customer:
        return {
            "success": False,
            "message": f"未找到客户：{customer_name}",
            "action": "not_found",
            "suggestion": "是否创建新客户？"
        }
    
    # 关联沟通记录
    result = linker.link_communication(customer["path"], communication_data)
    
    if result["success"]:
        # 同时更新画像
        if "profile_updates" in communication_data:
            update_profile(customer_name, communication_data["profile_updates"])
        
        return {
            "success": True,
            "message": f"沟通记录已关联：{customer_name}",
            "communication_file": result["file_path"],
            "action": "linked"
        }
    else:
        return result

def update_index(customer_name: str, pinyin_dir: str, action: str = "add"):
    """
    更新客户索引
    
    Args:
        customer_name: 客户名称
        pinyin_dir: 拼音目录
        action: add/update
    """
    if not INDEX_FILE.exists():
        create_index_file()
    
    content = INDEX_FILE.read_text(encoding='utf-8')
    now = "2026-03-29 11:18"  # TODO: 使用当前时间
    
    if action == "add":
        # 添加新行
        new_line = f"| - | {customer_name} | `{pinyin_dir}/` | {now.split()[0]} | {now.split()[0]} | 活跃 |\n"
        
        # 找到表格位置并插入
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '| 序号 | 客户名称 |' in line:
                # 找到表头，在下一行插入
                lines.insert(i + 2, new_line)
                break
        
        content = '\n'.join(lines)
    
    # 更新更新时间
    content = content.replace("**更新时间：**", f"**更新时间：** {now}")
    
    INDEX_FILE.write_text(content, encoding='utf-8')

# ============== 主函数 ==============

def main():
    """主函数 - 处理命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='客户管理技能')
    parser.add_argument('action', choices=['create', 'query', 'update', 'link-research', 'link-communication'],
                        help='操作类型')
    parser.add_argument('--name', required=True, help='客户名称')
    parser.add_argument('--data', help='数据（JSON 格式）')
    parser.add_argument('--auto', action='store_true', help='自动模式（不询问）')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        result = create_customer(args.name, auto_create=args.auto)
    elif args.action == 'query':
        result = query_customer(args.name)
    elif args.action == 'update':
        if not args.data:
            log_error("更新操作需要提供 --data 参数")
            sys.exit(1)
        updates = json.loads(args.data)
        result = update_profile(args.name, updates)
    elif args.action == 'link-research':
        if not args.data:
            log_error("关联调研需要提供 --data 参数")
            sys.exit(1)
        research_data = json.loads(args.data)
        result = link_research(args.name, research_data)
    elif args.action == 'link-communication':
        if not args.data:
            log_error("关联沟通需要提供 --data 参数")
            sys.exit(1)
        comm_data = json.loads(args.data)
        result = link_communication(args.name, comm_data)
    else:
        log_error(f"未知操作：{args.action}")
        sys.exit(1)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result["success"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
