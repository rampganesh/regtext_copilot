import json
import logging

from logging_setup import get_logger, log_event, new_request_id, timed


def test_timed_emits_duration_ms(caplog):
    logger = get_logger('test.timed')
    with caplog.at_level(logging.DEBUG, logger=logger.name):
        with timed(logger, 'demo_event', request_id='rid123', phase='x'):
            pass
    rec = [r for r in caplog.records if r.getMessage() == 'demo_event'][-1]
    assert rec.data['duration_ms'] >= 0
    assert rec.data['request_id'] == 'rid123'
    assert rec.data['phase'] == 'x'


def test_new_request_id_format():
    rid = new_request_id()
    assert isinstance(rid, str) and len(rid) == 8
    int(rid, 16)  # hex


def test_ask_logs_correlation_id(monkeypatch, caplog):
    from api import main

    monkeypatch.setattr(main, 'retrieve', lambda q, d: [{
        'location_id': 'p1', 'content': 'c', 'title': 't', 'doc_type': 'x',
        'status': 'final/operative', 'status_date': '2026-01-01',
    }])
    monkeypatch.setattr(main, 'synthesize', lambda q, r: 'The relevant sources indicate y.')
    monkeypatch.setattr(main, 'sanitize_html', lambda s: s)

    from fastapi.testclient import TestClient
    with caplog.at_level(logging.DEBUG, logger=get_logger('api').name):
        resp = TestClient(main.app).post('/api/v1/ask', json={'question': 'q'})
    assert resp.status_code == 200

    ask_recs = [r for r in caplog.records if getattr(r, 'data', {}).get('request_id')]
    rids = {r.data['request_id'] for r in ask_recs}
    assert len(rids) == 1
    assert any(r.getMessage() == 'ask_done' for r in ask_recs)


def test_json_formatter_structure():
    import logging_setup
    fmt = logging_setup._JsonFormatter()
    logger = logging.getLogger('jsonfmt.test')
    logger.setLevel(logging.DEBUG)
    import io
    from logging import StreamHandler
    stream = io.StringIO()
    h = StreamHandler(stream)
    h.setFormatter(fmt)
    logger.addHandler(h)
    log_event(logger, 'demo', request_id='rid1', n=3)
    line = stream.getvalue().strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload['event'] == 'demo'
    assert payload['request_id'] == 'rid1'
    assert payload['n'] == 3
    assert payload['level'] == 'INFO'
    logger.removeHandler(h)
