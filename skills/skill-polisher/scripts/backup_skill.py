#!/usr/bin/env python3
"""
Skill Backup Script
自动备份整个技能文件夹，确保修改前可回滚
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

def backup_skill(skill_path: str):
    """备份整个技能文件夹为 ZIP"""
    skill_dir = Path(skill_path)
    
    if not skill_dir.is_dir():
        print(f"❌ 错误：找不到技能目录 {skill_dir}")
        return None
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"SKILL_BACKUP_{timestamp}.zip"
    backup_path = skill_dir / backup_name
    temp_root = skill_dir.parent / f".{skill_dir.name}-backup-{timestamp}"
    stage_dir = temp_root / skill_dir.name
    
    # 执行备份：排除历史备份，避免 ZIP 递归膨胀
    shutil.copytree(
        skill_dir,
        stage_dir,
        ignore=shutil.ignore_patterns("SKILL_BACKUP_*.zip", "SKILL.md.backup.*"),
    )
    archive_base = backup_path.with_suffix("")
    shutil.make_archive(str(archive_base), "zip", root_dir=temp_root, base_dir=skill_dir.name)
    shutil.rmtree(temp_root)
    
    print(f"✅ 备份完成：{backup_path}")
    print(f"   原始目录：{skill_dir}")
    print(f"   备份文件：{backup_path}")
    
    return str(backup_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python backup_skill.py <skill-path>")
        print("示例：python backup_skill.py ~/.openclaw/skills/customer-research")
        sys.exit(1)
    
    backup_skill(sys.argv[1])
