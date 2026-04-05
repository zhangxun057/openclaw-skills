#!/usr/bin/env python3
"""
Skill Backup Script
自动备份技能文件，确保修改前可回滚
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

def backup_skill(skill_path: str):
    """备份技能的 SKILL.md 文件"""
    skill_dir = Path(skill_path)
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        print(f"❌ 错误：找不到 {skill_md}")
        return None
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"SKILL.md.backup.{timestamp}"
    backup_path = skill_dir / backup_name
    
    # 执行备份
    shutil.copy2(skill_md, backup_path)
    
    print(f"✅ 备份完成：{backup_path}")
    print(f"   原始文件：{skill_md}")
    print(f"   备份文件：{backup_path}")
    
    return str(backup_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python backup_skill.py <skill-path>")
        print("示例：python backup_skill.py ~/.openclaw/skills/customer-research")
        sys.exit(1)
    
    backup_skill(sys.argv[1])
