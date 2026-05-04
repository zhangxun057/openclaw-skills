# -*- coding: utf-8 -*-
"""
scan_session_errors.py
扫描 agent session 文件，提取工具执行层和模型调用层的异常记录。

输入：agent 名 + 日期
输出：结构化异常列表（每条含：时间、层级、工具/模型、问题类型、描述、文件名）
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import json
import os
import re
from datetime import datetime

def get_target_session_files(agent: str, date: str):
    """
    枚举目标 agent 的 sessions 目录，找出日期范围内的 session 文件。
    
    文件名格式：
      - uuid.jsonl                          （正常文件）
      - uuid.jsonl.reset.2026-04-21T00-07-59.374Z  （reset 快照）
      - uuid.jsonl.deleted.2026-04-20T21-23-28.126Z
      - uuid.jsonl.lock
      - uuid.jsonl.bak-1234567890
    
    判断方式：从文件名中提取 date 字符串，匹配目标日期。
    日期格式：reset/deleted/bak 等后缀中的 YYYY-MM-DD
    """
    sessions_dir = rf"C:\Users\44452\.openclaw\agents\{agent}\sessions"
    target_date = date  # e.g. '2026-04-21'
    
    if not os.path.exists(sessions_dir):
        print(f"WARNING: {sessions_dir} not found")
        return []

    target_files = []
    for fname in os.listdir(sessions_dir):
        # 跳过非 session 文件
        if not fname.endswith('.jsonl'):
            continue
        # 跳过 lock 文件
        if fname.endswith('.lock'):
            continue
        # 从文件名提取日期标签
        # 格式: uuid.jsonl.reset.YYYY-MM-DDTHH-MM-SS.fffZ
        #       uuid.jsonl.deleted.YYYY-MM-DDTHH-MM-SS.fffZ
        date_match = re.search(r'reset\.(\d{4}-\d{2}-\d{2})', fname)
        if not date_match:
            date_match = re.search(r'deleted\.(\d{4}-\d{2}-\d{2})', fname)
        if not date_match:
            # 没有后缀的 .jsonl，用 mtime 作为参考，但不排除
            # 只要文件名不含 reset/deleted 就可能是正常 session
            pass
        
        if date_match:
            file_date = date_match.group(1)
            if file_date != target_date:
                continue
        else:
            # 无日期后缀的文件（正常 session），检查 mtime
            fp = os.path.join(sessions_dir, fname)
            mtime = datetime.fromtimestamp(os.path.getmtime(fp))
            if mtime.strftime('%Y-%m-%d') != target_date:
                continue
        
        fp = os.path.join(sessions_dir, fname)
        if os.path.getsize(fp) > 0:
            target_files.append(fp)
    
    return target_files


def scan_session_errors(agent: str, date: str):
    target_files = get_target_session_files(agent, date)
    if not target_files:
        print(f"运行问题记录：0个（无）  # 无 session 文件")
        return []

    TOOL_ERROR_KEYWORDS = [
        'SyntaxError', 'UnicodeDecodeError', 'UnicodeEncodeError',
        'PathNotFound', 'TerminatorExpectedAtEndOfString',
        'FileNotFoundError', 'IsADirectoryError',
        "'gbk' codec", 'gbk codec',
        'InvalidEndOfLine', 'UnexpectedToken',
        'ParserError', 'OpenError',
        'Command failed', 'non-zero exit',
    ]
    MODEL_ERROR_KEYWORDS = [
        'idle timeout', 'timed out', 'timeout',
        'rate limit', '429',
    ]
    NETWORK_ERROR_KEYWORDS = [
        'fetch failed', 'Connection refused', 'ECONNREFUSED',
        'ConnectionResetError', 'NetworkError',
        'ETIMEDOUT', 'ENOTFOUND',
    ]
    all_keywords = TOOL_ERROR_KEYWORDS + MODEL_ERROR_KEYWORDS + NETWORK_ERROR_KEYWORDS

    def classify(text: str):
        t = text.lower()
        for kw in MODEL_ERROR_KEYWORDS:
            if kw.lower() in t:
                return '🟡模型', kw
        for kw in NETWORK_ERROR_KEYWORDS:
            if kw.lower() in t:
                return '⚠️网络', kw
        for kw in TOOL_ERROR_KEYWORDS:
            if kw.lower() in t:
                return '🔴工具', kw
        return '🔴工具', 'unknown'

    errors = []
    
    for fp in target_files:
        fname = os.path.basename(fp)
        
        try:
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except Exception as ex:
            errors.append({
                'seq': len(errors) + 1,
                'time': '??:??',
                'level': '🔴工具',
                'tool': 'file_read',
                'type': '读取失败',
                'desc': f'无法读取 session 文件: {ex}',
                'file': fname,
            })
            continue

        for line in lines:
            if not line.strip():
                continue
            try:
                obj = json.loads(line.strip())
            except:
                continue

            obj_type = obj.get('type', '')
            record = None

            # 1. toolResult isError=True
            if obj_type == 'toolResult' and obj.get('isError', False):
                content = obj.get('content', '')
                if isinstance(content, list):
                    text = ' '.join(c.get('text', '')[:300] for c in content if c.get('type') == 'text')
                else:
                    text = str(content)[:300]
                if any(kw in text for kw in all_keywords):
                    level, err_type = classify(text)
                    record = {
                        'seq': len(errors) + 1,
                        'time': '',
                        'level': level,
                        'tool': obj.get('name', 'exec'),
                        'type': err_type,
                        'desc': text[:150],
                        'file': fname,
                    }

            # 2. toolCall with error keyword in args
            elif obj_type == 'toolCall':
                args_str = json.dumps(obj.get('arguments', {}), ensure_ascii=False)
                if any(kw in args_str for kw in ['PathNotFound', 'FileNotFoundError', 'SyntaxError']):
                    record = {
                        'seq': len(errors) + 1,
                        'time': '',
                        'level': '🔴工具',
                        'tool': obj.get('name', 'unknown'),
                        'type': '路径/文件错误',
                        'desc': args_str[:150],
                        'file': fname,
                    }

            # 3. message with error signal
            elif obj_type == 'message':
                msg = obj.get('message', {})
                content = msg.get('content', '')
                if isinstance(content, list):
                    for c in content:
                        if c.get('type') == 'text':
                            text = c.get('text', '')
                            if any(kw in text for kw in all_keywords):
                                level, err_type = classify(text)
                                record = {
                                    'seq': len(errors) + 1,
                                    'time': '',
                                    'level': level,
                                    'tool': 'model',
                                    'type': err_type,
                                    'desc': text[:150],
                                    'file': fname,
                                }
                                break
                elif isinstance(content, str) and any(kw in content for kw in all_keywords):
                    level, err_type = classify(content)
                    record = {
                        'seq': len(errors) + 1,
                        'time': '',
                        'level': level,
                        'tool': 'model',
                        'type': err_type,
                        'desc': content[:150],
                        'file': fname,
                    }

            if record:
                errors.append(record)

    return errors


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python scan_session_errors.py <agent> <date>")
        print(" e.g.: python scan_session_errors.py main 2026-04-21")
        sys.exit(1)

    agent = sys.argv[1]
    date  = sys.argv[2]

    errors = scan_session_errors(agent, date)

    if not errors:
        print("运行问题记录：0个（无）")
        sys.exit(0)

    print("| # | 层级 | 工具/模型 | 问题类型 | 描述 | Session文件 |")
    print("|---|------|----------|---------|------|------------|")
    for e in errors:
        desc = e['desc'].replace('|', '\\|').replace('\n', ' ')[:80]
        print(f"| {e['seq']} | {e['level']} | {e['tool']} | {e['type']} | {desc} | {e['file']} |")

    tool  = sum(1 for e in errors if '工具' in e['level'])
    model = sum(1 for e in errors if '模型' in e['level'])
    net   = sum(1 for e in errors if '网络' in e['level'])
    print(f"\n运行问题记录：{len(errors)}个（🔴{tool} / 🟡{model} / ⚠️{net}）")
    print(f"涉及 session：{len(set(e['file'] for e in errors))} 个")