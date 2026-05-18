#!/usr/bin/env python3
"""
Process 20260510 moments - Phase 2+3: Agent analysis + save to L1/L2/checkpoint.
"""
import json
import os
import sys
import time

BASE = os.path.join(os.path.expanduser("~"), ".openclaw", "projects")

def analyze_post(post):
    """Analyze a single post and return the 4 dimensions."""
    pid = post.get("_post_id", "")
    nick = post.get("nickname", "")
    desc = (post.get("contentDesc") or "").strip()
    ptype = post.get("type", 0)
    likes = post.get("likes", [])
    comments = post.get("comments", [])
    
    # Determine if it's a share/forward
    is_finder = ptype == 28  # 视频号转发
    is_article = ptype == 3  # 公众号文章转发
    is_video = ptype == 15   # 小视频
    is_text_img = ptype == 1  # 文字+图片
    is_live_photo = ptype == 54  # Live Photo
    
    content_lower = desc.lower()
    
    # Classify post_type
    post_type = classify_post_type(desc, ptype, nick)
    
    # Determine mood
    mood = classify_mood(desc, post_type)
    
    # Extract traits
    traits = extract_traits(desc, nick, ptype)
    
    # Extract events
    events = extract_events(desc, nick, ptype, post)
    
    # Extract signals
    signals = extract_signals(desc, nick, ptype)
    
    # Build rels from likes/comments
    rels = []
    for c in comments:
        cn = c.get("nickname", "")
        cc = c.get("content", "")
        if cn and cn != nick:
            rels.append({"person": cn, "action": "评论", "content": cc[:50]})
    for l in likes:
        if isinstance(l, str) and l != nick:
            rels.append({"person": l, "action": "点赞"})
    
    return {
        "post_type": post_type,
        "mood": mood,
        "traits": traits,
        "events": events,
        "signals": signals,
        "rels": rels
    }

def classify_post_type(desc, ptype, nick):
    desc_lower = desc.lower() if desc else ""
    has_desc = len(desc) > 0 and not desc.isspace()
    
    if ptype == 3:  # 公众号文章
        return "转发内容"
    if ptype == 28:  # 视频号
        return "转发内容"
    if ptype == 15:  # 小视频
        if has_desc and len(desc) > 10:
            return "分享动态"
        return "其他"
    
    # Check if it's advertising
    if any(kw in desc_lower for kw in ["欢迎参加", "诚邀您", "扫码锁定", "关注", "回复", "送你"]):
        return "广告营销"
    
    # Check if it's just a greeting
    if any(kw in desc for kw in ["早安", "早上好", "各位微友"]):
        if len(desc) < 20:
            return "其他"
    
    if not has_desc:
        return "其他"
    
    # Has personal opinion/view
    if any(kw in desc for kw in ["我认为", "我觉得", "论", "应该", "致敬"]):
        return "输出观点"
    
    # Personal action/life
    if any(kw in desc for kw in ["出发", "参加", "抵达", "收到", "完成", "举办", "纪念"]):
        return "分享动态"
    
    # Poetry/poetic expression
    if len(desc) > 15 and not any(c.isdigit() for c in desc):
        # Check if it's poetry-like
        lines = desc.split('\n')
        if len(lines) >= 3 and all(len(l) < 20 for l in lines if l.strip()):
            return "输出观点"
    
    return "分享动态"

def classify_mood(desc, post_type):
    if post_type in ("转发内容", "其他"):
        return "无法判断"
    
    desc_lower = desc.lower() if desc else ""
    
    if any(kw in desc for kw in ["快乐", "开心", "快乐", "感恩", "❤", "🥇", "庆祝", "荣幸"]):
        return "开心"
    if any(kw in desc for kw in ["出发", "🛫", " excited", "!"]):
        if "!" in desc and desc.count("!") >= 2:
            return "兴奋"
        return "开心"
    if any(kw in desc for kw in ["垃圾", "焦人", "抓狂"]):
        return "失落"
    if any(kw in desc for kw in ["焦虑", "担忧", "压力"]):
        return "焦虑"
    
    return "平静"

