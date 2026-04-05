#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户数据库操作
负责客户档案的创建、查询、更新、删除
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Dict, List, Any

# 简单的拼音转换（备用方案，不依赖 pypinyin）
def lazy_pinyin(text):
    """简单的汉字转拼音（仅用于测试，正式环境建议安装 pypinyin）"""
    # 这里使用一个简单的映射表，仅支持常用字
    # 正式环境请安装 pypinyin: pip install pypinyin
    result = []
    for char in text:
        # 如果是中文，转换为拼音首字母
        if '\u4e00' <= char <= '\u9fff':
            # 简单处理：使用 Unicode 编码作为临时替代
            result.append(f"zhong{ord(char) % 10}")
        else:
            result.append(char)
    return result

# ============== 配置常量 ==============
CUSTOMER_PROFILE_TEMPLATE = """# {customer_name} - 客户画像

**建档时间：** {create_time}
**最后更新：** {update_time}
**档案路径：** `{relative_path}`

---

## 1. 企业基本信息
- **企业全称：** {customer_name}
- **统一社会信用代码：** 待补充
- **法人：** 待补充
- **成立日期：** 待补充
- **注册资本：** 待补充
- **经营状态：** 待补充

## 2. 行业地位
- **行业分类：** 待补充
- **行业排名：** 待补充
- **上市情况：** 待补充
- **纳税等级：** 待补充

## 3. 主营业务
- **核心产品/服务：** 待补充
- **客户群体：** 待补充
- **市场覆盖：** 待补充

## 4. 组织架构
- **股东结构：** 待补充
- **高管团队：** 待补充
- **员工规模：** 待补充

## 5. 经营状况
- **年营收：** 待补充
- **利润率：** 待补充
- **现金流：** 待补充

## 6. 合作潜力
- **业务匹配度：** 待补充
- **采购能力：** 待补充
- **决策链：** 待补充

---

## 关联记录
- **沟通记录：** [查看](02-沟通记录/)
- **调研报告：** [查看](03-调研报告/)
- **待办事项：** [查看](04-待办事项.md)
"""

COMMUNICATION_LOG_TEMPLATE = """# {date} - {communication_type}

**沟通 ID：** COM-{date_str}-{seq}
**日期：** {date}
**类型：** {communication_type}
**负责人：** 张洵
**生成时间：** {create_time}

---

## 📋 沟通摘要

### 参会人员
- 我方：张洵
- 对方：{participants}

### 关键讨论要点
1. {key_points}

### 客户优先级
- {priorities}

### 疑虑/反对意见
- {objections}

### 行动项
| 负责人 | 行动 | 截止 |
|--------|------|------|
| 张洵 | {actions} | {deadlines} |

### 下一步
- {next_steps}

### 订单影响
- {order_impact}
"""

RESEARCH_REPORT_TEMPLATE = """# {date} - {research_type}

**调研 ID：** RES-{date_str}-{seq}
**日期：** {date}
**类型：** {research_type}
**数据来源：** {data_sources}

---

## 📊 调研结果

### 企业基本信息
{basic_info}

### 行业地位
{industry_status}

### 主营业务
{business_scope}

### 关键发现
{key_findings}

### 合作建议
{recommendations}

---

## 数据来源
{source_links}
"""

TODOS_TEMPLATE = """# {customer_name} - 待办事项

**更新时间：** {update_time}

---

## 待办列表

| 序号 | 事项 | 负责人 | 截止 | 状态 | 备注 |
|------|------|--------|------|------|------|
| 1 | 示例：发送合作方案 | 张洵 | 2026-04-05 | 进行中 | 等待客户确认 |

---

## 已完成
- 示例：初次拜访（2026-03-28）

"""

