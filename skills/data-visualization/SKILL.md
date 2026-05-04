---
name: data-visualization
description: Transform data into visual charts. Use when the user wants to visualize data, create charts, generate graphs, or turn numbers/tables into visual images. Supports line, bar, column, pie, scatter, area, histogram, dual-axes, radar, funnel, treemap charts. Triggers on requests like "画个图", "做个图表", "可视化", "帮我画个柱状图", "chart", "graph", "visualize".
version: 1.0.0
---

# Data Visualization

Transform data into chart images via `@antv/g2`.

## Workflow

1. **Analyze data** → determine chart type (see `references/chart-selection.md`)
2. **Extract parameters** → map user data to chart args (see `references/chart-args.md`)
3. **Generate** → run script, return image

## Quick Start

```bash
python scripts/generate.py '<payload_json>'
# or pass a JSON file:
python scripts/generate.py path/to/input.json
```

Payload format:
```json
{
  "tool": "generate_line_chart",
  "args": { "data": [...], "xField": "...", "yField": "...", "title": "..." }
}
```

Output: JSON with `success`, `path` (local file path), `filename`.

**Tip:** On Windows PowerShell, JSON quoting is tricky. Write to a temp .json file and pass the file path instead.

## Available Charts

| Tool | Chart | Use When |
|------|-------|----------|
| `generate_line_chart` | 折线图 | Time series, trends |
| `generate_area_chart` | 面积图 | Accumulated trends |
| `generate_bar_chart` | 条形图 | Horizontal category comparison |
| `generate_column_chart` | 柱状图 | Vertical category comparison |
| `generate_pie_chart` | 饼图 | Part-to-whole (≤6 items) |
| `generate_scatter_chart` | 散点图 | Correlation between two variables |
| `generate_histogram_chart` | 直方图 | Frequency distribution |
| `generate_dual_axes_chart` | 双轴图 | Two different scales on same chart |
| `generate_radar_chart` | 雷达图 | Multi-dimension comparison |
| `generate_funnel_chart` | 漏斗图 | Process/conversion stages |
| `generate_treemap_chart` | 矩形树图 | Hierarchical proportions |

## Parameter Details

For full args specs per chart type, read `references/chart-args.md`.
For chart selection logic, read `references/chart-selection.md`.

## After Generation

1. Send the generated image to the user
2. Include the chart type and a brief interpretation of the data

## Usage Logging (Auto-injected)

Every time this skill is triggered, append a usage record to `~/.openclaw/skill-logs/data-visualization/log.md`.

Log format:
```markdown
## [YYYY-MM-DD HH:mm:ss]
- **User Request**: <what user asked>
- **Action**: <what chart was generated>
- **Result**: <outcome>
```
