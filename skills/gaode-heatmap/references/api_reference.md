# 高德地图 API 参考文档

## Web 服务 API

### POI 搜索

**端点：** `https://restapi.amap.com/v3/place/text`

**参数：**

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| key | 是 | Web 服务 API Key | `5edd3a2f42e77bec526e0b0bf9e0a9bf` |
| keywords | 是 | 搜索关键词 | `茅台专卖店` |
| city | 否 | 目标城市 | `贵阳市` |
| offset | 否 | 每页数量（最大 25） | `25` |
| page | 否 | 页码 | `1` |
| types | 否 | POI 类型编码 | `061210`（烟酒专卖店） |
| location | 否 | 中心点坐标（周边搜索） | `116.397428,39.90923` |
| radius | 否 | 搜索半径（米） | `1000` |

**响应示例：**

```json
{
  "status": "1",
  "count": "600",
  "pois": [
    {
      "name": "茅台专卖店",
      "location": "106.647675,26.639325",
      "address": "观山湖区某某路",
      "tel": "0851-12345678"
    }
  ]
}
```

### 地理编码

**端点：** `https://restapi.amap.com/v3/geocode/geo`

**参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| key | 是 | API Key |
| address | 是 | 地址 |
| city | 否 | 城市 |

**响应：**

```json
{
  "status": "1",
  "geocodes": [{
    "location": "106.647675,26.639325",
    "formatted_address": "贵州省贵阳市观山湖区某某路"
  }]
}
```

---

## JS API 2.0

### 加载方式

```html
<!-- 1. 安全密钥（必须在地图 JS 之前） -->
<script>
  window._AMapSecurityConfig = {
    securityJsCode: 'e11247881d953ce319b078137cd459ef'
  };
</script>

<!-- 2. 地图 JS -->
<script src="https://webapi.amap.com/maps?v=2.0&key=d42db0cde8f06cfbdf7cf29864f2a6f9"></script>
```

### 热力图插件

**加载方式：**

```javascript
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
  
  heatmap.setDataSet({
    data: [
      [106.647675, 26.639325, 10],
      [106.643735, 26.641852, 8]
    ],
    max: 10
  });
});
```

**配置参数：**

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| radius | Number | 热力半径 | 30 |
| opacity | Array | 透明度渐变 | [0, 0.8] |
| gradient | Object | 颜色渐变 | 蓝→红 |
| maxOpacity | Number | 最大透明度 | 0.8 |
| scaleByZoom | Boolean | 缩放时调整 | false |

### 数据格式

**热力图数据：** `[[经度，纬度，权重], ...]`

**注意：** 经度在前，纬度在后！

```javascript
// 正确
[106.647675, 26.639325, 10]

// 错误
[26.639325, 106.647675, 10]
```

---

## 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 10001 | 无效 Key | 检查 Key 是否正确 |
| 10002 | Key 过期 | 重新申请 Key |
| 10003 | 超配额 | 等待配额重置或升级 |
| 10004 | 安全密钥错误 | 检查 securityJsCode 配置 |

---

## 链接

- 控制台：https://console.amap.com/dev/keyapp
- JS API 文档：https://lbs.amap.com/api/javascript-api-v2
- Web 服务 API：https://lbs.amap.com/api/webservice/summary
- 热力图示例：https://lbs.amap.com/api/javascript-api/example/heatmap/heatmap
