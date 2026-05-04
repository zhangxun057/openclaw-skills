#!/usr/bin/env python3
"""
客户逐一盘点脚本
功能：为每位客户生成详细档案
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
import argparse

def load_data(data_dir):
    """加载微信数据"""
    data = {
        "contacts": [],
        "sessions": [],
        "messages": {}
    }
    
    # 加载联系人
    contacts_file = os.path.join(data_dir, "contacts", "all_contacts.json")
    if os.path.exists(contacts_file):
        with open(contacts_file, 'r', encoding='utf-8') as f:
            d = json.load(f)
            data["contacts"] = d.get("contacts", [])
    
    # 加载会话
    sessions_file = os.path.join(data_dir, "sessions.json")
    if os.path.exists(sessions_file):
        with open(sessions_file, 'r', encoding='utf-8') as f:
            d = json.load(f)
            data["sessions"] = d.get("sessions", [])
    
    # 加载消息
    messages_dir = os.path.join(data_dir, "messages")
    if os.path.exists(messages_dir):
        for file in os.listdir(messages_dir):
            if file.endswith('.json'):
                file_path = os.path.join(messages_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                    # 从文件名提取talker
                    talker = file.replace('.json', '')
                    data["messages"][talker] = d.get("messages", [])
    
    return data

def analyze_contact(contact, messages, session_info):
    """分析单个客户"""
    if not messages:
        return None
    
    profile = {
        "name": contact.get('displayName', contact.get('nickname', '未知')),
        "username": contact.get('username', ''),
        "type": contact.get('type', 'friend'),
        "message_count": len(messages),
        "analysis": {},
        "level": "普通客户"
    }
    
    # 基础统计
    my_messages = [m for m in messages if m.get('isSend') == 1]
    their_messages = [m for m in messages if m.get('isSend') == 0]
    
    profile['analysis']['my_count'] = len(my_messages)
    profile['analysis']['their_count'] = len(their_messages)
    profile['analysis']['my_ratio'] = len(my_messages) / len(messages) if messages else 0
    profile['analysis']['their_ratio'] = len(their_messages) / len(messages) if messages else 0
    
    # 消息长度分析
    my_avg_length = sum(len(m.get('content', '')) for m in my_messages) / max(len(my_messages), 1)
    their_avg_length = sum(len(m.get('content', '')) for m in their_messages) / max(len(their_messages), 1)
    profile['analysis']['my_avg_length'] = round(my_avg_length, 1)
    profile['analysis']['their_avg_length'] = round(their_avg_length, 1)
    
    # 内容分析
    all_content = ' '.join([m.get('parsedContent', m.get('content', '')) for m in messages if m.get('content')])
    
    # 关键词分类
    keyword_categories = {
        "business": ["项目", "合作", "投资", "生意", "赚钱", "业务", "客户", "公司", "老板", "融资"],
        "tech": ["代码", "产品", "设计", "开发", "技术", "AI", "系统", "软件", "算法", "数据"],
        "life": ["家庭", "孩子", "父母", "生活", "吃饭", "聚会", "旅游", "房子", "车子"],
        "social": ["朋友", "聚会", "喝酒", "吃饭", "一起玩", "介绍"],
        "emotion": ["喜欢", "开心", "难过", "想", "爱", "感谢", "谢谢"]
    }
    
    keyword_scores = {}
    for category, keywords in keyword_categories.items():
        score = sum(all_content.count(k) for k in keywords)
        keyword_scores[category] = score
    
    profile['analysis']['keyword_scores'] = keyword_scores
    dominant_category = max(keyword_scores, key=keyword_scores.get)
    profile['analysis']['dominant_category'] = dominant_category if keyword_scores[dominant_category] > 0 else "general"
    
    # 客户类型判断
    type_mapping = {
        "business": "商务型",
        "tech": "技术型",
        "life": "生活型",
        "social": "社交型",
        "emotion": "情感型",
        "general": "普通型"
    }
    profile['analysis']['type_label'] = type_mapping.get(profile['analysis']['dominant_category'], "普通型")
    
    # 性格判断
    if their_avg_length < 15:
        personality = "极简型"
    elif their_avg_length < 40:
        personality = "简洁型"
    elif their_avg_length < 100:
        personality = "分享型"
    else:
        personality = "深度型"
    
    # 结合主动性
    if profile['analysis']['their_ratio'] > 0.6:
        personality += "（主动）"
    elif profile['analysis']['their_ratio'] < 0.4:
        personality += "（被动）"
    else:
        personality += "（平衡）"
    
    profile['analysis']['personality'] = personality
    
    # 消费潜力推断
    consumption_indicators = {
        "high": ["别墅", "房子", "投资", "项目", "老板", "采购", "茅台", "高端", "定制"],
        "medium": ["吃饭", "聚会", "旅游", "品牌", "品质", "推荐"],
        "low": ["便宜", "优惠", "省钱", "性价比", "学生"]
    }
    
    high_score = sum(all_content.count(k) for k in consumption_indicators["high"])
    medium_score = sum(all_content.count(k) for k in consumption_indicators["medium"])
    low_score = sum(all_content.count(k) for k in consumption_indicators["low"])
    
    if high_score > 2:
        consumption_level = "高"
    elif medium_score > 2 or high_score > 0:
        consumption_level = "中高"
    elif low_score > 2:
        consumption_level = "价格敏感"
    else:
        consumption_level = "中等"
    
    profile['analysis']['consumption_level'] = consumption_level
    
    # 客户分级
    if len(messages) > 500 and profile['analysis']['their_ratio'] > 0.4:
        profile['level'] = "核心客户"
    elif len(messages) > 200:
        profile['level'] = "活跃客户"
    elif len(messages) > 50:
        profile['level'] = "普通客户"
    else:
        profile['level'] = "待激活客户"
    
    # 互动模式分析
    if profile['analysis']['their_ratio'] > 0.6:
        initiative = "对方主动"
    elif profile['analysis']['their_ratio'] < 0.3:
        initiative = "我方主动"
    else:
        initiative = "双向互动"
    profile['analysis']['initiative'] = initiative
    
    # 情感倾向
    positive_words = ["好", "棒", "赞", "哈哈", "开心", "谢谢", "感谢"]
    negative_words = ["不好", "差", "烦", "累", "忙", "没空", "不行"]
    
    positive_count = sum(all_content.count(w) for w in positive_words)
    negative_count = sum(all_content.count(w) for w in negative_words)
    
    if positive_count > negative_count * 2:
        emotion = "积极"
    elif negative_count > positive_count:
        emotion = "消极"
    else:
        emotion = "中性"
    profile['analysis']['emotion'] = emotion
    
    # 时间特征（如消息有时间戳）
    timestamps = [m.get('createTime') for m in messages if m.get('createTime')]
    if timestamps:
        profile['analysis']['first_contact'] = min(timestamps)
        profile['analysis']['last_contact'] = max(timestamps)
    
    return profile

def generate_md(profile, template_path=None):
    """生成Markdown档案"""
    
    # 默认模板
    if template_path and os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        template = get_default_template()
    
    # 格式化模板
    md_content = template.format(
        name=profile['name'],
        username=profile['username'],
        message_count=profile['message_count'],
        type_label=profile['analysis'].get('type_label', '普通型'),
        personality=profile['analysis'].get('personality', '未知'),
        consumption_level=profile['analysis'].get('consumption_level', '中等'),
        level=profile['level'],
        my_count=profile['analysis'].get('my_count', 0),
        their_count=profile['analysis'].get('their_count', 0),
        my_ratio=f"{profile['analysis'].get('my_ratio', 0)*100:.0f}%",
        their_ratio=f"{profile['analysis'].get('their_ratio', 0)*100:.0f}%",
        my_avg_length=profile['analysis'].get('my_avg_length', 0),
        their_avg_length=profile['analysis'].get('their_avg_length', 0),
        initiative=profile['analysis'].get('initiative', '未知'),
        emotion=profile['analysis'].get('emotion', '中性'),
        dominant_category=profile['analysis'].get('dominant_category', 'general'),
        date=datetime.now().strftime('%Y-%m-%d')
    )
    
    return md_content

def get_default_template():
    """默认档案模板"""
    return '''# 客户档案：{name}

## 一、基础画像

**关系类型**：{type_label}  
**消息数量**：{message_count}条  
**客户分级**：{level}  
**分析日期**：{date}

---

## 二、社交强度分析

**消息分布**：
- 我方发送：{my_count}条（{my_ratio}）
- 对方发送：{their_count}条（{their_ratio}）
- 平均长度：我方{my_avg_length}字 / 对方{their_avg_length}字

**互动特征**：{initiative}

**互动频率**：{'高频' if message_count > 500 else '中频' if message_count > 200 else '低频'}

---

## 三、互动模式分析

**客户类型**：{type_label}

类型说明：
- **商务型**：关注项目、合作、投资，决策力强
- **技术型**：关注产品、开发、技术，理性分析
- **生活型**：关注家庭、日常，重视体验
- **社交型**：活跃、热情，重视人际关系
- **情感型**：表达丰富，重视情感连接

**性格特征**：{personality}

**情感倾向**：{emotion}

---

## 四、消费特征推断

**消费层级**：{consumption_level}

层级说明：
- **高**：有投资、房产、商务等关键词，消费力强
- **中高**：关注品质、品牌，愿意为体验付费
- **中等**：常规消费，需挖掘需求
- **价格敏感**：关注优惠、性价比，价格导向

**消费偏好推断**：
基于聊天内容关键词分析，该客户属于{type_label}，
{'决策较快，重视效率和回报' if type_label == '商务型' else 
 '理性消费，重视产品功能和性价比' if type_label == '技术型' else
 '重视体验和情感价值' if type_label in ['生活型', '情感型'] else
 '社交驱动型消费，重视分享和认同' if type_label == '社交型' else
 '暂无明显消费特征，需进一步观察'}

---

## 五、价值评估

### 直接价值
- **消费潜力**：{consumption_level}
- **转化难度**：{'低' if type_label == '商务型' else '中' if type_label in ['技术型', '生活型'] else '需培养'}

### 间接价值
- **信息价值**：{'高（掌握行业/业务信息）' if dominant_category == 'business' else 
                '中（技术视角）' if dominant_category == 'tech' else
                '中（社交资源）' if dominant_category == 'social' else '一般'}
- **影响力**：{'高（决策层特征）' if type_label == '商务型' else '中' if message_count > 200 else '待观察'}

### 网络位置
- **关系深度**：{'深（高频互动）' if message_count > 500 else '中等' if message_count > 200 else '浅'}
- **连接度**：{initiative}

---

## 六、触达策略建议

### 最佳时机
- {'工作日上午10-11点，下午15-17点（商务习惯）' if type_label == '商务型' else
   '晚上20-22点（技术交流时间）' if type_label == '技术型' else
   '周末或节假日（生活场景）' if type_label == '生活型' else
   '灵活时间（社交型适应性强）' if type_label == '社交型' else
   '观察对方活跃时段'}
- 节日前2周（礼赠需求高峰）
- 项目节点/季度交替时

### 沟通方式
- {'正式提案 > 社交闲聊，数据说话' if type_label == '商务型' else
   '技术细节 > 营销话术，功能优先' if type_label == '技术型' else
   '情感共鸣 > 产品推销，体验优先' if type_label in ['生活型', '情感型'] else
   '轻松互动 > 正式商务，共同话题切入' if type_label == '社交型' else
   '观察后调整'}
- 尊重对方沟通习惯（{'简洁高效，结论前置' if personality.startswith('极简') else '可深入讨论，分享细节' if personality.startswith('深度') else '保持平衡'}）

### 注意事项
- ❌ 避免：{'过多细节，直接给结论' if personality.startswith('极简') else '空洞承诺，要数据支撑' if type_label == '技术型' else '功利性太强，先建立信任' if message_count < 100 else '过度打扰'}
- ⚠️ 注意：{'对方时间宝贵，降低决策成本' if personality.startswith('极简') else '保持专业度，准备充分' if type_label == '商务型' else '保持适度距离，尊重边界' if emotion == '中性' else '积极互动，回应热情'}
- ✅ 建议：{'提供一站式方案，减少对方工作量' if personality.startswith('极简') else '提供技术细节和案例' if type_label == '技术型' else '创造共同体验机会' if type_label in ['生活型', '社交型'] else '先建立情感连接' if type_label == '情感型' else '根据互动反馈调整策略'}

---

## 七、行动建议

### 立即执行
- [ ] 根据客户类型准备相应资料
- [ ] {'预约正式沟通' if type_label == '商务型' else '寻找技术交流切入点' if type_label == 'tech' else '寻找共同话题/活动机会' if type_label in ['生活型', 'social'] else '发送问候，建立联系'}
- [ ] 记录客户偏好和禁忌

### 持续跟进
- [ ] 定期互动（频率：{'每周' if message_count > 500 else '每两周' if message_count > 200 else '每月'}）
- [ ] 节点触达（节日、生日、项目节点）
- [ ] 价值提供（信息分享、资源对接）

### 关键节点
- 首次深度沟通后：记录反馈，调整策略
- 建立信任后：探索合作机会
- 转化成功后：维护长期关系，挖掘转介绍

---

## 八、备注

- 客户类型：{type_label}
- 消费预估：{consumption_level}
- 优先级：{'最高' if level == '核心客户' else '高' if level == '活跃客户' else '中' if level == '普通客户' else '待激活'}
- 下次联系时间：待填写

---
*档案生成时间：{date}*
*下次更新：首次触达后*
'''

def main():
    parser = argparse.ArgumentParser(description="客户逐一盘点")
    parser.add_argument("--data-dir", default="./微信数据", help="数据目录")
    parser.add_argument("--output", default="./客户档案", help="输出目录")
    parser.add_argument("--template", help="自定义模板路径")
    parser.add_argument("--min-messages", type=int, default=50, help="最少消息数")
    args = parser.parse_args()
    
    data_dir = os.path.expanduser(args.data_dir)
    output_dir = os.path.expanduser(args.output)
    
    if not os.path.exists(data_dir):
        print(f"[ERROR] 数据目录不存在: {data_dir}")
        print("[INFO] 请先执行 download_all.py 下载数据")
        return
    
    # 加载数据
    print("[INFO] 正在加载数据...")
    data = load_data(data_dir)
    print(f"[OK] 加载了 {len(data['contacts'])} 个联系人，{len(data['messages'])} 个会话")
    
    # 创建输出目录
    for level in ["核心客户", "活跃客户", "普通客户", "待激活客户"]:
        os.makedirs(os.path.join(output_dir, level), exist_ok=True)
    
    # 分析每个联系人
    print(f"\n[INFO] 开始客户逐一盘点...")
    profiles = []
    
    # 按消息量排序
    sorted_sessions = sorted(data['sessions'], key=lambda x: x.get('messageCount', 0), reverse=True)
    
    for i, session in enumerate(sorted_sessions, 1):
        talker = session.get('username', '')
        msg_count = session.get('messageCount', 0)
        
        if msg_count < args.min_messages:
            continue
        
        # 查找联系人信息
        contact = next((c for c in data['contacts'] if c.get('username') == talker), {})
        if not contact:
            contact = {
                'username': talker,
                'displayName': session.get('displayName', talker),
                'nickname': session.get('displayName', talker)
            }
        
        # 查找消息
        messages = data['messages'].get(f"{contact.get('displayName', talker)}_{talker}", [])
        if not messages:
            # 尝试其他匹配方式
            for key, msgs in data['messages'].items():
                if talker in key:
                    messages = msgs
                    break
        
        if not messages:
            continue
        
        print(f"[{i}] 分析 {contact.get('displayName', talker)} ({msg_count}条消息)...", end=" ")
        
        # 分析
        profile = analyze_contact(contact, messages, session)
        if profile:
            profiles.append(profile)
            
            # 生成档案
            md_content = generate_md(profile, args.template)
            
            # 保存
            safe_name = "".join(c for c in profile['name'] if c.isalnum() or c in '_-').strip()
            if not safe_name:
                safe_name = talker.replace('@', '_').replace('.', '_')
            
            level_dir = profile['level']
            md_path = os.path.join(output_dir, level_dir, f"{safe_name}.md")
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"[OK] {profile['level']}")
        else:
            print("[SKIP]")
    
    # 生成统计报告
    stats = {
        "analysis_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_analyzed": len(profiles),
        "level_distribution": {
            "核心客户": len([p for p in profiles if p['level'] == '核心客户']),
            "活跃客户": len([p for p in profiles if p['level'] == '活跃客户']),
            "普通客户": len([p for p in profiles if p['level'] == '普通客户']),
            "待激活客户": len([p for p in profiles if p['level'] == '待激活客户'])
        },
        "type_distribution": {},
        "profiles": profiles
    }
    
    # 类型统计
    for p in profiles:
        t = p['analysis'].get('type_label', '普通型')
        stats['type_distribution'][t] = stats['type_distribution'].get(t, 0) + 1
    
    stats_file = os.path.join(output_dir, "客户盘点统计.json")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 客户盘点完成 ===")
    print(f"总分析数: {stats['total_analyzed']}")
    print(f"  - 核心客户: {stats['level_distribution']['核心客户']}")
    print(f"  - 活跃客户: {stats['level_distribution']['活跃客户']}")
    print(f"  - 普通客户: {stats['level_distribution']['普通客户']}")
    print(f"  - 待激活客户: {stats['level_distribution']['待激活客户']}")
    print(f"档案保存: {output_dir}")

if __name__ == "__main__":
    main()
