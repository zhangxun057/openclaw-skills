#!/usr/bin/env python3
import json
import os
import requests

# 读取 prompts
with open('news_infographic_20260324_prompts.json', 'r', encoding='utf-8') as f:
    prompts = json.load(f)

# 从 openclaw.json 读取 API key
with open(os.path.expanduser('~/.openclaw/openclaw.json'), 'r') as f:
    config = json.load(f)

api_key = config['models']['providers']['dashscope']['apiKey']

# 生成每个模块的图像
for module in prompts:
    print(f"生成模块 {module['id']}: {module['name']}")
    
    payload = {
        "model": "wanx2.1-t2i-turbo",
        "input": {
            "prompt": module['prompt']
        },
        "parameters": {
            "size": "1024x768",
            "n": 1
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 提交任务
    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        json=payload,
        headers=headers
    )
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"  任务提交成功：{result.get('output', {}).get('task_id', 'N/A')}")
    else:
        print(f"  失败：{resp.status_code} - {resp.text[:200]}")

print("\n所有模块图像生成任务已提交")
