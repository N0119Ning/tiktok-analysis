import pandas as pd
import re
import os
import time

from utils.logger import get_logger
from utils.metrics import get_metrics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_log = get_logger('app')
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


def inspect_csv(filepath):
    """检查 CSV 文件，返回数据摘要"""
    t0 = time.time()
    df = pd.read_csv(filepath)

    info = {
        'filepath': filepath,
        'total_rows': len(df),
        'columns': list(df.columns),
        'column_count': len(df.columns),
        'sample_rows': 3,
        'samples': df.head(3).to_dict(orient='records'),
        'missing_values': {},
        'language': 'unknown',
        'text_column': None,
        'score_column': None,
    }

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            info['missing_values'][col] = null_count

    text_col, lang = _detect_text_column(df)
    info['text_column'] = text_col
    info['language'] = lang

    score_col = _detect_score_column(df)
    info['score_column'] = score_col

    if text_col:
        sample_texts = df[text_col].dropna().head(20).tolist()
        info['text_samples'] = [str(t)[:100] for t in sample_texts]

    return info


def _detect_text_column(df):
    """自动检测文本列 + 语言"""
    candidates = []
    id_patterns = ['id', 'key', 'uuid', 'row', 'index', 'number', 'code', 'date', 'time']

    for col in df.columns:
        col_lower = col.lower()

        # 跳过明显是 ID/编码类的列
        if any(p in col_lower for p in id_patterns) and ('review' not in col_lower.split('_')[0] if '_' in col_lower else True):
            if col_lower.endswith('id') or col_lower.endswith('key'):
                continue

        if any(kw in col_lower for kw in ['content', 'comment', 'text', 'translated', 'cleaned', 'review']):
            if col_lower in ('reviewid', 'review_id', 'commentid', 'comment_id'):
                continue
            candidates.append((col, 10))
        elif any(kw in col_lower for kw in ['message', 'description', 'feedback', 'body']):
            candidates.append((col, 5))

    if not candidates:
        for col in df.columns:
            if df[col].dtype == object:
                avg_len = df[col].dropna().apply(lambda x: len(str(x))).mean()
                if avg_len > 20:  # 提高阈值，避免短 ID 串误判
                    candidates.append((col, 3))

    if not candidates:
        return (df.columns[0], 'unknown')

    text_col = sorted(candidates, key=lambda x: x[1], reverse=True)[0][0]
    samples = df[text_col].dropna().head(50).apply(lambda x: str(x)[:200]).tolist()
    lang = _detect_language(samples)

    return (text_col, lang)


def _detect_language(texts):
    """检测语言：chinese / english / mixed"""
    cn_count = 0
    en_count = 0
    for t in texts:
        cn_chars = len(re.findall(r'[一-鿿]', t))
        en_words = len(re.findall(r'[a-zA-Z]+', t))
        if cn_chars > en_words:
            cn_count += 1
        elif en_words > cn_chars:
            en_count += 1

    if cn_count > len(texts) * 0.3:
        return 'chinese'
    elif en_count > len(texts) * 0.3:
        return 'english'
    return 'mixed'


def _detect_score_column(df):
    """检测评分列"""
    for col in df.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in ['score', 'rating', 'star', '评分']):
            return col
    return None


def build_plan(info):
    """基于数据检查结果，构建分析计划"""
    plan = {
        'text_column': info['text_column'],
        'score_column': info['score_column'],
        'language': info['language'],
        'total_rows': info['total_rows'],
        'parameters': {},
        'strategy': [],
        'risks': [],
    }

    total = info['total_rows']

    if total < 100:
        plan['parameters']['n_clusters'] = 3
        plan['risks'].append('数据量较小(<100条)，聚类结果可能不够稳定')
    elif total < 500:
        plan['parameters']['n_clusters'] = 5
    elif total < 2000:
        plan['parameters']['n_clusters'] = 6
    else:
        plan['parameters']['n_clusters'] = 8

    lang = info['language']
    if lang == 'chinese':
        plan['parameters']['cleaning'] = 'chinese_standard'
        plan['strategy'].append('使用中文停用词 + 中文分词适配')
        plan['strategy'].append('Category 分类使用中文关键词')
    elif lang == 'english':
        plan['parameters']['cleaning'] = 'english_standard'
        plan['strategy'].append('使用英文停用词 + 拼写纠正')
        plan['strategy'].append('Category 分类使用英文关键词')
    else:
        plan['parameters']['cleaning'] = 'mixed'
        plan['strategy'].append('混合语言模式，中英文分别处理')

    if info['score_column']:
        plan['strategy'].append(f'检测到评分列: {info["score_column"]}，将启用评分加权严重度分析')
    else:
        plan['strategy'].append('未检测到评分列，将仅基于评论数量判断严重度')

    missing_cols = [k for k, v in info['missing_values'].items() if v > info['total_rows'] * 0.5]
    if missing_cols:
        plan['risks'].append(f'列 {missing_cols} 缺失值超过50%，将在清洗中自动排除')

    return plan


def explain_plan(plan):
    """生成人类可读的计划说明"""
    lines = [
        f"## 分析计划",
        f"",
        f"- **数据规模**: {plan['total_rows']} 条评论",
        f"- **语言**: {plan['language']}",
        f"- **文本列**: `{plan['text_column']}`",
        f"- **评分列**: {'`' + plan['score_column'] + '`' if plan['score_column'] else '无'}",
        f"- **建议聚类数**: {plan['parameters']['n_clusters']}",
        f"- **清洗策略**: {plan['parameters']['cleaning']}",
        f"",
        f"### 分析步骤",
    ]
    for i, s in enumerate(plan['strategy'], 1):
        lines.append(f"{i}. {s}")

    if plan['risks']:
        lines.append(f"")
        lines.append(f"### [!] 注意事项")
        for r in plan['risks']:
            lines.append(f"- {r}")

    return '\n'.join(lines)


def agent_plan(filepath):
    """Agent Plan 主入口：检查数据 → 构建计划 → 返回"""
    t0 = time.time()
    info = inspect_csv(filepath)
    plan = build_plan(info)
    explanation = explain_plan(plan)
    elapsed = (time.time() - t0) * 1000

    _log.info(
        f'Plan generated: {info["total_rows"]} rows, lang={info["language"]}, '
        f'text_col={info["text_column"]}, score_col={info["score_column"]}, '
        f'clusters={plan["parameters"]["n_clusters"]}'
    )
    _plog.info(f'plan_generation elapsed={elapsed:.0f}ms rows={info["total_rows"]}')
    get_metrics().record_plan_generated()
    return plan, explanation, info
