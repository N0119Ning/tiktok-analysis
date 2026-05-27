"""指标收集模块 — 单例 Collector，线程安全."""

import json
import os
import threading
import time
from datetime import datetime, timezone, timedelta

TZ_BEIJING = timezone(timedelta(hours=8))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

_metrics = None
_lock = threading.Lock()


def _now_iso():
    return datetime.now(TZ_BEIJING).isoformat(timespec='milliseconds')


class MetricsCollector:
    """线程安全的指标收集器."""

    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self._data = {
                'session_start': _now_iso(),
                'pipeline': {
                    'runs': 0,
                    'step1_count': 0,
                    'step1_total_ms': 0.0,
                    'step3_count': 0,
                    'step3_total_ms': 0.0,
                    'total_items_processed': 0,
                    'total_items_filtered': 0,
                },
                'llm': {
                    'total_calls': 0,
                    'total_tokens_in': 0,
                    'total_tokens_out': 0,
                    'total_latency_ms': 0.0,
                    'errors': 0,
                    'by_purpose': {},
                },
                'review': {
                    'total_checks': 0,
                    'confidence': {'high': 0, 'medium': 0, 'low': 0},
                    'retry_rounds': 0,
                    'retry_items_fixed': 0,
                },
                'app': {
                    'uploads': 0,
                    'plans_generated': 0,
                    'pipelines_run': 0,
                    'chat_questions': 0,
                    'errors': 0,
                },
            }

    # ---------- pipeline ----------

    def record_step(self, step_name, elapsed_ms, items_in=0, items_out=0):
        with self._lock:
            d = self._data['pipeline']
            d[f'{step_name}_count'] += 1
            d[f'{step_name}_total_ms'] += elapsed_ms
            d['total_items_processed'] += items_in
            d['total_items_filtered'] += (items_in - items_out)

    def record_pipeline_run(self):
        with self._lock:
            self._data['pipeline']['runs'] += 1

    # ---------- llm ----------

    def record_llm_call(self, purpose, latency_ms, tokens_in=0, tokens_out=0, error=False):
        with self._lock:
            d = self._data['llm']
            d['total_calls'] += 1
            d['total_tokens_in'] += tokens_in
            d['total_tokens_out'] += tokens_out
            d['total_latency_ms'] += latency_ms
            if error:
                d['errors'] += 1
            bp = d['by_purpose']
            if purpose not in bp:
                bp[purpose] = {'calls': 0, 'total_latency_ms': 0.0, 'errors': 0}
            bp[purpose]['calls'] += 1
            bp[purpose]['total_latency_ms'] += latency_ms
            if error:
                bp[purpose]['errors'] += 1

    # ---------- review ----------

    def record_review_check(self, confidence):
        if confidence in ('high', 'medium', 'low'):
            with self._lock:
                d = self._data['review']
                d['total_checks'] += 1
                d['confidence'][confidence] += 1

    def record_retry_round(self, items_fixed):
        with self._lock:
            d = self._data['review']
            d['retry_rounds'] += 1
            d['retry_items_fixed'] += items_fixed

    # ---------- app ----------

    def record_upload(self):
        with self._lock:
            self._data['app']['uploads'] += 1

    def record_plan_generated(self):
        with self._lock:
            self._data['app']['plans_generated'] += 1

    def record_pipeline_complete(self):
        with self._lock:
            self._data['app']['pipelines_run'] += 1

    def record_chat_question(self):
        with self._lock:
            self._data['app']['chat_questions'] += 1

    def record_error(self):
        with self._lock:
            self._data['app']['errors'] += 1

    # ---------- export ----------

    def snapshot(self):
        with self._lock:
            d = json.loads(json.dumps(self._data))
        d['snapshot_at'] = _now_iso()
        d['pipeline'].pop('step1_total_ms', None)
        d['pipeline'].pop('step3_total_ms', None)
        d['llm']['avg_latency_ms'] = (
            round(d['llm']['total_latency_ms'] / d['llm']['total_calls'], 1)
            if d['llm']['total_calls'] > 0 else 0
        )
        d['llm']['total_latency_ms'] = round(d['llm']['total_latency_ms'], 0)
        return d

    def flush(self):
        """将当前快照写入 logs/metrics.jsonl."""
        path = os.path.join(LOGS_DIR, 'metrics.jsonl')
        snap = self.snapshot()
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(snap, ensure_ascii=False) + '\n')
        return snap


def get_metrics():
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics


def reset_metrics():
    global _metrics
    _metrics = MetricsCollector()
    return _metrics


def export_metrics():
    return get_metrics().flush()
