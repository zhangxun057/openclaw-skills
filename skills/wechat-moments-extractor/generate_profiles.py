"""从 JSONL log 生成 Profile Markdown 文档"""
import json, os, sys, argparse
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

LOG_DIR = r'C:\Users\44452\.openclaw\projects\moments-analysis\logs'
PROFILES_DIR = r'C:\Users\44452\.openclaw\projects\moments-analysis\profiles'


def load_log(date_str):
    path = os.path.join(LOG_DIR, f"{date_str}.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"日志文件不存在: {path}")
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def aggregate_profiles(records):
    """按 wxid+nickname 聚合，合并4个维度结果"""
    # 只处理有 post 内容的记录（排除纯日志条目）
    posts = [r for r in records if 'content' in r or 'wxid' in r]

    # 按 wxid 聚合
    people = defaultdict(list)
    for r in posts:
        wxid = r.get('wxid', '')
        people[wxid].append(r)

    return people


def format_profile(wxid, entries, date_str):
    lines = []
    # 取第一条的 nickname
    nickname = entries[0].get('nickname', wxid)
    lines.append(f"## {nickname} ({wxid})")

    for entry in entries:
        content = entry.get('content', entry.get('contentDesc', ''))
        post_type = entry.get('post_type', '')
        events = entry.get('events', [])
        traits = entry.get('traits', {})
        signals = entry.get('signals', [])

        lines.append(f"- **原文**：{content}")
        lines.append(f"- **post_type**：{post_type}")
        lines.append(f"- **events**：{events}")
        lines.append(f"- **traits**：{traits}")
        lines.append(f"- **signals**：{signals}")
        lines.append("")

    lines.append("---")
    return '\n'.join(lines)


def generate(date_str):
    records = load_log(date_str)
    people = aggregate_profiles(records)

    os.makedirs(PROFILES_DIR, exist_ok=True)
    out_path = os.path.join(PROFILES_DIR, f"{date_str}_profiles.md")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"# 朋友圈 Profile - {date_str}\n\n")
        for wxid, entries in people.items():
            f.write(format_profile(wxid, entries, date_str))
            f.write('\n\n')

    print(f"生成完成: {out_path}（{len(people)} 人）")
    return out_path


def main():
    parser = argparse.ArgumentParser(description='从 JSONL log 生成 Profile 文档')
    parser.add_argument('--date', type=str, required=True, help='日期，格式 YYYY-MM-DD')
    args = parser.parse_args()
    generate(args.date)


if __name__ == '__main__':
    main()
