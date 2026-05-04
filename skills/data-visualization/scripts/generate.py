"""
Data Visualization Chart Generator (Python + Matplotlib)
Usage: python generate.py '<json_payload>'
Payload: { "tool": "generate_line_chart", "args": { ... } }
Output: JSON with success, path, filename
"""

import json
import sys
import os
from datetime import datetime

import matplotlib
matplotlib.use('Agg')  # headless
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ---- Font setup for Chinese ----
def setup_chinese_font():
    """Try to find a Chinese font."""
    candidates = [
        'SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi',
        'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC',
        'WenQuanYi Micro Hei', 'AR PL UMing CN',
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams['font.sans-serif'] = [name, 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            return name
    return None

setup_chinese_font()

# ---- Config ----
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'output')

def ensure_output():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def gen_filename(tool):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:19]
    return f'{tool}_{ts}.png'

def save(fig, tool):
    ensure_output()
    filename = gen_filename(tool)
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return {'success': True, 'path': os.path.abspath(path), 'filename': filename}

# ---- Chart renderers ----

def render_line_chart(args):
    data = args['data']
    x, y = args['xField'], args['yField']
    series = args.get('seriesField')
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    if series:
        groups = {}
        for d in data:
            groups.setdefault(d[series], {'xs':[], 'ys':[]})
            groups[d[series]]['xs'].append(d[x])
            groups[d[series]]['ys'].append(d[y])
        for label, g in groups.items():
            ax.plot(g['xs'], g['ys'], marker='o', label=label)
        ax.legend()
    else:
        ax.plot([d[x] for d in data], [d[y] for d in data], marker='o')
    ax.set_xlabel(x); ax.set_ylabel(y)
    if args.get('title'): ax.set_title(args['title'])
    ax.grid(True, alpha=0.3)
    return save(fig, 'line_chart')

def render_area_chart(args):
    data = args['data']
    x, y = args['xField'], args['yField']
    series = args.get('seriesField')
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    if series:
        groups = {}
        for d in data:
            groups.setdefault(d[series], {'xs':[], 'ys':[]})
            groups[d[series]]['xs'].append(d[x])
            groups[d[series]]['ys'].append(d[y])
        for label, g in groups.items():
            ax.fill_between(g['xs'], g['ys'], alpha=0.4, label=label)
            ax.plot(g['xs'], g['ys'])
        ax.legend()
    else:
        ax.fill_between([d[x] for d in data], [d[y] for d in data], alpha=0.4)
        ax.plot([d[x] for d in data], [d[y] for d in data])
    ax.set_xlabel(x); ax.set_ylabel(y)
    if args.get('title'): ax.set_title(args['title'])
    ax.grid(True, alpha=0.3)
    return save(fig, 'area_chart')

def render_bar_chart(args):
    data = args['data']
    x, y = args['xField'], args['yField']
    series = args.get('seriesField')
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    categories = [d[x] for d in data]
    if series:
        groups = {}
        for d in data:
            groups.setdefault(d[series], [])
            groups[d[series]].append(d[y])
        vals = list(groups.values())
        labels = list(groups.keys())
        y_pos = np.arange(len(categories))
        h = 0.8 / len(labels)
        for i, (lbl, vs) in enumerate(zip(labels, vals)):
            ax.barh(y_pos + i*h - 0.4 + h/2, vs, h, label=lbl)
        ax.set_yticks(y_pos); ax.set_yticklabels(categories)
        ax.legend()
    else:
        values = [d[y] for d in data]
        ax.barh(categories, values)
    ax.set_xlabel(y); ax.set_ylabel(x)
    if args.get('title'): ax.set_title(args['title'])
    ax.grid(True, alpha=0.3, axis='x')
    return save(fig, 'bar_chart')

def render_column_chart(args):
    data = args['data']
    x, y = args['xField'], args['yField']
    series = args.get('seriesField')
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    categories = [d[x] for d in data]
    if series:
        groups = {}
        for d in data:
            groups.setdefault(d[series], [])
            groups[d[series]].append(d[y])
        vals = list(groups.values())
        labels = list(groups.keys())
        x_pos = np.arange(len(categories))
        w = 0.8 / len(labels)
        for i, (lbl, vs) in enumerate(zip(labels, vals)):
            ax.bar(x_pos + i*w - 0.4 + w/2, vs, w, label=lbl)
        ax.set_xticks(x_pos); ax.set_xticklabels(categories)
        ax.legend()
    else:
        values = [d[y] for d in data]
        ax.bar(categories, values)
    ax.set_xlabel(x); ax.set_ylabel(y)
    if args.get('title'): ax.set_title(args['title'])
    ax.grid(True, alpha=0.3, axis='y')
    return save(fig, 'column_chart')

def render_pie_chart(args):
    data = args['data']
    angle = args['angleField']
    color = args['colorField']
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    values = [d[angle] for d in data]
    labels = [d[color] for d in data]
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    if args.get('title'): ax.set_title(args['title'])
    return save(fig, 'pie_chart')

