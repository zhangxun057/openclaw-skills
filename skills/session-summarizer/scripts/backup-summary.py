#!/usr/bin/env python3
"""
会话摘要备份脚本
用途：在生成新摘要前，备份现有摘要文件
"""

import shutil
from pathlib import Path
from datetime import datetime

def backup_summary(date_str: str, workspace_dir: Path) -> str:
    """
    备份指定日期的摘要文件
    
    Args:
        date_str: 日期字符串（YYYY-MM-DD）
        workspace_dir: 工作空间目录
    
    Returns:
        备份文件路径，如果没有可备份的文件则返回 None
    """
    memory_dir = workspace_dir / "memory"
    source_file = memory_dir / f"session-summary-{date_str}.md"
    
    if not source_file.exists():
        return None
    
    # 创建备份文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = memory_dir / f"session-summary-{date_str}.backup.{timestamp}.md"
    
    # 执行备份
    shutil.copy2(source_file, backup_file)
    
    print(f"已备份：{source_file.name} -> {backup_file.name}")
    return str(backup_file)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python backup-summary.py <date>")
        print("示例：python backup-summary.py 2026-04-03")
        sys.exit(1)
    
    date_str = sys.argv[1]
    workspace_dir = Path.home() / ".openclaw/agents/guaiguaixia/workspace"
    
    backup_file = backup_summary(date_str, workspace_dir)
    if backup_file:
        print(f"备份完成：{backup_file}")
    else:
        print(f"没有找到可备份的文件：{date_str}")
