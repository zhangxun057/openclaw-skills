#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Backup Script
自动备份 Skill 文件，保留最近 5 个版本
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

def backup_skill(skill_path: str, max_backups: int = 5) -> str:
    """
    备份 skill 的 SKILL.md 文件
    
    Args:
        skill_path: skill 目录路径
        max_backups: 最多保留的备份数量
        
    Returns:
        备份文件路径
    """
    skill_dir = Path(skill_path)
    skill_file = skill_dir / "SKILL.md"
    
    if not skill_file.exists():
        print(f"❌ SKILL.md not found in {skill_path}")
        sys.exit(1)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = skill_dir / f"SKILL.md.backup.{timestamp}"
    
    # 执行备份
    shutil.copy2(skill_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # 清理旧备份（保留最近 max_backups 个）
    cleanup_old_backups(skill_dir, max_backups)
    
    return str(backup_file)


def cleanup_old_backups(skill_dir: Path, max_backups: int):
    """清理旧备份，保留最近 max_backups 个"""
    backup_files = list(skill_dir.glob("SKILL.md.backup.*"))
    
    if len(backup_files) > max_backups:
        # 按修改时间排序，删除最旧的
        backup_files.sort(key=lambda x: x.stat().st_mtime)
        
        files_to_delete = backup_files[:-max_backups]
        for file in files_to_delete:
            file.unlink()
            print(f"🗑️ Deleted old backup: {file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python backup_skill.py <skill-path>")
        print("Example: python backup_skill.py C:\\Users\\...\\skills\\skill-name")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    backup_file = backup_skill(skill_path)
    print(f"\n✅ Backup complete: {backup_file}")


if __name__ == "__main__":
    main()
