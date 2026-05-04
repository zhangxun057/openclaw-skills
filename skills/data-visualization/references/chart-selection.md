# Chart Type Selection Guide

## Quick Decision Matrix

| 数据特征 | 推荐图表 | tool name |
|---------|---------|-----------|
| 趋势（时间序列） | 折线图 | `generate_line_chart` |
| 累积趋势 | 面积图 | `generate_area_chart` |
| 分类对比（横） | 条形图 | `generate_bar_chart` |
| 分类对比（纵） | 柱状图 | `generate_column_chart` |
| 占比/比例 | 饼图 | `generate_pie_chart` |
| 相关性 | 散点图 | `generate_scatter_chart` |
| 频率分布 | 直方图 | `generate_histogram_chart` |
| 双轴（不同量级） | 双轴图 | `generate_dual_axes_chart` |
| 多维对比 | 雷达图 | `generate_radar_chart` |
| 流程/转化 | 漏斗图 | `generate_funnel_chart` |
| 层级占比 | 矩形树图 | `generate_treemap_chart` |

## Selection Rules

1. **有时间维度** → 折线图 / 面积图
2. **无时间，分类少** → 柱状图 / 条形图
3. **占比关系** → 饼图（≤6项）/ 矩形树图（>6项）
4. **两个变量关系** → 散点图
5. **同一对象多指标** → 雷达图
6. **转化/阶段** → 漏斗图
7. **数据分布** → 直方图
8. **两组不同量级数据** → 双轴图
