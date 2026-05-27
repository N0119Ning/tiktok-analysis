import os
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import numpy as np
import json
import os
import time
import re
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from keybert import KeyBERT
    HAS_KEYBERT = True
except ImportError:
    HAS_KEYBERT = False

BASE_DIR = 'e:/pycharm_project2/tiktok_project'

sys.path.insert(0, os.path.dirname(BASE_DIR))
from tiktok_project.utils.logger import get_logger
from tiktok_project.utils.metrics import get_metrics

_plog = get_logger('pipeline')
_llog = get_logger('llm')

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

# Category 定义
CATEGORIES = {
    "account": {
        "label": "登录/账号问题", 
        "keywords": ['account', 'login', 'sign in', 'password', 'email', 'phone', 'banned',
                     'ban', 'blocked', 'verify', 'verification', 'unlock', 'disabled',
                     'deleted', 'deactivate', 'recover', 'access', 'username', 'id',
                     'profile', 'message', 'dm', 'inbox', 'send', 'receive']
    },
    "content": {
        "label": "内容推荐问题", 
        "keywords": ['feed', 'fyp', 'recommend', 'algorithm', 'content', 'video',
                     'trending', 'discover', 'explore', 'search', 'interest',
                     'relevance', 'relevant', 'irrelevant', 'show', 'shown',
                     'for you', 'foru', 'page']
    },
    "video": {
        "label": "视频播放问题", 
        "keywords": ['video', 'videos', 'play', 'playing', 'watch', 'watching',
                     'stream', 'streaming', 'loading', 'buffer', 'buffering',
                     'quality', 'resolution', 'freeze', 'frozen', 'black screen',
                     'sound', 'audio', 'mute', 'volume', 'crash', 'crashing']
    },
    "ads": {
        "label": "广告问题", 
        "keywords": ['ad', 'ads', 'advertisement', 'advertising', 'spam', 'promoted',
                     'commercial', 'pop up', 'popup', 'too many', 'every', 'skip',
                     'unskippable', 'interrupt']
    },
    "feature": {
        "label": "功能异常", 
        "keywords": ['feature', 'function', 'tool', 'edit', 'create', 'duet', 'stitch',
                     'filter', 'effect', 'sticker', 'music', 'sound', 'share',
                     'download', 'upload', 'save', 'draft', 'live', 'broadcast',
                     'remove', 'add', 'missing', 'cant', "can't"]
    },
    "performance": {
        "label": "性能问题", 
        "keywords": ['slow', 'lag', 'lagging', 'laggy', 'freeze', 'freezing',
                     'hang', 'hanging', 'stuck', 'crash', 'crashing', 'slowdown',
                     'performance', 'battery', 'memory', 'storage', 'ram',
                     'cpu', 'heat', 'hot', 'warm']
    },
    "privacy": {
        "label": "隐私安全", 
        "keywords": ['privacy', 'security', 'data', 'personal', 'information',
                     'tracking', 'tracked', 'collect', 'collected', 'permission',
                     'access', 'safe', 'unsafe', 'leak', 'leaked', 'stolen',
                     'hack', 'hacked', 'scam']
    },
    "social": {
        "label": "社交互动", 
        "keywords": ['follow', 'follower', 'following', 'like', 'comment', 'share',
                     'message', 'chat', 'dm', 'friend', 'reply', 'mention', 'tag',
                     'notification', 'like', 'heart']
    },
    "ui": {
        "label": "界面体验", 
        "keywords": ['interface', 'design', 'layout', 'button', 'menu', 'screen',
                     'color', 'font', 'text', 'display', 'ui', 'ux', 'navigation',
                     'navigate', 'tab', 'icon', 'theme', 'dark mode', 'light mode']
    },
    "other": {
        "label": "其他问题", 
    }
}

# KeyBERT 模型初始化
kw_model = None
if HAS_KEYBERT:
    try:
        kw_model = KeyBERT()
        print("[OK] KeyBERT model loaded successfully")
    except Exception as e:
        print(f"[Warning] KeyBERT failed to load: {e}")
        HAS_KEYBERT = False

