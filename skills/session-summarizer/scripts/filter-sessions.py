#!/usr/bin/env python3
"""
会话筛选脚本
用途：快速读取会话元数据，筛选出有价值的会话
"""

import json
from pathlib import Path
from datetime import datetime

def read_session_metadata(session_file: Path) -> dict:
    """
    读取会话文件的元数据（不读取完整内容）
    
    Returns:
        {
            "file": str,
            "first_message": str,
            "last_message": str,
            "message_count": int,
            "time_range": str,
            "keywords": list
        }
    """
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return None
        
        # 读取第一条和最后一条消息
        first_msg = json.loads(lines[0].strip())
        last_msg = json.loads(lines[-1].strip())
        
        # 提取关键词（前 100 字符）
        first_text = first_msg.get('text', '')[:100]
        
        return {
            "file": session_file.name,
            "first_message": first_text,
            "last_message": last_msg.get('text', '')[:100],
            "message_count": len(lines),
            "time_range": f"{first_msg.get('time', '?')} ~ {last_msg.get('time', '?')}",
            "keywords": extract_keywords(first_text)
        }
    except Exception as e:
        print(f"读取失败 {session_file.name}: {e}")
        return None

def extract_keywords(text: str) -> list:
    """
    从文本中提取关键词
    """
    keywords = []
    
    # 业务相关关键词
    business_terms = ['客户', '调研', '业务', '决策', '技能', '开发', '复盘', '日记']
    for term in business_terms:
        if term in text:
            keywords.append(term)
    
    # 技术调试关键词（用于过滤）
    tech_terms = ['API', 'Key', 'Referer', 'HeatMap', 'constructor', 'error']
    for term in tech_terms:
        if term in text:
            keywords.append(f"[技术]{term}")
    
    return keywords

def should_include_session(metadata: dict) -> bool:
    """
    判断是否应该包含该会话
    
    保留标准：
    - 包含业务关键词
    - 消息数 > 5（过滤短对话）
    
    过滤标准：
    - 纯技术调试（只有技术关键词，没有业务关键词）
    - 消息数 <= 2（太短）
    """
    if metadata['message_count'] <= 2:
        return False
    
    keywords = metadata['keywords']
    has_business = any(k not in ['[技术]API', '[技术]Key', '[技术]Referer', '[技术]HeatMap', '[技术]constructor', '[技术]error'] for k in keywords)
    has_tech = any(k.startswith('[技术]') for k in keywords)
    
    # 纯技术调试，过滤
    if has_tech and not has_business:
        return False
    
    # 有业务内容，保留
    if has_business:
        return True
    
    # 默认保留（不确定时不过滤）
    return True

def filter_sessions(chat_logs_dir: Path, date_str: str) -> list:
    """
    筛选指定日期的会话
    
    Returns:
        包含会话元数据的列表
    """
    pattern = f"{date_str}_*.jsonl"
    session_files = list(chat_logs_dir.glob(pattern))
    
    included = []
    excluded = []
    
    for session_file in session_files:
        metadata = read_session_metadata(session_file)
        if metadata is None:
            continue
        
        if should_include_session(metadata):
            included.append(metadata)
        else:
            excluded.append(metadata)
    
    return {
        "included": included,
        "excluded": excluded,
        "total": len(session_files),
        "included_count": len(included),
        "excluded_count": len(excluded)
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python filter-sessions.py <date>")
        print("示例：python filter-sessions.py 2026-04-03")
        sys.exit(1)
    
    date_str = sys.argv[1]
    chat_logs_dir = Path.home() / ".openclaw/chat-logs/guaiguaixia"
    
    result = filter_sessions(chat_logs_dir, date_str)
    
    print(f"\n=== 会话筛选报告 · {date_str} ===")
    print(f"总会话数：{result['total']}")
    print(f"保留：{result['included_count']}")
    print(f"过滤：{result['excluded_count']}")
    
    if result['included']:
        print(f"\n保留的会话:")
        for session in result['included']:
            print(f"  - {session['file']}: {session['message_count']}条消息，{session['time_range']}")
            print(f"    关键词：{', '.join(session['keywords'])}")
    
    if result['excluded']:
        print(f"\n过滤的会话:")
        for session in result['excluded']:
            print(f"  - {session['file']}: {session['message_count']}条消息")
