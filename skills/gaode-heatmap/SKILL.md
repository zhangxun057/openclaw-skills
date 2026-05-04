---
name: gaode-heatmap
description: 高德地图热力图生成与分析。使用场景：(1) 门店/竞品分布可视化，(2) 渠道网络密度分析，(3) 选址评估，(4) 区域市场覆盖分析。自动搜索 POI 数据、生成可交互热力图 HTML、发布为永久 URL。
---

# 高德地图热力图生成 Skill

## 触发场景

当用户提到以下需求时触发此 Skill：
- "生成热力图"、"门店分布图"、"区域密度分析"
- "竞品分布"、"渠道布局图"、"市场覆盖分析"
- "高德地图可视化"、"heatmap"
- "搜索 XX 店并展示分布"（如茅台店、餐厅、酒店等）

## 核心能力

1. **POI 数据搜索** - 调用高德 Web 服务 API 搜索门店/竞品数据
2. **热力图生成** - 使用高德 JS API 2.0 生成可交互热力图
3. **网页发布** - 上传 HTML 到文件服务器，获得永久分享链接
4. **分析报告** - 生成业务洞察和建议

## 完整工作流

```
1. 信息搜索 → 2. 热力图生成 → 3. 网页发布 → 4. 分析报告
```

### 步骤 1：信息搜索

使用高德 Web 服务 API 搜索 POI 数据：

```bash
# 搜索关键词：茅台专卖店，城市：贵阳市
curl "https://restapi.amap.com/v3/place/text?key=5edd3a2f42e77bec526e0b0bf9e0a9bf&keywords=茅台专卖店&city=贵阳市&output=json&offset=25"
```

**参数说明：**
- `key`: Web 服务 API Key（见 apis.md）
- `keywords`: 搜索关键词
- `city`: 目标城市
- `offset`: 每页数量（最大 25）

**输出：** JSON 格式，包含门店名称、地址、经纬度

### 步骤 2：热力图生成

生成 HTML 文件，关键配置：

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>热力图标题</title>
  
  <!-- 1. 安全密钥必须在地图 JS 之前 -->
  <script>
    window._AMapSecurityConfig = {
      securityJsCode: 'e11247881d953ce319b078137cd459ef'
    };
  </script>
  
  <!-- 2. 地图 JS 不要加&plugin 参数 -->
  <script src="https://webapi.amap.com/maps?v=2.0&key=d42db0cde8f06cfbdf7cf29864f2a6f9"></script>
</head>
<body>
  <div id="container"></div>
  
  <script>
    var map = new AMap.Map('container', {
      zoom: 11,
      center: [106.65, 26.65]
    });
    
    // 3. 必须用 map.plugin() 异步加载热力图插件
    map.plugin(['AMap.HeatMap'], function() {
      var heatmap = new AMap.HeatMap(map, {
        radius: 30,
        opacity: [0, 0.7],
        gradient: {
          0.5: 'blue',
          0.65: 'rgb(117,211,248)',
          0.7: 'rgb(0, 255, 0)',
          0.9: '#ffea00',
          1.0: 'red'
        }
      });
      
      // 4. 数据格式：[经度，纬度，权重]
      heatmap.setDataSet({
        data: [
          [106.647675, 26.639325, 10],
          [106.643735, 26.641852, 8]
        ],
        max: 10
      });
    });
  </script>
</body>
</html>
```

### 步骤 3：网页发布

上传 HTML 到文件服务器：

```bash
curl -s -X POST "https://mjy.gzlex.com:8095/api/sse/file/upload" \
  -H "Authorization: Bearer ampzOmhjenFAMTIz" \
  -F "file=@heatmap.html"
