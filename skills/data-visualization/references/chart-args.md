# Chart Args Reference

## 通用参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| data | array | ✅ | 数据数组，每项是一个对象 |
| title | string | ❌ | 图表标题 |
| width | number | ❌ | 宽度，默认 800 |
| height | number | ❌ | 高度，默认 500 |
| theme | string | ❌ | 主题: 'default' 或 'classic' |

## generate_line_chart / generate_area_chart

```json
{
  "tool": "generate_line_chart",
  "args": {
    "data": [
      {"month": "Jan", "value": 30},
      {"month": "Feb", "value": 45}
    ],
    "xField": "month",
    "yField": "value",
    "seriesField": "category",
    "title": "月度趋势"
  }
}
```

- `xField`: X轴字段
- `yField`: Y轴字段
- `seriesField`: 分组字段（多条线时）

## generate_bar_chart / generate_column_chart

```json
{
  "tool": "generate_bar_chart",
  "args": {
    "data": [
      {"category": "A", "value": 100},
      {"category": "B", "value": 80}
    ],
    "xField": "category",
    "yField": "value",
    "title": "分类对比"
  }
}
```

- bar = 横向, column = 纵向

## generate_pie_chart

```json
{
  "tool": "generate_pie_chart",
  "args": {
    "data": [
      {"type": "白酒", "sales": 400},
      {"type": "红酒", "sales": 300}
    ],
    "angleField": "sales",
    "colorField": "type",
    "title": "品类占比"
  }
}
```

- `angleField`: 角度映射字段（数值）
- `colorField`: 颜色映射字段（分类）

## generate_scatter_chart

```json
{
  "tool": "generate_scatter_chart",
  "args": {
    "data": [
      {"x": 10, "y": 20, "group": "A"},
      {"x": 15, "y": 35, "group": "B"}
    ],
    "xField": "x",
    "yField": "y",
    "colorField": "group",
    "title": "相关性分析"
  }
}
```

## generate_histogram_chart

```json
{
  "tool": "generate_histogram_chart",
  "args": {
    "data": [{"price": 100}, {"price": 150}, {"price": 200}],
    "field": "price",
    "binNumber": 10,
    "title": "价格分布"
  }
}
```

## generate_dual_axes_chart

```json
{
  "tool": "generate_dual_axes_chart",
  "args": {
    "data": [
      {"month": "Jan", "sales": 100, "growth": 0.15},
      {"month": "Feb", "sales": 120, "growth": 0.20}
    ],
    "xField": "month",
    "yFields": ["sales", "growth"],
    "title": "销售与增长率"
  }
}
```

## generate_radar_chart

```json
{
  "tool": "generate_radar_chart",
  "args": {
    "data": [
      {"name": "产品A", "口感": 80, "香气": 90, "包装": 70},
      {"name": "产品B", "口感": 75, "香气": 85, "包装": 85}
    ],
    "fields": ["口感", "香气", "包装"],
    "nameField": "name",
    "title": "产品对比"
  }
}
```

## generate_funnel_chart

```json
{
  "tool": "generate_funnel_chart",
  "args": {
    "data": [
      {"stage": "访问", "count": 1000},
      {"stage": "咨询", "count": 500},
      {"stage": "下单", "count": 200}
    ],
    "xField": "stage",
    "yField": "count",
    "title": "转化漏斗"
  }
}
```

## generate_treemap_chart

```json
{
  "tool": "generate_treemap_chart",
  "args": {
    "data": [
      {"name": "酱香型", "value": 500},
      {"name": "浓香型", "value": 300}
    ],
    "nameField": "name",
    "valueField": "value",
    "title": "品类结构"
  }
}
```
