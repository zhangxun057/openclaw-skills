"""事件提取脚本"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_api import call_with_fallback

SYSTEM_PROMPT = '''【事件提取】
记录发帖人亲身经历或主动发起的具体行动。
格式：动词开头，只讲一件事，抓主要矛盾。
能回答"谁+做了什么/去了哪"，不附加次要信息。

禁止提炼为event的情况：
- 社交用语（"晚上见"、"来了"）
- 动态描述（"发布求职信息"是行为，非事件）
- 纯转发内容（对方发布的活动描述，非本人参与的事件）
- 纯信息发布（发布通知、转发文章）

正确示例："抵达北京西站"（出行）、"商务宴请喝15年茅台"、"参加中国酒业渠道领袖峰会"
错误示例："高强度工作"（状态标签）、"博鳌乐城高端体检"（缺动词）、"吴向东珍酒直播烤酒车间"（转发内容）

无具体事件时填[]。某条分析失败该条填[]。

输出JSON数组，每条只有events字段。'''


def extract_events(posts, api_key, base_url, fallback_configs=None):
    result = call_with_fallback(posts, SYSTEM_PROMPT, api_key, base_url, fallback_configs, content_len=150)
    if result is None:
        return [None] * len(posts)
    return [
        (item.get('events', []) if isinstance(item, dict) and isinstance(item.get('events'), list) else [])
        for item in result
    ]


if __name__ == '__main__':
    from shared_api import call_with_fallback
    import json
    cfg_path = os.path.expanduser('~/.openclaw/openclaw.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    ali = cfg['models']['providers']['aliyun-bailian']
    test_posts = [
        {'nickname': '杨香雪儿', 'content': '和双币基金朋友介绍项目后干饭'},
        {'nickname': '国台黄建英', 'content': '组织VIP客户包机茅台镇回厂探秘'},
    ]
    print(json.dumps(extract_events(test_posts, ali['apiKey'], ali['baseUrl']), ensure_ascii=False))