```

**响应：**
```json
{"code":"0","data":{"fileUrl":"https://mjy.gzlex.com/heatmap-xxx.html"}}
```

### 步骤 4：分析报告

生成飞书云文档，包含：
- 数据概览（门店总数、覆盖区域）
- 高密度区分析
- 空白市场识别
- 业务建议

## 关键配置要点（血泪教训）

| 问题 | 错误做法 | 正确做法 |
|------|---------|---------|
| 安全密钥 | 和地图 JS 一起加载 | 必须在地图 JS **之前** 单独配置 |
| 插件加载 | `&plugin=AMap.Heatmap` | `map.plugin(['AMap.HeatMap'], callback)` |
| 数据格式 | `[lat, lng, count]` | `[lng, lat, count]`（经度在前！） |
| 协议 | 以为必须用 HTTP | `file://` 协议可直接打开 |
| Referer | 以为不填=全禁止 | 不填=不限制 |

## 问题排查清单

| 问题 | 检查项 | 解决方案 |
|------|--------|---------|
| 地图空白 | F12 Console 报错 | 查看具体错误信息 |
| 地图空白 | Network 标签地图 JS 状态 | 检查 Key 是否有效 |
| 地图空白 | 安全密钥顺序 | 调整 script 顺序 |
| 热力图不显示 | 是否用 map.plugin() | 改为异步加载 |
| 热力图不显示 | 数据格式 | 检查经度纬度顺序 |
| 跨域拦截 | 是否用 file:// 协议 | 高德 2.0 支持 |

## API 配置

所有 API Key 存储在 `~/.openclaw/apis.md` 第 10 节。

| 名称 | 值 |
|------|-----|
| Web 服务 API Key | `5edd3a2f42e77bec526e0b0bf9e0a9bf` |
| 前端 JS API Key | `d42db0cde8f06cfbdf7cf29864f2a6f9` |
| 安全密钥 | `e11247881d953ce319b078137cd459ef` |

**控制台：** https://console.amap.com/dev/keyapp

## 示例场景

### 场景 1：茅台店分布分析

**用户请求：** "生成贵阳市茅台专卖店热力图"

**执行流程：**
1. 搜索 POI：`keywords=茅台专卖店&city=贵阳市`
2. 获取 600 家门店数据
3. 生成热力图 HTML
4. 上传获得 URL
5. 生成分析报告

**交付物：**
- 热力图 URL：https://mjy.gzlex.com/heatmap-xxx.html
- 数据 CSV
- 飞书分析文档

### 场景 2：竞品对比分析

**用户请求：** "对比贵阳茅台和五粮液的门店分布"

**执行流程：**
1. 分别搜索两个品牌 POI
2. 生成对比热力图（不同颜色）
3. 输出竞争格局分析

### 场景 3：潜在客户挖掘

**用户请求：** "搜索贵阳市高档餐厅，生成热力图"

**执行流程：**
1. 搜索 `keywords=高档餐厅&city=贵阳市`
2. 生成热力图
3. 识别高密度区（适合发展经销商）

## 资源文件

### scripts/poi_search.py

执行 POI 搜索的 Python 脚本：

```python
#!/usr/bin/env python3
"""高德 POI 搜索脚本"""
import requests
import json

def search_poi(keywords, city, api_key):
    """搜索 POI 数据"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": api_key,
        "keywords": keywords,
        "city": city,
        "output": "json",
        "offset": 25
    }
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    result = search_poi("茅台专卖店", "贵阳市", "5edd3a2f42e77bec526e0b0bf9e0a9bf")
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

### references/api_reference.md

详细 API 文档，包含：
- Web 服务 API 完整参数说明
- JS API 2.0 配置指南
- 热力图插件 API 参考
- 错误码说明

## 成本控制

| 项目 | 用量 | 单价 | 小计 |
|------|------|------|------|
| 高德 API 调用 | 600 次/城市 | 免费 5 万次/天 | ¥0 |
| 文件服务器上传 | 1 次/图 | 免费 | ¥0 |
| **合计** | - | - | **¥0** |

---

## Usage Logging

每次触发后执行以下脚本记录调用情况：

```bash
node ~/.openclaw/skills/_shared/log-usage.mjs "gaode-heatmap" "<触发原因>" "<结果>"
```