class CustomerDB:
    """客户数据库操作类"""
    
    def __init__(self, customers_dir: Path):
        self.customers_dir = customers_dir
    
    def to_pinyin_dir(self, customer_name: str) -> str:
        """
        将客户名称转换为拼音目录
        
        Args:
            customer_name: 客户名称
        
        Returns:
            拼音目录（如：gui-zhou-xx-jiu-ye）
        """
        # 汉字转拼音
        pinyin_list = lazy_pinyin(customer_name)
        return '-'.join(pinyin_list)
    
    def find_customer(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """
        查找客户（支持模糊匹配）
        
        Args:
            customer_name: 客户名称
        
        Returns:
            客户信息字典，包含 name, path, pinyin_dir
            如果未找到，返回 None
        """
        # 遍历所有客户目录
        if not self.customers_dir.exists():
            return None
        
        for pinyin_dir in self.customers_dir.iterdir():
            if not pinyin_dir.is_dir():
                continue
            
            # 遍历客户名称目录
            for customer_dir in pinyin_dir.iterdir():
                if not customer_dir.is_dir():
                    continue
                
                # 模糊匹配（包含即匹配）
                if customer_name in customer_dir.name or customer_dir.name in customer_name:
                    return {
                        "name": customer_dir.name,
                        "path": customer_dir,
                        "pinyin_dir": pinyin_dir.name
                    }
        
        return None
    
    def create_customer(self, customer_name: str) -> Dict[str, Any]:
        """
        创建客户档案
        
        Args:
            customer_name: 客户名称
        
        Returns:
            创建结果字典
        """
        from datetime import datetime
        
        # 生成拼音目录
        pinyin_dir = self.to_pinyin_dir(customer_name)
        customer_path = self.customers_dir / pinyin_dir / customer_name
        
        # 检查是否已存在
        if customer_path.exists():
            return {
                "success": False,
                "message": f"客户档案已存在：{customer_path}",
                "path": str(customer_path)
            }
        
        # 创建目录结构
        customer_path.mkdir(parents=True, exist_ok=True)
        (customer_path / "02-沟通记录").mkdir(exist_ok=True)
        (customer_path / "03-调研报告").mkdir(exist_ok=True)
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 创建客户画像文件
        profile_content = CUSTOMER_PROFILE_TEMPLATE.format(
            customer_name=customer_name,
            create_time=now,
            update_time=now,
            relative_path=f"{pinyin_dir}/{customer_name}/"
        )
        (customer_path / "01-客户画像.md").write_text(profile_content, encoding='utf-8')
        
        # 创建待办事项文件
        todos_content = TODOS_TEMPLATE.format(
            customer_name=customer_name,
            update_time=now
        )
        (customer_path / "04-待办事项.md").write_text(todos_content, encoding='utf-8')
        
        return {
            "success": True,
            "message": f"客户档案创建成功",
            "path": str(customer_path),
            "pinyin_dir": pinyin_dir
        }
    
    def read_profile(self, customer_path: Path) -> Optional[str]:
        """
        读取客户画像
        
        Args:
            customer_path: 客户档案路径
        
        Returns:
            画像内容（Markdown）
        """
        profile_file = customer_path / "01-客户画像.md"
        if profile_file.exists():
            return profile_file.read_text(encoding='utf-8')
        return None
    
    def list_communications(self, customer_path: Path) -> List[Dict[str, Any]]:
        """
        列出沟通记录
        
        Args:
            customer_path: 客户档案路径
        
        Returns:
            沟通记录列表
        """
        comm_dir = customer_path / "02-沟通记录"
        if not comm_dir.exists():
            return []
        
        communications = []
        for f in sorted(comm_dir.iterdir(), key=lambda x: x.name, reverse=True):
            if f.suffix == '.md':
                communications.append({
                    "name": f.stem,
                    "path": str(f),
                    "date": f.stem.split('-')[0] if '-' in f.stem else ""
                })
        
        return communications
    
    def list_researches(self, customer_path: Path) -> List[Dict[str, Any]]:
        """
        列出调研报告
        
        Args:
            customer_path: 客户档案路径
        
        Returns:
            调研报告列表
        """
        research_dir = customer_path / "03-调研报告"
        if not research_dir.exists():
            return []
        
        researches = []
        for f in sorted(research_dir.iterdir(), key=lambda x: x.name, reverse=True):
            if f.suffix == '.md':
                researches.append({
                    "name": f.stem,
                    "path": str(f),
                    "date": f.stem.split('-')[0] if '-' in f.stem else ""
                })
        
        return researches
    
    def read_todos(self, customer_path: Path) -> Optional[str]:
        """
        读取待办事项
        
        Args:
            customer_path: 客户档案路径
        
        Returns:
            待办事项内容
        """
        todos_file = customer_path / "04-待办事项.md"
        if todos_file.exists():
            return todos_file.read_text(encoding='utf-8')
        return None
    
    def delete_customer(self, customer_name: str) -> Dict[str, Any]:
        """
        删除客户档案（慎用！）
        
        Args:
            customer_name: 客户名称
        
        Returns:
            删除结果
        """
        customer = self.find_customer(customer_name)
        
        if not customer:
            return {
                "success": False,
                "message": f"未找到客户：{customer_name}"
            }
        
        # 删除目录
        import shutil
        shutil.rmtree(customer["path"])
        
        return {
            "success": True,
            "message": f"客户档案已删除：{customer_name}"
        }
