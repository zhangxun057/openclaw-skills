#!/usr/bin/env python3
"""
朋友圈报告生成工具
功能：读取 logs/YYYY-MM-DD.jsonl，生成 actions_YYYY-MM-DD.json 和 report_YYYY-MM-DD.md
用法：
  python generate_report.py
  python generate_report.py --date 2026-04-28
  python generate_report.py --base-dir ~/.openclaw/projects
"""
import argparse
import json
import os
from collections import Counter, defaultdict
from datetime import datetime


DIRECT_ACTION_BY_SIGNAL = {
    "婚宴定制酒": ("微信私信", "发消息祝贺，并询问婚宴/纪念场景用酒是否需要定制方案。", "定制酒（婚宴款）"),
    "企业定制酒": ("微信私信", "发消息祝贺企业节点，并提供企业定制酒或庆典伴手礼方向。", "定制酒（企业款）"),
    "会议伴手礼": ("微信私信", "围绕会议/峰会场景联系，询问是否需要会议用酒或伴手礼。", "定制酒（会议款）"),
    "宴请用酒": ("微信私信", "跟进宴请或酒局场景，询问近期接待用酒需求。", "定制酒"),
    "节日礼盒": ("微信私信", "提前沟通节日送礼计划，推荐定制礼盒方向。", "定制酒（礼盒款）"),
    "合伙人机会": ("微信私信", "围绕创业/投资动态祝贺，介绍创始合伙人机会。", "创始合伙人"),
}


def load_jsonl(path):
    records = []
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    return records


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def compact_text(text, limit=120):
    return " ".join((text or "").split())[:limit]


def is_reportable_event(event):
    event = compact_text(event, limit=80)
    if not event:
        return False
    low_value_keywords = [
        "打卡", "已瘦", "早吖", "早安", "晚安", "人间四月天",
        "饭后小点", "小王爷", "无聊机场", "忙时有序"
    ]
    high_value_keywords = [
        "会议", "峰会", "论坛", "沙龙", "签约", "启动", "发布会",
        "开业", "周年", "庆典", "拜访", "接待", "参观", "项目",
        "宴请", "婚礼", "订婚", "乔迁", "团建", "公益行"
    ]
    if any(keyword in event for keyword in low_value_keywords) and not any(keyword in event for keyword in high_value_keywords):
        return False
    return True


def build_actions(records, previous_actions):
    previous_targets = {a.get("wxid") for a in previous_actions if isinstance(a, dict) and a.get("wxid")}
    actions = []
    direct_by_user = {}

    for record in records:
        wxid = record.get("wxid") or ""
        if wxid in previous_targets:
            continue
        for signal in record.get("signals") or []:
            action, detail, product = DIRECT_ACTION_BY_SIGNAL.get(
                signal,
                ("微信私信", "基于当天机会线索联系对方，确认是否有进一步需求。", "待匹配")
            )
            if not wxid:
                continue
            item = direct_by_user.setdefault(wxid, {
                "priority": "direct",
                "wxid": wxid,
                "nickname": record.get("nickname") or "",
                "signals": [],
                "actions": [],
                "details": [],
                "basis_list": [],
                "products": [],
                "post_ids": [],
                "post_times": [],
            })
            if signal not in item["signals"]:
                item["signals"].append(signal)
            if action not in item["actions"]:
                item["actions"].append(action)
            if detail not in item["details"]:
                item["details"].append(detail)
            basis = compact_text(record.get("content"))
            if basis and basis not in item["basis_list"]:
                item["basis_list"].append(basis)
            if product and product not in item["products"]:
                item["products"].append(product)
            post_id = record.get("post_id") or ""
            if post_id and post_id not in item["post_ids"]:
                item["post_ids"].append(post_id)
            post_time = record.get("post_time") or ""
            if post_time and post_time not in item["post_times"]:
                item["post_times"].append(post_time)

    for item in direct_by_user.values():
        actions.append({
            "priority": "direct",
            "wxid": item["wxid"],
            "nickname": item["nickname"],
            "signal": "、".join(item["signals"]),
            "action": "、".join(item["actions"]),
            "detail": "；".join(item["details"]),
            "basis": " / ".join(item["basis_list"][:3]),
            "matched_product": "、".join(item["products"]),
            "post_id": ",".join(item["post_ids"]),
            "post_time": "、".join(item["post_times"][:3]),
        })

    indirect_candidates = []
    for record in records:
        if record.get("signals"):
            continue
        reportable_events = [
            event for event in (record.get("events") or [])
            if is_reportable_event(event)
        ]
        score = 0
        if reportable_events:
            score += 3
        if record.get("rels"):
            score += 2
        image_trigger = record.get("image_trigger")
        if image_trigger in ("strong", 1, True):
            score += 1
        elif image_trigger == "optional":
            score += 0.5
        if score:
            indirect_candidates.append((score, record))

    seen = set()
    for _, record in sorted(indirect_candidates, key=lambda item: item[0], reverse=True)[:10]:
        wxid = record.get("wxid") or ""
        if not wxid or wxid in seen:
            continue
        seen.add(wxid)
        actions.append({
            "priority": "indirect",
            "wxid": wxid,
            "nickname": record.get("nickname") or "",
            "signal": None,
            "action": "朋友圈评论",
            "detail": "围绕当天动态做轻量评论，保持连接，不推进销售。",
            "basis": compact_text(record.get("content")),
            "matched_product": None,
            "post_id": record.get("post_id") or "",
            "post_time": record.get("post_time") or "",
        })

    return actions


