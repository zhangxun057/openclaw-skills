#!/usr/bin/env python3
"""
全量数据下载脚本
功能：下载联系人、聊天记录、群聊、朋友圈、媒体文件
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
from pathlib import Path
import time

API_BASE = "http://127.0.0.1:5032"

def check_api():
    """检查API是否可用"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def download_with_retry(url, params=None, max_retries=3, timeout=60):
    """带重试的下载"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  [WARN] HTTP {response.status_code}, 重试...")
        except Exception as e:
            print(f"  [WARN] 请求失败: {e}, 重试...")
        time.sleep(2)
    return None

def download_contacts(output_dir):
    """下载所有联系人"""
    print("\n[INFO] 正在下载联系人列表...")
    
    url = f"{API_BASE}/api/v1/contacts"
    data = download_with_retry(url, {"limit": 5000})
    
    if not data:
        print("[ERROR] 联系人下载失败")
        return []
    
    contacts = data.get('contacts', [])
    
    # 保存到文件
    contacts_file = os.path.join(output_dir, "contacts", "all_contacts.json")
    os.makedirs(os.path.dirname(contacts_file), exist_ok=True)
    with open(contacts_file, 'w', encoding='utf-8') as f:
        json.dump({"count": len(contacts), "contacts": contacts}, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 下载了 {len(contacts)} 个联系人")
    return contacts

def download_sessions(output_dir):
    """下载所有会话"""
    print("\n[INFO] 正在下载会话列表...")
    
    url = f"{API_BASE}/api/v1/sessions"
    data = download_with_retry(url, {"limit": 5000})
    
    if not data:
        print("[ERROR] 会话下载失败")
        return []
    
    sessions = data.get('sessions', [])
    
    # 保存到文件
    sessions_file = os.path.join(output_dir, "sessions.json")
    with open(sessions_file, 'w', encoding='utf-8') as f:
        json.dump({"count": len(sessions), "sessions": sessions}, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 下载了 {len(sessions)} 个会话")
    return sessions

def download_messages_batch(talker, output_dir, limit=500):
    """下载单个联系人的消息"""
    url = f"{API_BASE}/api/v1/messages"
    params = {
        "talker": talker,
        "limit": limit
    }
    
    data = download_with_retry(url, params, timeout=120)
    if data:
        return data.get('messages', [])
    return []

def download_all_messages(sessions, output_dir):
    """下载所有聊天记录"""
    print(f"\n[INFO] 正在下载聊天记录（共{len(sessions)}个会话）...")
    
    messages_dir = os.path.join(output_dir, "messages")
    os.makedirs(messages_dir, exist_ok=True)
    
    total_messages = 0
    for i, session in enumerate(sessions, 1):
        talker = session.get('username', '')
        display_name = session.get('displayName', talker)
        msg_count = session.get('messageCount', 0)
        
        if not talker or msg_count == 0:
            continue
        
        print(f"  [{i}/{len(sessions)}] {display_name} ({msg_count}条消息)...", end=" ")
        
        # 下载消息
        messages = download_messages_batch(talker, output_dir, limit=min(msg_count, 1000))
        
        if messages:
            # 保存到文件
            safe_name = "".join(c for c in display_name if c.isalnum() or c in '_-').strip()
            if not safe_name:
                safe_name = talker.replace('@', '_').replace('.', '_')
            
            msg_file = os.path.join(messages_dir, f"{safe_name}_{talker}.json")
            with open(msg_file, 'w', encoding='utf-8') as f:
                json.dump({"messages": messages}, f, ensure_ascii=False, indent=2)
            
            total_messages += len(messages)
            print(f"[OK] {len(messages)}条")
        else:
            print("[SKIP]")
    
    print(f"[OK] 共下载 {total_messages} 条消息")
    return total_messages

def download_media_files(messages, output_dir, contact_name, talker):
    """下载媒体文件（图片、视频、语音）"""
    media_dir = os.path.join(output_dir, "media", f"{contact_name}_{talker}")
    os.makedirs(media_dir, exist_ok=True)
    
    images_dir = os.path.join(media_dir, "images")
    videos_dir = os.path.join(media_dir, "videos")
    voices_dir = os.path.join(media_dir, "voices")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    os.makedirs(voices_dir, exist_ok=True)
    
    downloaded = {"images": 0, "videos": 0, "voices": 0}
    
    for msg in messages:
        content = msg.get('content', '')
        parsed = msg.get('parsedContent', '')
        
        # 图片
        if '[图片]' in parsed or 'img' in content.lower():
            # 这里需要根据实际API返回的媒体URL下载
            pass
        
        # 视频
        if '[视频]' in parsed or 'video' in content.lower():
            pass
        
        # 语音
        if '[语音]' in parsed or 'voicemsg' in content.lower():
            pass
    
    return downloaded

def download_moments(output_dir, start_date=None, end_date=None):
    """下载朋友圈数据（使用新版 SNS 导出 API，支持时间范围）"""
    print("\n[INFO] 正在下载朋友圈数据...")
    
    # 新版 WeFlow 使用 SNS 导出 API
    url = f"{API_BASE}/api/v1/sns/export"
    
    # 构建导出请求
    export_dir = os.path.join(output_dir, "moments_export")
    os.makedirs(export_dir, exist_ok=True)
    
    payload = {
        "outputDir": export_dir,
        "format": "html",
        "exportMedia": True,
        "exportImages": True,
        "exportLivePhotos": True,
        "exportVideos": True
    }
    
    # 添加时间范围参数
    if start_date:
        payload["start"] = start_date
        print(f"  开始日期: {start_date}")
    if end_date:
        payload["end"] = end_date
        print(f"  结束日期: {end_date}")
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                post_count = data.get('postCount', 0)
                file_path = data.get('filePath', '')
                print(f"[OK] 导出 {post_count} 条朋友圈到: {file_path}")
                
                # 保存导出信息
                info_file = os.path.join(output_dir, "moments", "export_info.json")
                os.makedirs(os.path.dirname(info_file), exist_ok=True)
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return data
            else:
                print(f"[WARN] 导出失败: {data.get('error', '未知错误')}")
        else:
            print(f"[WARN] HTTP {response.status_code}")
    except Exception as e:
        print(f"[WARN] 朋友圈导出失败: {e}")
    
    return {}

def generate_data_report(output_dir, contacts, sessions, total_messages):
    """生成数据下载报告"""
    report = {
        "download_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "statistics": {
            "total_contacts": len(contacts),
            "total_sessions": len(sessions),
            "total_messages": total_messages,
            "active_sessions": len([s for s in sessions if s.get('messageCount', 0) > 0])
        },
        "top_contacts": sorted(sessions, key=lambda x: x.get('messageCount', 0), reverse=True)[:20]
    }
    
    report_file = os.path.join(output_dir, "download_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] 数据报告已保存: {report_file}")
    return report

def main():
    parser = argparse.ArgumentParser(description="微信全量数据下载")
    parser.add_argument("--output", default="./微信数据", help="输出目录")
    parser.add_argument("--include-media", action="store_true", help="下载媒体文件")
    parser.add_argument("--include-moments", action="store_true", help="下载朋友圈")
    parser.add_argument("--limit", type=int, default=0, help="限制下载联系人数（0=全部）")
    parser.add_argument("--start-date", type=str, help="朋友圈开始日期 (YYYYMMDD)")
    parser.add_argument("--end-date", type=str, help="朋友圈结束日期 (YYYYMMDD)")
    args = parser.parse_args()
    
    # 检查API
    if not check_api():
        print("[ERROR] WeFlow API未运行，请先启动:")
        print("  python weflow_manager.py --action start --wait-wechat")
        return
    
    # 准备输出目录
    output_dir = os.path.expanduser(args.output)
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== 微信全量数据下载 ===")
    print(f"输出目录: {output_dir}")
    
    # 1. 下载联系人
    contacts = download_contacts(output_dir)
    
    # 2. 下载会话列表
    sessions = download_sessions(output_dir)
    
    # 限制数量
    if args.limit > 0:
        sessions = sessions[:args.limit]
        print(f"[INFO] 限制下载前{args.limit}个会话")
    
    # 3. 下载聊天记录
    total_messages = download_all_messages(sessions, output_dir)
    
    # 4. 下载朋友圈
    if args.include_moments:
        download_moments(output_dir, args.start_date, args.end_date)
    
    # 5. 生成报告
    report = generate_data_report(output_dir, contacts, sessions, total_messages)
    
    print("\n=== 下载完成 ===")
    print(f"联系人: {report['statistics']['total_contacts']}")
    print(f"会话: {report['statistics']['total_sessions']}")
    print(f"消息: {report['statistics']['total_messages']}")
    print(f"数据保存: {output_dir}")

if __name__ == "__main__":
    main()
