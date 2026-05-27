import streamlit as st
import pandas as pd
import json
import os
import sys
import time
import subprocess
import shutil
import tempfile
import altair as alt

from utils.logger import get_logger, log_event
from utils.metrics import get_metrics, export_metrics
from agent_plan import agent_plan, explain_plan
from agent_review import review_all_categories, review_single_subproblem, retry_subproblem_analysis
from agent_chat import react_chat, load_results

_applog = get_logger('app')
_plog = get_logger('pipeline')
_llog = get_logger('llm')

CHART_THEME = {
    'background': 'transparent',
    'view': {'stroke': 'transparent'},
    'title': {'color': '#1a1b20', 'fontSize': 15, 'anchor': 'middle', 'fontWeight': 600,
              'font': 'Inter, sans-serif'},
    'axis': {
        'labelColor': '#434751', 'titleColor': '#1a1b20',
        'gridColor': '#eeedf4', 'domainColor': '#c4c6d1', 'tickColor': '#c4c6d1',
    },
    'legend': {'labelColor': '#434751', 'titleColor': '#1a1b20'},
}

# 问题类别分布用5色蓝色家族（从深到浅）
SEVERITY_COLORS = ['#1a1b20', '#3d5e99', '#4c5e86', '#bfd1ff', '#d8e2ff']
SEVERITY_DOMAIN = ['critical', 'high', 'medium', 'low', 'info']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(os.path.dirname(BASE_DIR), '.venv', 'Scripts', 'python.exe')
if sys.platform != 'win32':
    VENV_PYTHON = os.path.join(os.path.dirname(BASE_DIR), '.venv', 'bin', 'python')

sys.path.insert(0, BASE_DIR)


def _prepare_input_for_pipeline(filepath, info):
    """将上传的 CSV 映射为 pipeline 能用的格式 (data/TikTok.csv)"""
    df = pd.read_csv(filepath)
    text_col = info.get('text_column')
    score_col = info.get('score_column')

    # 确保有 'content' 列（step1 会映射为 'translated'）
    if text_col and text_col != 'content':
        df.rename(columns={text_col: 'content'}, inplace=True)
    elif text_col is None:
        return

    # 确保有 'score' 列
    if score_col and score_col != 'score':
        df.rename(columns={score_col: 'score'}, inplace=True)

    target = os.path.join(BASE_DIR, 'data', 'TikTok.csv')
    df.to_csv(target, index=False)

st.set_page_config(page_title="AI 评论分析 Agent", layout="wide")

