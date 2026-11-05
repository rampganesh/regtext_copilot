"""Single source of truth for RegCopilot execution logging.

JSON-structured stdlib logging to stdout plus a rotating file, with a small
`timed` context manager for per-stage durations and short request IDs for
correlating a question's stages. Zero new dependencies; a config error falls
back to a no-op handler so logging can never break the request path.
"""

import json
import logging
import logging.handlers
import os
import sys
import time
import uuid
from contextlib import contextmanager

import config

_configured = False

_LOGS_DIR_NAME = 'logs'
_DEFAULT_LOG_FILE = 'regcopilot.log'


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            'ts': self.formatTime(record, '%Y-%m-%dT%H:%M:%S'),
            'level': record.levelname,
            'logger': record.name,
            'event': record.getMessage(),
        }
        data = getattr(record, 'data', None)
        if isinstance(data, dict):
            payload.update(data)
        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging():
    """Configure root logging once. Idempotent; on any handler error, no-op."""
    global _configured
    if _configured:
        return
    _configured = True

    level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = os.environ.get('LOG_FILE', None)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))

    try:
        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(_JsonFormatter())
        root.addHandler(stream)

        if log_file is None:
            log_file = str(_logs_dir() / _DEFAULT_LOG_FILE)
        path = os.fspath(log_file)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        rotating = logging.handlers.RotatingFileHandler(
            path, maxBytes=5_000_000, backupCount=3, encoding='utf-8'
        )
        rotating.setFormatter(_JsonFormatter())
        root.addHandler(rotating)
    except Exception:
        root.addHandler(logging.NullHandler())


def _backend_dir():
    from pathlib import Path

    return Path(__file__).resolve().parent


def _logs_dir():
    return _backend_dir() / _LOGS_DIR_NAME


def get_logger(name):
    return logging.getLogger('regcopilot.' + name)


def new_request_id():
    return uuid.uuid4().hex[:8]


def log_event(logger, event, level=logging.INFO, request_id=None, **fields):
    data = dict(fields)
    if request_id is not None:
        data['request_id'] = request_id
    logger.log(level, event, extra={'data': data})


@contextmanager
def timed(logger, event, level=logging.DEBUG, request_id=None, **fields):
    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        log_event(logger, event, level=level, request_id=request_id, duration_ms=duration_ms, **fields)
