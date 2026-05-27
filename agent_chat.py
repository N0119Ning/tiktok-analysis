import json
import os
import time
import pandas as pd
from openai import OpenAI

from utils.logger import get_logger
from utils.metrics import get_metrics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_llog = get_logger('llm')
_applog = get_logger('app')

# ---- cached resources ----
_cleaned_df_cache = None


def _load_cleaned_data():
    """Lazy-load cleaned_data.csv for search_comments tool."""
    global _cleaned_df_cache
    if _cleaned_df_cache is not None:
        return _cleaned_df_cache
    path = os.path.join(BASE_DIR, 'outputs', 'cleaned_data.csv')
    if os.path.exists(path):
        _cleaned_df_cache = pd.read_csv(path)
    return _cleaned_df_cache


def load_api_key():
    env_path = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('DEEPSEEK_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return os.environ.get('DEEPSEEK_API_KEY', '')


DEEPSEEK_API_KEY = load_api_key()
DEEPSEEK_API_URL = 'https://api.deepseek.com'

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)
    return _client


def load_results():
    reviewed_path = os.path.join(BASE_DIR, 'outputs', 'result_reviewed.json')
    result_path = os.path.join(BASE_DIR, 'outputs', 'result.json')
    path = reviewed_path if os.path.exists(reviewed_path) else result_path
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================
#  Tool implementations (operate on loaded results dict)
# ============================================================

def _tool_get_overall_stats(results):
    dash = results.get('dashboard_data', {})
    overall_sent = dash.get('overall_sentiment', {})
    return {
        'total_comments': results.get('total_comments', 0),
        'overall_avg_score': results.get('overall_avg_score', 'N/A'),
        'category_count': results.get('category_count', 0),
        'sentiment': {
            'positive': overall_sent.get('positive', 0),
            'negative': overall_sent.get('negative', 0),
            'neutral': overall_sent.get('neutral', 0),
            'positive_pct': overall_sent.get('positive_pct', 0),
            'negative_pct': overall_sent.get('negative_pct', 0),
            'neutral_pct': overall_sent.get('neutral_pct', 0),
            'dominant': overall_sent.get('dominant', 'unknown'),
        }
    }


def _tool_get_category_list(results):
    categories = results.get('categories', {})
    cat_list = []
    for cat_id, cat_data in categories.items():
        cat_list.append({
            'category_id': cat_id,
            'label': cat_data.get('category_label', cat_id),
            'comment_count': cat_data.get('total_comments', 0),
            'percentage': cat_data.get('percentage', 0),
            'severity': cat_data.get('severity', 'unknown'),
            'avg_score': cat_data.get('avg_score', 'N/A'),
        })
    cat_list.sort(key=lambda x: x['comment_count'], reverse=True)
    return {'categories': cat_list, 'total': len(cat_list)}


def _tool_get_category_detail(results, category_id):
    categories = results.get('categories', {})
    cat_data = categories.get(category_id)
    if cat_data is None:
        return {'error': f"Category '{category_id}' not found. Available: {list(categories.keys())}"}

    detail = {
        'category_id': category_id,
        'label': cat_data.get('category_label', category_id),
        'comment_count': cat_data.get('total_comments', 0),
        'percentage': cat_data.get('percentage', 0),
        'severity': cat_data.get('severity', 'unknown'),
        'avg_score': cat_data.get('avg_score', 'N/A'),
        'subproblems': []
    }

    for sp in cat_data.get('subproblems', []):
        sp_info = {
            'name': sp.get('name', 'unknown'),
            'comment_count': sp.get('comment_count', 0),
            'keywords': sp.get('keywords', []),
            'problem': sp.get('problem', ''),
            'scene': sp.get('scene', ''),
            'impact': sp.get('impact', ''),
            'short_term': sp.get('short_term', ''),
            'long_term': sp.get('long_term', ''),
            'metrics': sp.get('metrics', []),
            'representative_comments': sp.get('representative_comments', [])[:3],
            'confidence': sp.get('review', {}).get('confidence', 'N/A'),
        }
        sent = sp.get('sentiment', {})
        if sent:
            sp_info['sentiment'] = {
                'positive_pct': sent.get('positive_pct', 0),
                'negative_pct': sent.get('negative_pct', 0),
                'neutral_pct': sent.get('neutral_pct', 0),
            }
        detail['subproblems'].append(sp_info)

    return detail


