"""
朋友圈分析 - 分批处理脚本

读取 state/new_posts.json 和 checkpoint.json，按批次格式化帖子数据，
输出 LLM 提示词。接收 LLM 返回的 JSON 结果，写入 log 并更新 checkpoint。

用法：
  python analyze_batch.py              # 输出第1批（10条）的提示词
  python analyze_batch.py --batch 2    # 输出第2批
  python analyze_batch.py --batch 3 --batch-size 15
  python analyze_batch.py --apply      # 从 stdin 读取 LLM 结果，写入 log + 更新 checkpoint
"""

import json
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_DIR = r"C:\Users\44452\.openclaw\projects\moments-analysis"
SKILL_DIR = r"C:\Users\44452\.openclaw\skills\wechat-moments-analyzer"

BATCH_PROMPT_PREFIX = """对以下帖子逐条进行信息提取，每条输出一个 JSON 对象。

【输出格式】
{
  "wxid": "发帖人wxid",
  "nickname": "发帖人昵称",
  "post_type": "内容分类",
  "traits": ["画像特征"],
  "events": ["可记录事件"],
  "signals": ["销售信号"],
  "rels": ["互动用户wxid"]
}

如果是无信息量的噪声帖，输出 null。

【内容分类参考】
消费展示（酒、美食、高端消费）、商务动态（项目、合作、展会）、行业洞察（趋势分析、深度观点）、竞品信号（提到竞品）、人生里程碑（生日、结婚、升职）、情绪信号（感慨、庆祝）、社交互动（聚餐、出行）、广告营销、日常打卡等。不限于以上分类，按实际内容判断。

【画像特征提取方向】
关注能反映用户特征的信号，每条为不超过10字的短语：
- 消费实力：高端品牌、高价消费、商务宴请等
- 生活调性：品味偏好、审美取向、生活方式等
- 行业身份：职业特征、行业资源、专业深度等
- 社交特征：活跃度、社交圈层、人际关系等
- 白酒偏好：香型、价格带、消费场合、品牌认知等
- 性格特征：活跃/低调、务实/理想等
不强制填满，有线索才提取。

【事件提取】
记录有价值的动态，每条不超过15字：
- 消费事件：什么场景、什么产品
- 商务事件：什么合作、什么进展
- 行业事件：什么趋势、什么变化
- 关系事件：和谁互动、什么性质

【销售信号提取方向】
识别可能关联以下业务的信号（不是行动建议，是发现机会的线索）：
- 定制酒服务：庆功宴、公司活动、礼品需求、企业定制、宴席
- 创始合伙人/创业投资：创业动态、投资意向、资源对接

绝大多数事件没有销售信号，宁缺毋滥。只有当事件本身暗示了业务可能性时才标记。
例如："公司办周年庆" → ["企业定制酒"]；日常吃饭 → []

【规则】
1. 评论内容与正文合并分析，关系维度只记谁参与（wxid）
2. 特征/事件/销售信号都是高密度短语，不写完整句子
3. 严格输出 JSON，不要任何解释

【帖子数据】
"""


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=int, default=1, help='批次号（从1开始）')
    parser.add_argument('--batch-size', type=int, default=10, help='每批条数')
    parser.add_argument('--apply', action='store_true', help='从 stdin 读取 LLM 结果，写入 log')
    args = parser.parse_args()

    # 加载数据
    new_posts_path = os.path.join(PROJECT_DIR, 'state', 'new_posts.json')
    checkpoint_path = os.path.join(PROJECT_DIR, 'checkpoint.json')

    if not os.path.exists(new_posts_path):
        print("ERROR: new_posts.json 不存在，请先运行 prepare_data.py")
        sys.exit(1)

    with open(new_posts_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_posts = data.get('posts', [])

    # 加载 checkpoint
    analyzed_ids = []
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            ckpt = json.load(f)
            analyzed_ids = set(ckpt.get('analyzed_ids', []))
    else:
        analyzed_ids = set()

    # 过滤未分析的帖子
    pending = [p for p in all_posts if p.get('id') or p.get('username') not in analyzed_ids]

    # 检查是否按 id 分析过
    pending_by_id = []
    for p in pending:
        pid = p.get('id') or f"{p.get('username', '')}_{p.get('createTime', '')}"
        if pid not in analyzed_ids:
            pending_by_id.append((pid, p))

    if not pending_by_id:
        print("NO_PENDING: 所有帖子已分析完毕")
        sys.exit(0)

    if args.apply:
        # 读取 stdin 的 LLM 结果
        input_text = sys.stdin.read().strip()
        if not input_text:
            print("ERROR: stdin 为空")
            sys.exit(1)

        # 解析 JSON
        try:
            # 尝试直接解析
            results = json.loads(input_text)
            if not isinstance(results, list):
                results = [results]
        except json.JSONDecodeError:
            # 尝试提取 JSON 数组
            import re
            match = re.search(r'\[.*\]', input_text, re.DOTALL)
            if match:
                results = json.loads(match.group())
            else:
                print(f"ERROR: 无法解析 JSON，输入前200字符：{input_text[:200]}")
                sys.exit(1)

        # 写入 log
        today = '2026-04-16'  # 默认，可通过环境变量覆盖
        log_file = os.path.join(PROJECT_DIR, 'logs', f'{today}.jsonl')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        written = 0
        with open(log_file, 'a', encoding='utf-8') as f:
            for i, record in enumerate(results):
                if record is None:
                    continue
                # 兼容 actions → signals
                if 'actions' in record and 'signals' not in record:
                    record['signals'] = record.pop('actions')
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                written += 1

        # 更新 checkpoint
        batch_start = (args.batch - 1) * args.batch_size
        batch_posts = pending_by_id[batch_start:batch_start + args.batch_size]
        for pid, _ in batch_posts:
            analyzed_ids.add(pid)

        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump({
                'analyzed_ids': list(analyzed_ids),
                'total_analyzed': len(analyzed_ids),
                'last_updated': '2026-04-17'
            }, f, ensure_ascii=False, indent=2)

        print(f"APPLIED: 写入 {written} 条记录到 log，checkpoint 已更新（共 {len(analyzed_ids)} 条）")
        print(f"REMAINING: {len(pending_by_id) - args.batch_size} 条待分析")
        sys.exit(0)

    # 输出批次提示词
    batch_start = (args.batch - 1) * args.batch_size
    batch_posts = pending_by_id[batch_start:batch_start + args.batch_size]

    if not batch_posts:
        print(f"NO_MORE: 第 {args.batch} 批为空，共 {len(pending_by_id)} 条待分析，每批 {args.batch_size} 条")
        sys.exit(0)

    print(f"BATCH: {args.batch} | 本批 {len(batch_posts)} 条 | 已分析 {len(analyzed_ids)} | 剩余 {len(pending_by_id) - len(batch_posts)}")
    print()
    print(BATCH_PROMPT_PREFIX)

    for i, (pid, p) in enumerate(batch_posts, 1):
        wxid = p.get('username', '')
        nick = p.get('nickname', '')
        desc = (p.get('contentDesc', '') or '').strip() or '无文字'
        comments = p.get('comments', [])
        likes = p.get('likes_count', 0)
        media = p.get('media_count', 0)
        comment_text = '; '.join([c.get('content', '') for c in comments]) if comments else '无'

        print(f"\n帖子{i}:")
        print(f"发帖人: {nick} ({wxid})")
        print(f"正文: {desc}")
        print(f"评论: {comment_text}")
        print(f"点赞数: {likes}")
        print(f"媒体数: {media}")

    print(f"\n=== END BATCH {args.batch} ===")


if __name__ == '__main__':
    main()
