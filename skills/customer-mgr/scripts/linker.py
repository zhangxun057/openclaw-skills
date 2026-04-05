#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关联调研/拜访结果到客户档案
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class ResultLinker:
    """结果关联器"""
    
    def __init__(self):
        pass
    
    def link_research(self, customer_path: Path, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        关联调研报告到客户档案
        
        Args:
            customer_path: 客户档案路径
            research_data: 调研数据
        
        Returns:
            关联结果
        """
        research_dir = customer_path / "03-调研报告"
        
        if not research_dir.exists():
            research_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        date_str = datetime.now().strftime("%Y%m%d")
        research_type = research_data.get("type", "调研")
        file_name = f"{date_str}-{research_type}.md"
        file_path = research_dir / file_name
        
        # 生成报告内容
        content = self._generate_research_report(research_data)
        
        # 写入文件
        file_path.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "message": f"调研报告已保存",
            "file_path": str(file_path)
        }
    
    def link_communication(self, customer_path: Path, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        关联沟通记录到客户档案
        
        Args:
            customer_path: 客户档案路径
            communication_data: 沟通数据
        
        Returns:
            关联结果
        """
        comm_dir = customer_path / "02-沟通记录"
        
        if not comm_dir.exists():
            comm_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        date_str = datetime.now().strftime("%Y%m%d")
        comm_type = communication_data.get("type", "沟通")
        file_name = f"{date_str}-{comm_type}.md"
        file_path = comm_dir / file_name
        
        # 生成沟通记录内容
        content = self._generate_communication_log(communication_data)
        
        # 写入文件
        file_path.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "message": f"沟通记录已保存",
            "file_path": str(file_path)
        }
    
    def _generate_research_report(self, data: Dict[str, Any]) -> str:
        """
        生成调研报告内容
        
        Args:
            data: 调研数据
        
        Returns:
            Markdown 内容
        """
        date = datetime.now().strftime("%Y-%m-%d")
        date_str = datetime.now().strftime("%Y%m%d")
        
        template = f"""# {date} - {data.get('type', '调研')}

**调研 ID：** RES-{date_str}-001
**日期：** {date}
**类型：** {data.get('type', '调研')}
**数据来源：** {data.get('sources', '企查查')}

---

## 📊 调研结果

### 企业基本信息
{data.get('basic_info', '待补充')}

### 行业地位
{data.get('industry_status', '待补充')}

### 主营业务
{data.get('business_scope', '待补充')}

### 关键发现
{data.get('key_findings', '待补充')}

### 合作建议
{data.get('recommendations', '待补充')}

---

## 数据来源
{data.get('source_links', '待补充')}
"""
        return template
    
    def _generate_communication_log(self, data: Dict[str, Any]) -> str:
        """
        生成沟通记录内容
        
        Args:
            data: 沟通数据
        
        Returns:
            Markdown 内容
        """
        date = datetime.now().strftime("%Y-%m-%d")
        date_str = datetime.now().strftime("%Y%m%d")
        
        template = f"""# {date} - {data.get('type', '沟通')}

**沟通 ID：** COM-{date_str}-001
**日期：** {date}
**类型：** {data.get('type', '沟通')}
**负责人：** 张洵
**生成时间：** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 📋 沟通摘要

### 参会人员
- 我方：张洵
- 对方：{data.get('participants', '待补充')}

### 关键讨论要点
1. {data.get('key_points', '待补充')}

### 客户优先级
- {data.get('priorities', '待补充')}

### 疑虑/反对意见
- {data.get('objections', '待补充')}

### 行动项
| 负责人 | 行动 | 截止 |
|--------|------|------|
| 张洵 | {data.get('actions', '待补充')} | {data.get('deadlines', '待补充')} |

### 下一步
- {data.get('next_steps', '待补充')}

### 订单影响
- {data.get('order_impact', '待补充')}
"""
        return template