def render_scatter_chart(args):
    data = args['data']
    x, y = args['xField'], args['yField']
    color = args.get('colorField')
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    if color:
        groups = {}
        for d in data:
            groups.setdefault(d[color], {'xs':[], 'ys':[]})
            groups[d[color]]['xs'].append(d[x])
            groups[d[color]]['ys'].append(d[y])
        for label, g in groups.items():
            ax.scatter(g['xs'], g['ys'], label=label, alpha=0.7)
        ax.legend()
    else:
        ax.scatter([d[x] for d in data], [d[y] for d in data], alpha=0.7)
    ax.set_xlabel(x); ax.set_ylabel(y)
    if args.get('title'): ax.set_title(args['title'])
    ax.grid(True, alpha=0.3)
    return save(fig, 'scatter_chart')

def render_histogram_chart(args):
    data = args['data']
    field = args['field']
    bins = args.get('binNumber', 10)
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    values = [d[field] for d in data]
    ax.hist(values, bins=bins, edgecolor='white', alpha=0.8)
    ax.set_xlabel(field); ax.set_ylabel('Frequency')
    if args.get('title'): ax.set_title(args['title'])
    ax.grid(True, alpha=0.3, axis='y')
    return save(fig, 'histogram_chart')

def render_dual_axes_chart(args):
    data = args['data']
    x = args['xField']
    y_fields = args['yFields']
    fig, ax1 = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    xs = [d[x] for d in data]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    ax1.set_xlabel(x)
    for i, yf in enumerate(y_fields):
        ys = [d[yf] for d in data]
        if i == 0:
            ax1.set_ylabel(yf, color=colors[i % len(colors)])
            ax1.plot(xs, ys, marker='o', color=colors[i % len(colors)], label=yf)
            ax1.tick_params(axis='y', labelcolor=colors[i % len(colors)])
        else:
            ax2 = ax1.twinx()
            ax2.set_ylabel(yf, color=colors[i % len(colors)])
            ax2.plot(xs, ys, marker='s', color=colors[i % len(colors)], label=yf)
            ax2.tick_params(axis='y', labelcolor=colors[i % len(colors)])
    lines1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(lines1, labels1, loc='upper left')
    if args.get('title'): ax1.set_title(args['title'])
    ax1.grid(True, alpha=0.3)
    return save(fig, 'dual_axes_chart')

def render_radar_chart(args):
    data = args['data']
    fields = args['fields']
    name = args['nameField']
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100), subplot_kw=dict(polar=True))
    angles = np.linspace(0, 2*np.pi, len(fields), endpoint=False).tolist()
    angles += angles[:1]
    for row in data:
        vals = [row[f] for f in fields]
        vals += vals[:1]
        ax.plot(angles, vals, 'o-', label=row[name])
        ax.fill(angles, vals, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(fields)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    if args.get('title'): ax.set_title(args['title'], pad=20)
    return save(fig, 'radar_chart')

def render_funnel_chart(args):
    data = args['data']
    x, y = args['xField'], args['yField']
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    labels = [d[x] for d in data]
    values = [d[y] for d in data]
    max_val = max(values)
    widths = [v / max_val for v in values]
    y_pos = np.arange(len(labels))
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(labels)))
    for i, (label, val, w) in enumerate(zip(labels, values, widths)):
        left = (1 - w) / 2
        ax.barh(i, w, left=left, height=0.6, color=colors[i], edgecolor='white')
        ax.text(0.5, i, f'{label}: {val}', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines[:].set_visible(False)
    if args.get('title'): ax.set_title(args['title'])
    return save(fig, 'funnel_chart')

def render_treemap_chart(args):
    data = args['data']
    name_f, val_f = args['nameField'], args['valueField']
    fig, ax = plt.subplots(figsize=(args.get('width',800)/100, args.get('height',500)/100))
    labels = [d[name_f] for d in data]
    values = [d[val_f] for d in data]
    total = sum(values)
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    y_pos = np.arange(len(labels))
    ax.barh(labels, values, color=colors, edgecolor='white')
    for i, (l, v) in enumerate(zip(labels, values)):
        pct = v / total * 100
        ax.text(v + total*0.01, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)
    ax.set_xlabel(val_f)
    if args.get('title'): ax.set_title(args['title'])
    ax.grid(True, alpha=0.3, axis='x')
    return save(fig, 'treemap_chart')

# ---- Main ----

TOOL_MAP = {
    'generate_line_chart': render_line_chart,
    'generate_area_chart': render_area_chart,
    'generate_bar_chart': render_bar_chart,
    'generate_column_chart': render_column_chart,
    'generate_pie_chart': render_pie_chart,
    'generate_scatter_chart': render_scatter_chart,
    'generate_histogram_chart': render_histogram_chart,
    'generate_dual_axes_chart': render_dual_axes_chart,
    'generate_radar_chart': render_radar_chart,
    'generate_funnel_chart': render_funnel_chart,
    'generate_treemap_chart': render_treemap_chart,
}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'Usage: python generate.py <json_or_filepath>'}))
        sys.exit(1)
    raw = sys.argv[1]
    if os.path.isfile(raw):
        with open(raw, 'r', encoding='utf-8') as f:
            raw = f.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({'success': False, 'error': f'Invalid JSON: {e}'}))
        sys.exit(1)

    tool = payload.get('tool')
    args = payload.get('args', {})
    renderer = TOOL_MAP.get(tool)
    if not renderer:
        print(json.dumps({'success': False, 'error': f'Unknown tool: {tool}. Available: {", ".join(TOOL_MAP.keys())}'}))
        sys.exit(1)
    try:
        result = renderer(args)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False))
        sys.exit(1)

if __name__ == '__main__':
    main()
