import json
import os
import time
from openai import OpenAI

from utils.logger import get_logger, log_event
from utils.metrics import get_metrics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_llog = get_logger('llm')
_plog = get_logger('pipeline')


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


def review_single_subproblem(sp_data, category_label):
    """LLM 自检单个子问题的分析质量"""
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)
    t0 = time.time()

    prompt = f"""你是资深产品经理，正在审核一份AI生成的用户反馈分析质量。

类别: {category_label}
子问题名: {sp_data.get('name', 'unknown')}
提取的关键词: {sp_data.get('keywords', [])}

已生成的分析:
- 问题: {sp_data.get('problem', 'N/A')}
- 场景: {sp_data.get('scene', 'N/A')}
- 影响: {sp_data.get('impact', 'N/A')}
- 短期方案: {sp_data.get('short_term', 'N/A')}
- 指标: {sp_data.get('metrics', [])}

代表性评论 (共{len(sp_data.get('representative_comments', []))}条):
{chr(10).join(sp_data.get('representative_comments', [])[:5])}

评论数量: {sp_data.get('comment_count', 0)}

任务: 审核此分析的质量。只输出一个JSON对象:
{{"confidence":"high/medium/low", "issues":["问题1"], "strengths":["优点1"]}}

质量标准:
- 问题陈述是否具体、是否基于实际评论？（不能模糊笼统）
- 分析是否识别了具体的用户行为和使用场景？
- 关键词是否有信息量（不能是"app""video""good"等无意义词）？
- 建议方案是否可执行、可衡量？
- 是否存在幻觉（说了评论中未提及的内容）？

issues和strengths每项不超过20个汉字。无问题则返回空列表。"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是质量审核员。只输出有效JSON，不要别的。所有分析用中文。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=300,
            timeout=20
        )
        elapsed = (time.time() - t0) * 1000
        usage = response.usage
        tokens_in = usage.prompt_tokens if usage else 0
        tokens_out = usage.completion_tokens if usage else 0
        _llog.info(f'review_single elapsed={elapsed:.0f}ms tokens_in={tokens_in} tokens_out={tokens_out}')
        get_metrics().record_llm_call('review', elapsed, tokens_in, tokens_out)

        content = response.choices[0].message.content.strip()
        content = content.replace('```json', '').replace('```', '').strip()
        result = json.loads(content)
        return result
    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        _llog.error(f'review_single FAILED elapsed={elapsed:.0f}ms exc={str(e)[:100]}')
        get_metrics().record_llm_call('review', elapsed, error=True)
        return {"confidence": "low", "issues": [f"Review failed: {str(e)[:80]}"], "strengths": []}


def retry_subproblem_analysis(sp_data, category_label):
    """重新分析低置信度子问题，返回更新后的 sp_data"""
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)
    t0 = time.time()

    comments_text = '\n'.join(sp_data.get('representative_comments', [])[:10])
    keywords = sp_data.get('keywords', [])

    prompt = f"""你正在分析类别为"{category_label}"的用户反馈。
子问题名: {sp_data.get('name', 'unknown')}
关键词: {keywords}
评论数量: {sp_data.get('comment_count', 0)}

代表性评论:
{comments_text}

重要：必须用中文输出所有内容。

仅基于这些评论提供详细分析。只输出JSON:
{{"problem":"...", "scene":"...", "impact":"...", "short_term":"...", "long_term":"...", "metrics":["..."]}}

规则:
- problem: 具体、基于评论、不使用笼统描述
- scene: 评论中描述的具体用户行为
- impact: 量化的业务影响
- short_term: 2周内可执行的方案
- long_term: 3个月内可实现的系统性方案
- metrics: 2-3个可衡量的KPI
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是产品分析师。只输出有效JSON，不要别的。所有分析必须用中文。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400,
            timeout=30
        )
        elapsed = (time.time() - t0) * 1000
        usage = response.usage
        tokens_in = usage.prompt_tokens if usage else 0
        tokens_out = usage.completion_tokens if usage else 0
        _llog.info(f'retry_analysis elapsed={elapsed:.0f}ms tokens_in={tokens_in} tokens_out={tokens_out}')
        get_metrics().record_llm_call('retry_analysis', elapsed, tokens_in, tokens_out)

        content = response.choices[0].message.content.strip()
        content = content.replace('```json', '').replace('```', '').strip()
        result = json.loads(content)
        sp_data['problem'] = result.get('problem', sp_data.get('problem', ''))
        sp_data['scene'] = result.get('scene', sp_data.get('scene', ''))
        sp_data['impact'] = result.get('impact', sp_data.get('impact', ''))
        sp_data['short_term'] = result.get('short_term', sp_data.get('short_term', ''))
        sp_data['long_term'] = result.get('long_term', sp_data.get('long_term', ''))
        sp_data['metrics'] = result.get('metrics', sp_data.get('metrics', []))
    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        _llog.error(f'retry_analysis FAILED elapsed={elapsed:.0f}ms exc={str(e)[:100]}')
        get_metrics().record_llm_call('retry_analysis', elapsed, error=True)
        sp_data['review'] = sp_data.get('review', {})
        sp_data['review']['retry_failed'] = str(e)[:100]

    return sp_data


def review_all_categories(result_json_path):
    """遍历所有子问题，LLM 自检质量"""
    with open(result_json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)

    review_log = {
        'total_checks': 0,
        'high_confidence': 0,
        'medium_confidence': 0,
        'low_confidence': 0,
        'checks': []
    }

    metrics = get_metrics()
    categories = results.get('categories', {})
    for cat_id, cat_data in categories.items():
        cat_label = cat_data.get('category_label', cat_id)
        for sp in cat_data.get('subproblems', []):
            sp_review = review_single_subproblem(sp, cat_label)
            sp['review'] = sp_review
            review_log['checks'].append({
                'category': cat_label,
                'subproblem': sp.get('name', ''),
                'review': sp_review
            })
            review_log['total_checks'] += 1
            conf = sp_review.get('confidence', 'low')
            review_log[f'{conf}_confidence'] += 1
            metrics.record_review_check(conf)

    _plog.info(
        f'review_complete total={review_log["total_checks"]} '
        f'high={review_log["high_confidence"]} mid={review_log["medium_confidence"]} low={review_log["low_confidence"]}'
    )

    output_path = result_json_path.replace('.json', '_reviewed.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return review_log, output_path