def collect_report_data(records):
    events_by_user = defaultdict(list)
    traits_by_user = defaultdict(dict)
    rels = []

    for record in records:
        name = record.get("nickname") or record.get("wxid") or "未知"
        post_time = record.get("post_time") or ""
        for event in record.get("events") or []:
            event = compact_text(event, limit=80)
            event_item = {"time": post_time, "event": event}
            if is_reportable_event(event) and event and event_item not in events_by_user[name]:
                events_by_user[name].append(event_item)
        for key, value in (record.get("traits") or {}).items():
            if value:
                traits_by_user[name][key] = value
        for rel in record.get("rels") or []:
            rels.append((name, rel))

    return events_by_user, traits_by_user, rels


def render_report(date, records, actions):
    users = {record.get("wxid") for record in records if record.get("wxid")}
    effective = [
        record for record in records
        if record.get("events") or record.get("traits") or record.get("signals") or record.get("rels") or record.get("content")
    ]
    signal_count = sum(len(record.get("signals") or []) for record in records)
    signal_counter = Counter(signal for record in records for signal in (record.get("signals") or []))
    post_type_counter = Counter(record.get("post_type") or "unknown" for record in records)
    events_by_user, traits_by_user, rels = collect_report_data(records)

    lines = [
        "# 朋友圈分析报告 — %s" % date,
        "",
        "> 分析时段：%s | %d条帖子 | %d位用户 | %d条有效记录 | %d个销售信号" % (
            date, len(records), len(users), len(effective), signal_count
        ),
        "",
        "## 概览",
        "本次分析了 %s 的 %d 条朋友圈记录，涉及 %d 位联系人，其中 %d 条包含可用于关系维护或业务判断的信息。" % (
            date, len(records), len(users), len(effective)
        ),
    ]

    if signal_counter:
        lines.append("销售信号分布：" + "、".join("%s %d次" % item for item in signal_counter.most_common()))
    else:
        lines.append("本次未发现明确销售信号。")
    lines.append("内容类型分布：" + "、".join("%s %d条" % item for item in post_type_counter.most_common()))

    lines.extend(["", "## 事件"])
    if events_by_user:
        for name, events in list(events_by_user.items())[:50]:
            details = []
            for item in events:
                prefix = item["time"] + " " if item.get("time") else ""
                details.append(prefix + item["event"])
            lines.append("- %s：%s" % (name, "；".join(details)))
    else:
        lines.append("- 暂无可聚合事件。")

    lines.extend(["", "## 新特征"])
    if traits_by_user:
        for name, traits in list(traits_by_user.items())[:30]:
            detail = "，".join("%s：%s" % (key, value) for key, value in traits.items())
            lines.append("- %s：%s" % (name, detail))
    else:
        lines.append("- 暂无可聚合新特征。")

    lines.extend(["", "## 新关系"])
    if rels:
        for left, right in rels[:30]:
            lines.append("- %s ↔ %s" % (left, right))
    else:
        lines.append("- 暂无可聚合新关系。")

    direct = [action for action in actions if action.get("priority") == "direct"]
    indirect = [action for action in actions if action.get("priority") == "indirect"]

    lines.extend(["## 今日行动建议", "", "### 优先：有明确机会的对象"])
    if direct:
        for action in direct[:20]:
            lines.append("**%s（%s）**" % (action["nickname"], action["wxid"]))
            lines.append("动作：" + action["action"])
            lines.append("详情：" + action["detail"])
            if action.get("post_time"):
                lines.append("时间：" + action["post_time"])
            lines.append("依据：%s；%s" % (action.get("signal") or "", action.get("basis") or ""))
            lines.append("")
    else:
        lines.extend(["暂无。", ""])

    lines.append("### 其次：值得关注但暂无直接机会的对象")
    if indirect:
        for action in indirect[:10]:
            lines.append("**%s（%s）**" % (action["nickname"], action["wxid"]))
            lines.append("动作：" + action["action"])
            lines.append("详情：" + action["detail"])
            if action.get("post_time"):
                lines.append("时间：" + action["post_time"])
            lines.append("依据：" + (action.get("basis") or ""))
            lines.append("")
    else:
        lines.append("暂无。")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成朋友圈行动建议和日报")
    parser.add_argument(
        "--base-dir",
        default=os.path.join(os.path.expanduser("~"), ".openclaw", "projects"),
        help="数据根目录，默认为 ~/.openclaw/projects"
    )
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d%H"), help="报告标识，格式 YYYYMMDDHH")
    parser.add_argument("--previous-actions", help="历史行动建议 JSON 文件，用于避免跨日重复建议")
    args = parser.parse_args()

    base = os.path.expanduser(args.base_dir)
    # 输入从 L1 提取目录读取，遵循推送命名规范 moment_extracted_YYYYMMDDHH.jsonl
    log_path = os.path.join(base, "raw", "extracted_moment", f"moment_extracted_{args.date}.jsonl")
    reports_dir = os.path.join(base, "reports")
    actions_path = os.path.join(reports_dir, "actions_" + args.date + ".json")
    report_path = os.path.join(reports_dir, "report_" + args.date + ".md")

    records = load_jsonl(log_path)
    if not records:
        print("NO_LOG_DATA: " + log_path)
        return

    previous_actions = load_json(args.previous_actions, default=[]) if args.previous_actions else []
    actions = build_actions(records, previous_actions)
    save_json(actions_path, actions)
    save_text(report_path, render_report(args.date, records, actions))

    users = {record.get("wxid") for record in records if record.get("wxid")}
    signal_count = sum(len(record.get("signals") or []) for record in records)
    print("OK: records=%d, users=%d, signals=%d, actions=%d" % (
        len(records), len(users), signal_count, len(actions)
    ))
    print("ACTIONS: " + actions_path)
    print("REPORT: " + report_path)


if __name__ == "__main__":
    main()
