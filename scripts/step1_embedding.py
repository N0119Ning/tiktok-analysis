import pandas as pd
import numpy as np
import re
import os
import sys
import json
import time
from sentence_transformers import SentenceTransformer

BASE_DIR = 'e:/pycharm_project2/tiktok_project'
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

sys.path.insert(0, os.path.dirname(BASE_DIR))
from tiktok_project.utils.logger import get_logger, log_event
from tiktok_project.utils.metrics import get_metrics

_plog = get_logger('pipeline')

PURE_EMOTION_WORDS = {
    'good', 'nice', 'ok', 'okay', 'great', 'love', 'like', 'best', 'awesome',
    'amazing', 'excellent', 'perfect', 'wonderful', 'fantastic', 'brilliant',
    'super', 'cool', 'fine', 'bad', 'terrible', 'horrible', 'awful', 'worst',
    'hate', 'disgusting', 'stupid', 'idiot', 'ugly', 'boring', 'annoying',
    'lol', 'lmao', 'wow', 'omg', 'haha', 'hehe'
}

PRODUCT_RELATED_WORDS = {
    'app', 'tiktok', 'account', 'video', 'videos', 'login', 'message', 'feed',
    'comment', 'like', 'share', 'follow', 'follow', 'ads', 'ad', 'search',
    'upload', 'download', 'notification', 'profile', 'password', 'email', 'phone',
    'update', 'bug', 'crash', 'lag', 'slow', 'error', 'feature', 'music', 'sound',
    'live', 'stream', 'filter', 'effect', 'duet', 'stitch', 'inbox', 'dm',
    'creator', 'view', 'views', 'algorithm', 'fyp', 'content', 'privacy',
    'security', 'report', 'ban', 'banned', 'delete', 'install', 'uninstall'
}

def clean_text(text):
    text = str(text)
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f900-\U0001f9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002600-\U000026FF"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    text = re.sub(r'[^a-z0-9\s\.\?\!\,\']', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

COMMON_MISSPELLINGS = {
    'tiktok': 'tiktok', 'tik tok': 'tiktok', 'toktok': 'tiktok', 'ticktok': 'tiktok',
    'accout': 'account', 'acount': 'account', 'accont': 'account',
    'lgin': 'login', 'logn': 'login', 'log in': 'login', 'signin': 'sign in',
    'mesage': 'message', 'massge': 'message', 'msg': 'message', 'messege': 'message',
    'vidoe': 'video', 'vedio': 'video', 'vids': 'video', 'vidoe': 'video',
    'notifcation': 'notification', 'notificaton': 'notification', 'notif': 'notification',
    'updat': 'update', 'updte': 'update',
    'probem': 'problem', 'probelm': 'problem', 'issu': 'issue',
    'cant': "can't", 'dont': "don't", 'wont': "won't", 'doesnt': "doesn't",
    'didnt': "didn't", 'wouldnt': "wouldn't", 'shouldnt': "shouldn't",
    'im': "i'm", 'ive': "i've", 'ill': "i'll", 'id': "i'd",
    'thats': "that's", 'whats': "what's", 'its': "it's", 'theyre': "they're",
    'youre': "you're", 'were': "we're", 'hes': "he's", 'shes': "she's",
    'recomend': 'recommend', 'recomendation': 'recommendation', 'reccomend': 'recommend',
    'algoritm': 'algorithm', 'algorithim': 'algorithm',
    'frezzing': 'freezing', 'freezin': 'freezing', 'crsh': 'crash',
    'laag': 'lag', 'lagg': 'lag', 'laggy': 'lag',
    'bugy': 'buggy', 'buggs': 'bugs', 'eror': 'error', 'errror': 'error',
    'pssword': 'password', 'pasword': 'password', 'passward': 'password',
    'uninstal': 'uninstall', 'instal': 'install', 'intall': 'install',
    'pleas': 'please', 'plz': 'please', 'pls': 'please',
    'helpp': 'help', 'halp': 'help',
    'fixx': 'fix', 'fiix': 'fix',
    'openn': 'open', 'oppen': 'open',
    'sendd': 'send', 'recieve': 'receive',
    'pepole': 'people', 'peopl': 'people', 'ppl': 'people',
    'evrytime': 'everytime', 'everytim': 'everytime',
    'becuase': 'because', 'bc': 'because', 'coz': 'because',
    'abt': 'about', 'thng': 'thing', 'thngs': 'things',
}