def extract_keywords_with_keybert(texts, top_n=5):
    """使用增强版 TF-IDF 提取短语级关键词（KeyBERT 在当前环境有兼容性问题）"""
    return extract_keywords_with_tfidf(texts, top_n)

def extract_keywords_with_tfidf(texts, top_n=5):
    """TF-IDF 备选方案"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    try:
        # 根据评论数量动态调整 min_df
        if len(texts) >= 10:
            min_df = 2
        elif len(texts) >= 5:
            min_df = 2
        else:
            min_df = 1  # 少量评论时降低阈值
        
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=min_df,
            max_df=0.95,
            max_features=100
        )
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = np.sum(tfidf_matrix.toarray(), axis=0)
        keyword_scores = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names))]
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        noise_words = {
            'tiktok', 'tik', 'tok', 'app', 'don', 'make', 'need', 'want',
            'get', 'got', 'try', 'use', 'used', 'using', 'one', 'two',
            'thing', 'things', 'stuff', 'something', 'everything', 'nothing',
            'really', 'very', 'much', 'way', 'also', 'just', 'still', 'even',
            'good', 'bad', 'love', 'like', 'best', 'great', 'nice', 'awesome',
            'can', "can't", 'cant', "don't", "dont", 'wont', "won't",
            'will', 'would', 'could', 'should', 'does', "doesn", 'did',
            'has', 'have', 'had', 'being', 'been', 'is', 'are', 'was',
            'they', 'them', 'their', 'this', 'that', 'these', 'those',
            'people', 'user', 'users', 'video', 'videos', 'time', 'times'
        }
        
        filtered = []
        for phrase, score in keyword_scores:
            phrase_lower = phrase.lower().strip()
            if len(phrase_lower) < 3:
                continue
            if phrase_lower in noise_words:
                continue
            filtered.append((phrase_lower, score))
        
        return filtered[:top_n]
    except Exception as e:
        print(f"  [Fallback] TF-IDF failed: {e}")
        return [('issue identified', 1.0)]

def classify_category(text):
    """使用关键词匹配为单条评论分配 Category"""
    text_lower = text.lower()
    
    category_scores = {cat: 0 for cat in CATEGORIES.keys()}
    
    for cat, cat_info in CATEGORIES.items():
        if cat == 'other':
            continue
        for keyword in cat_info['keywords']:
            if keyword in text_lower:
                category_scores[cat] += 1
    
    max_score = max(category_scores.values())
    if max_score == 0:
        return 'other'
    
    best_category = max(category_scores, key=category_scores.get)
    return best_category

def calculate_severity(avg_score, comment_count, total_count):
    """计算严重程度"""
    frequency = comment_count / total_count
    if avg_score < 2:
        score_weight = 3
    elif avg_score < 2.5:
        score_weight = 2
    elif avg_score < 3:
        score_weight = 1
    else:
        score_weight = 0
    
    severity_score = score_weight * frequency * 100
    if severity_score > 15 or avg_score < 2:
        return 'critical'
    elif severity_score > 8 or avg_score < 2.5:
        return 'high'
    elif severity_score > 3 or avg_score < 3:
        return 'medium'
    else:
        return 'low'

POSITIVE_WORDS = {
    'good', 'great', 'love', 'like', 'best', 'awesome', 'amazing', 'perfect',
    'wonderful', 'fantastic', 'nice', 'excellent', 'cool', 'super', 'brilliant',
    'enjoy', 'happy', 'fun', 'beautiful', 'incredible', 'impressive',
    'recommend', 'favorite', 'addictive', 'smooth', 'fast', 'easy'
}

NEGATIVE_WORDS = {
    'bad', 'terrible', 'horrible', 'awful', 'worst', 'hate', 'disgusting',
    'stupid', 'idiot', 'ugly', 'boring', 'annoying', 'frustrating',
    'crash', 'crashing', 'freeze', 'freezing', 'lag', 'lagging', 'slow',
    'bug', 'buggy', 'error', 'broken', 'fail', 'failed', 'issue', 'problem',
    'ban', 'banned', 'blocked', 'delete', 'removed', 'lost', 'cant',
    "can't", 'wont', 'wont', 'dont', 'doesnt', 'not working', 'useless',
    'waste', 'unacceptable', 'disappointing', 'overload', 'spam', 'ads'
}

def analyze_sentiment(text, score=None):
    """分析单条评论的情绪"""
    text_lower = text.lower()
    words = set(text_lower.split())
    
    pos_count = len(words & POSITIVE_WORDS)
    neg_count = len(words & NEGATIVE_WORDS)
    
    if score is not None:
        if score <= 2:
            base_sentiment = 'negative'
            base_confidence = 0.7 + (2 - score) * 0.15
        elif score >= 4:
            base_sentiment = 'positive'
            base_confidence = 0.6 + (score - 4) * 0.15
        else:
            base_sentiment = 'neutral'
            base_confidence = 0.5
        
        if pos_count > neg_count + 2:
            return 'positive', min(base_confidence + 0.2, 0.95)
        elif neg_count > pos_count + 2:
            return 'negative', min(base_confidence + 0.2, 0.95)
        else:
            return base_sentiment, base_confidence
    else:
        if pos_count > neg_count + 1:
            return 'positive', 0.65
        elif neg_count > pos_count + 1:
            return 'negative', 0.65
        else:
            return 'neutral', 0.5

def calculate_sentiment_stats(comments_with_scores):
    """计算一组评论的情绪分布统计"""
    sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for comment, score in comments_with_scores:
        sentiment, _ = analyze_sentiment(comment, score)
        sentiments[sentiment] += 1
    
    total = sum(sentiments.values())
    if total == 0:
        return {'positive': 0, 'negative': 0, 'neutral': 0, 'dominant': 'neutral', 'negativity_rate': 0}
    
    negativity_rate = round(sentiments['negative'] / total * 100, 1)
    dominant = max(sentiments, key=sentiments.get)
    
    return {
        'positive': sentiments['positive'],
        'negative': sentiments['negative'],
        'neutral': sentiments['neutral'],
        'total': total,
        'positive_pct': round(sentiments['positive'] / total * 100, 1),
        'negative_pct': round(sentiments['negative'] / total * 100, 1),
        'neutral_pct': round(sentiments['neutral'] / total * 100, 1),
        'dominant': dominant,
        'negativity_rate': negativity_rate
    }

def generate_complete_analysis_with_llm(comments_text, keywords, max_retries=2):
    """使用 LLM 动态生成完整的分析（问题/场景/影响/短期方案/长期方案/指标）"""
    if not HAS_OPENAI:
        return generate_analysis_with_template(comments_text, keywords)
    
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)
    metrics = get_metrics()

    sample_comments = comments_text[:800]

    prompt = f"""重要：你必须用中文输出所有内容，即使下面的评论是英文也必须用中文回答。