def _tool_search_comments(results, keyword, category_id=None):
    df = _load_cleaned_data()
    if df is None:
        return {'error': 'Unable to load comment data for search.'}

    text_col = 'cleaned' if 'cleaned' in df.columns else 'translated'
    if text_col not in df.columns:
        return {'error': f'No text column found in data. Available: {list(df.columns)}'}

    keyword_lower = keyword.lower()
    mask = df[text_col].astype(str).str.lower().str.contains(keyword_lower, na=False)

    if mask.sum() == 0:
        return {'results': [], 'keyword': keyword, 'total_found': 0}

    matched = df[mask].head(10)
    results_list = []
    for _, row in matched.iterrows():
        item = {'text': str(row[text_col])[:200]}
        if 'score' in df.columns:
            item['score'] = row['score'] if not pd.isna(row['score']) else None
        results_list.append(item)

    return {'results': results_list, 'keyword': keyword, 'total_found': int(mask.sum())}


def _tool_compare_categories(results, cat_a, cat_b):
    categories = results.get('categories', {})
    if cat_a not in categories:
        return {'error': f"Category '{cat_a}' not found."}
    if cat_b not in categories:
        return {'error': f"Category '{cat_b}' not found."}
    if cat_a == cat_b:
        return {'error': f"Both categories are the same: '{cat_a}'. Please specify two different categories."}

    a = categories[cat_a]
    b = categories[cat_b]

    def extract(cat_data):
        sent = {}
        for sp in cat_data.get('subproblems', []):
            s = sp.get('sentiment', {})
            if s:
                sent = {
                    'positive_pct': s.get('positive_pct', 0),
                    'negative_pct': s.get('negative_pct', 0),
                    'neutral_pct': s.get('neutral_pct', 0),
                }
                break
        return {
            'label': cat_data.get('category_label', ''),
            'comment_count': cat_data.get('total_comments', 0),
            'percentage': cat_data.get('percentage', 0),
            'severity': cat_data.get('severity', 'unknown'),
            'avg_score': cat_data.get('avg_score', 'N/A'),
            'sentiment': sent,
        }

    return {'category_a': extract(a), 'category_b': extract(b)}


