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
核心目标：通过图片了解发帖人的消费场景和消费能力。

要求：
- 是分析指令，不是问答题
- 结合具体正文内容，不要泛泛而问
- 中文，20字以内
- 如果图片不值得分析，输出 null

生成原则：
- 有产品/品牌 → 问具体产品信息（品牌、型号、规格、档次）
- 有场景/活动 → 问场景细节（地点、人员、消费层次）
- 有人物互动 → 问关系和消费能力线索（穿着、配饰、车辆）
- 无法判断消费场景 → 输出 null

示例：
正文"和双币基金朋友干饭" → "饭局喝的什么酒？什么档次？几人？"
正文"寒夜客来茶当酒" → "什么茶？什么茶具？环境档次？"
正文"电影首映，喝龍國宴酒" → "什么酒？包装？现场几人？什么场合？"

输出格式（必须严格JSON数组，每条帖子对应一个元素，数量必须与输入一致）：
[
  {"signals": ["信号1"], "image_prompt": "分析指令或null"},
  {"signals": [], "image_prompt": null}
]

注意：image_prompt 要引导 AI 描述看到的一切细节，而不是只能回答 Yes/No'''

def extract_signals(posts, api_key, base_url, fallback_configs=None):
    result = call_with_fallback(posts, SYSTEM_PROMPT, api_key, base_url, fallback_configs)
    if result is None:
        return [[{'signals': [], 'image_prompt': None}]] * len(posts)
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