你正在分析 TikTok 用户反馈。请根据以下评论生成结构化分析。

关键词: {', '.join(keywords[:10])}

评论样本:
{sample_comments}

输出格式（必须严格遵守，每项不超过50字）:
【问题本质】：[明确的问题陈述，必须包含产品对象和用户行为]
【用户场景】：[问题发生时的典型用户场景]
【影响】：[影响范围和严重程度，尽量量化]
【短期方案】：[可立即执行的修复措施]
【长期方案】：[系统性的长期解决方案]
【指标】：[2-3个可量化的成功指标]

规则:
- 必须基于具体评论，不得泛泛而谈
- 必须包含具体产品对象（如APP/账号/视频/算法等）
- 必须包含具体用户行为（如登录/观看/滑动等）
- 禁止使用空洞词汇（如"优化""提升""改善"，除非附带具体上下文）
- 指标必须量化（如"登录成功率提升至95%"）
"""
    
    for attempt in range(max_retries):
        t0 = time.time()
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一名资深产品经理。无论输入是什么语言，所有分析输出必须使用简体中文。分析要具体、有数据支撑。"},
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
            _llog.info(f'step3_analysis attempt={attempt+1} elapsed={elapsed:.0f}ms tokens_in={tokens_in} tokens_out={tokens_out}')
            metrics.record_llm_call('analysis', elapsed, tokens_in, tokens_out)

            content = response.choices[0].message.content.strip()
            
            # 解析输出
            result = {
                'problem': '',
                'scene': '',
                'impact': '',
                'short_term': '',
                'long_term': '',
                'metrics': []
            }
            
            for line in content.split('\n'):
                line = line.strip()
                if '【问题本质】' in line or line.startswith('问题本质'):
                    result['problem'] = line.split('】', 1)[-1].split('：', 1)[-1].strip()
                elif '【用户场景】' in line or line.startswith('用户场景'):
                    result['scene'] = line.split('】', 1)[-1].split('：', 1)[-1].strip()
                elif '【影响】' in line or line.startswith('影响'):
                    result['impact'] = line.split('】', 1)[-1].split('：', 1)[-1].strip()
                elif '【短期方案】' in line or line.startswith('短期方案'):
                    result['short_term'] = line.split('】', 1)[-1].split('：', 1)[-1].strip()
                elif '【长期方案】' in line or line.startswith('长期方案'):
                    result['long_term'] = line.split('】', 1)[-1].split('：', 1)[-1].strip()
                elif '【指标】' in line or line.startswith('指标'):
                    metrics_text = line.split('】', 1)[-1].split('：', 1)[-1].strip()
                    result['metrics'] = [m.strip() for m in metrics_text.replace('，', ',').split(',') if m.strip()]
            
            # 验证必填字段
            if result['problem'] and result['short_term']:
                return result
            elif result['problem']:
                # 部分成功也返回
                return result
            
        except Exception as e:
            elapsed = (time.time() - t0) * 1000
            print(f"  LLM call attempt {attempt+1} failed: {e}")
            _llog.error(f'step3_analysis FAILED attempt={attempt+1} elapsed={elapsed:.0f}ms exc={str(e)[:100]}')
            metrics.record_llm_call('analysis', elapsed, error=True)
            if attempt < max_retries - 1:
                time.sleep(2)

    return generate_analysis_with_template(comments_text, keywords)

def generate_analysis_with_template(comments_text, keywords):
    """模板备选方案"""
    # 基于关键词生成简单的模板分析
    keywords_text = ', '.join(keywords[:5])
    
    return {
        'problem': f'用户反馈中存在以下问题：{keywords_text}',
        'scene': '用户在日常使用中遇到相关功能异常',
        'impact': '影响用户体验，可能导致满意度下降',
        'short_term': '排查问题根因，修复已知异常',
        'long_term': '建立完善的监控和反馈机制',
        'metrics': ['相关投诉减少30%', '用户满意度提升10%']
    }

def split_subproblems_with_llm(comments_list, category, max_retries=2):
    """使用 LLM 在 Category 内部自动拆分子问题"""
    if not HAS_OPENAI:
        return [{'name': f'{category}问题', 'comments': comments_list}]

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)
    metrics = get_metrics()
    
    sample_comments = '\n'.join(comments_list[:30])
    
    prompt = f"""你正在分析TikTok用户反馈，类别: {category}。
