"""销售信号提取脚本"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_api import call_with_fallback

SYSTEM_PROMPT = '''【销售信号提取】
判断核心：现在或近期，有没有理由去联系对方卖酒？

强信号 = 有人生节点或明确需求，能支撑具体销售行动：
- 人生节点：婚礼、升学、开业、乔迁、周年庆、生日
- 活动预告：峰会、发布会、庆典、展会、宴请（有具体时间）
- 需求暗示：正在选伴手礼、新店筹备中、想找定制方案

不提取为信号（归入画像 traits）：
- 消费实力展示（开拉菲、酒柜全是茅台）
- 饮酒偏好表达（只喝酱香）
- 一般性商务动态（无明确用酒需求）

约束：
- 每个 signal 必须<10 字，超过则精简（例："孩子周岁封坛，有定制储酒需求"→"周岁封坛"）
- 只提取强信号。纯转发内容无本人需求填[]。无信号则 signals 为[]。

输出 JSON 数组，每条只有 signals 字段。'''


def extract_signals(posts, api_key, base_url, fallback_configs=None):
    result = call_with_fallback(posts, SYSTEM_PROMPT, api_key, base_url, fallback_configs)
    if result is None:
        return [[]] * len(posts)
    return [
        (item.get('signals', []) if isinstance(item, dict) and isinstance(item.get('signals'), list) else [])
        for item in result
    ]


if __name__ == '__main__':
    cfg_path = os.path.expanduser('~/.openclaw/openclaw.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    ali = cfg['models']['providers']['aliyun-bailian']
    test_posts = [{'nickname': '杨香雪儿', 'content': '和双币基金朋友介绍项目'}]
    print(json.dumps(extract_signals(test_posts, ali['apiKey'], ali['baseUrl']), ensure_ascii=False))
