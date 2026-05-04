"""画像特征提取脚本"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_api import call_with_fallback

SYSTEM_PROMPT = '''【画像特征提取】

## 提取原则
从朋友圈内容中推断发帖人的个人特征。特征必须从正文中有明确线索，不做猜测、不填占位符。宁可留空，不可编造，你的输出必须是 key-value 格式的 JSON 对象。

## Key（仅用以下 18 个，禁止自创）
所在城市、婚姻状况、学历、毕业院校、在职单位、职务，行业、家庭结构、社交圈层、人脉资源、性格特征、表达风格、兴趣爱好、价值观倾向、资产档次，投资风格、饮酒偏好，香型偏好

## Value 规范
- 有依据的具体描述
- 每条 <10 字，精简
- 禁止占位符（待确认、未知、推测）
- 禁止示例值（"名车名表"→"高档"）

## 异常处理
- 正文 <30 字或无有效信息：所有 key 填 ""
- 纯转发无法推断：填 ""
- 某条失败：该条所有 key 填 ""

输出 JSON 数组。'''

def extract_traits(posts, api_key, base_url, fallback_configs=None):
    result = call_with_fallback(posts, SYSTEM_PROMPT, api_key, base_url, fallback_configs)
    if result is None:
        return [{}] * len(posts)
    return [
        (item.get('traits', {}) if isinstance(item, dict) and isinstance(item.get('traits'), dict) else {})
        for item in result
    ]

if __name__ == '__main__':
    cfg_path = os.path.expanduser('~/.openclaw/openclaw.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    ali = cfg['models']['providers']['aliyun-bailian']
    test_posts = [{'nickname': '杨香雪儿', 'content': '和双币基金朋友介绍项目后干饭'}]
    print(json.dumps(extract_traits(test_posts, ali['apiKey'], ali['baseUrl']), ensure_ascii=False))