def extract_traits(desc, nick, ptype):
    traits = {}
    
    # 巨石研究院 related
    if "巨石研究院" in nick:
        traits["在职单位"] = "巨石研究院"
        traits["职务"] = "校长"
    
    # 珍酒
    if "珍酒" in nick:
        traits["在职单位"] = "贵州珍酒"
        traits["职务"] = "传承运营"
    
    # 华创计算机
    if "华创计算机" in nick:
        traits["在职单位"] = "华创计算机"
    
    # 知识图谱
    if "知识图谱" in nick:
        traits["在职单位"] = "柯基数据"
        traits["职务"] = "知识图谱"
    
    # 习酒
    if "习酒" in nick:
        traits["在职单位"] = "习酒"
    
    # 青酒
    if "青酒" in nick:
        traits["在职单位"] = "贵州青酒"
    
    # STOBI葡萄酒
    if "STOBI" in nick and "五粮液" in nick:
        traits["在职单位"] = "STOBI葡萄酒"
        traits["饮酒偏好"] = "葡萄酒/白酒"
    
    # Investment interest
    if "行情跌宕" in desc and "股市" in desc:
        traits["投资风格"] = "关注风险"
    
    # Parenting
    if "养育孩子" in desc:
        traits["家庭结构"] = "有子女"
        traits["价值观倾向"] = "包容教育"
    
    # Yellow wine interest
    if "黄酒" in desc and "转行" in desc:
        traits["兴趣爱好"] = "黄酒"
        traits["表达风格"] = "文艺叙事"
    
    # Panda guide
    if "熊猫指南" in desc:
        traits["在职单位"] = "熊猫指南"
    
    # Soccer
    if "足球" in desc:
        traits["兴趣爱好"] = "足球"
    
    # Wine collection
    if "罗曼尼康帝" in desc:
        traits["饮酒偏好"] = "高端葡萄酒"
    
    # Water purifier
    if "怡口净水" in nick:
        traits["在职单位"] = "怡口净水"
    
    # 国台
    if "国台" in nick:
        traits["在职单位"] = "国台"
    
    # 高鹏楼梯
    if "高鹏楼梯" in nick:
        traits["在职单位"] = "高鹏楼梯"
    
    # 劲络养生
    if "劲络养生" in nick:
        traits["在职单位"] = "劲络养生"
    
    # 桐梓窖酒
    if "桐梓窖酒" in desc:
        traits["在职单位"] = "桐宸酒业"
    
    return traits

def extract_events(desc, nick, ptype, post):
    events = []
    
    # Medal award
    if "第二块奖牌" in desc and "观山湖区体育局" in desc:
        events.append("获得观山湖区体育局今年第二块奖牌")
    
    # Child's first Mother's Day gift
    if "第一份母亲节礼物" in desc:
        events.append("收到孩子第一份母亲节礼物")
    
    # Child's exam results (from comments)
    comments = post.get("comments", [])
    for c in comments:
        cc = c.get("content", "")
        if "648" in cc and "全省" in cc:
            events.append("孩子高考648分全省排位952名")
    
    # Wine collection showcase
    if "罗曼尼康帝" in desc:
        events.append("展示收藏几十年罗曼尼康帝葡萄酒")
    
    # Shaoxing trip
    if "绍兴" in desc and "黄酒" in desc:
        events.append("赴绍兴考察黄酒产业并写长文记录")
    
    # Departure
    if "出发" in desc and "滴滴" in desc:
        events.append("出发预约滴滴出行")
    
    # Anti-Fascist memorial
    if "反法西斯" in desc:
        loc = post.get("location", {})
        city = loc.get("city", "")
        if city:
            events.append(f"在白俄罗斯{city}纪念反法西斯战争胜利日")
    
    # WWII memorial (任飞)
    if "卫国战争胜利81周年" in desc:
        events.append("在白俄罗斯巨石工业园纪念卫国战争胜利81周年")
    
    # 贵州青酒 at 莫干山大会
    if "贵州青酒" in desc and "莫干山大会" in desc:
        events.append("贵州青酒亮相2026世界品牌莫干山大会")
    
    return events

def extract_signals(desc, nick, ptype):
    """Extract sales signals."""
    signals = []
    
    # No clear demand signals found in these posts
    # 冯永兴's post about 贵州青酒 is from the brand's perspective, not external demand
    # 老欧's post about yellow wine is personal interest, not external demand
    
    return signals

