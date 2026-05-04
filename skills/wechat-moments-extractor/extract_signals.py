#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""销售信号提取 + 图片分析指令生成"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_api import call_with_fallback

SYSTEM_PROMPT = '''【销售信号提取 + 图片分析指令生成】

## 一、销售信号
判断核心：对方是否有近期向"我"采购定制酒/会员服务/贵州文旅产品的需求？

强信号类型：
- 人生节点：婚礼、订婚、满月、周岁、升学、乔迁、开业、周年庆、寿宴
- 活动预告：峰会、展会、招商会、发布会、宴请（有具体时间）
- 定制需求：正在选伴手礼、封坛储酒、企业定制、婚宴用酒
- 投资信号：对会员模式、理财型酒有兴趣暗示

禁止：
- 纯消费展示（酒柜、喝酒晒图）
- 饮酒偏好表达（只喝酱香）
- 一般商务动态（无明确采购需求）
- 对方在卖自己产品（不是向"我"采购）

## 二、图片分析指令生成
结合正文上下文，生成针对性的图片分析指令。

要求：
- 是分析指令，不是问答题
- 引导描述场景，不预设答案
- 中文，15 字以内
- 不要生成只能回答"是/否"的弱智问题
- 如果图片不值得分析，输出 null

生成原则：
- 有具体产品/品牌 → 描述产品细节
- 有场景 → 描述场景信息
- 有时间节点 → 描述相关细节
- 无法判断 → 输出 null

输出格式（必须严格 JSON 数组，每条输入对应一个对象）：
[{"signals": [...], "image_prompt": "..."}, {"signals": [...], "image_prompt": "..."}, ...]

注意：
- 数组长度必须等于输入帖子数量
- 每个对象对应一条帖子
- image_prompt 要引导 AI 描述看到的一切细节，而不是只能回答 Yes/No'''

def extract_signals(posts, api_key, base_url, fallback_configs=None):
    result = call_with_fallback(posts, SYSTEM_PROMPT, api_key, base_url, fallback_configs)
    if result is None:
        return [{'signals': [], 'image_prompt': None} for _ in posts]
    processed = []
    for item in result:
        if isinstance(item, dict):
            processed.append({
                'signals': item.get('signals', []),
                'image_prompt': item.get('image_prompt', None)
            })
        else:
            processed.append({'signals': [], 'image_prompt': None})
    return processed

if __name__ == '__main__':
    cfg_path = os.path.expanduser('~/.openclaw/openclaw.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    ali = cfg['models']['providers']['aliyun-bailian']
    test_posts = [{'nickname': '杨香雪儿', 'content': '和双币基金朋友介绍项目'}]
    print(json.dumps(extract_signals(test_posts, ali['apiKey'], ali['baseUrl']), ensure_ascii=False, indent=2))
