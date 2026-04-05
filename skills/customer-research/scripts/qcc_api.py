# -*- coding: utf-8 -*-
"""
企查查 API 封装模块
提供企业搜索、工商查询、深度尽调等能力
"""

import requests
import hashlib
import time
import json
import os
from typing import Dict, List, Optional


def load_api_keys() -> tuple:
    """加载 API 密钥（硬编码，从对话中获取）"""
    # 从 2026-03-28 对话中获取的凭证
    api_key = "56ffd2c150294cb4ad6fbe9fc21a62ab"
    secret_key = "F6899B72B4E3EB76C00CA73C96E51D53"
    return api_key, secret_key


def generate_token(api_key: str, secret_key: str) -> tuple:
    """生成 Token 和 Timespan"""
    timespan = str(int(time.time()))
    token_str = f"{api_key}{timespan}{secret_key}"
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest().upper()
    return token, timespan


# ==================== API 调用函数 ====================

def qcc_search_886(search_key: str) -> Dict:
    """
    886 接口 - 企业模糊搜索
    
    用途：快速确认企业是否存在，获取准确企业全称
    成本：¥0.10
    返回：企业列表（名称、法人、成立日期、状态、信用代码）
    """
    api_key, secret_key = load_api_keys()
    if not api_key:
        return {'Status': 'Error', 'Message': 'API 密钥未配置'}
    
    token, timespan = generate_token(api_key, secret_key)
    url = "https://api.qichacha.com/FuzzySearch/GetList"
    params = {'key': api_key, 'searchKey': search_key}
    headers = {'Token': token, 'Timespan': timespan}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {'Status': 'Error', 'Message': str(e)}


def qcc_verify_2001(exact_name: str) -> Dict:
    """
    2001 接口 - 企业身份核验
    
    用途：获取准确工商信息（注册资本、员工规模、联系方式）
    成本：¥1.00
    返回：企业详细信息
    """
    api_key, secret_key = load_api_keys()
    if not api_key:
        return {'Status': 'Error', 'Message': 'API 密钥未配置'}
    
    token, timespan = generate_token(api_key, secret_key)
    url = "https://api.qichacha.com/EnterpriseInfo/Verify"
    params = {'key': api_key, 'searchKey': exact_name}
    headers = {'Token': token, 'Timespan': timespan}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        return response.json()
    except Exception as e:
        return {'Status': 'Error', 'Message': str(e)}


def qcc_kyc_2003(exact_name: str) -> Dict:
    """
    2003 接口 - 客户身份识别（KYC 深度尽调）
    
    用途：获取股东、高管、对外投资、风险信息等
    成本：¥3.00
    返回：企业完整信息
    """
    api_key, secret_key = load_api_keys()
    if not api_key:
        return {'Status': 'Error', 'Message': 'API 密钥未配置'}
    
    token, timespan = generate_token(api_key, secret_key)
    url = "https://api.qichacha.com/CustomerDueDiligence/KYC"
    params = {'key': api_key, 'searchKey': exact_name}
    headers = {'Token': token, 'Timespan': timespan}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        return response.json()
    except Exception as e:
        return {'Status': 'Error', 'Message': str(e)}


# ==================== 高层封装函数 ====================

def qcc_search_and_extract(company_name: str, depth: str = 'basic') -> Dict:
    """
    企业查询与提取（高层封装）
    
    Args:
        company_name: 企业名称
        depth: 查询深度
            - 'basic': 仅 886 搜索（¥0.10）
            - 'standard': 886+2001（¥1.10）
            - 'deep': 886+2003（¥3.10）
    
    Returns:
        查询结果字典
    """
    result = {
        'company_name': company_name,
        'depth': depth,
        'interfaces_used': [],
        'total_cost': 0.0,
        'data': {}
    }
    
    # 第一步：886 搜索
    data_886 = qcc_search_886(company_name)
    
    if data_886.get('Status') != '200':
        result['error'] = data_886.get('Message', '查询失败')
        return result
    
    companies = data_886.get('Result', [])
    if not companies:
        result['error'] = '未找到相关企业'
        return result
    
    # 使用第一个结果
    exact_name = companies[0].get('Name')
    result['data']['basic'] = companies[0]
    result['interfaces_used'].append('886')
    result['total_cost'] += 0.10
    
    # 第二步：根据深度选择接口
    if depth == 'standard':
        data_2001 = qcc_verify_2001(exact_name)
        if data_2001.get('Status') == '200':
            result['data']['detail'] = data_2001.get('Result', {}).get('Data', {})
            result['interfaces_used'].append('2001')
            result['total_cost'] += 1.00
    
    elif depth == 'deep':
        data_2003 = qcc_kyc_2003(exact_name)
        if data_2003.get('Status') == '200':
            result['data']['detail'] = data_2003.get('Result', {}).get('Data', {})
            result['interfaces_used'].append('2003')
            result['total_cost'] += 3.00
    
    return result


def extract_key_info(qcc_result: Dict) -> Dict:
    """
    从企查查结果中提取关键信息
    
    Returns:
        关键信息字典
    """
    data = qcc_result.get('data', {}).get('detail', {})
    
    return {
        '企业全称': data.get('Name'),
        '法人': data.get('OperName'),
        '注册资本': data.get('RegistCapi'),
        '成立日期': data.get('StartDate'),
        '经营状态': data.get('Status'),
        '员工规模': data.get('PersonScope'),
        '参保人数': data.get('InsuredCount'),
        '行业': data.get('Industry', {}).get('SmallCategory'),
        '经营范围': data.get('Scope'),
        '联系方式': data.get('ContactInfo', {}).get('Tel'),
        '网站': data.get('ContactInfo', {}).get('WebSiteList', []),
        '股东数量': len(data.get('PubPartnerList', [])),
        '高管数量': len(data.get('EmployeeList', [])),
        '对外投资': len(data.get('InvestmentList', [])),
        '风险信息': {
            '失信被执行': data.get('ShiXin'),
            '被执行人': data.get('ZhiXing'),
            '行政处罚': data.get('AdminPenalty'),
            '经营异常': data.get('Exception'),
        },
    }


if __name__ == '__main__':
    print("企查查 API 模块已加载")
