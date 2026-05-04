"""内容分类提取脚本"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_api import call_with_fallback

SYSTEM_PROMPT = '''【内容分类】
从内容表达性质判断分类：

- 动态分享：发布自己的活动、行程、工作进展、生活动态
- 观点输出：发表看法、感悟、行业观点、人生思考
- 内容转发：转文章/海报/新闻/视频
- 展示分享：展示消费场景、产品、成果、生活片段
- 广告推广：产品推广、品牌宣传、活动招商

只输出分类名称，不要解释。内容无法归类填"未知"，纯表情/纯链接填"内容转发"。

输出JSON数组，每条只有post_type字段。'''


def extract_post_type(posts, api_key, base_url, fallback_configs=None):
    result = call_with_fallback(posts, SYSTEM_PROMPT, api_key, base_url, fallback_configs)
    if result is None:
        return [None] * len(posts)
    return [
        (item.get('post_type') or None if isinstance(item, dict) else None)
        for item in result
    ]


if __name__ == '__main__':
    cfg_path = os.path.expanduser('~/.openclaw/openclaw.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    ali = cfg['models']['providers']['aliyun-bailian']
    test_posts = [{'nickname': '杨香雪儿', 'content': '和双币基金朋友介绍项目'}]
    print(json.dumps(extract_post_type(test_posts, ali['apiKey'], ali['baseUrl']), ensure_ascii=False))
