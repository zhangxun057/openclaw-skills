#!/usr/bin/env python3
import json
import os
import requests
import time

# 读取 prompts
with open('news_infographic_20260324_prompts.json', 'r', encoding='utf-8') as f:
    prompts = json.load(f)

# 从 openclaw.json 读取 API key
with open(os.path.expanduser('~/.openclaw/openclaw.json'), 'r') as f:
    config = json.load(f)

api_key = config['models']['providers']['dashscope']['apiKey']

# 简化内容映射
content_map = {
    'A-01': 'A 股市场数据可视化信息图，实验室手册风格，技术参数刻度表，成交额 2 万亿，三大指数收涨，5100 只个股上涨。浅灰网格背景，鼠尾草绿主色，荧光粉高亮。',
    'B-05': '中东局势对比信息图，实验室手册风格，场景对比卡片，美伊和谈，巴基斯坦斡旋，伊朗埃及通话。浅灰网格背景，细线分隔。',
    'C-12': '国防科技结构拆解信息图，阿里玄铁 C950 处理器，RISC-V 架构，AI Agent 定制，国产芯片突破。技术爆炸图风格，放大圈标注。',
    'D-03': '能源市场警告信息图，日本释放石油储备，供应缺口千万桶/日，霍尔木兹风险。荧光粉背景，黑色文字，高对比度。',
    'E-07': 'ETF 分红数据表，沪市 34 只 ETF 分红，规模 182 亿元。实验室数据表风格，表格布局。',
    'F-10': '关键观察状态栏，A 股活跃，中东和谈，芯片突破，能源地缘政治。信息块堆叠，条形码图案。'
}

print("使用 dashscope 文生图 API (wanx-v1)\n")

for i, module in enumerate(prompts):
    print(f"生成模块 {module['id']}: {module['name']}")
    
    # 使用正确的 wanx API 端点
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-to-image/generation"
    
    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": content_map[module['id']]
        },
        "parameters": {
            "style": "<auto>",
            "size": "1024x768",
            "n": 1
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 同步调用
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    
    print(f"  API 响应状态：{resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"  响应：{json.dumps(result, ensure_ascii=False)[:300]}")
        
        # 提取图像 URL
        img_url = result.get('output', {}).get('results', [{}])[0].get('url', '')
        if img_url:
            # 下载图像
            img_resp = requests.get(img_url, timeout=30)
            if img_resp.status_code == 200:
                filename = f"{module['id']}_{module['name']}.png"
                with open(filename, 'wb') as img_file:
                    img_file.write(img_resp.content)
                print(f"  ✓ 图像已保存：{filename}")
            else:
                print(f"  ✗ 下载失败：{img_resp.status_code}")
        else:
            print(f"  ✗ 无图像 URL")
    else:
        print(f"  ✗ 错误：{resp.text[:300]}")
    
    time.sleep(1)  # 避免限流

print("\n\n所有模块处理完成")
