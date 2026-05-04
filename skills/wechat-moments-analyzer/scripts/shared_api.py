"""共享 HTTP Session + API 调用工具"""
import json, time, re, requests, warnings
from requests.adapters import HTTPAdapter

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# 全局 Session，限制连接池大小防止内存泄漏
_session = requests.Session()
_session.verify = False
_session.mount('https://', HTTPAdapter(pool_connections=4, pool_maxsize=20))
_session.mount('http://', HTTPAdapter(pool_connections=4, pool_maxsize=20))


def call_api(posts, api_key, base_url, model, system_prompt, content_len=200):
    user_content = '\n'.join(
        '%d. %s|type=%s|%s' % (i+1, p.get('nickname', ''), p.get('type', ''), p.get('content', p.get('contentDesc', ''))[:content_len])
        for i, p in enumerate(posts)
    )
    # dashscope 国内直连，绕过系统代理
    proxies = {'http': None, 'https': None} if 'dashscope.aliyuncs.com' in base_url else None
    resp = _session.post(
        base_url + '/chat/completions',
        headers={'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'},
        json={
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content},
            ],
            'temperature': 0.1,
            'max_tokens': 4096,
        },
        timeout=180,
        proxies=proxies,
    )
    if resp.status_code != 200:
        raise Exception(f"API error: {resp.status_code} {resp.text[:200]}")
    content = resp.json()['choices'][0]['message']['content'].strip()
    # 剥离 <think>...</think> 推理块
    import re
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    if content.startswith('```'):
        lines = content.split('\n')
        content = '\n'.join(lines[1:-1])
    return json.loads(content)


def call_with_retry(posts, api_key, base_url, model, system_prompt, max_retries=2, content_len=200):
    for attempt in range(max_retries + 1):
        try:
            return call_api(posts, api_key, base_url, model, system_prompt, content_len)
        except Exception as e:
            if attempt < max_retries:
                wait = 5 * (3 ** attempt)
                print(f"    API调用失败，{wait}秒后重试 ({attempt+1}/{max_retries}): {str(e)[:80]}")
                time.sleep(wait)
    return None


def call_with_fallback(posts, system_prompt, api_key, base_url, fallback_configs=None, model='qwen3.6-plus', content_len=200):
    result = call_with_retry(posts, api_key, base_url, model, system_prompt, content_len=content_len)
    if result is None and fallback_configs:
        for fb in fallback_configs:
            print(f"    切换到备选模型: {fb.get('model', 'unknown')}")
            result = call_with_retry(posts, fb['apiKey'], fb['baseUrl'], fb.get('model', 'qwen3.5-plus'), system_prompt, max_retries=1, content_len=content_len)
            if result is not None:
                break
    return result
