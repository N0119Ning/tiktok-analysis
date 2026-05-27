import json
import html as html_lib

BASE_DIR = 'e:/pycharm_project2/tiktok_project'

SEVERITY_CONFIG = {
    'critical': {'label': '紧急', 'color': '#e05d5d', 'bg': '#2a1a1f', 'icon': '●'},
    'high': {'label': '高', 'color': '#e8963c', 'bg': '#2a2218', 'icon': '●'},
    'medium': {'label': '中', 'color': '#d4b84a', 'bg': '#2a2618', 'icon': '●'},
    'low': {'label': '低', 'color': '#5eb88d', 'bg': '#182a23', 'icon': '●'}
}

def escape_html(text):
    return html_lib.escape(str(text), quote=True)

def generate_html(results):
    categories = results.get('categories', {})
    total_comments = results.get('total_comments', 0)
    overall_avg_score = results.get('overall_avg_score', 0)
    dashboard_data = results.get('dashboard_data', {})
    category_distribution = dashboard_data.get('category_distribution', [])
    severity_ranking = dashboard_data.get('severity_ranking', [])

    most_critical = severity_ranking[0] if severity_ranking else None
    most_critical_label = most_critical['label'] if most_critical else '无'

    cat_labels = [c['label'] for c in category_distribution]
    cat_counts = [c['count'] for c in category_distribution]
    cat_percentages = [round(c['percentage'], 1) for c in category_distribution]

    sorted_categories = sorted(
        categories.items(),
        key=lambda x: {
            'critical': 0, 'high': 1, 'medium': 2, 'low': 3
        }.get(x[1].get('severity', 'low'), 4)
    )

    overall_sentiment = results.get('dashboard_data', {}).get('overall_sentiment', {})
    neg_rate = overall_sentiment.get('negativity_rate', 0)

    # ====== 侧边导航 ======
    nav_items = ''
    for i, (cat_id, cat_data) in enumerate(sorted_categories):
        sev_config = SEVERITY_CONFIG.get(cat_data.get('severity', 'low'), SEVERITY_CONFIG['low'])
        nav_items += f'''
            <a href="#cat-{cat_id}" class="nav-item" style="border-left-color: {sev_config['color']};">
                <span class="nav-icon">{sev_config['icon']}</span>
                <span class="nav-text">{escape_html(cat_data.get('category_label', ''))}</span>
                <span class="nav-count">{cat_data.get('total_comments', 0)}</span>
            </a>'''

    # ====== 紧凑 Dashboard ======
    dashboard_html = f'''
        <div class="dash-row">
            <div class="dash-metric"><span class="dm-num">{total_comments}</span><span class="dm-lbl">总评论</span></div>
            <div class="dash-metric"><span class="dm-num">{results.get('category_count', 0)}</span><span class="dm-lbl">类别数</span></div>
            <div class="dash-metric"><span class="dm-num">{overall_avg_score}</span><span class="dm-lbl">均分</span></div>
            <div class="dash-metric dm-alert"><span class="dm-num">{'😠' if neg_rate > 50 else '😐'}{neg_rate}%</span><span class="dm-lbl">负面率</span></div>
            <div class="dash-metric dm-critical"><span class="dm-num">{most_critical_label}</span><span class="dm-lbl">最严重</span></div>
        </div>

        <div class="chart-tabs">
            <button class="chart-tab active" onclick="switchChart(this,'bar')">📊 分布柱状图</button>
            <button class="chart-tab" onclick="switchChart(this,'pie')">🥧 占比饼图</button>
            <button class="chart-tab" onclick="switchChart(this,'sentiment')">🎭 情绪分布</button>
        </div>
        <div class="chart-area">
            <canvas id="chartBar"></canvas>
            <canvas id="chartPie" style="display:none;"></canvas>
            <canvas id="chartSentiment" style="display:none;"></canvas>
        </div>'''

    # ====== Category 卡片（折叠式） ======
    cards_html = ''
    for cat_id, cat_data in sorted_categories:
        sev_config = SEVERITY_CONFIG.get(cat_data.get('severity', 'low'), SEVERITY_CONFIG['low'])

        # 子问题摘要行（紧凑表格）
        sp_rows = ''
        for sp in cat_data.get('subproblems', []):
            sentiment = sp.get('sentiment', {})
            sp_neg = sentiment.get('negativity_rate', 0)
            sp_emoji = '😠' if sp_neg > 60 else '😐' if sp_neg > 40 else '😊'

            keywords_str = ', '.join(sp.get('keywords', [])[:3])

            sp_rows += f'''
                <tr class="sp-row" onclick="toggleSpDetail(this)">
                    <td class="sp-name-col">
                        <span class="sp-toggle-icon">▶</span>
                        <strong>{escape_html(sp.get('name', ''))}</strong>
                    </td>
                    <td>{sp.get('comment_count', 0)}</td>
                    <td><span class="mini-tag">{sp_emoji} {sp_neg:.0f}%</span></td>
                    <td class="sp-problem-col">{escape_html(sp.get('problem', '')[:60])}...</td>
                    <td class="sp-solution-col">{escape_html(sp.get('short_term', '')[:50])}...</td>
                </tr>
                <tr class="sp-detail" style="display:none;">
                    <td colspan="5">
                        <div class="sp-detail-inner">
                            <div class="detail-grid">
                                <div class="detail-block">
                                    <h6>📌 问题分析</h6>
                                    <p><b>本质：</b>{escape_html(sp.get('problem', ''))}</p>
                                    <p><b>场景：</b>{escape_html(sp.get('scene', ''))}</p>
                                    <p><b>影响：</b>{escape_html(sp.get('impact', ''))}</p>
                                </div>
                                <div class="detail-block detail-solution">
                                    <h6>💡 解决方案</h6>
                                    <p><b>短期：</b>{escape_html(sp.get('short_term', ''))}</p>
                                    <p><b>长期：</b>{escape_html(sp.get('long_term', ''))}</p>
                                    <p><b>指标：</b>{" · ".join([escape_html(m) for m in sp.get('metrics', [])])}</p>
                                </div>
                            </div>
                            <div class="detail-keywords">
                                <b>关键词：</b>
                                {" ".join([f'<span class="kw-tag">{escape_html(kw)}</span>' for kw in sp.get('keywords', [])])}
                            </div>
                            <div class="detail-comments">
                                <b>典型评论：</b>
                                {" ".join([f'<span class="cm-quote">"{escape_html(c)}"</span>' for c in sp.get('representative_comments', [])])}
                            </div>
                        </div>
                    </td>
                </tr>'''

        cards_html += f'''
            <div class="cat-card" id="cat-{cat_id}">
                <div class="cat-header" onclick="toggleCat(this)">
                    <span class="cat-arrow">▶</span>
                    <span class="cat-title">{cat_data.get('category_label', '')}</span>
                    <span class="cat-badges">
                        <span class="badge-sev" style="background:{sev_config['bg']};color:{sev_config['color']};border-color:{sev_config['color']};">{sev_config['icon']} {sev_config['label']}</span>
                        <span class="badge-count">{cat_data.get('total_comments', 0)}条 ({cat_data.get('percentage', 0)}%)</span>
                        <span class="badge-score">均分 {cat_data.get('avg_score', 0)}</span>
                    </span>
                </div>
                <div class="cat-body" style="display:none;">
                    <table class="sp-table">
                        <thead>
                            <tr><th>子问题</th><th width="70">评论</th><th width="80">情绪</th><th>问题概述</th><th>短期方案</th></tr>
                        </thead>
                        <tbody>
                            {sp_rows}
                        </tbody>
                    </table>
                </div>
            </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok 评论分析报告</title>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #1c2128;
            --bg-elevated: #21262d;
            --border-default: #30363d;
            --border-muted: #21262d;

            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;

            --accent-teal: #58a6ff;
            --accent-teal-dim: #1f3a5f;
            --accent-teal-glow: rgba(88, 166, 255, 0.15);

            --severity-critical: #e05d5d;
            --severity-high: #e8963c;
            --severity-medium: #d4b84a;
            --severity-low: #5eb88d;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}

        .layout {{
            display: flex;
            max-width: 1440px;
            margin: 0 auto;
            gap: 0;
        }}

        .sidebar {{
            width: 220px;
            flex-shrink: 0;
            background: var(--bg-secondary);
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            border-right: 1px solid var(--border-default);
            padding: 24px 0;
        }}

        .sidebar h3 {{
            padding: 0 20px 16px;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-muted);
            margin-bottom: 12px;
            font-weight: 600;
        }}

        .nav-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 11px 20px;
            text-decoration: none;
            color: var(--text-secondary);
            border-left: 3px solid transparent;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 0.875rem;
            font-weight: 400;
        }}

        .nav-item:hover {{
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }}

        .nav-item .nav-icon {{
            font-size: 0.5rem;
            width: 12px;
            flex-shrink: 0;
        }}

        .nav-item .nav-text {{
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .nav-item .nav-count {{
            background: var(--bg-tertiary);
            padding: 3px 9px;
            border-radius: 12px;
            font-size: 0.72rem;
            color: var(--text-muted);
            font-weight: 500;
            font-variant-numeric: tabular-nums;
        }}

        .main-content {{
            flex: 1;
            padding: 32px 40px;
            max-width: 1200px;
        }}

        .page-header {{
            margin-bottom: 32px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-muted);
        }}

        .page-header h1 {{
            font-size: 1.875rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            margin-bottom: 6px;
            line-height: 1.2;
        }}

        .page-header p {{
            color: var(--text-muted);
            font-size: 0.85rem;
            font-weight: 400;
        }}

        .dash-section {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 28px;
            border: 1px solid var(--border-default);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }}

        .dash-row {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 14px;
            margin-bottom: 20px;
        }}

        .dash-metric {{
            background: var(--bg-primary);
            border-radius: 10px;
            padding: 18px 16px;
            text-align: center;
            border: 1px solid var(--border-muted);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .dash-metric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }}

        .dm-num {{
            display: block;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            font-variant-numeric: tabular-nums;
        }}

        .dm-lbl {{
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-top: 4px;
            font-weight: 500;
        }}

        .dm-alert .dm-num {{ color: var(--severity-medium); }}
        .dm-critical {{ border-color: rgba(224, 93, 93, 0.3) !important; }}
        .dm-critical .dm-num {{ color: var(--severity-critical); }}

        .chart-tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }}

        .chart-tab {{
            background: var(--bg-primary);
            border: 1px solid var(--border-default);
            color: var(--text-secondary);
            padding: 7px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.82rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .chart-tab.active {{
            background: var(--accent-teal-dim);
            color: var(--accent-teal);
            border-color: var(--accent-teal);
        }}

        .chart-tab:hover:not(.active) {{
            border-color: var(--text-muted);
            color: var(--text-primary);
        }}

        .chart-area {{
            background: var(--bg-primary);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid var(--border-muted);
            min-height: 240px;
        }}

        .chart-area canvas {{ max-height: 220px; }}

        .cat-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-default);
            border-radius: 10px;
            margin-bottom: 12px;
            overflow: hidden;
            transition: box-shadow 0.2s ease;
        }}

        .cat-card:hover {{
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
        }}

        .cat-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            cursor: pointer;
            transition: background 0.15s ease;
            user-select: none;
        }}

        .cat-header:hover {{ background: var(--bg-tertiary); }}

        .cat-arrow {{
            font-size: 0.6rem;
            color: var(--text-muted);
            transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            width: 14px;
            text-align: center;
            flex-shrink: 0;
        }}

        .cat-card.open .cat-arrow {{ transform: rotate(90deg); }}

        .cat-title {{
            font-weight: 600;
            font-size: 0.95rem;
            flex: 1;
            color: var(--text-primary);
        }}

        .cat-badges {{ display: flex; gap: 8px; align-items: center; }}

        .badge-sev {{
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 600;
            border: 1px solid;
            letter-spacing: 0.3px;
        }}

        .badge-count, .badge-score {{
            background: var(--bg-primary);
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.74rem;
            color: var(--text-secondary);
            font-weight: 500;
            font-variant-numeric: tabular-nums;
        }}

        .cat-body {{ padding: 0 20px 20px; }}

        .sp-table {{ width: 100%; border-collapse: collapse; }}

        .sp-table th {{
            text-align: left;
            padding: 10px 12px;
            font-size: 0.73rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.6px;
            border-bottom: 1px solid var(--border-default);
            font-weight: 600;
        }}

        .sp-row td {{
            padding: 12px 10px;
            font-size: 0.84rem;
            cursor: pointer;
            border-bottom: 1px solid var(--border-muted);
            transition: background 0.15s ease;
            color: var(--text-secondary);
        }}

        .sp-row:hover td {{ background: var(--bg-tertiary); }}
        .sp-name-col {{ font-weight: 550; white-space: nowrap; color: var(--text-primary) !important; }}

        .sp-toggle-icon {{
            font-size: 0.55rem;
            color: var(--text-muted);
            margin-right: 8px;
            display: inline-block;
            width: 10px;
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .sp-row.expanded .sp-toggle-icon {{ transform: rotate(90deg); }}

        .sp-problem-col, .sp-solution-col {{
            color: var(--text-secondary);
            font-size: 0.8rem;
            max-width: 260px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .mini-tag {{
            background: var(--bg-tertiary);
            padding: 3px 9px;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 500;
        }}

        .sp-detail td {{ padding: 0 !important; background: var(--bg-primary) !important; }}
        .sp-detail-inner {{ padding: 20px 24px; }}

        .detail-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
            margin-bottom: 16px;
        }}

        .detail-block {{
            background: var(--bg-secondary);
            border-radius: 10px;
            padding: 18px;
            border: 1px solid var(--border-default);
        }}

        .detail-block h6 {{
            font-size: 0.8rem;
            color: var(--accent-teal);
            margin-bottom: 10px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}

        .detail-block p {{
            font-size: 0.84rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
            line-height: 1.65;
        }}

        .detail-solution {{
            background: linear-gradient(135deg, #1a2744 0%, #151f35 100%);
            border-color: rgba(88, 166, 255, 0.2);
        }}

        .detail-keywords {{
            margin-bottom: 12px;
            font-size: 0.84rem;
            color: var(--text-secondary);
        }}

        .kw-tag {{
            background: var(--accent-teal-glow);
            color: var(--accent-teal);
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.74rem;
            margin: 3px;
            display: inline-block;
            font-weight: 500;
        }}

        .detail-comments {{
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        .cm-quote {{
            background: var(--bg-secondary);
            padding: 8px 12px;
            border-radius: 6px;
            margin: 5px 3px;
            display: inline-block;
            font-style: italic;
            color: var(--text-secondary);
            font-size: 0.78rem;
            max-width: 100%;
            word-break: break-word;
            border-left: 2px solid var(--border-default);
        }}

        @media (max-width: 900px) {{
            .sidebar {{ display: none; }}
            .dash-row {{ grid-template-columns: repeat(3, 1fr); }}
            .detail-grid {{ grid-template-columns: 1fr; }}
            .main-content {{ padding: 24px 20px; }}
        }}
    </style>
</head>
<body>
<div class="layout">
    <!-- 左侧导航 -->
    <nav class="sidebar">
        <h3>[*] 问题分类</h3>
        {nav_items}
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
        <header class="page-header">
            <h1>TikTok 评论分析报告</h1>
            <p>AI 产品分析工具 · Category 分类 · LLM 动态分析 · 情绪检测</p>
        </header>

        <section class="dash-section">
            {dashboard_html}
        </section>

        <div class="categories-container">
            {cards_html}
        </div>

        <footer style="text-align:center;color:#475569;font-size:0.75rem;margin-top:32px;padding-bottom:24px;">
            Pipeline: 清洗 → Embedding → Category 分类 → 子问题拆分 → TF-IDF 关键词 → DeepSeek LLM → 情绪分析
        </footer>
    </main>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// ====== Chart.js 配置 ======
const chartColors = [
    '#58a6ff',
    '#e05d5d',
    '#e8963c',
    '#d4b84a',
    '#5eb88d',
    '#a78bfa',
    '#f472b6',
    '#22d3ee',
    '#8b949e'
];

function switchChart(btn,type) {{
    document.querySelectorAll('.chart-tab').forEach(t=>t.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('chartBar').style.display = type==='bar'?'block':'none';
    document.getElementById('chartPie').style.display = type==='pie'?'block':'none';
    document.getElementById('chartSentiment').style.display = type==='sentiment'?'block':'none';
}}

// 柱状图
new Chart(document.getElementById('chartBar'),{{
    type:'bar',
    data:{{
        labels:{json.dumps(cat_labels,ensure_ascii=False)},
        datasets:[{{label:'评论数',data:{json.dumps(cat_counts)},backgroundColor:'#58a6ff',borderRadius:6,borderWidth:0}}]
    }},
    options:{{
        responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}}}},
        scales:{{
            y:{{
                beginAtZero:true,
                ticks:{{color:'#6e7681',font:{{size:11}}}},
                grid:{{color:'#21262d',drawBorder:false}}
            }},
            x:{{
                ticks:{{color:'#8b949e',font:{{size:11}},maxRotation:45}},
                grid:{{display:false}}
            }}
        }}
    }}
}});

// 饼图
new Chart(document.getElementById('chartPie'),{{
    type:'doughnut',
    data:{{
        labels:{json.dumps(cat_labels,ensure_ascii=False)},
        datasets:[{{data:{json.dumps(cat_percentages)},backgroundColor:chartColors,borderWidth:2,borderColor:'#0d1117'}}]
    }},
    options:{{
        responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{position:'right',labels:{{color:'#8b949e',padding:12,usePointStyle:true,pointStyle:'circle',font:{{size:11}}}}}}}},
        cutout:'58%',
        animation:{{animateRotate:true,animateScale:true}}
    }}
}});

// 情绪饼图
new Chart(document.getElementById('chartSentiment'),{{
    type:'doughnut',
    data:{{
        labels:['😠 负面','😐 中性','😊 正面'],
        datasets:[{{data:[
            {overall_sentiment.get('negative_pct',0)},
            {overall_sentiment.get('neutral_pct',0)},
            {overall_sentiment.get('positive_pct',0)}
        ],backgroundColor:['#e05d5d','#8b949e','#5eb88d'],borderWidth:2,borderColor:'#0d1117'}}]
    }},
    options:{{
        responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{position:'bottom',labels:{{color:'#8b949e',padding:12,usePointStyle:true,pointStyle:'circle',font:{{size:11}}}}}}}},
        cutout:'58%',
        animation:{{animateRotate:true,animateScale:true}}
    }}
}});

// ====== 折叠交互 ======
function toggleCat(header) {{
    const card = header.closest('.cat-card');
    const body = card.querySelector('.cat-body');
    const isOpen = card.classList.contains('open');

    if(isOpen) {{
        card.classList.remove('open');
        body.style.display='none';
    }} else {{
        card.classList.add('open');
        body.style.display='block';
    }}
}}

function toggleSpDetail(row) {{
    const nextRow = row.nextElementSibling;
    const isExpanded = row.classList.contains('expanded');

    if(isExpanded) {{
        row.classList.remove('expanded');
        nextRow.style.display='none';
    }} else {{
        row.classList.add('expanded');
        nextRow.style.display='table-row';
    }}
}}
</script>
</body>
</html>'''

    return html

def main():
    input_json = f'{BASE_DIR}/outputs/result.json'
    output_html = f'{BASE_DIR}/outputs/report.html'

    with open(input_json, 'r', encoding='utf-8') as f:
        results = json.load(f)

    html = generate_html(results)

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML report saved to {output_html}")

if __name__ == '__main__':
    main()