def spell_correct(text):
    words = text.split()
    corrected = []
    for word in words:
        if word in COMMON_MISSPELLINGS:
            corrected.append(COMMON_MISSPELLINGS[word])
        else:
            corrected.append(word)
    return ' '.join(corrected)

def is_pure_emotion(text):
    words = set(text.lower().split())
    if len(words) <= 2:
        return False
    emotion_words = words & PURE_EMOTION_WORDS
    non_emotion_words = words - PURE_EMOTION_WORDS - {'', 'it', 'is', 'so', 'very', 'really', 'the', 'a', 'an', 'this', 'that', 'i', 'you', 'he', 'she', 'we', 'they', 'and', 'but', 'not'}
    if len(non_emotion_words) <= 1 and len(emotion_words) >= 2:
        return True
    return False

def filter_low_quality(df, min_words=3):
    original_count = len(df)
    df = df.copy()
    df['cleaned'] = df['translated'].apply(clean_text)
    df['cleaned'] = df['cleaned'].apply(spell_correct)

    df['word_count'] = df['cleaned'].apply(lambda x: len(x.split()))

    before_len = len(df)
    df = df[df['word_count'] >= min_words]
    filtered_by_length = before_len - len(df)

    before_emotion = len(df)
    df['is_emotion'] = df['cleaned'].apply(is_pure_emotion)
    df = df[~df['is_emotion']]
    filtered_by_emotion = before_emotion - len(df)

    dropped_count = original_count - len(df)
    print(f"原始数据: {original_count} 条")
    print(f"过滤低质量评论: {dropped_count} 条")
    print(f"  - 长度 < {min_words} 词: {filtered_by_length} 条")
    print(f"  - 纯情绪评论: {filtered_by_emotion} 条")
    print(f"保留数据: {len(df)} 条 ({len(df)/original_count*100:.1f}%)")

    filter_stats = {
        'original_count': original_count,
        'kept_count': len(df),
        'dropped_total': dropped_count,
        'filtered_by_length': filtered_by_length,
        'filtered_by_emotion': filtered_by_emotion,
        'min_words': min_words,
    }
    return df, filter_stats

def main():
    t0 = time.time()
    output_embeddings = f'{BASE_DIR}/outputs/embeddings.npy'
    output_cleaned = f'{BASE_DIR}/outputs/cleaned_data.csv'

    # 支持新数据格式（TikTok.csv）和旧格式（tiktok_keywords_final.csv）
    input_file_new = f'{BASE_DIR}/data/TikTok.csv'
    input_file_old = f'{BASE_DIR}/data/tiktok_keywords_final.csv'

    # 优先使用新数据
    if os.path.exists(input_file_new):
        input_file = input_file_new
        print(f"[Step 1] Loading new data from {input_file}...")
        df = pd.read_csv(input_file)

        # 新数据列名映射：content -> translated
        if 'content' in df.columns and 'translated' not in df.columns:
            df = df.rename(columns={'content': 'translated'})
    else:
        input_file = input_file_old
        print(f"[Step 1] Loading old data from {input_file}...")
        df = pd.read_csv(input_file)

    orig_rows = len(df)
    print(f"原始数据: {orig_rows} 条")

    print("\n[Step 2] Cleaning and filtering text...")
    clean_t0 = time.time()
    df, filter_stats = filter_low_quality(df, min_words=2)
    clean_elapsed = (time.time() - clean_t0) * 1000

    filter_stats_path = f'{BASE_DIR}/outputs/filter_stats.json'
    with open(filter_stats_path, 'w', encoding='utf-8') as f:
        json.dump(filter_stats, f, ensure_ascii=False, indent=2)
    print(f"\nFilter stats saved to {filter_stats_path}")

    df.to_csv(output_cleaned, index=False)
    print(f"\nCleaned data saved to {output_cleaned}")

    print("\n[Step 3] Generating embeddings...")
    emb_t0 = time.time()
    texts = df['cleaned'].tolist()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts)
    emb_elapsed = (time.time() - emb_t0) * 1000

    np.save(output_embeddings, embeddings)
    print(f"\nEmbeddings saved to {output_embeddings}")
    print(f"Shape: {embeddings.shape}")

    total_elapsed = (time.time() - t0) * 1000
    _plog.info(
        f'step1_detail rows_in={orig_rows} rows_out={len(df)} '
        f'clean_ms={clean_elapsed:.0f} embed_ms={emb_elapsed:.0f} total_ms={total_elapsed:.0f}'
    )

if __name__ == '__main__':
    main()
