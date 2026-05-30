"""结构化 JSON 日志模块 — 自动轮转，分类输出."""

import logging
import json
import os
import sys
import time
import threading
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# 北京时区
TZ_BEIJING = timezone(timedelta(hours=8))

_loggers = {}


def _beijing_time(*args):
    """返回北京时间 ISO 格式字符串."""
    return datetime.now(TZ_BEIJING).isoformat(timespec='milliseconds')


class JsonFormatter(logging.Formatter):
    """JSON lines 格式化器."""

    def format(self, record):
        entry = {
            'ts': _beijing_time(),
            'level': record.levelname,
            'logger': record.name,
            'msg': record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            entry['exc'] = str(record.exc_info[1])
        for k in ('event', 'elapsed_ms', 'rows', 'model', 'tokens', 'purpose', 'status'):
            if hasattr(record, k):
                entry[k] = getattr(record, k)
        return json.dumps(entry, ensure_ascii=False)


def _make_handler(filename, max_bytes=10 * 1024 * 1024, backup_count=5):
    """创建 RotatingFileHandler."""
    path = os.path.join(LOGS_DIR, filename)
    handler = RotatingFileHandler(path, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
    handler.setFormatter(JsonFormatter())
    return handler


_setup_lock = threading.Lock()

def setup_logging():
    """初始化全部 logger（幂等）."""
    if _loggers:
        return
    with _setup_lock:
        if _loggers:
            return

        # pipeline 日志
        pl = logging.getLogger('pipeline')
        pl.setLevel(logging.DEBUG)
        pl.addHandler(_make_handler('pipeline.log'))
        pl.propagate = False

        # LLM 调用日志
        llm = logging.getLogger('llm')
        llm.setLevel(logging.DEBUG)
        llm.addHandler(_make_handler('llm_calls.log'))
        llm.propagate = False

        # 应用日志
        app = logging.getLogger('app')
        app.setLevel(logging.DEBUG)
        h = _make_handler('app.log')
        h.setLevel(logging.DEBUG)
        app.addHandler(h)
        app.propagate = False

        _loggers['pipeline'] = pl
        _loggers['llm'] = llm
        _loggers['app'] = app


def get_logger(name='app'):
    """获取 logger，自动初始化."""
    setup_logging()
    return _loggers.get(name, logging.getLogger(name))


def log_event(logger_name, msg, **kwargs):
    """便捷事件日志."""
    logger = get_logger(logger_name)
    extra = kwargs
    record = logger.makeRecord(logger.name, logging.INFO, '', 0, msg, (), None)
    for k, v in extra.items():
        setattr(record, k, v)
    logger.handle(record)