# ============================================================
#  Tool definitions (OpenAI function calling format)
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_overall_stats",
            "description": "获取整体统计数据：总评论数、平均评分、情绪分布（正面/负面/中性数量和百分比）",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_category_list",
            "description": "获取所有问题类别的概览：类别名、评论数、严重度、占比",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_category_detail",
            "description": "获取某个类别的详细分析：子问题、关键词、典型评论、评分、情绪分布",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "string", "description": "类别ID，如 account, ads, content, video, feature, performance, privacy, social, ui"}
                },
                "required": ["category_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_comments",
            "description": "在原始评论中搜索包含某关键词的评论，可选按类别过滤",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "要搜索的关键词"},
                    "category_id": {"type": "string", "description": "可选：限定搜索的类别ID"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_categories",
            "description": "并排对比两个类别的指标：评论数、评分、严重度、情绪分布",
            "parameters": {
                "type": "object",
                "properties": {
                    "cat_a": {"type": "string", "description": "第一个类别ID"},
                    "cat_b": {"type": "string", "description": "第二个类别ID"}
                },
                "required": ["cat_a", "cat_b"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a data-driven product analyst. Users ask you questions about app feedback analysis results.

You have tools to query the data. Follow this process:
1. Understand the user's question
2. Call the right tools to gather relevant data
3. Review the results — do you have enough to answer? If not, call another tool
4. Once you have enough data, give a clear, data-backed answer

Rules:
- ALWAYS use tools to get data — never guess or make up numbers
- Cite specific numbers from tool results (comment counts, percentages, scores)
- Use compare_categories when the user wants to compare two issues
- Use search_comments when the user asks about a specific keyword or term
- Answer in Chinese unless the user asks in English
- 3-5 sentences is enough unless the user asks for more detail"""

# ============================================================
#  Main ReAct loop
# ============================================================

TOOL_MAP = {
    'get_overall_stats': _tool_get_overall_stats,
    'get_category_list': _tool_get_category_list,
    'get_category_detail': _tool_get_category_detail,
    'search_comments': _tool_search_comments,
    'compare_categories': _tool_compare_categories,
}

MAX_TOOL_ROUNDS = 8


def react_chat(question, results=None):
    """ReAct agent: think → act → observe → repeat.
    Returns (answer_text, thinking_process_list).
    """
    if results is None:
        results = load_results()
    if results is None:
        return "暂无可用的分析结果，请先运行分析 pipeline。", []

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question[:2000]}
    ]
    thinking = []

    client = _get_client()

    for _round in range(MAX_TOOL_ROUNDS):
        t0 = time.time()
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=TOOLS,
                temperature=0.3,
                max_tokens=500,
                timeout=30
            )
            elapsed = (time.time() - t0) * 1000
            usage = response.usage
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0
            _llog.info(f'chat_react round={_round+1} elapsed={elapsed:.0f}ms tokens_in={tokens_in} tokens_out={tokens_out}')
            get_metrics().record_llm_call('chat_react', elapsed, tokens_in, tokens_out)
        except Exception as e:
            elapsed = (time.time() - t0) * 1000
            _llog.error(f'chat_react FAILED round={_round+1} elapsed={elapsed:.0f}ms exc={str(e)[:100]}')
            get_metrics().record_llm_call('chat_react', elapsed, error=True)
            return f"回答失败: {str(e)}", thinking

        msg = response.choices[0].message

        # If LLM returned a text answer (finish_reason=stop), we're done
        if msg.content and not msg.tool_calls:
            return msg.content.strip(), thinking

        # If LLM wants to call tools
        if msg.tool_calls:
            messages.append(msg)

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                # Execute tool
                tool_fn = TOOL_MAP.get(tool_name)
                if tool_fn:
                    tool_result = tool_fn(results, **tool_args)
                else:
                    tool_result = {'error': f'Unknown tool: {tool_name}'}

                thinking.append({
                    'tool': tool_name,
                    'args': tool_args,
                    'result_preview': _summarize_result(tool_name, tool_result),
                    'result': tool_result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
        else:
            # No content, no tool calls — shouldn't happen
            break

    # Ran out of rounds — force a final answer
    try:
        messages.append({"role": "user", "content": "根据以上所有工具返回的数据，请回答最初的问题。精简回答。"})
        t0 = time.time()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,
            max_tokens=400,
            timeout=30
        )
        elapsed = (time.time() - t0) * 1000
        usage = response.usage
        tokens_in = usage.prompt_tokens if usage else 0
        tokens_out = usage.completion_tokens if usage else 0
        _llog.info(f'chat_final_answer elapsed={elapsed:.0f}ms tokens_in={tokens_in} tokens_out={tokens_out}')
        get_metrics().record_llm_call('chat_final', elapsed, tokens_in, tokens_out)
        return response.choices[0].message.content.strip(), thinking
    except Exception as e:
        _llog.error(f'chat_final_answer FAILED exc={str(e)[:100]}')
        get_metrics().record_llm_call('chat_final', 0, error=True)
        return f"回答失败: {str(e)}", thinking


def _summarize_result(tool_name, result):
    """Create a short preview of tool result for the thinking expander."""
    if 'error' in result:
        return f"[错误] {result['error']}"
    if tool_name == 'get_overall_stats':
        return f"总评论: {result['total_comments']}, 均分: {result['overall_avg_score']}, 情绪: {result['sentiment']['dominant']}"
    if tool_name == 'get_category_list':
        cats = result.get('categories', [])
        return f"共{result['total']}个类别, 最大: {cats[0]['label']}({cats[0]['comment_count']}条)" if cats else "无数据"
    if tool_name == 'get_category_detail':
        sps = result.get('subproblems', [])
        return f"{result.get('label','')}: {result['comment_count']}条, {len(sps)}个子问题"
    if tool_name == 'search_comments':
        return f"找到{result.get('total_found',0)}条含关键词'{result.get('keyword','')}'的评论"
    if tool_name == 'compare_categories':
        a = result.get('category_a', {})
        b = result.get('category_b', {})
        return f"{a.get('label','A')}:{a.get('comment_count',0)}条 vs {b.get('label','B')}:{b.get('comment_count',0)}条"
    return str(result)[:100]


def chat(question, results=None):
    """回答用户对分析报告的追问 (backward-compatible wrapper)."""
    answer, _ = react_chat(question, results)
    return answer
