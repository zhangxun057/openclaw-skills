#!/usr/bin/env python3
"""
高德 POI 搜索脚本
用于搜索门店、竞品、餐厅等兴趣点数据
"""
import requests
import json
import sys

# 从 apis.md 读取 API Key
API_KEY = "5edd3a2f42e77bec526e0b0bf9e0a9bf"
BASE_URL = "https://restapi.amap.com/v3/place/text"

def search_poi(keywords, city, page=1, offset=25):
    """
    搜索 POI 数据
    
    Args:
        keywords: 搜索关键词（如"茅台专卖店"、"餐厅"）
        city: 目标城市（如"贵阳市"）
        page: 页码（默认 1）
        offset: 每页数量（最大 25）
    
    Returns:
        dict: POI 搜索结果
    """
    params = {
        "key": API_KEY,
        "keywords": keywords,
        "city": city,
        "output": "json",
        "offset": offset,
        "page": page
    }
    
    response = requests.get(BASE_URL, params=params)
    return response.json()

def extract_locations(poi_result):
    """
    从 POI 结果中提取经纬度数据
    
    Args:
        poi_result: POI 搜索结果的 JSON
    
    Returns:
        list: [[经度，纬度，权重], ...]
    """
    locations = []
    if poi_result.get("pois"):
        for poi in poi_result["pois"]:
            if "location" in poi:
                lng, lat = poi["location"].split(",")
                locations.append([float(lng), float(lat), 1])
    return locations

def main():
    if len(sys.argv) < 3:
        print("用法：python poi_search.py <关键词> <城市>")
        print("示例：python poi_search.py 茅台专卖店 贵阳市")
        sys.exit(1)
    
    keywords = sys.argv[1]
    city = sys.argv[2]
    
    print(f"搜索：{keywords} - {city}")
    result = search_poi(keywords, city)
    
    if result.get("status") == "1":
        count = result.get("count", 0)
        print(f"找到 {count} 条记录")
        
        # 输出前 10 条详情
        if result.get("pois"):
            print(f"\n前 10 条结果：")
            for i, poi in enumerate(result["pois"][:10], 1):
                print(f"{i}. {poi.get('name', 'N/A')} - {poi.get('address', 'N/A')}")
    else:
        print(f"搜索失败：{result.get('info', 'Unknown error')}")

if __name__ == "__main__":
    main()
