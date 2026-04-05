#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户画像更新逻辑
基于 6 维度框架更新客户画像
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ProfileUpdater:
    """客户画像更新器"""
    
    def __init__(self):
        # 6 维度框架
        self.dimensions = [
            "企业基本信息",
            "行业地位",
            "主营业务",
            "组织架构",
            "经营状况",
            "合作潜力"
        ]
    
    def update_profile(self, customer_path: Path, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新客户画像
        
        Args:
            customer_path: 客户档案路径
            updates: 更新内容（6 维度框架）
        
        Returns:
            更新结果
        """
        profile_file = customer_path / "01-客户画像.md"
        
        if not profile_file.exists():
            return {
                "success": False,
                "message": "客户画像文件不存在"
            }
        
        # 读取现有画像
        content = profile_file.read_text(encoding='utf-8')
        
        updated_fields = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 逐个维度更新
        for dimension, value in updates.items():
            if dimension in self.dimensions:
                content = self._update_dimension(content, dimension, value)
                updated_fields.append(dimension)
        
        # 更新最后更新时间
        content = re.sub(
            r'\*\*最后更新：\*\* .*',
            f'**最后更新：** {now}',
            content
        )
        
        # 写回文件
        profile_file.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "message": f"客户画像已更新，更新{len(updated_fields)}个维度",
            "updated_fields": updated_fields
        }
    
    def _update_dimension(self, content: str, dimension: str, value: Any) -> str:
        """
        更新单个维度
        
        Args:
            content: 画像内容
            dimension: 维度名称
            value: 新值
        
        Returns:
            更新后的内容
        """
        # 找到维度位置
        pattern = rf'(## {dimension}\n.*?)(?=## |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            # 维度不存在，添加到末尾
            return content
        
        # 替换维度内容
        old_section = match.group(1)
        new_section = self._format_dimension(dimension, value)
        
        content = content.replace(old_section, new_section)
        
        return content
    
    def _format_dimension(self, dimension: str, value: Any) -> str:
        """
        格式化维度内容
        
        Args:
            dimension: 维度名称
            value: 值（可以是字符串、字典、列表）
        
        Returns:
            格式化后的 Markdown 内容
        """
        if isinstance(value, str):
            # 简单字符串，直接替换
            return f"## {dimension}\n{value}\n\n"
        
        elif isinstance(value, dict):
            # 字典，逐行格式化
            lines = [f"## {dimension}"]
            for key, val in value.items():
                lines.append(f"- **{key}：** {val}")
            lines.append("")
            return '\n'.join(lines)
        
        elif isinstance(value, list):
            # 列表，逐行格式化
            lines = [f"## {dimension}"]
            for item in value:
                if isinstance(item, dict):
                    # 字典项
                    item_str = ', '.join([f"{k}: {v}" for k, v in item.items()])
                    lines.append(f"- {item_str}")
                else:
                    lines.append(f"- {item}")
            lines.append("")
            return '\n'.join(lines)
        
        else:
            # 未知类型，转为字符串
            return f"## {dimension}\n{str(value)}\n\n"
    
    def add_communication_summary(self, customer_path: Path, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加沟通摘要到画像
        
        Args:
            customer_path: 客户档案路径
            summary: 沟通摘要
        
        Returns:
            添加结果
        """
        updates = {
            "合作潜力": {
                "最近沟通": summary.get("date", ""),
                "沟通重点": summary.get("key_points", ""),
                "下一步": summary.get("next_steps", "")
            }
        }
        
        return self.update_profile(customer_path, updates)
    
    def add_research_summary(self, customer_path: Path, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加调研摘要到画像
        
        Args:
            customer_path: 客户档案路径
            summary: 调研摘要
        
        Returns:
            添加结果
        """
        updates = {
            "企业基本信息": {
                "企业全称": summary.get("company_name", ""),
                "法人": summary.get("legal_rep", ""),
                "注册资本": summary.get("registered_capital", ""),
                "成立日期": summary.get("establish_date", "")
            },
            "行业地位": {
                "行业分类": summary.get("industry", ""),
                "纳税等级": summary.get("tax_level", "")
            }
        }
        
        return self.update_profile(customer_path, updates)
