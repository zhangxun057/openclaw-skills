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
print(f"使用 API Key: {api_key[:10]}...")

# 使用 wanx 文生图 API
for i, module in enumerate(prompts):
    print(f"\n生成模块 {module['id']}: {module['name']}")
    
    # 简化 prompt 为中文
    content_map = {
        'A-01': 'A 股市场数据可视化信息图，实验室手册风格，技术参数刻度表，显示：成交额突破 2 万亿，三大指数收涨，超 5100 只个股上涨，沪指涨超 1%，微盘股大涨 4%，电力医药反弹，恒指涨 2%，老铺黄金涨 10%。浅灰色网格背景，鼠尾草绿主色，荧光粉高亮，柠檬黄数字。',
        'B-05': '中东局势对比信息图，实验室手册风格，场景对比卡片，显示：美伊和谈信号，巴基斯坦斡旋，伊朗埃及外长通话，特朗普称协议形成，伊朗议长否认，本周巴基斯坦会谈，伊朗警告波斯湾布水雷。浅灰网格背景，细线分隔各场景。',
        'C-12': '国防科技结构拆解信息图，实验室手册风格，技术爆炸图，显示：阿里玄铁 C950 处理器，刷新全球纪录，AI Agent 定制，RISC-V 架构，千问加入无剑联盟，国产芯片突破，AI+ 芯片协同。放大圈标注细节，技术草图风格。',
        'D-03': '能源市场警告信息图，高对比度警示区，显示：日本释放最大石油储备，绕行油轮抵日，摩根大通预测供应缺口千万桶/日，霍尔木兹海峡风险，油价波动，多国启动储备。荧光粉背景，黑色文字，高对比度设计。',
        'E-07': 'ETF 分红数据表信息图，实验室数据表风格，显示：年内沪市 34 只 ETF 分红，规模超 182 亿元，分红密集，投资者收益增加。浅灰网格背景，表格布局，柠檬黄高亮关键数值。',
        'F-10': '关键观察状态栏信息图，实验室手册风格，信息块堆叠，显示：A 股活跃情绪积极，中东和谈信号但表态不一，国产芯片突破，能源受地缘政治影响。浅灰网格背景，信息块布局，条形码图案。'
    }
    
    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": content_map[module['id']],
            "negative_prompt": "模糊，低质量，失真，文字不清，混乱"
        },
        "parameters": {
            "style": "<auto>",
            "size": "1024x768",
            "n": 1
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    
    # 提交异步任务
    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        json=payload,
        headers=headers
    )
    
    if resp.status_code == 200:
        result = resp.json()
        task_id = result.get('output', {}).get('task_id', 'N/A')
        print(f"  任务提交成功：{task_id}")
        
        # 轮询任务状态
        for attempt in range(10):
            time.sleep(3)
            status_resp = requests.get(
                f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                task_status = status_data.get('output', {}).get('task_status', '')
                if task_status == 'SUCCEEDED':
                    img_url = status_data.get('output', {}).get('results', [{}])[0].get('url', '')
                    if img_url:
                        # 下载图像
                        img_resp = requests.get(img_url)
                        if img_resp.status_code == 200:
                            filename = f"{module['id']}_{module['name']}.png"
                            with open(filename, 'wb') as img_file:
                                img_file.write(img_resp.content)
                            print(f"  图像已保存：{filename}")
                        break
                elif task_status == 'FAILED':
                    print(f"  任务失败：{status_data}")
                    break
            else:
                print(f"  状态查询失败：{status_resp.status_code}")
    else:
        print(f"  提交失败：{resp.status_code} - {resp.text[:200]}")

print("\n\n所有模块处理完成")