阅读以下评论，识别出不同的子问题。将相似抱怨归组。

评论:
{sample_comments}

输出格式（只输出编号列表，不要其他内容，必须用中文命名）:
1. 子问题名: [简短描述]
2. 子问题名: [简短描述]

规则:
- 最多3个子问题
- 名称应具体可操作，使用中文
- 只返回编号列表，不要其他内容
"""
    
    for attempt in range(max_retries):
        t0 = time.time()
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是产品经理。无论输入是什么语言，子问题名称必须用中文输出。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=150,
                timeout=20
            )

            elapsed = (time.time() - t0) * 1000
            usage = response.usage
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0
            _llog.info(f'step3_split elapsed={elapsed:.0f}ms tokens_in={tokens_in} tokens_out={tokens_out}')
            metrics.record_llm_call('split_subproblems', elapsed, tokens_in, tokens_out)

            content = response.choices[0].message.content.strip()
            
            # 解析子问题名称
            subproblem_names = []
            for line in content.split('\n'):
                line = line.strip()
                if line and ('.' in line or '、' in line):
                    # 提取名称部分
                    name = line.split('.')[0].strip() if '.' in line else line.split('、')[0].strip()
                    # 清理序号
                    name = re.sub(r'^\d+\s*', '', name)
                    if name and len(name) > 2:
                        subproblem_names.append(name)
            
            if not subproblem_names:
                return [{'name': f'{category}_general', 'comments': comments_list}]
            
            # 将评论分配到子问题（基于关键词匹配）
            subproblems = []
            for sp_name in subproblem_names[:3]:  # 最多3个子问题
                # 简单的关键词匹配
                sp_keywords = sp_name.lower().split()
                matched_comments = []
                unmatched_comments = []
                
                for comment in comments_list:
                    comment_lower = comment.lower()
                    if any(kw in comment_lower for kw in sp_keywords if len(kw) > 2):
                        matched_comments.append(comment)
                    else:
                        unmatched_comments.append(comment)
                
                if matched_comments:
                    subproblems.append({
                        'name': sp_name,
                        'comments': matched_comments
                    })
                
                comments_list = unmatched_comments
            
            # 剩余评论归入通用子问题
            if comments_list:
                subproblems.append({
                    'name': f'{category}_general',
                    'comments': comments_list
                })
            
            return subproblems
            
        except Exception as e:
            elapsed = (time.time() - t0) * 1000
            print(f"  LLM subproblem split attempt {attempt+1} failed: {e}")
            _llog.error(f'step3_split FAILED attempt={attempt+1} elapsed={elapsed:.0f}ms exc={str(e)[:100]}')
            metrics.record_llm_call('split_subproblems', elapsed, error=True)
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return [{'name': f'{category}_general', 'comments': comments_list}]

def select_representative_comments(comments, keywords, top_n=3):
    """选择最能代表该问题的典型评论"""
    if not comments:
        return []
    
    # 评分函数：问题相关度越高、内容越丰富、负面程度越高，得分越高
    def score_comment(comment):
        score = 0
        comment_lower = comment.lower()
        
        # 1. 关键词匹配度（包含多少子问题关键词）
        for kw in keywords:
            if kw.lower() in comment_lower:
                score += 10
        
        # 2. 问题表达词（负面评论更典型）
        problem_words = ['not', "n't", 'no', 'cant', 'wont', 'dont', 'doesnt', 'didnt',
                        'failed', 'failure', 'error', 'bug', 'crash', 'broken', 'issue',
                        'problem', 'wrong', 'terrible', 'horrible', 'awful', 'worst',
                        'hate', 'worse', 'bad', 'poor', 'useless', 'waste', 'annoying',
                        'frustrating', 'disappointing', 'unacceptable', 'fix', 'please', 'help']
        for w in problem_words:
            if w in comment_lower:
                score += 5
        
        # 3. 惩罚正面评论（好评论不适合作为问题典型）
        positive_words = ['good', 'great', 'love', 'awesome', 'amazing', 'perfect',
                         'wonderful', 'fantastic', 'nice', 'best', 'excellent', 'cool']
        for w in positive_words:
            if w in comment_lower:
                score -= 15
        
        # 4. 长度权重（太短的信息量不足）
        word_count = len(comment.split())
        if word_count >= 5:
            score += 3
        elif word_count >= 10:
            score += 5
        
        # 5. 包含具体行为/场景的描述更典型
        action_words = ['when', 'after', 'before', 'while', 'trying', 'attempt', 'open', 'use', 'click', 'tap', 'try']
        for w in action_words:
            if w in comment_lower:
                score += 2
        
        return score
    
    # 排序并选 top_n
    scored_comments = [(c, score_comment(c)) for c in comments]
    scored_comments.sort(key=lambda x: x[1], reverse=True)
    
    # 只选得分>0的评论（至少有一定问题相关性）
    top_comments = [c for c, score in scored_comments if score > 0][:top_n]
    
    # 如果得分>0的不够，补充原始评论
    if len(top_comments) < top_n:
        for c, score in scored_comments:
            if c not in top_comments:
                top_comments.append(c)
                if len(top_comments) >= top_n:
                    break
    
    return top_comments[:top_n]

def main():
    t0 = time.time()
    input_file = f'{BASE_DIR}/outputs/cleaned_data.csv'
    output_file = f'{BASE_DIR}/outputs/result.json'

    df = pd.read_csv(input_file)
    total_count = len(df)
    
    print(f"\n{'='*60}")
    print(f"[Step 1] Classifying comments by Category...")
    print(f"{'='*60}")
    
    # Step 1: 为每条评论分配 Category
    df['category'] = df['cleaned'].apply(lambda x: classify_category(x))
    
    # 统计 Category 分布
    category_counts = df['category'].value_counts()
    print(f"\nCategory distribution:")
    for cat, count in category_counts.items():
        cat_info = CATEGORIES.get(cat, CATEGORIES['other'])
        print(f"  {cat_info['label']}: {count} comments")
    
    print(f"\n{'='*60}")
    print(f"[Step 2] Splitting sub-problems within each Category...")
    print(f"{'='*60}")
    
    # Step 2: 对每个 Category 拆分子问题
    category_results = {}
    
    for category in sorted(df['category'].unique()):
        if category == 'other':
            continue
        
        cat_data = df[df['category'] == category]
        cat_comments = cat_data['cleaned'].tolist()
        cat_avg_score = round(cat_data['score'].mean(), 2)
        cat_count = len(cat_comments)
        
        print(f"\n  Processing {category} ({cat_count} comments)...")
        
        # 拆分子问题
        subproblems = split_subproblems_with_llm(cat_comments, category)
        
        category_results[category] = {
            'category': category,
            'category_label': CATEGORIES[category]['label'],
            'total_comments': cat_count,
            'avg_score': cat_avg_score,
            'percentage': round(cat_count / total_count * 100, 1),
            'severity': calculate_severity(cat_avg_score, cat_count, total_count),
            'subproblems': subproblems
        }
    
    print(f"\n{'='*60}")
    print(f"[Step 3] Generating analysis for each sub-problem with LLM...")
    print(f"{'='*60}")
    
    # Step 3: 为每个子问题生成完整分析
    final_results = {
        'categories': {},
        'total_comments': total_count,
        'overall_avg_score': round(df['score'].mean(), 2),
        'category_count': len(category_results),
        'dashboard_data': {
            'category_distribution': [],
            'severity_ranking': []
        }
    }
    
    for category, cat_info in category_results.items():
        print(f"\n  Analyzing {category}...")
        
        category_output = {
            'category_label': cat_info['category_label'],
            'total_comments': cat_info['total_comments'],
            'avg_score': cat_info['avg_score'],
            'percentage': cat_info['percentage'],
            'severity': cat_info['severity'],
            'subproblems': []
        }
        
        for sp in cat_info['subproblems']:
            sp_name = sp['name']
            sp_comments = sp['comments']
            sp_count = len(sp_comments)
            
            if sp_count < 2:
                continue
            
            print(f"    Sub-problem: {sp_name} ({sp_count} comments)")
            
            # 提取关键词
            keywords = extract_keywords_with_keybert(sp_comments, top_n=5)
            keyword_list = [kw for kw, score in keywords]
            
            print(f"    Keywords: {keyword_list}")
            
            # 生成完整分析
            sp_avg_score = round(np.mean([
                df[df['cleaned'] == c]['score'].values[0] 
                for c in sp_comments 
                if c in df['cleaned'].values
            ]), 2) if sp_comments else cat_info['avg_score']
            
            analysis = generate_complete_analysis_with_llm(
                ' '.join(sp_comments),
                keyword_list
            )
            
            # 典型评论（智能选择）
            representative_comments = select_representative_comments(sp_comments, keyword_list)
            
            # 情绪分析
            comments_with_scores = []
            for c in sp_comments:
                matching = df[df['cleaned'] == c]
                if len(matching) > 0:
                    score_val = matching['score'].values[0]
                    if not pd.isna(score_val):
                        comments_with_scores.append((c, score_val))
            sentiment_stats = calculate_sentiment_stats(comments_with_scores)
            
            category_output['subproblems'].append({
                'name': sp_name,
                'comment_count': sp_count,
                'keywords': keyword_list,
                'problem': analysis.get('problem', ''),
                'scene': analysis.get('scene', ''),
                'impact': analysis.get('impact', ''),
                'short_term': analysis.get('short_term', ''),
                'long_term': analysis.get('long_term', ''),
                'metrics': analysis.get('metrics', []),
                'representative_comments': representative_comments,
                'sentiment': sentiment_stats
            })
        
        if category_output['subproblems']:
            final_results['categories'][category] = category_output
            
            # Dashboard 数据
            final_results['dashboard_data']['category_distribution'].append({
                'category': category,
                'label': cat_info['category_label'],
                'count': cat_info['total_comments'],
                'percentage': cat_info['percentage'],
                'severity': cat_info['severity']
            })
    
    # 按严重程度排序
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    final_results['dashboard_data']['severity_ranking'] = sorted(
        final_results['dashboard_data']['category_distribution'],
        key=lambda x: severity_order.get(x['severity'], 4)
    )
    
    # 全局情绪统计
    all_comments_with_scores = [(row['cleaned'], row['score']) for _, row in df.iterrows() if not pd.isna(row.get('score'))]
    overall_sentiment = calculate_sentiment_stats(all_comments_with_scores)
    final_results['dashboard_data']['overall_sentiment'] = overall_sentiment
    
    print(f"\n{'='*60}")
    print(f"[Sentiment Analysis] Overall sentiment distribution:")
    print(f"  Positive: {overall_sentiment['positive_pct']}% | Negative: {overall_sentiment['negative_pct']}% | Neutral: {overall_sentiment['neutral_pct']}%")
    print(f"  Dominant: {overall_sentiment['dominant']} | Negativity Rate: {overall_sentiment['negativity_rate']}%")
    print(f"{'='*60}")
    
    # 保存结果
    print(f"\n{'='*60}")
    print(f"[Step 4] Saving results...")
    print(f"{'='*60}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {output_file}")
    print(f"\n{'='*60}")
    print(f"Total comments: {total_count}")
    print(f"Overall avg score: {final_results['overall_avg_score']}")
    print(f"Number of categories: {final_results['category_count']}")
    print(f"{'='*60}")
    
    # 打印摘要
    for cat_id, cat_data in final_results['categories'].items():
        print(f"\n{cat_data['category_label']}:")
        print(f"  Severity: {cat_data['severity']} | Comments: {cat_data['total_comments']} ({cat_data['percentage']}%)")
        for sp in cat_data['subproblems']:
            print(f"  └─ {sp['name']} ({sp['comment_count']} comments)")
            print(f"     Problem: {sp['problem']}")
            print(f"     Keywords: {sp['keywords']}")

    total_elapsed = (time.time() - t0) * 1000
    _plog.info(f'step3_detail categories={len(final_results["categories"])} total_ms={total_elapsed:.0f}')

if __name__ == '__main__':
    main()
