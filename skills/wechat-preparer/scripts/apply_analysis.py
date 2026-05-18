#!/usr/bin/env python3
"""
朋友圈模型分析结果落库工具
功能：读取 state/new_posts.json 和模型分析结果，写入 logs/customers/checkpoint，可继续生成报告。
用法：
  python apply_analysis.py --analysis-file state/analysis_result.json
  python apply_analysis.py --analysis-file state/analysis_result.json --report
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def get_post_id(post):
    return str(post.get("_post_id") or post.get("id") or post.get("tid") or "")


def format_post_time(post):
    raw = (
        post.get("createTime")
        or post.get("create_time")
        or post.get("created_at")
        or post.get("time")
    )
    if raw in (None, ""):
        return ""
    try:
        if isinstance(raw, str) and not raw.strip().isdigit():
            text = raw.strip().replace("T", " ").replace("Z", "")
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M"):
                try:
                    return datetime.strptime(text[:19], fmt).strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
            return text[:19]
        ts = float(raw)
        if ts > 100000000000:
            ts = ts / 1000
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(raw)[:19]


def get_like_count(post):
    if isinstance(post.get("likes_count"), int):
        return post["likes_count"]
    likes = post.get("likes", [])
    return len(likes) if isinstance(likes, list) else 0


def get_comment_count(post):
    if isinstance(post.get("comments_count"), int):
        return post["comments_count"]
    comments = post.get("comments", [])
    return len(comments) if isinstance(comments, list) else 0


def get_media_count(post):
    if isinstance(post.get("media_count"), int):
        return post["media_count"]
    media = post.get("media", [])
    return len(media) if isinstance(media, list) else 0


def get_post_text(post):
    return str(post.get("contentDesc") or post.get("content") or post.get("text") or "").strip()


def load_whitelist(base):
    data = load_json(os.path.join(base, "customers", "whitelist.json"), default=[])
    if isinstance(data, list):
        return set(str(x) for x in data)
    if isinstance(data, dict):
        return set(str(x) for x in data.get("wxids", []))
    return set()


def parse_rels(post):
    rels = []
    self_id = str(post.get("wxid") or post.get("username") or "")
    self_nick = str(post.get("nickname") or "")

    def add_rel(item, action):
        person_id = ""
        person_name = ""
        text = ""
        if isinstance(item, str):
            match = re.search(r"nickname=([^,}]+)", item)
            person_name = match.group(1).strip() if match else item[:20].strip()
            text_match = re.search(r"(?:content|text|comment)=([^,}]+)", item)
            text = text_match.group(1).strip() if text_match else ""
        elif isinstance(item, dict):
            person_id = str(item.get("wxid") or item.get("username") or "")
            person_name = str(item.get("nickname") or item.get("username") or item.get("wxid") or "")
            text = str(item.get("content") or item.get("text") or item.get("comment") or "")
        if not person_id and not person_name:
            return
        if (person_id and person_id == self_id) or (person_name and person_name == self_nick):
            return
        rel = {
            "person_id": person_id,
            "person": person_name,
            "action": action,
        }
        if text:
            rel["text"] = text[:80]
        rels.append(rel)

    likes = post.get("likes", [])
    if isinstance(likes, list):
        for item in likes:
            add_rel(item, "like")

    comments = post.get("comments", [])
    if isinstance(comments, list):
        for item in comments:
            add_rel(item, "comment")

    seen = set()
    result = []
    for rel in rels:
        key = (rel.get("person_id"), rel.get("person"), rel.get("action"), rel.get("text", ""))
        if key not in seen:
            seen.add(key)
            result.append(rel)
    return result


def normalize_list(value, limit=8, item_len=60):
    if not isinstance(value, list):
        return []
    return [str(item)[:item_len] for item in value if item][:limit]


BAD_EVENT_PREFIXES = ("[文件]", "[音乐]", "[链接]", "[小程序]", "[视频号]", "[图片]", "[视频]", "[语音消息]")
BAD_EVENT_PATTERNS = (
    "quote:",
    "| quote",
    "邀请你加入飞书视频会议",
    "邀请您参加腾讯会议",
    "会议链接",
    "会议 ID",
    "http://",
    "https://",
)
BAD_EVENT_STARTS = (
    "洵总",
    "您看",
    "你看看",
    "麻烦",
    "好的",
    "收到",
    "默认",
    "我觉得",
    "我感觉",
    "我问的是",
    "只是",
)
QUESTION_PATTERNS = ("是不是", "能不能", "要不要", "需不需要", "有没有", "怎么", "什么")


def is_bad_event(text):
    if not text:
        return True
    if text.startswith(BAD_EVENT_PREFIXES):
        return True
    if text.startswith(BAD_EVENT_STARTS):
        return True
    if any(pattern in text for pattern in BAD_EVENT_PATTERNS):
        return True
    if any(pattern in text for pattern in QUESTION_PATTERNS):
        return True
    stripped = text.rstrip()
    if stripped.endswith(("?", "？", "吗", "么", "呢", "吧")):
        return True
    if len(stripped) > 60:
        return True
    return False


def normalize_events(value, limit=20, item_len=60):
    if not isinstance(value, list):
        return []
    result = []
    seen = set()
    for item in value:
        text = str(item or "").strip()[:item_len]
        if is_bad_event(text):
            continue
        if text in seen:
            continue
        seen.add(text)
        result.append(text)
        if len(result) >= limit:
            break
    return result


def normalize_traits(value):
    if not isinstance(value, dict):
        return {}
    return {str(k): str(v)[:30] for k, v in value.items() if v}


def normalize_post_type(value):
    return value if value in {"转发内容", "输出观点", "分享动态", "广告营销", "其他"} else "其他"


def normalize_mood(value):
    allowed = {"开心", "失落", "焦虑", "兴奋", "平静", "无法判断"}
    return value if value in allowed else "无法判断"


PROMO_RE = re.compile(
    r"优惠|促销|折扣|购买|下单|到店|欢迎|垂询|扫码|进群|福利官|买\d*送|"
    r"活动[一二三四五六七八九\d]|招商|代理|加盟|开业大促|试营业|专属福利|"
    r"产品体系|合作低门槛|运营高利润|限时|免费体验|畅饮|刚发了篇文章|"
    r"yyds\.co|咖啡|美式|拿铁|"
    r"品牌|产品|市场|招商|酒业|集团|国台|董酒|丹泉|净台|青酒|刘伶醉|"
    r"茅台|酱香|美酒|洞藏|酿造|致敬每一位|通透你我他"
)
DRINKING_RE = re.compile(r"喝酒|小酌|慢酌|微醺|啤酒|红酒|葡萄酒|威士忌|酒局|饭局|晚宴|午宴|宴请|聚会.*酒|酒.*聚会")
SOCIAL_RE = re.compile(r"聚会|同学|校友|朋友|团建|生日|亲子")
LIFESTYLE_RE = re.compile(r"户外|露营|徒步|骑行|登山|爬山|跑步|马拉松|斯巴达|健身|旅行|旅游|出游|露营|烧烤")


def lifestyle_media_priority(post, item):
    media_count = get_media_count(post)
    if not media_count:
        return "none"
    if item.get("post_type") in {"广告营销", "转发内容"}:
        return "none"

    text = get_post_text(post)
    if not text or PROMO_RE.search(text):
        return "none"

    if re.search(r"徒步.*公里|走了.*步|黄山|上方山|云水洞", text):
        return "none"

    if DRINKING_RE.search(text):
        return "strong"

    if SOCIAL_RE.search(text) and media_count >= 2:
        if len(text) <= 40 or "圆满收官" in text:
            return "optional"

    if LIFESTYLE_RE.search(text) and media_count >= 2:
        if len(text) <= 35 or "圆满收官" in text:
            return "optional"

    return "none"


def image_trigger_level(post, item, whitelist):
    wxid = post.get("wxid") or post.get("username") or ""
    if wxid in whitelist:
        return "strong"
    if get_like_count(post) + get_comment_count(post) >= 3:
        return "strong"
    if item.get("signals") and get_media_count(post):
        return "strong"
    return lifestyle_media_priority(post, item)


def should_analyze_image(post, item, whitelist):
    return image_trigger_level(post, item, whitelist) != "none"


def build_record(post, item, whitelist):
    item = item if isinstance(item, dict) else {}
    normalized = {
        "post_type": normalize_post_type(item.get("post_type")),
        "mood": normalize_mood(item.get("mood")),
        "traits": normalize_traits(item.get("traits")),
        "events": normalize_events(item.get("events"), limit=20, item_len=60),
        "signals": normalize_list(item.get("signals"), limit=6, item_len=30),
    }
    image_trigger = image_trigger_level(post, normalized, whitelist)

    return {
        "post_id": get_post_id(post),
        "post_time": format_post_time(post),
        "wxid": post.get("wxid") or post.get("username") or "",
        "nickname": post.get("nickname") or "",
        "post_type": normalized["post_type"],
        "mood": normalized["mood"],
        "traits": normalized["traits"],
        "events": normalized["events"],
        "signals": normalized["signals"],
        "rels": parse_rels(post),
        "image_trigger": image_trigger,
    }


def load_existing_jsonl_ids(path):
    ids = set()
    if not os.path.exists(path):
        return ids
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                if record.get("post_id"):
                    ids.add(record["post_id"])
            except Exception:
                pass
    return ids


def append_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing_ids = load_existing_jsonl_ids(path)
    written = 0
    with open(path, "a", encoding="utf-8") as f:
        for record in records:
            pid = record.get("post_id")
            if not pid or pid in existing_ids:
                continue
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            existing_ids.add(pid)
            written += 1
    return written


def relation_key(edge):
    return "|".join([
        str(edge.get("from_id") or edge.get("from_name") or ""),
        str(edge.get("relation") or ""),
        str(edge.get("to_id") or edge.get("to_name") or ""),
        str(edge.get("source_type") or ""),
        str(edge.get("source_id") or ""),
    ])


def load_existing_relation_keys(path):
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                keys.add(relation_key(record))
            except Exception:
                pass
    return keys


def append_relation_jsonl(path, edges):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = load_existing_relation_keys(path)
    written = 0
    with open(path, "a", encoding="utf-8") as f:
        for edge in edges:
            key = relation_key(edge)
            if not key or key in existing:
                continue
            f.write(json.dumps(edge, ensure_ascii=False) + "\n")
            existing.add(key)
            written += 1
    return written


def build_relation_edges(record):
    source_id = record.get("post_id") or ""
    if not source_id:
        return []
    to_id = record.get("wxid") or ""
    to_name = record.get("nickname") or to_id
    if not to_id:
        return []
    date = (record.get("post_time") or "")[:10]
    edges = []
    for rel in record.get("rels") or []:
        if isinstance(rel, str):
            person_id = ""
            person_name = rel
            action = "interaction"
        elif isinstance(rel, dict):
            person_id = rel.get("person_id") or ""
            person_name = rel.get("person") or person_id
            action = rel.get("action") or "interaction"
        else:
            continue
        if not person_id and not person_name:
            continue
        relation = {"like": "点赞", "comment": "评论"}.get(action, "朋友圈互动")
        edge = {
            "from_id": person_id,
            "from_name": person_name,
            "relation": relation,
            "to_id": to_id,
            "to_name": to_name,
            "status": "",
            "source_type": "moment",
            "source_id": source_id,
            "date": date,
        }
        edges.append(edge)
    return edges


def write_relation_edges(base, records):
    written = 0
    for record in records:
        for edge in build_relation_edges(record):
            customer_ids = []
            if edge.get("from_id"):
                customer_ids.append(edge["from_id"])
            if edge.get("to_id"):
                customer_ids.append(edge["to_id"])
            for customer_id in dict.fromkeys(customer_ids):
                rel_path = os.path.join(
                    base, "customers", customer_id, "wechat-analysis",
                    customer_id + "_relations.jsonl"
                )
                written += append_relation_jsonl(rel_path, [edge])
    return written


def write_customers(base, records):
    """按 wxid 写入 customers/{wxid}/wechat-analysis/{wxid}_moment_extracted.jsonl"""
    written = 0
    users = set()
    for record in records:
        wxid = record.get("wxid")
        if not wxid:
            continue
        users.add(wxid)
        profile_path = os.path.join(base, "customers", wxid, "wechat-analysis", wxid + "_moment_extracted.jsonl")
        written += append_jsonl(profile_path, [record])
    return written, len(users)


def save_checkpoint(path, existing_ids, records, data_source):
    ids = set(str(x) for x in existing_ids)
    for record in records:
        if record.get("post_id"):
            ids.add(record["post_id"])
    payload = {
        "analyzed_ids": sorted(ids),
        "total_analyzed": len(ids),
        "last_data_source": data_source,
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return len(ids)


def align_analysis(posts, analysis):
    if not isinstance(analysis, list):
        raise ValueError("analysis 必须是 JSON 数组")
    if len(analysis) != len(posts):
        raise ValueError("analysis 数量不匹配：posts=%d, analysis=%d" % (len(posts), len(analysis)))
    return analysis


def main():
    parser = argparse.ArgumentParser(description="写入朋友圈模型分析结果")
    parser.add_argument(
        "--base-dir",
        default=os.path.join(os.path.expanduser("~"), ".openclaw", "projects"),
        help="数据根目录，默认为 ~/.openclaw/projects"
    )
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d%H"), help="日志标识，格式 YYYYMMDDHH")
    parser.add_argument("--report", action="store_true", help="落库后继续生成 actions 和 report")
    args = parser.parse_args()

    base = args.base_dir
    extracted_dir = os.path.join(base, "raw", "extracted_moment")
    checkpoint_path = os.path.join(extracted_dir, "checkpoint.json")

    # 从 stdin 读取 prepare_data 的输出（posts）+ Agent 分析结果（analysis）
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')
    input_data = json.load(sys.stdin)

    posts = input_data.get("posts", [])
    analysis = input_data.get("analysis", [])

    if not posts:
        print("NO_POSTS", file=sys.stderr)
        return
    if not analysis:
        print("NO_ANALYSIS", file=sys.stderr)
        return

    items = align_analysis(posts, analysis)
    whitelist = load_whitelist(base)
    records = [build_record(post, item, whitelist) for post, item in zip(posts, items)]

    extracted_filename = f"moment_extracted_{args.date}.jsonl"
    log_path = os.path.join(extracted_dir, extracted_filename)
    log_written = append_jsonl(log_path, records)
    customer_written, customer_users = write_customers(base, records)
    relation_written = write_relation_edges(base, records)

    checkpoint = load_json(checkpoint_path, default={}) or {}
    data_sources = input_data.get("data_sources", [])
    total_analyzed = save_checkpoint(
        checkpoint_path,
        checkpoint.get("analyzed_ids", []),
        records,
        ", ".join(data_sources) if data_sources else ""
    )

    print("OK: %d analyzed records" % len(records), file=sys.stderr)
    print("LOGS: %d records -> %s" % (log_written, log_path), file=sys.stderr)
    print("CUSTOMERS: %d records, %d users" % (customer_written, customer_users), file=sys.stderr)
    print("RELATIONS: %d records updated" % relation_written, file=sys.stderr)
    print("CHECKPOINT: %d analyzed ids -> %s" % (total_analyzed, checkpoint_path), file=sys.stderr)

    if args.report:
        report_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_report.py")
        report_result = subprocess.run([
            sys.executable, report_script,
            "--base-dir", base,
            "--date", args.date
        ], capture_output=True, text=True)
        if report_result.stdout:
            print(report_result.stdout.strip(), file=sys.stderr)
        if report_result.returncode != 0:
            print("REPORT_WARN: " + (report_result.stderr or "")[:200], file=sys.stderr)


if __name__ == "__main__":
    main()
