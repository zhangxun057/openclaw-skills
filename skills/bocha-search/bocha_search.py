# -*- coding: utf-8 -*-
"""
博查搜索主脚本
支持网页搜索、实时信息查询
"""

import sys
import io
import os
import json
from datetime import datetime

# 修复 Windows 控制台 Unicode 输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class BochaSearch:
    """
    博查搜索客户端
    """
    
    # 搜索上下文映射
    CONTEXT_MAP = {
        "product_specs": "产品参数",
        "visual_style": "视觉风格",
        "marketing": "营销信息",
        "audience": "受众洞察",
        "competitor": "竞品对比",
        "general": "通用搜索"
    }
    
    def __init__(self):
        """
        初始化博查搜索
        """
        # 优先使用环境变量中的 API Key
        self.api_key = os.environ.get("BOCHA_API_KEY", "")
        
        if not self.api_key:
            print("[BochaSearch] Warning: BOCHA_API_KEY not configured")
            print("[BochaSearch] Please set: export BOCHA_API_KEY='your-key'")
    
    def search(self, query, context="general"):
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            context: 搜索上下文（product_specs/visual_style/marketing/audience/competitor/general）
        
        Returns:
            dict: {
                "query": str,
                "context": str,
                "facts": [],
                "sources": []
            }
        """
        if not self.api_key:
            return {
                "error": "BOCHA_API_KEY not configured",
                "query": query
            }
        
        try:
            import requests
            
            # 博查搜索 API（示例，实际 API 请参考官方文档）
            url = "https://api.bochaai.com/v1/web-search"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "query": query,
                "count": 5,
                "freshness": "noLimit"  # noLimit/oneDay/oneWeek/oneMonth
            }
            
            print("[BochaSearch] Searching: {} (context: {})".format(
                query, self.CONTEXT_MAP.get(context, context)))
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            results = response.json()
            
            # 提取关键信息
            extracted = {
                "query": query,
                "context": context,
                "facts": [],
                "sources": []
            }
            
            if "data" in results and "web_pages" in results["data"]:
                for item in results["data"]["web_pages"][:5]:
                    extracted["sources"].append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "url": item.get("url", "")
                    })
                    
                    # 简单提取事实
                    snippet = item.get("snippet", "")
                    if snippet:
                        extracted["facts"].append(snippet[:200])
            
            return extracted
            
        except Exception as e:
            return {
                "error": str(e),
                "query": query
            }
    
    def search_multiple(self, queries, context="general"):
        """
        批量搜索多个关键词
        
        Args:
            queries: 搜索词列表
            context: 搜索上下文
        
        Returns:
            list: 搜索结果列表
        """
        results = []
        for query in queries:
            result = self.search(query, context)
            results.append(result)
        return results
    
    def organize_results(self, search_results):
        """
        组织搜索结果，返回结构化信息
        
        Args:
            search_results: 搜索结果列表
        
        Returns:
            dict: {
                "facts": [],
                "visual_keywords": [],
                "marketing_claims": [],
                "audience_insights": [],
                "competitor_info": []
            }
        """
        organized = {
            "facts": [],
            "visual_keywords": [],
            "marketing_claims": [],
            "audience_insights": [],
            "competitor_info": []
        }
        
        for result in search_results:
            if "error" in result:
                continue
            
            facts = result.get("facts", [])
            sources = result.get("sources", [])
            
            # 简单分类
            for fact in facts:
                if any(k in fact for k in ["价格", "price", "万", "元", "参数", "配置"]):
                    organized["facts"].append(fact)
                
                if any(k in fact for k in ["设计", "配色", "风格", "visual"]):
                    organized["visual_keywords"].append(fact)
                
                if any(k in fact for k in ["促销", "权益", "优惠", "offer", "活动"]):
                    organized["marketing_claims"].append(fact)
                
                if any(k in fact for k in ["用户", "评价", "关心", "audience"]):
                    organized["audience_insights"].append(fact)
                
                if any(k in fact for k in ["vs", "对比", "竞品", "competitor"]):
                    organized["competitor_info"].append(fact)
        
        # 去重
        for key in organized:
            organized[key] = list(set(organized[key]))[:5]
        
        return organized
    
    def log_to_file(self, filepath="search_log.md"):
        """
        将搜索日志写入文件
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "a", encoding="utf-8") as f:
                f.write("\n## Search Log - {}\n\n".format(
                    datetime.now().strftime("%Y-%m-%d %H:%M")))
                f.write("- **博查搜索** - {}\n".format(datetime.now().strftime("%H:%M:%S")))
                f.write("\n")
            
            print("[BochaSearch] Logged to {}".format(filepath))
            
        except Exception as e:
            print("[BochaSearch] Log error: {}".format(e))
    
    def format_output(self, result):
        """
        格式化输出，用于展示给用户
        
        Args:
            result: 搜索结果
        
        Returns:
            str: 格式化的 Markdown 输出
        """
        if "error" in result:
            return "## ❌ 搜索失败\n\n错误：{}\n\n查询：{}".format(
                result["error"], result.get("query", ""))
        
        output = "## 🔍 搜索结果\n\n"
        output += "**查询**: {}\n\n".format(result["query"])
        
        # 事实信息
        if result.get("facts"):
            output += "### 事实信息\n"
            for fact in result["facts"][:5]:
                output += "- {}\n".format(fact)
            output += "\n"
        
        # 参考来源
        if result.get("sources"):
            output += "### 参考来源\n"
            for i, source in enumerate(result["sources"][:5], 1):
                output += "{}. [{}]({})\n".format(
                    i, source.get("title", "无标题"), source.get("url", "#"))
                output += "   {}\n".format(source.get("snippet", "")[:100])
        
        return output


def main():
    """
    命令行入口
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="博查搜索工具")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--context", "-c", default="general",
                       choices=["product_specs", "visual_style", "marketing", 
                               "audience", "competitor", "general"],
                       help="搜索上下文")
    parser.add_argument("--json", "-j", action="store_true",
                       help="输出 JSON 格式")
    
    args = parser.parse_args()
    
    # 初始化搜索
    search = BochaSearch()
    
    # 执行搜索
    result = search.search(args.query, args.context)
    
    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(search.format_output(result))


if __name__ == "__main__":
    main()