# 初始加载状态
init_placeholder = st.empty()
init_placeholder.markdown("""
<div style="
    display: flex; align-items: center; justify-content: center;
    padding: 48px 24px; margin: 16px 0;
    background: #F0F9FF; border: 1px solid #BAE6FD;
    border-radius: 14px; color: #0369A1;
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 15px; font-weight: 500;
">
    <span style="display:inline-block;width:20px;height:20px;border:3px solid #BAE6FD;border-top-color:#0369A1;border-radius:50%;animation:spin 0.8s linear infinite;margin-right:12px;"></span>
    正在初始化 AI 评论分析引擎...
</div>
<style>
@keyframes spin { to { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    :root {
        --bg-primary: #faf9ff;
        --bg-secondary: #f3f3fa;
        --bg-card: #ffffff;
        --border-color: #c4c6d1;
        --text-primary: #1a1b20;
        --text-secondary: #434751;
        --text-muted: #747781;
        --primary: #3d5e99;
        --primary-light: #e8e7ee;
        --secondary: #4c5e86;
        --secondary-light: #d8e2ff;
        --success: #22C55E;
        --success-light: #F0FDF4;
        --warning: #F59E0B;
        --warning-light: #FFFBEB;
        --error: #ba1a1a;
        --error-light: #ffdad6;
        --surface-high: #e8e7ee;
        --surface-highest: #e2e2e9;
        --radius-default: 16px;
        --radius-lg: 24px;
        --radius-full: 9999px;
    }

    * { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }

    body, [data-testid="stAppViewBlock"], [data-testid="stAppViewContainer"], .main, .app {
        background: var(--bg-primary) !important;
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
        letter-spacing: -0.02em;
        color: var(--text-primary) !important;
    }
    h1 { font-size: 1.75rem !important; font-weight: 700 !important; margin-bottom: 0.25rem !important; }
    h2 { font-size: 1.25rem !important; font-weight: 600 !important; margin-bottom: 0.75rem !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; color: var(--text-secondary) !important; }

    /* ====== Sidebar Navigation ====== */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 16px !important;
        border-radius: 12px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin-bottom: 2px !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: #434751 !important;
    }
    section[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
        background: #e8e7ee !important;
        color: #1a1b20 !important;
    }

    /* ====== Metric Cards ====== */
    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-default);
        padding: 1.25rem 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(61,94,153,0.08);
        border-color: rgba(61,94,153,0.2);
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
        font-family: 'JetBrains Mono', 'SF Mono', 'Consolas', monospace !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }

    /* ====== Expander (Accordion) ====== */
    div[data-testid="stExpander"] details {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-default);
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
        margin-bottom: 10px;
    }
    div[data-testid="stExpander"]:hover details {
        border-color: rgba(61,94,153,0.3);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] summary {
        background: transparent;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 1rem 1.25rem !important;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    div[data-testid="stExpander"] summary:hover {
        background: rgba(61,94,153,0.04);
    }

    /* Severity left-border for expanders */
    .sev-critical details { border-left: 4px solid #1a1b20 !important; }
    .sev-high details { border-left: 4px solid #3d5e99 !important; }
    .sev-medium details { border-left: 4px solid #4c5e86 !important; }
    .sev-low details { border-left: 4px solid #bfd1ff !important; }
    .sev-info details { border-left: 4px solid #d8e2ff !important; }

    /* ====== Chat Messages ====== */
    .stChatMessage {
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-default) !important;
        background: var(--bg-card) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    /* ====== File Uploader ====== */
    .stFileUploader {
        border: 2px dashed var(--border-color) !important;
        border-radius: var(--radius-default) !important;
        padding: 2.5rem !important;
        background: var(--bg-secondary) !important;
        transition: all 0.25s ease;
    }
    .stFileUploader:hover {
        border-color: var(--primary) !important;
        background: rgba(61,94,153,0.03) !important;
        box-shadow: 0 4px 16px rgba(61,94,153,0.06);
    }

    /* ====== Buttons ====== */
    button[kind="primary"] {
        background: var(--primary) !important;
        border: none !important;
        border-radius: var(--radius-default) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.75rem 2rem !important;
        letter-spacing: 0.02em;
        font-family: 'Inter', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
        box-shadow: 0 2px 8px rgba(61,94,153,0.25);
        transition: all 0.2s ease;
    }
    button[kind="primary"]:hover {
        background: #344d82 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(61,94,153,0.35);
    }
    button[kind="secondary"] {
        background: var(--bg-card) !important;
        border: 2px solid var(--primary) !important;
        border-radius: var(--radius-default) !important;
        color: var(--primary) !important;
        font-weight: 600 !important;
        font-family: 'Inter', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover {
        background: rgba(61,94,153,0.05) !important;
    }

    /* ====== Status Widget ====== */
    div[data-testid="stStatusWidget"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        padding: 24px !important;
    }

    /* ====== Alerts ====== */
    .stInfo {
        background: rgba(61,94,153,0.05) !important;
        border: 1px solid rgba(61,94,153,0.15) !important;
        border-radius: 12px !important;
        color: var(--primary) !important;
    }
    .stSuccess {
        background: rgba(76,94,134,0.06) !important;
        border: 1px solid rgba(76,94,134,0.2) !important;
        border-radius: 12px !important;
        color: var(--secondary) !important;
    }
    .stError {
        background: var(--error-light) !important;
        border: 1px solid rgba(186,26,26,0.3) !important;
        border-left: 4px solid var(--error) !important;
        border-radius: 12px !important;
        color: var(--error) !important;
    }

    /* ====== Text Elements ====== */
    blockquote {
        border-left: 4px solid var(--primary) !important;
        background: rgba(61,94,153,0.04) !important;
        border-radius: 0 12px 12px 0 !important;
        color: var(--text-secondary) !important;
        padding: 0.85rem 1.1rem !important;
    }
    code {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--primary) !important;
        border-radius: 6px !important;
        padding: 2px 7px !important;
        font-family: 'JetBrains Mono', 'SF Mono', 'Consolas', monospace !important;
        font-size: 0.88em !important;
    }
    pre {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
    }
    hr {
        border-top: 1px solid var(--border-color) !important;
        margin: 1.5rem 0 !important;
    }
    .stMarkdown, .stCaption {
        color: var(--text-secondary) !important;
        line-height: 1.65 !important;
    }
    p, li, span, td, th {
        color: var(--text-primary) !important;
    }
    strong, b {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ====== Pipeline Progress Bar Animation ====== */
    @keyframes pulse-bar {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.55; }
    }
    .progress-fill-active {
        animation: pulse-bar 2s infinite ease-in-out;
    }

    /* ====== Typing Dots Animation ====== */
    @keyframes typing-bounce {
        0%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-6px); }
    }
    .typing-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: var(--primary);
        animation: typing-bounce 1.4s infinite ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

if 'pipeline_plan' not in st.session_state:
    st.session_state.pipeline_plan = None
if 'pipeline_info' not in st.session_state:
    st.session_state.pipeline_info = None
if 'pipeline_ran' not in st.session_state:
    st.session_state.pipeline_ran = False
if 'reviewed' not in st.session_state:
    st.session_state.reviewed = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_filepath' not in st.session_state:
    st.session_state.uploaded_filepath = None
if 'plan_generated' not in st.session_state:
    st.session_state.plan_generated = False
if 'page' not in st.session_state:
    st.session_state.page = 'upload'

init_placeholder.empty()

PAGES = {"upload": "上传与规划", "report": "分析报告", "chat": "追问"}

with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:8px 0 20px 4px;">
        <div style="width:40px;height:40px;border-radius:12px;background:#3d5e99;
                    display:flex;align-items:center;justify-content:center;color:white;
                    font-size:18px;font-weight:700;flex-shrink:0;">A</div>
        <div>
            <div style="font-size:14px;font-weight:700;color:#3d5e99;">当前项目</div>
            <div style="font-size:12px;color:#434751;">评论分析</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for key, label in PAGES.items():
        is_active = st.session_state.page == key
        bg = "#d8e2ff" if is_active else "transparent"
        fw = "600" if is_active else "400"
        color = "#4c5e86" if is_active else "#434751"
        if st.button(label, key=f"nav_{key}",
                     type=("primary" if is_active else "secondary"),
                     use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown('<div style="margin-top:auto;padding-top:16px;border-top:1px solid #c4c6d1;"></div>', unsafe_allow_html=True)

st.title("AI 评论分析 Agent")
st.caption("上传 CSV / 自动分析 / 交互式追问")

if st.session_state.page == 'upload':
    uploaded_file = st.file_uploader("上传评论 CSV 文件（支持中文、英文）", type=["csv"], key="csv_uploader")

    if not uploaded_file and not st.session_state.pipeline_plan:
        st.markdown("""
        <div style="
            padding: 36px 28px; margin-top: 12px;
            background: #f3f3fa; border: 1px solid #c4c6d1;
            border-radius: 16px; color: #434751;
            font-size: 14px; line-height: 1.8;
        ">
            <div style="font-weight: 700; font-size: 16px; color: #1a1b20; margin-bottom: 10px;">
                欢迎使用 AI 评论分析 Agent
            </div>
            上传 CSV 后，Agent 将自动：<br>
            &nbsp;&nbsp;1. 检测文本列、评分列、语言<br>
            &nbsp;&nbsp;2. 评估数据规模并制定分析计划<br>
            &nbsp;&nbsp;3. 清洗数据 → 9 类问题分类 → AI 深度分析<br>
            &nbsp;&nbsp;4. 质量自检 + 自动重试低质量结果<br>
            &nbsp;&nbsp;5. 生成可视化报告并可追问
        </div>
        """, unsafe_allow_html=True)

    if uploaded_file:
        tmpdir = os.path.join(BASE_DIR, 'data')
        os.makedirs(tmpdir, exist_ok=True)
        filepath = os.path.join(tmpdir, uploaded_file.name)
        with open(filepath, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.uploaded_filepath = filepath
        file_size_kb = os.path.getsize(filepath) / 1024
        st.success(f"已保存: {uploaded_file.name} ({file_size_kb:.1f} KB)")
        _applog.info(f'file_uploaded name={uploaded_file.name} size_kb={file_size_kb:.1f}')
        get_metrics().record_upload()

        if st.button("Agent 检查数据并生成计划", key="btn_plan"):
            with st.spinner("正在检查数据结构，生成分析策略..."):
                try:
                    plan, explanation, info = agent_plan(filepath)
                    st.session_state.pipeline_plan = plan
                    st.session_state.pipeline_info = info
                    st.session_state.plan_generated = True
                    _prepare_input_for_pipeline(filepath, info)
                except Exception as e:
                    _applog.error(f'plan_generation_failed exc={str(e)[:200]}')
                    get_metrics().record_error()
                    st.error(f"数据检查失败: {str(e)[:300]}")
                    st.stop()

    if st.session_state.pipeline_plan:
        st.success("计划生成完毕！确认后即可开始分析。")
        st.divider()
        st.subheader("数据概览")
        info = st.session_state.pipeline_info
        cols = st.columns(4)
        cols[0].metric("总评论数", info['total_rows'])
        cols[1].metric("语言", {'chinese': '中文', 'english': '英文', 'mixed': '混合'}.get(info['language'], info['language']))
        cols[2].metric("文本列", info.get('text_column', '?'))
        cols[3].metric("评分列", info.get('score_column', '无'))

        st.divider()
        st.subheader("Agent 分析计划")
        st.markdown(explain_plan(st.session_state.pipeline_plan))

        if st.button("确认计划，开始分析", key="btn_confirm"):
            plan = st.session_state.pipeline_plan
            info = st.session_state.pipeline_info
            filepath = info['filepath']

            with st.status("正在执行分析流水线...", expanded=True) as status:
                pipeline_t0 = time.time()
                metrics = get_metrics()
                metrics.record_pipeline_run()

                st.write("**步骤 1/3: 数据清洗 + 向量化...**")
                step1_t0 = time.time()
                env = os.environ.copy()
                env['PYTHONPATH'] = os.path.join(BASE_DIR, 'scripts')
                env['HF_HUB_OFFLINE'] = '1'
                r1 = subprocess.run(
                    [VENV_PYTHON, os.path.join(BASE_DIR, 'scripts', 'step1_embedding.py')],
                    cwd=BASE_DIR, capture_output=True, text=True, env=env, timeout=900
                )
                step1_elapsed = (time.time() - step1_t0) * 1000
                if r1.returncode != 0:
                    _plog.error(f'step1 FAILED elapsed={step1_elapsed:.0f}ms stderr={r1.stderr[-200:]}')
                    metrics.record_error()
                    st.error(f"步骤1 执行失败: {r1.stderr[-500:]}")
                    st.stop()
                _plog.info(f'step1_embedding elapsed={step1_elapsed:.0f}ms')

                # ---- Checkpoint 1: 数据清洗质量 ----
                original_file = os.path.join(BASE_DIR, 'data', 'TikTok.csv')
                cleaned_file = os.path.join(BASE_DIR, 'outputs', 'cleaned_data.csv')
                if os.path.exists(cleaned_file) and os.path.exists(original_file):
                    df_orig = pd.read_csv(original_file)
                    df_clean = pd.read_csv(cleaned_file)
                    orig_rows = len(df_orig)
                    clean_rows = len(df_clean)
                    filter_rate = (orig_rows - clean_rows) / orig_rows * 100 if orig_rows > 0 else 0
                    avg_words = df_clean['word_count'].mean() if 'word_count' in df_clean.columns else 0
                    st.write(f"[检查点 1/2] 清洗完成 — {orig_rows}条→{clean_rows}条 (过滤{filter_rate:.1f}%) | 平均{avg_words:.1f}词/条")

                    filter_stats_path = os.path.join(BASE_DIR, 'outputs', 'filter_stats.json')
                    if os.path.exists(filter_stats_path):
                        with open(filter_stats_path, 'r', encoding='utf-8') as f:
                            fs = json.load(f)
                        st.caption(
                            f"过滤明细: 词数不足({fs.get('min_words',3)}词) {fs.get('filtered_by_length',0)}条 | "
                            f"纯情绪评论 {fs.get('filtered_by_emotion',0)}条"
                        )

                    _plog.info(f'checkpoint1 rows_in={orig_rows} rows_out={clean_rows} filter_pct={filter_rate:.1f} avg_words={avg_words:.1f}')
                    metrics.record_step('step1', step1_elapsed, items_in=orig_rows, items_out=clean_rows)
                else:
                    st.write("[检查点 1/2] 清洗完成")
                    _plog.info('checkpoint1 no_data')

                st.write("**步骤 2/3: 问题分类 + AI 深度分析...**")
                step3_t0 = time.time()
                r3 = subprocess.run(
                    [VENV_PYTHON, os.path.join(BASE_DIR, 'scripts', 'step3_summary.py')],
                    cwd=BASE_DIR, capture_output=True, text=True, env=env, timeout=600
                )
                step3_elapsed = (time.time() - step3_t0) * 1000
                if r3.returncode != 0:
                    _plog.error(f'step3 FAILED elapsed={step3_elapsed:.0f}ms stderr={r3.stderr[-200:]}')
                    metrics.record_error()
                    st.error(f"步骤3 执行失败: {r3.stderr[-500:]}")
                    st.stop()
                _plog.info(f'step3_summary elapsed={step3_elapsed:.0f}ms')
                metrics.record_step('step3', step3_elapsed)

                # ---- Review + Checkpoint 2: 分析质量自检 + 重试 ----
                result_path = os.path.join(BASE_DIR, 'outputs', 'result.json')
                review_log, reviewed_path = review_all_categories(result_path)
                low_count = review_log['low_confidence']

                st.write(f"[检查点 2/2] 质量自检 — 子问题:{review_log['total_checks']} | 高:{review_log['high_confidence']} 中:{review_log['medium_confidence']} 低:{review_log['low_confidence']}")
                _plog.info(
                    f'checkpoint2_review total={review_log["total_checks"]} '
                    f'high={review_log["high_confidence"]} mid={review_log["medium_confidence"]} low={review_log["low_confidence"]}'
                )

                # 低置信度子问题过多 → 重试
                if low_count > 2 and review_log['total_checks'] > 0:
                    st.write(f"  [!]发现 {low_count} 个低置信度子问题，自动重试中（最多2轮）...")
                    _plog.info(f'retry_start initial_low={low_count}')

                    with open(reviewed_path, 'r', encoding='utf-8') as f:
                        reviewed_data = json.load(f)

                    retry_round = 0
                    max_retry_rounds = 2
                    while retry_round < max_retry_rounds:
                        retry_round += 1
                        retried = 0
                        categories = reviewed_data.get('categories', {})
                        for cat_id, cat_data in categories.items():
                            cat_label = cat_data.get('category_label', cat_id)
                            for sp in cat_data.get('subproblems', []):
                                conf = sp.get('review', {}).get('confidence', 'low')
                                if conf == 'low':
                                    sp = retry_subproblem_analysis(sp, cat_label)
                                    retried += 1
                                    # 重新 review 该子问题
                                    new_review = review_single_subproblem(sp, cat_label)
                                    sp['review'] = new_review

                        # 统计本轮结果
                        new_low = sum(
                            1 for c in categories.values()
                            for sp in c.get('subproblems', [])
                            if sp.get('review', {}).get('confidence', 'low') == 'low'
                        )
                        st.write(f"  [R]重试第{retry_round}轮 — 修复{retried}个 | 低置信度: {low_count}→{new_low}")
                        _plog.info(f'retry_round round={retry_round} fixed={retried} low_before={low_count} low_after={new_low}')
                        metrics.record_retry_round(retried)
                        if new_low == 0 or retried == 0:
                            break
                        low_count = new_low

                    # 保存更新后的结果
                    with open(reviewed_path, 'w', encoding='utf-8') as f:
                        json.dump(reviewed_data, f, indent=2, ensure_ascii=False)
                    st.write(f"  [OK]重试完成 — 最终低置信度: {new_low}")
                else:
                    st.write(f"  [OK]质量通过")

                pipeline_elapsed = (time.time() - pipeline_t0) * 1000
                _plog.info(f'pipeline_complete total_elapsed={pipeline_elapsed:.0f}ms')
                metrics.record_pipeline_complete()
                export_metrics()

                status.update(label="全部分析完成!", state="complete")

            st.session_state.pipeline_ran = True
            st.session_state.reviewed = True
            st.rerun()

    # 分析完成后显示持久状态提示
    if st.session_state.pipeline_ran:
        st.success("分析已完成！点击上方「分析报告」查看结果，点击「追问」与 AI 深入讨论。")

elif st.session_state.page == 'report':
    if not st.session_state.pipeline_ran:
        st.info("请先在「上传与规划」页面上传 CSV 并确认分析计划，完成后自动跳转至此。")
    else:
        results = load_results()
        if results is None:
            st.error("找不到分析结果文件。")
            st.stop()

        categories = results.get('categories', {})
        dashboard = results.get('dashboard_data', {})

        st.subheader("全局总览")
        cols = st.columns(5)
        cols[0].metric("总评论", results.get('total_comments', 0))
        cols[1].metric("类别数", results.get('category_count', 0))
        cols[2].metric("均分", results.get('overall_avg_score', 'N/A'))
        overall_sent = dashboard.get('overall_sentiment', {})
        cols[3].metric("负面情绪占比", f"{overall_sent.get('negativity_rate', 0)}%")
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        most_severe = min(categories.items(), key=lambda x: severity_order.get(x[1].get('severity', 'low'), 4)) if categories else None
        cols[4].metric("最严重", most_severe[1].get('category_label', '') if most_severe else 'N/A')

        st.divider()

        # ---- 数据可视化 ----
        st.subheader("数据可视化")

        # Chart 1: 整体情绪分布环形图
        overall_sent = dashboard.get('overall_sentiment', {})
        sentiment_df = pd.DataFrame({
            '情绪': ['正面', '负面', '中性'],
            '占比': [
                overall_sent.get('positive_pct', 0),
                overall_sent.get('negative_pct', 0),
                overall_sent.get('neutral_pct', 0),
            ],
            '数量': [
                overall_sent.get('positive', 0),
                overall_sent.get('negative', 0),
                overall_sent.get('neutral', 0),
            ],
        })
        total_sent = overall_sent.get('total', 0)

        sent_base = alt.Chart(sentiment_df).mark_arc(
            innerRadius=55, outerRadius=110, stroke='transparent', strokeWidth=0
        ).encode(
            theta=alt.Theta('占比:Q', stack=True),
            color=alt.Color('情绪:N',
                scale=alt.Scale(domain=['正面', '负面', '中性'],
                                range=['#4c5e86', '#ba1a1a', '#c4c6d1']),
                legend=alt.Legend(title=None, orient='right')),
            tooltip=[
                alt.Tooltip('情绪:N', title='情绪'),
                alt.Tooltip('数量:Q', title='数量'),
                alt.Tooltip('占比:Q', title='占比', format='.1f'),
            ],
        ).properties(title='整体情绪分布', height=320)

        sent_text = alt.Chart(pd.DataFrame({'t': [f'{total_sent}\n总评论']})).mark_text(
            size=18, color='#1E293B', align='center', baseline='middle'
        ).encode(text='t:N')

        sentiment_chart = (sent_base + sent_text).configure(**CHART_THEME)

        # Chart 2: 问题类别分布环形图
        cat_dist = dashboard.get('category_distribution', [])
        if cat_dist:
            cat_df = pd.DataFrame(cat_dist)
            cat_base = alt.Chart(cat_df).mark_arc(
                innerRadius=40, outerRadius=110, stroke='transparent', strokeWidth=0
            ).encode(
                theta=alt.Theta('percentage:Q', stack=True),
                color=alt.Color('severity:N',
                    scale=alt.Scale(domain=SEVERITY_DOMAIN, range=SEVERITY_COLORS),
                    legend=alt.Legend(title=None, orient='right',
                        labelExpr="{'critical':'CRITICAL','high':'HIGH','medium':'MEDIUM','low':'LOW','info':'INFO'}[datum.label]")),
                order=alt.Order('severity:N', sort='ascending'),
                tooltip=[
                    alt.Tooltip('label:N', title='类别'),
                    alt.Tooltip('count:Q', title='评论数'),
                    alt.Tooltip('percentage:Q', title='占比', format='.1f'),
                ],
            ).properties(title='问题类别分布', height=320)

            cat_text = alt.Chart(pd.DataFrame({'t': [f'{len(cat_dist)}\n个类别']})).mark_text(
                size=18, color='#1E293B', align='center', baseline='middle'
            ).encode(text='t:N')

            category_chart = (cat_base + cat_text).configure(**CHART_THEME)
        else:
            category_chart = None

        # Chart 3: 各类别评论量水平柱状图
        if cat_dist:
            cat_df2 = pd.DataFrame(cat_dist)
            volume_chart = alt.Chart(cat_df2).mark_bar().encode(
                x=alt.X('count:Q', title='评论数量'),
                y=alt.Y('label:N', sort='-x', title=None),
                color=alt.Color('count:Q',
                    scale=alt.Scale(scheme='blues'),
                    legend=None),
                tooltip=[
                    alt.Tooltip('label:N', title='类别'),
                    alt.Tooltip('count:Q', title='评论数'),
                    alt.Tooltip('percentage:Q', title='占比', format='.1f'),
                ],
            ).properties(title='各类别评论量', height=360).configure(**CHART_THEME)
        else:
            volume_chart = None

        # Chart 4: 各类别均分柱状图（升序）
        score_rows = []
        for cat_id, cat_data in categories.items():
            label = cat_data.get('category_label', cat_id)
            raw_score = cat_data.get('avg_score', 0)
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                score = 0.0
            sev = cat_data.get('severity', 'low')
            score_rows.append({'类别': label, '均分': score, '严重度': sev})

        if score_rows:
            score_df = pd.DataFrame(score_rows).sort_values('均分', ascending=True)
            score_bars = alt.Chart(score_df).mark_bar(size=20).encode(
                x=alt.X('均分:Q', title='平均评分', scale=alt.Scale(domain=[0, 5])),
                y=alt.Y('类别:N', sort='x', title=None),
                color=alt.Color('均分:Q',
                    scale=alt.Scale(scheme='blues'),
                    legend=None),
                tooltip=[
                    alt.Tooltip('类别:N', title='类别'),
                    alt.Tooltip('均分:Q', title='均分', format='.2f'),
                ],
            )

            score_text = alt.Chart(score_df).mark_text(
                align='left', baseline='middle', dx=5, color='#1E293B', fontSize=11
            ).encode(
                x=alt.X('均分:Q'),
                y=alt.Y('类别:N', sort='x'),
                text=alt.Text('均分:Q', format='.2f'),
            )

            score_chart = (score_bars + score_text).properties(
                title='各类别均分（升序：低分即问题区）', height=360
            ).configure(**CHART_THEME)
        else:
            score_chart = None

        # 2x2 布局
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.altair_chart(sentiment_chart, use_container_width=True, theme=None)
        with row1_col2:
            if category_chart is not None:
                st.altair_chart(category_chart, use_container_width=True, theme=None)
            else:
                st.info("暂无分类数据")

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            if volume_chart is not None:
                st.altair_chart(volume_chart, use_container_width=True, theme=None)
            else:
                st.info("暂无分类数据")
        with row2_col2:
            if score_chart is not None:
                st.altair_chart(score_chart, use_container_width=True, theme=None)
            else:
                st.info("暂无分类数据")

        st.divider()

        severity_cfg = {
            'critical': {'label': 'CRITICAL', 'color': '#1E3A5F'},
            'high': {'label': 'HIGH', 'color': '#2563EB'},
            'medium': {'label': 'MEDIUM', 'color': '#3B82F6'},
            'low': {'label': 'LOW', 'color': '#93C5FD'},
            'info': {'label': 'INFO', 'color': '#BFDBFE'},
        }

        filter_options = ["所有程度", "仅 Critical", "仅 High", "仅 Medium", "仅 Low"]
        severity_filter = st.selectbox("筛选严重程度", filter_options, index=0, key="severity_filter",
                                       label_visibility="collapsed")

        sorted_cats = sorted(categories.items(), key=lambda x: severity_order.get(x[1].get('severity', 'low'), 4))
        if severity_filter != "所有程度":
            filter_map = {"仅 Critical": "critical", "仅 High": "high", "仅 Medium": "medium", "仅 Low": "low"}
            sorted_cats = [(k, v) for k, v in sorted_cats if v.get('severity') == filter_map[severity_filter]]

        for cat_id, cat_data in sorted_cats:
            sev = cat_data.get('severity', 'low')
            sev_cfg = severity_cfg.get(sev, severity_cfg['low'])

            st.markdown(f'<div class="sev-{sev}">', unsafe_allow_html=True)
            with st.expander(f"{cat_data.get('category_label', cat_id)} — {cat_data.get('total_comments', 0)}条 ({cat_data.get('percentage', 0)}%) | 严重度: {sev_cfg['label']}", expanded=(sev == 'critical')):
                for sp in cat_data.get('subproblems', []):
                    review = sp.get('review', {})
                    conf = review.get('confidence', 'N/A')
                    conf_labels = {'high': '高', 'medium': '中', 'low': '低'}
                    conf_marker = {'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}.get(conf, '[?]')
                    conf_text = conf_labels.get(conf, conf)

                    st.markdown(f"##### {conf_marker} {sp.get('name', '')}  "
                                f"（{sp.get('comment_count', 0)} 条评论，置信度: {conf_text}）")

                    pcol1, pcol2 = st.columns(2)
                    with pcol1:
                        st.markdown(f"**问题**\n\n{sp.get('problem', '')}")
                        st.markdown(f"**场景**\n\n{sp.get('scene', '')}")
                        st.markdown(f"**影响**\n\n{sp.get('impact', '')}")
                    with pcol2:
                        st.markdown(f"**短期方案**\n\n{sp.get('short_term', '')}")
                        st.markdown(f"**长期方案**\n\n{sp.get('long_term', '')}")
                        metrics = sp.get('metrics', [])
                        if metrics:
                            st.markdown("**验证指标**")
                            for m in metrics:
                                st.markdown(f"- {m}")

                    kw_tags = ' '.join([f'`{kw}`' for kw in sp.get('keywords', [])])
                    st.markdown(f"**关键词**: {kw_tags}")

                    if sp.get('representative_comments'):
                        st.markdown("**典型评论**")
                        for c in sp.get('representative_comments', []):
                            st.markdown(f"> _{c}_")

                    if review.get('issues'):
                        st.markdown(f"**Review 发现**: {'; '.join(review['issues'])}")
                    if review.get('strengths'):
                        st.markdown(f"**优点**: {'; '.join(review['strengths'])}")

                    st.divider()

            st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            "下载完整结果 (JSON)",
            data=json.dumps(results, indent=2, ensure_ascii=False),
            file_name="analysis_result.json",
            mime="application/json"
        )

elif st.session_state.page == 'chat':
    if not st.session_state.pipeline_ran:
        st.info("分析完成后可在此向 AI 提问，AI 会基于实际分析数据回答。")
    else:
        st.subheader("追问")
        st.caption("基于当前分析结果，你可以向 AI 提问任何问题。AI 只根据实际数据回答，不会凭空编造。")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
                if msg['role'] == 'assistant' and msg.get('thinking'):
                    with st.expander("思考链", expanded=False):
                        for step in msg['thinking']:
                            st.caption(f"**调用: {step['tool']}**")
                            st.json(step['args'])
                            st.caption(f"**返回: {step['result_preview']}**")
                            with st.expander("查看完整数据", expanded=False):
                                st.json(step['result'])
                            st.divider()

        st.markdown("""
        <div style="padding:8px 16px;background:rgba(61,94,153,0.05);border:1px solid rgba(61,94,153,0.15);
                    border-radius:12px;display:flex;align-items:center;gap:8px;font-size:12px;color:#3d5e99;margin-bottom:8px;">
            <b>[i]</b> 上下文：<b>Review Analysis 已激活</b>。详细数据可供查询。
        </div>
        """, unsafe_allow_html=True)
        question = st.chat_input("试试问：最严重的问题是什么？哪个问题影响用户最多？有什么改进建议？")
        if question:
            _applog.info(f'chat_question len={len(question)}')
            get_metrics().record_chat_question()
            st.session_state.chat_history.append({'role': 'user', 'content': question})
            with st.chat_message('user'):
                st.markdown(question)

            with st.spinner("AI 正在查阅数据、推理分析中..."):
                results = load_results()
                answer, thinking = react_chat(question, results)

            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': answer,
                'thinking': thinking
            })
            with st.chat_message('assistant'):
                st.markdown(answer)
                if thinking:
                    with st.expander("思考链", expanded=False):
                        for step in thinking:
                            st.caption(f"**调用: {step['tool']}**")
                            st.json(step['args'])
                            st.caption(f"**返回: {step['result_preview']}**")
                            with st.expander("查看完整数据", expanded=False):
                                st.json(step['result'])
                            st.divider()
            st.rerun()

        if st.button("清空对话记录", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
