"""Pipeline Agent — 将分析流程拆为10个独立tool，Agent在ReAct循环中自主调用."""

import json
import os
import time
import pandas as pd
from openai import OpenAI

from utils.logger import get_logger
from utils.metrics import get_metrics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_llog = get_logger('llm')
_plog = get_logger('pipeline')


def _load_api_key():
    env_path = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('DEEPSEEK_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return os.environ.get('DEEPSEEK_API_KEY', '')


DEEPSEEK_API_KEY = _load_api_key()
DEEPSEEK_API_URL = 'https://api.deepseek.com'

# ============================================================
#  PipelineState — 工具间共享状态
# ============================================================

class PipelineState:
    """在 Agent 循环中各 tool 共享的全局状态."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.cleaned_path = os.path.join(BASE_DIR, 'outputs', 'cleaned_data.csv')
        self.embedding_path = os.path.join(BASE_DIR, 'outputs', 'embeddings.npy')
        self.result_path = os.path.join(BASE_DIR, 'outputs', 'result.json')

        # 进度标记
        self.cleaned = False
        self.embedded = False
        self.classified = False
        self.categories = {}        # {cat_id: {label, comments: [...], subproblems: [...]}}
        self.subproblems_analyzed = 0
        self.review_checks = 0
        self.low_confidence = 0
        self.retry_count = 0  # 每个子问题最多2次

        # 上一次 tool+参数 用于死循环检测
        self._last_tool = ''
        self._last_args_hash = ''
        self._repeat_count = 0


_state = None  # module-level singleton


def init_state(filepath):
    global _state
    _state = PipelineState(filepath)
    return _state


def get_state():
    return _state


# ============================================================
#  Tool schemas
# ============================================================

PIPELINE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_data",
            "description": "读取CSV文件，返回列名、数据类型、样本、评分分布、语言检测结果。每次分析第一步必须调用。",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clean_data",
            "description": "清洗评论数据：去噪、拼写纠正、过滤低质量评论。如果过滤率太高(>40%)可调低min_words重试。",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_words": {"type": "integer", "description": "最小词数阈值，默认2。过滤太多短评时调到1"},
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "classify_comments",
            "description": "将清洗后的评论按9大类别(登录/内容/视频/广告/功能/性能/隐私/社交/UI/其他)进行关键词分类。调用前必须先clean_data。",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "split_subproblems",
            "description": "对某个类别内的评论用LLM自动拆解为子问题。只对评论数>20的类别调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "string", "description": "类别ID(account/content/video/ads/feature/performance/privacy/social/ui)"}
                },
                "required": ["category_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_subproblem",
            "description": "用LLM对一个子问题生成结构化分析：问题本质、用户场景、影响、短期方案、长期方案、验证指标。调用前必须先split_subproblems。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "string"},
                    "subproblem_name": {"type": "string"}
                },
                "required": ["category_id", "subproblem_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "review_analysis",
            "description": "LLM自检某个子问题的分析质量，返回置信度标签(high/medium/low)和问题清单。analyze_subproblem后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "string"},
                    "subproblem_name": {"type": "string"}
                },
                "required": ["category_id", "subproblem_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retry_analysis",
            "description": "对低质量子问题重新分析。仅在review_analysis返回low时调用。同一子问题最多retry 2次。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "string"},
                    "subproblem_name": {"type": "string"}
                },
                "required": ["category_id", "subproblem_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pipeline_status",
            "description": "查看当前分析进度：已完成步骤、数据量、分类数、置信度分布。做决策前先查状态。",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finalize_report",
            "description": "确认分析完成，汇总结果生成最终报告JSON。所有子问题都analyze+review完成后调用。",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
]

# ============================================================
#  Tool implementations
# ============================================================

def _tool_inspect_data():
    """封装 agent_plan.inspect_csv"""
    from agent_plan import inspect_csv
    st = get_state()
    info = inspect_csv(st.filepath)

    # 为 pipeline 准备数据: 写入 data/TikTok.csv
    text_col = info['text_column']
    score_col = info['score_column']
    df = pd.read_csv(st.filepath)
    if text_col and text_col != 'content':
        df.rename(columns={text_col: 'content'}, inplace=True)
    if score_col and score_col != 'score':
        df.rename(columns={score_col: 'score'}, inplace=True)
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    df.to_csv(os.path.join(BASE_DIR, 'data', 'TikTok.csv'), index=False)

    return {
        'total_rows': info['total_rows'],
        'columns': info['columns'],
        'text_column': info['text_column'],
        'score_column': info['score_column'],
        'language': info['language'],
        'score_distribution': _score_dist(df),
        'sample_comments': info.get('text_samples', [])[:5],
        'missing_pct': {k: round(v / info['total_rows'] * 100, 1)
                        for k, v in info.get('missing_values', {}).items()},
    }


def _score_dist(df):
    """评分分布摘要"""
    score_col = 'score' if 'score' in df.columns else None
    if not score_col:
        return 'no score column'
    scores = df[score_col].dropna()
    if len(scores) == 0:
        return 'no valid scores'
    dist = scores.value_counts().sort_index().to_dict()
    return {str(k): int(v) for k, v in dist.items()}


def _tool_clean_data(min_words=2):
    """封装 step1_embedding 清洗逻辑"""
    from scripts.step1_embedding import filter_low_quality
    st = get_state()
    input_path = os.path.join(BASE_DIR, 'data', 'TikTok.csv')
    df = pd.read_csv(input_path)

    # 列名映射
    if 'content' in df.columns and 'translated' not in df.columns:
        df.rename(columns={'content': 'translated'}, inplace=True)

    df, filter_stats = filter_low_quality(df, min_words=min_words)
    os.makedirs(os.path.join(BASE_DIR, 'outputs'), exist_ok=True)
    df.to_csv(st.cleaned_path, index=False)

    st.cleaned = True

    return {
        'rows_in': filter_stats['original_count'],
        'rows_out': filter_stats['kept_count'],
        'filter_rate': round((filter_stats['dropped_total'] / filter_stats['original_count'] * 100), 1),
        'filtered_by_length': filter_stats['filtered_by_length'],
        'filtered_by_emotion': filter_stats['filtered_by_emotion'],
        'avg_words': round(df['word_count'].mean(), 1) if 'word_count' in df.columns else 0,
        'min_words_used': min_words,
    }


def _tool_classify_comments():
    """封装 step3_summary 分类逻辑"""
    from scripts.step3_summary import classify_category, CATEGORIES
    st = get_state()
    df = pd.read_csv(st.cleaned_path)

    df['category'] = df['cleaned'].apply(lambda x: classify_category(x))
    counts = df['category'].value_counts().to_dict()
    total = len(df)

    categories = {}
    for cat_id, count in counts.items():
        if cat_id == 'other':
            continue
        cat_info = CATEGORIES.get(cat_id, {})
        categories[cat_id] = {
            'label': cat_info.get('label', cat_id),
            'count': int(count),
            'pct': round(count / total * 100, 1),
        }

    st.classified = True
    st.categories = categories
    st._df = df  # keep for later subproblem access

    return {
        'total_classified': total,
        'category_count': len(categories),
        'categories': categories,
    }


def _tool_split_subproblems(category_id):
    """封装 step3_summary.split_subproblems_with_llm"""
    from scripts.step3_summary import split_subproblems_with_llm
    st = get_state()
    df = st._df if hasattr(st, '_df') and st._df is not None else pd.read_csv(st.cleaned_path)

    cat_comments = df[df['category'] == category_id]['cleaned'].tolist()
    if len(cat_comments) < 2:
        return {'error': f'类别 {category_id} 评论数不足(<2)，跳过', 'subproblems': []}

    subproblems = split_subproblems_with_llm(cat_comments, category_id)

    # 存储到 state
    if category_id not in st.categories:
        st.categories[category_id] = {}
    st.categories[category_id]['subproblems'] = subproblems

    return {
        'category_id': category_id,
        'total_comments': len(cat_comments),
        'subproblems': [{'name': sp['name'], 'comment_count': len(sp['comments'])} for sp in subproblems],
    }


def _tool_analyze_subproblem(category_id, subproblem_name):
    """封装 step3_summary 分析 + 情绪 + 典型评论"""
    from scripts.step3_summary import (generate_complete_analysis_with_llm,
                                        select_representative_comments,
                                        extract_keywords_with_tfidf,
                                        calculate_sentiment_stats)
    st = get_state()
    df = st._df if hasattr(st, '_df') and st._df is not None else pd.read_csv(st.cleaned_path)

    sp_data = _find_subproblem(st, category_id, subproblem_name)
    if not sp_data:
        return {'error': f'子问题 {subproblem_name} 未找到，请先 split_subproblems({category_id})'}

    comments = sp_data['comments']
    keywords_raw = extract_keywords_with_tfidf(comments, top_n=5)
    keyword_list = [kw for kw, _ in keywords_raw]

    # LLM 分析
    comments_text = ' '.join(comments)
    analysis = generate_complete_analysis_with_llm(comments_text, keyword_list)

    # 典型评论 + 情绪
    rep_comments = select_representative_comments(comments, keyword_list)
    comments_with_scores = []
    for c in comments:
        matched = df[df['cleaned'] == c]
        if len(matched) > 0:
            s = matched['score'].values[0]
            if not pd.isna(s):
                comments_with_scores.append((c, s))
    sentiment = calculate_sentiment_stats(comments_with_scores)

    sp_data['analysis'] = analysis
    sp_data['keywords'] = keyword_list
    sp_data['representative_comments'] = rep_comments
    sp_data['sentiment'] = sentiment
    sp_data['comment_count'] = len(comments)

    st.subproblems_analyzed += 1

    return {
        'name': subproblem_name,
        'comment_count': len(comments),
        'keywords': keyword_list,
        'problem': analysis.get('problem', '')[:100],
        'short_term': analysis.get('short_term', '')[:80],
        'negativity_rate': sentiment.get('negativity_rate', 0),
    }


def _find_subproblem(state, category_id, subproblem_name):
    """在 state.categories 中查找子问题"""
    cat = state.categories.get(category_id, {})
    for sp in cat.get('subproblems', []):
        if sp['name'] == subproblem_name:
            return sp
    return None


def _tool_review_analysis(category_id, subproblem_name):
    """封装 agent_review.review_single_subproblem"""
    from agent_review import review_single_subproblem
    st = get_state()

    sp_data = _find_subproblem(st, category_id, subproblem_name)
    if not sp_data:
        return {'error': f'子问题 {subproblem_name} 未找到'}

    cat_label = st.categories.get(category_id, {}).get('label', category_id)
    review = review_single_subproblem(sp_data, cat_label)
    sp_data['review'] = review

    st.review_checks += 1
    conf = review.get('confidence') or 'low'
    if conf == 'low':
        st.low_confidence += 1
        sp_data['retry_count'] = sp_data.get('retry_count', 0)

    return {
        'confidence': review.get('confidence') or 'low',
        'issues': review.get('issues', []),
        'strengths': review.get('strengths', []),
    }


def _tool_retry_analysis(category_id, subproblem_name):
    """封装 agent_review.retry_subproblem_analysis"""
    from agent_review import retry_subproblem_analysis, review_single_subproblem
    st = get_state()

    sp_data = _find_subproblem(st, category_id, subproblem_name)
    if not sp_data:
        return {'error': f'子问题 {subproblem_name} 未找到'}

    retry_n = sp_data.get('retry_count', 0)
    if retry_n >= 2:
        return {'error': f'子问题 {subproblem_name} 已重试{retry_n}次，不再重试', 'skipped': True}

    cat_label = st.categories.get(category_id, {}).get('label', category_id)
    sp_data = retry_subproblem_analysis(sp_data, cat_label)
    sp_data['retry_count'] = retry_n + 1
    sp_data['review'] = review_single_subproblem(sp_data, cat_label)

    st.retry_count += 1
    new_conf = sp_data['review'].get('confidence') or 'low'
    if new_conf != 'low':
        st.low_confidence = max(0, st.low_confidence - 1)

    return {
        'retry_round': retry_n + 1,
        'new_confidence': new_conf,
        'problem': sp_data.get('problem', '')[:100],
    }


def _tool_get_pipeline_status():
    """查询当前进度"""
    st = get_state()
    total_subproblems = sum(
        len(cat.get('subproblems', [])) for cat in st.categories.values()
    )
    return {
        'file': os.path.basename(st.filepath),
        'cleaned': st.cleaned,
        'classified': st.classified,
        'categories_found': len(st.categories),
        'total_subproblems': total_subproblems,
        'subproblems_analyzed': st.subproblems_analyzed,
        'review_checks': st.review_checks,
        'low_confidence_count': st.low_confidence,
        'retry_count': st.retry_count,
    }


def _tool_finalize_report():
    """汇总所有分析结果写入 result.json"""
    from scripts.step3_summary import calculate_severity
    st = get_state()
    df = pd.read_csv(st.cleaned_path)
    total = len(df)

    categories_out = {}
    dashboard_cats = []
    for cat_id, cat_data in st.categories.items():
        subproblems = cat_data.get('subproblems', [])
        cat_total = sum(sp.get('comment_count', 0) for sp in subproblems)
        scores = []
        for sp in subproblems:
            for c in sp.get('comments', []):
                matched = df[df['cleaned'] == c]
                if len(matched) > 0 and not pd.isna(matched['score'].values[0]):
                    scores.append(float(matched['score'].values[0]))
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0
        severity = calculate_severity(avg_score, cat_total, total)

        categories_out[cat_id] = {
            'category_label': cat_data.get('label', cat_id),
            'total_comments': cat_total,
            'avg_score': avg_score,
            'percentage': round(cat_total / total * 100, 1),
            'severity': severity,
            'subproblems': [{
                'name': sp.get('name', ''),
                'comment_count': sp.get('comment_count', 0),
                'keywords': sp.get('keywords', []),
                'problem': sp.get('analysis', {}).get('problem', ''),
                'scene': sp.get('analysis', {}).get('scene', ''),
                'impact': sp.get('analysis', {}).get('impact', ''),
                'short_term': sp.get('analysis', {}).get('short_term', ''),
                'long_term': sp.get('analysis', {}).get('long_term', ''),
                'metrics': sp.get('analysis', {}).get('metrics', []),
                'representative_comments': sp.get('representative_comments', []),
                'sentiment': sp.get('sentiment', {}),
                'review': sp.get('review', {}),
            } for sp in subproblems],
        }
        dashboard_cats.append({
            'category': cat_id,
            'label': cat_data.get('label', cat_id),
            'count': cat_total,
            'percentage': round(cat_total / total * 100, 1),
            'severity': severity,
        })

    # 全局情绪
    all_neg = sum(
        sp.get('sentiment', {}).get('negative', 0)
        for cat in categories_out.values()
        for sp in cat.get('subproblems', [])
    )
    all_pos = sum(
        sp.get('sentiment', {}).get('positive', 0)
        for cat in categories_out.values()
        for sp in cat.get('subproblems', [])
    )
    all_neu = sum(
        sp.get('sentiment', {}).get('neutral', 0)
        for cat in categories_out.values()
        for sp in cat.get('subproblems', [])
    )
    sent_total = all_pos + all_neg + all_neu
    overall_sent = {
        'positive': all_pos, 'negative': all_neg, 'neutral': all_neu,
        'total': sent_total,
        'positive_pct': round(all_pos / sent_total * 100, 1) if sent_total else 0,
        'negative_pct': round(all_neg / sent_total * 100, 1) if sent_total else 0,
        'neutral_pct': round(all_neu / sent_total * 100, 1) if sent_total else 0,
        'dominant': 'positive' if all_pos >= all_neg else 'negative',
        'negativity_rate': round(all_neg / sent_total * 100, 1) if sent_total else 0,
    }

    result = {
        'categories': categories_out,
        'total_comments': total,
        'overall_avg_score': round(df['score'].mean(), 2) if 'score' in df.columns else 'N/A',
        'category_count': len(categories_out),
        'dashboard_data': {
            'category_distribution': dashboard_cats,
            'severity_ranking': sorted(dashboard_cats,
                                       key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x['severity'], 4)),
            'overall_sentiment': overall_sent,
        }
    }

    os.makedirs(os.path.dirname(st.result_path), exist_ok=True)
    with open(st.result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return {
        'success': True,
        'result_path': st.result_path,
        'summary': f"共{total}条评论，{len(categories_out)}个类别，分析完成",
    }


# ============================================================
#  Tool map
# ============================================================

TOOL_MAP = {
    'inspect_data': _tool_inspect_data,
    'clean_data': _tool_clean_data,
    'classify_comments': _tool_classify_comments,
    'split_subproblems': _tool_split_subproblems,
    'analyze_subproblem': _tool_analyze_subproblem,
    'review_analysis': _tool_review_analysis,
    'retry_analysis': _tool_retry_analysis,
    'get_pipeline_status': _tool_get_pipeline_status,
    'finalize_report': _tool_finalize_report,
}

# ============================================================
#  System Prompt
# ============================================================

SYSTEM_PROMPT = """你是评论分析Agent。你可以调用工具来完成从原始CSV到最终分析报告的完整流程。

工作流程建议（但可根据数据实际情况灵活调整）:
1. inspect_data → 了解数据规模、语言、评分分布
2. clean_data → 清洗数据（默认min_words=2，如果过滤率太高可以调到1）
3. classify_comments → 将评论分到9个类别
4. get_pipeline_status → 查看分类结果
5. 对评论数>20的重要类别: split_subproblems → 对每个子问题 analyze_subproblem → review_analysis
6. 如果review返回low: retry_analysis（同一子问题最多2次）
7. 感觉分析足够了 → finalize_report

规则:
- 不要跳过inspect_data，这是了解数据的唯一途径
- clean_data后如果filter_rate>40%，考虑调min_words=1重试一次
- analyze_subproblem之前必须先split_subproblems
- review_analysis发现low必须retry，但最多retry 2次
- 不要对评论数<5的类别深入分析（不值得）
- 同一个tool+同一个参数不要连续调3次以上（死循环）
- 分析几个最重要的类别就够了（3-5个），不要试图覆盖所有
- get_pipeline_status可以帮助你决定下一步
- 觉得OK了就finalize_report

用中文回答，简洁专业。每步调工具前先想好理由。"""

# ============================================================
#  Agent ReAct 主循环
# ============================================================

MAX_TOOL_ROUNDS = 30


def run_pipeline_agent(filepath):
    """Agent 自主分析主入口。返回 (success: bool, summary: str, result_path: str)."""
    init_state(filepath)
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)
    st = get_state()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请分析这份CSV文件: {filepath}"}
    ]
    tool_log = []
    last_tool_name = ''
    last_tool_args = ''

    for round_idx in range(MAX_TOOL_ROUNDS):
        t0 = time.time()
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=PIPELINE_TOOLS,
                temperature=0.3,
                max_tokens=500,
                timeout=60
            )
        except Exception as e:
            _llog.error(f'pipeline_agent LLM round={round_idx+1} FAILED: {str(e)[:100]}')
            return False, f"Agent LLM 调用失败: {str(e)[:200]}", None

        elapsed = (time.time() - t0) * 1000
        msg = response.choices[0].message
        usage = response.usage

        if msg.content and not msg.tool_calls:
            # Agent decided to stop with a message
            _plog.info(f'pipeline_agent finished at round {round_idx+1}: {msg.content[:100]}')
            return True, msg.content.strip(), st.result_path

        if msg.tool_calls:
            messages.append(msg)

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                # 死循环检测
                args_hash = json.dumps(tool_args, sort_keys=True)
                if tool_name == last_tool_name and args_hash == last_tool_args:
                    st._repeat_count += 1
                else:
                    st._repeat_count = 0
                last_tool_name = tool_name
                last_tool_args = args_hash

                if st._repeat_count >= 3:
                    tool_result = {'error': '同一工具+参数连续调用3次，强制停止以防死循环。请换一个工具或finalize_report。'}
                else:
                    try:
                        tool_fn = TOOL_MAP.get(tool_name)
                        if tool_fn:
                            tool_result = tool_fn(**tool_args)
                        else:
                            tool_result = {'error': f'Unknown tool: {tool_name}'}
                    except Exception as e:
                        tool_result = {'error': f'工具执行失败: {str(e)[:200]}'}
                        _plog.error(f'tool {tool_name} FAILED: {str(e)[:200]}')

                tool_log.append({
                    'round': round_idx + 1,
                    'tool': tool_name,
                    'args': tool_args,
                    'result_summary': str(tool_result)[:200],
                })

                _plog.info(f'pipeline_agent round={round_idx+1} tool={tool_name} '
                           f'elapsed={elapsed:.0f}ms tokens_in={usage.prompt_tokens if usage else 0}')

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(tool_result, ensure_ascii=False)[:4000],
                })
        else:
            break

    # 达到 max_rounds — 尝试强制结束
    _plog.info(f'pipeline_agent hit max_rounds ({MAX_TOOL_ROUNDS})')
    messages.append({
        "role": "user",
        "content": "已达到最大轮次。请直接调用finalize_report结束分析。"
    })
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=PIPELINE_TOOLS,
            temperature=0.2,
            max_tokens=400,
            timeout=60
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.function.name == 'finalize_report':
                    result = _tool_finalize_report()
                    return result['success'], result['summary'], st.result_path
        return True, msg.content or '达到最大轮次，分析可能不完整', st.result_path
    except Exception:
        return False, '达到最大轮次后无法完成', None