def save_to_l1_l2(posts, analyses):
    """Save extracted results to L1 and L2."""
    # Ensure directories exist
    l1_dir = os.path.join(BASE, "raw", "extracted_moment")
    os.makedirs(l1_dir, exist_ok=True)
    
    customers_dir = os.path.join(BASE, "customers")
    
    # Generate timestamp
    now = int(time.time())
    date_label = "20260510"
    
    # L1 output
    l1_path = os.path.join(l1_dir, f"moment_extracted_{date_label}00.jsonl")
    
    # Check if file already exists
    existing_ids = set()
    if os.path.exists(l1_path):
        with open(l1_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                    existing_ids.add(item.get("post_id", ""))
                except:
                    pass
    
    with open(l1_path, "a", encoding="utf-8") as f:
        for post, analysis in zip(posts, analyses):
            pid = post.get("_post_id", "")
            if pid in existing_ids:
                continue
            
            username = post.get("username", "")
            
            # Format post_time
            ct = post.get("createTime", 0)
            post_time = ""
            if ct:
                import datetime
                post_time = datetime.datetime.fromtimestamp(ct, tz=datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
            
            record = {
                "post_id": pid,
                "username": username,
                "nickname": post.get("nickname", ""),
                "post_time": post_time,
                "content_desc": (post.get("contentDesc") or "")[:500],
                "type": post.get("type", 0),
                "likes_count": len(post.get("likes", [])),
                "comments_count": len(post.get("comments", [])),
                "media_count": len(post.get("media", [])),
                "analysis": analysis,
                "raw_date": date_label
            }
            
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
            # L2 output - save to customer dir
            if username:
                cust_dir = os.path.join(customers_dir, username, "wechat-analysis")
                os.makedirs(cust_dir, exist_ok=True)
                l2_path = os.path.join(cust_dir, f"{username}_moment_extracted.jsonl")
                
                with open(l2_path, "a", encoding="utf-8") as f2:
                    f2.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    # Update checkpoint
    cp_path = os.path.join(l1_dir, "checkpoint.json")
    checkpoint = {}
    if os.path.exists(cp_path):
        try:
            with open(cp_path, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
        except:
            pass
    
    analyzed_ids = set(str(x) for x in checkpoint.get("analyzed_ids", []))
    for post in posts:
        pid = post.get("_post_id", "")
        if pid:
            analyzed_ids.add(pid)
    
    checkpoint["analyzed_ids"] = sorted(list(analyzed_ids))
    checkpoint["last_updated"] = date_label
    checkpoint["last_run"] = now
    
    with open(cp_path, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    return len(posts)

def main():
    raw_path = os.path.join(BASE, "raw", "moments-analysis", "20260510.json")
    
    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    posts = data.get("posts", [])
    
    # Add _post_id
    for p in posts:
        if "_post_id" not in p:
            pid = p.get("id") or p.get("tid")
            if pid:
                p["_post_id"] = str(pid)
            else:
                p["_post_id"] = "%s_%s" % (p.get("username",""), p.get("createTime",""))
    
    print(f"Processing {len(posts)} posts from 20260510...", file=sys.stderr)
    
    # Analyze all posts
    analyses = []
    for post in posts:
        analysis = analyze_post(post)
        analyses.append(analysis)
    
    # Save to L1/L2
    count = save_to_l1_l2(posts, analyses)
    
    # Print summary
    event_count = sum(len(a["events"]) for a in analyses)
    signal_count = sum(len(a["signals"]) for a in analyses)
    trait_count = sum(1 for a in analyses if a["traits"])
    
    print(f"L1/L2 saved: {count} posts", file=sys.stderr)
    print(f"Events: {event_count}, Signals: {signal_count}, Traits: {trait_count}", file=sys.stderr)
    
    # Print detailed analysis for review
    for i, (post, analysis) in enumerate(zip(posts, analyses)):
        nick = post.get("nickname", "")
        desc = (post.get("contentDesc") or "")[:60]
        pt = analysis["post_type"]
        m = analysis["mood"]
        ev = analysis["events"]
        sig = analysis["signals"]
        tr = analysis["traits"]
        
        summary = f"[{i+1}] {nick}: {pt} | {m}"
        if desc:
            summary += f" | {desc}"
        if ev:
            summary += f" | events: {ev}"
        if sig:
            summary += f" | signals: {sig}"
        if tr:
            summary += f" | traits: {tr}"
        print(summary, file=sys.stderr)
    
    sys.stderr.flush()

if __name__ == "__main__":
    main()
