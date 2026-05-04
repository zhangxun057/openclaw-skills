"""事件提取脚本"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_api import call_with_fallback

SYSTEM_PROMPT = '''【事件提取】
记录发帖人亲身经历或主动发起的具体行动。
格式：动词开头，只讲一件事，抓主要矛盾。
能回答"谁+做了什么/去了哪"，不附加次要信息。
保留专有名词：活动名称、品牌名、机构名、地点名必须完整保留，不得泛化替换。

判断是否为本人事件，依据 type 字段：
- type=3（链接/公众号文章转发）、type=28（视频号）、type=34（小程序）：视为转发内容，不提取事件，填[]
- 其他 type（1/15/54等图文/纯文字动态）：即使内容主语是机构或组织，也视为本人参与的事件，正常提取

禁止提炼为event的情况：
- 社交用语（"晚上见"、"来了"）
- 动态描述（"发布求职信息"是行为，非事件）
- 纯信息发布（发布通知）

正确示例："参加2026中国酒业渠道领袖峰会青岛站"、"出席AIROBO与和泓服务签约启动仪式"、"商务宴请喝15年茅台"
错误示例："参加温泉团建"（丢失机构名）、"进行真假产品对比实测"（泛化，应保留品牌名）、"高强度工作"（状态标签）

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
