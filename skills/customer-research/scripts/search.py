# -*- coding: utf-8 -*-
"""
customer-research 搜索模块
整合多数据源（Serper/web_fetch/企查查/browser），支持二阶挖掘
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

# 导入工具
try:
    from qcc_api import qcc_search_and_extract, extract_key_info
except ImportError:
    qcc_search_and_extract = None


# ==================== 配置区 ====================

HIGH_PRIORITY = ['上市情况', '纳税等级', '员工规模']
MEDIUM_PRIORITY = ['注册资本', '年营收', '主营业务']
LOW_PRIORITY = ['行业排名', '发展历程', '企业荣誉']

# 二阶挖掘阈值
SECONDARY_MIN_HOLDING = 10  # 持股>10% 触发挖掘
SECONDARY_MAX_DEPTH = 3     # 最多 3 个方向
SECONDARY_MAX_SEARCHES = 2  # 每方向最多 2 次搜索


# ==================== 数据源函数 ====================

def search_with_serper(query: str) -> Dict:
    """
    L1 - Serper 搜索
    
    Args:
        query: 搜索词
    
    Returns:
        搜索结果
    """
    import requests
    import os
    
    # Serper API Key (从 apis.md 获取)
    SERPER_API_KEY = 'a1b5573c9dae9041939d841fd602d1abba333ee7'
    
    url = 'https://google.serper.dev/search'
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'q': query,
        'num': 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('organic', []):
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'date': item.get('date')
            })
        
        return {
            'source': 'serper',
            'query': query,
            'results': results,
            'info': {}
        }
    except Exception as e:
        return {
            'source': 'serper',
            'query': query,
            'results': [],
            'error': str(e),
            'info': {}
        }


def fetch_with_webfetch(url: str) -> Dict:
    """
    L2 - web_fetch 获取详情页
    
    Args:
        url: 网址
    
    Returns:
        页面内容
    """
    # 实际应调用 web_fetch 工具
    return {
        'source': 'web_fetch',
        'url': url,
        'content': '',
        'info': {}
    }


def query_with_qcc(company_name: str, depth: str = 'basic') -> Dict:
    """
    L3 - 企查查 API
    
    Args:
        company_name: 企业名称
        depth: basic/standard/deep
    
    Returns:
        企查查结果
    """
    if not qcc_search_and_extract:
        return {'error': '企查查 API 未可用'}
    
    return qcc_search_and_extract(company_name, depth=depth)


def browse_with_browser(url: str, action: str = 'snapshot') -> Dict:
    """
    L4 - browser 复杂场景
    
    Args:
        url: 网址
        action: snapshot/screenshot/act
    
    Returns:
        浏览器结果
    """
    # 实际应调用 browser 工具
    return {
        'source': 'browser',
        'url': url,
        'action': action,
        'content': ''
    }


# ==================== 核心搜索函数 ====================

def extract_info_from_serper_results(company_name: str, sources: List[Dict]) -> Dict:
    """
    从 Serper 搜索结果中提取企业信息
    
    Args:
        company_name: 企业名称
        sources: Serper 搜索结果列表
    
    Returns:
        提取的信息字典
    """
    import re
    
    info = {
        'scale': {},
        'industry_status': {},
        'business': {},
        'key_tags': []
    }
    
    # 合并所有搜索结果的文本
    all_text = []
    websites = []
    qcc_result = None
    
    for source in sources:
        for result in source.get('results', []):
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            link = result.get('link', '')
            all_text.append(f"{title}: {snippet}")
            
            # 检测企查查结果
            if 'qcc.com' in link or '企查查' in title:
                qcc_result = f"{title}: {snippet}"
            
            # 检测官网
            if '官网' in title or ('.com' in link and company_name.split(' ')[0] in link):
                websites.append(link)
    
    full_text = '\n'.join(all_text)
    
    # 1. 从企查查结果提取基本信息（优先级最高）
    if qcc_result:
        # 提取法人
        legal_match = re.search(r'法定代表人 ([^\s，,]+)', qcc_result)
        if legal_match:
            info['scale']['法人'] = legal_match.group(1)
        
        # 提取成立时间
        date_match = re.search(r'成立于 (\d{4}年\d{1,2}月)', qcc_result)
        if date_match:
            info['scale']['成立日期'] = date_match.group(1)
        
        # 提取地点
        location_match = re.search(r'位于 ([^\s，,]+)', qcc_result)
        if location_match:
            info['scale']['注册地'] = location_match.group(1)
    
    # 2. 提取上市情况
    if any(kw in full_text for kw in ['上市', 'IPO', 'A 股', '港股', '美股', '科创板']):
        if '未上市' in full_text or '非上市' in full_text:
            info['industry_status']['上市情况'] = '未上市'
        else:
            info['industry_status']['上市情况'] = '已上市（详情需进一步确认）'
            info['key_tags'].append('上市公司')
    else:
        info['industry_status']['上市情况'] = '未上市'
    
    # 3. 提取纳税等级
    if any(kw in full_text for kw in ['纳税大户', '纳税百强', '纳税信用 A 级']):
        info['industry_status']['纳税等级'] = '纳税大户/信用 A 级'
        info['key_tags'].append('纳税大户')
    
    # 4. 提取员工规模
    employee_match = re.search(r'(\d+[+-]?)\s*[个名]?员 [工丁]', full_text)
    if employee_match:
        info['scale']['员工数'] = employee_match.group(1)
    elif any(kw in full_text for kw in ['小微企业', '中小企业', '大型企业', '集团']):
        if '集团' in full_text:
            info['scale']['企业规模'] = '大型/集团'
            info['key_tags'].append('企业集团')
        elif '小微' in full_text:
            info['scale']['企业规模'] = '小微企业'
    
    # 5. 提取注册资本
    regist_match = re.search(r'(\d+(?:\.\d+)?)\s*[万千亿]元', full_text)
    if regist_match:
        info['scale']['注册资本'] = regist_match.group(0)
    
    # 6. 提取主营业务（从官网描述或snippet 中提取）
    business_keywords = ['专注于', '主要从事', '主营业务', '致力于', '提供']
    for keyword in business_keywords:
        pattern = re.compile(rf'{keyword}([^，,.。]+)')
        match = pattern.search(full_text)
        if match:
            info['business']['主营业务'] = match.group(1).strip()
            break
    
    # 7. 提取官网
    if websites:
        info['business']['官网'] = websites[0]
    
    # 8. 提取行业标签
    industry_keywords = {
        '科技': '科技企业',
        'AI': 'AI 企业',
        '人工智能': '人工智能企业',
        '自然语言处理': 'NLP 企业',
        '政务': '政务智能',
        '软件': '软件企业',
        '系统服务': '系统服务'
    }
    
    for keyword, tag in industry_keywords.items():
        if keyword in full_text:
            info['key_tags'].append(tag)
    
    return info


def search_company(company_name: str, use_qcc: bool = False) -> Dict:
    """
    搜索企业信息
    
    Args:
        company_name: 企业名称
        use_qcc: 是否使用企查查
    
    Returns:
        搜索结果
    """
    result = {
        'company_name': company_name,
        'search_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'sources': [],
        'info': {
            'scale': {},
            'industry_status': {},
            'business': {},
            'key_tags': []
        },
        'secondary_digging': []
    }
    
    # L1: Serper 搜索（必做）
    serper_queries = [
        f"{company_name} 上市 纳税 规模 员工",
        f"{company_name} 官网 主营业务 产品",
        f"{company_name} 行业地位 排名"
    ]
    
    print(f"  执行 Serper 搜索...")
    for query in serper_queries:
        print(f"    - 搜索：{query}")
        serper_result = search_with_serper(query)
        if serper_result.get('results'):
            result['sources'].append(serper_result)
            print(f"      找到 {len(serper_result['results'])} 条结果")
        else:
            error_msg = serper_result.get('error', '无结果')
            print(f"      {error_msg}")
    
    # 从搜索结果中提取信息
    print(f"\n  提取企业信息...")
    extracted_info = extract_info_from_serper_results(company_name, result['sources'])
    result['info'].update(extracted_info)
    
    # 打印提取到的信息
    for category, items in extracted_info.items():
        if items:
            print(f"  {category}:")
            if isinstance(items, list):
                for item in items:
                    if item:
                        print(f"    - {item}")
            elif isinstance(items, dict):
                for key, value in items.items():
                    if value:
                        print(f"    - {key}: {value}")
    
    # L2: web_fetch（如有官网）
    official_website = extracted_info.get('business', {}).get('官网')
    if official_website:
        print(f"\n  获取官网内容：{official_website}")
        webfetch_result = fetch_with_webfetch(official_website)
        if webfetch_result.get('content'):
            result['sources'].append(webfetch_result)
            print(f"    获取到 {len(webfetch_result['content'])} 字符内容")
    
    # L3: 企查查（可选）
    if use_qcc and qcc_search_and_extract:
        print(f"\n  调用企查查 API...")
        qcc_result = query_with_qcc(company_name, depth='basic')
        if not qcc_result.get('error'):
            result['sources'].append({'source': 'qcc', 'data': qcc_result})
            print(f"    获取到企查查数据")
        else:
            print(f"    企查查查询失败：{qcc_result.get('error')}")
    
    return result


def search_person(person_info: str) -> Dict:
    """
    搜索个人客户信息
    
    Args:
        person_info: 个人信息（姓名 + 职务/商会等）
    
    Returns:
        搜索结果
    """
    result = {
        'person_info': person_info,
        'search_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'sources': [],
        'associated_companies': [],
        'info': {}
    }
    
    # L1: Serper 搜索
    queries = [
        f"{person_info} 公司",
        f"{person_info} 职务",
        f"{person_info} 商会 协会"
    ]
    
    for query in queries:
        serper_result = search_with_serper(query)
        if serper_result.get('results'):
            result['sources'].append(serper_result)
    
    # 提取关联企业
    companies = extract_companies_from_person_search(result['sources'])
    result['associated_companies'] = companies
    
    return result


# ==================== 二阶挖掘函数 ====================

def check_secondary_digging(search_result: Dict) -> List[Dict]:
    """
    检查是否触发二阶挖掘
    
    Args:
        search_result: 一级搜索结果
    
    Returns:
        需要挖掘的方向列表
    """
    digging_directions = []
    
    # 检查股东
    shareholders = search_result.get('info', {}).get('shareholders', [])
    for shareholder in shareholders:
        holding = shareholder.get('holding_percent', 0)
        if holding > SECONDARY_MIN_HOLDING:
            digging_directions.append({
                'type': 'shareholder',
                'target': shareholder['name'],
                'reason': f'持股{holding}%（>{SECONDARY_MIN_HOLDING}%）'
            })
    
    # 检查对外投资
    investments = search_result.get('info', {}).get('investments', [])
    for inv in investments:
        digging_directions.append({
            'type': 'investment',
            'target': inv['name'],
            'reason': '对外投资'
        })
    
    # 检查高管关联
    executives = search_result.get('info', {}).get('executives', [])
    for exec in executives:
        other_positions = exec.get('other_positions', [])
        if other_positions:
            digging_directions.append({
                'type': 'executive',
                'target': exec['name'],
                'reason': f'在其他{len(other_positions)}家公司任职'
            })
    
    # 限制挖掘方向数量
    return digging_directions[:SECONDARY_MAX_DEPTH]


def execute_secondary_digging(directions: List[Dict]) -> List[Dict]:
    """
    执行二阶挖掘
    
    Args:
        directions: 挖掘方向列表
    
    Returns:
        挖掘结果
    """
    results = []
    
    for direction in directions:
        dig_type = direction['type']
        target = direction['target']
        
        # 根据类型选择搜索策略
        if dig_type == 'shareholder':
            queries = [
                f"{target} 背景 经历",
                f"{target} 公司 投资"
            ]
        elif dig_type == 'investment':
            queries = [
                f"{target} 公司 业务",
                f"{target} 工商信息"
            ]
        elif dig_type == 'executive':
            queries = [
                f"{target} 任职 公司",
                f"{target} 背景"
            ]
        else:
            continue
        
        # 执行搜索（最多 SECONDARY_MAX_SEARCHES 次）
        for query in queries[:SECONDARY_MAX_SEARCHES]:
            result = search_with_serper(query)
            if result.get('results'):
                results.append({
                    'direction': direction,
                    'query': query,
                    'result': result
                })
    
    return results


# ==================== 辅助函数 ====================

def extract_website(sources: List) -> Optional[str]:
    """从搜索结果中提取官网 URL"""
    for source in sources:
        for result in source.get('results', []):
            link = result.get('link', '')
            if '官网' in result.get('title', '') or 'official' in link.lower():
                return link
    return None


def extract_companies_from_person_search(sources: List) -> List[str]:
    """从个人搜索结果中提取关联企业"""
    companies = []
    # 简化实现，实际应解析搜索结果
    return companies


def judge_search_result(result: Dict) -> str:
    """判断搜索结果类型"""
    if not result.get('sources'):
        return 'none'
    
    high_priority_count = sum(
        1 for key in HIGH_PRIORITY 
        if result.get('info', {}).get(key.lower())
    )
    
    if high_priority_count >= 2:
        return 'sufficient'
    elif high_priority_count >= 1:
        return 'insufficient'
    else:
        return 'none'


def request_qcc_authorization(cost: float, purpose: str) -> bool:
    """请求用户授权使用企查查"""
    print(f"\n⚠️  检测到企查查 API 可用：")
    print(f"   - 成本：¥{cost:.2f}")
    print(f"   - 用途：{purpose}")
    print(f"\n是否继续？(确认/取消)")
    return False


if __name__ == '__main__':
    # 测试
    print("搜索模块测试")
