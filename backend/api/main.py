from datetime import date
from pathlib import Path
import logging
import os
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from retrieval.retrieve import retrieve
from synthesis.synthesize import synthesize
from verify.verify import sanitize_html

import logging_setup
import config as _config

logging_setup.setup_logging()
_log = logging_setup.get_logger('api')

TOP_K = 5


def _db_summary():
    url = _config.DATABASE_URL
    try:
        scheme, rest = url.split('://', 1)
        if '@' in rest:
            rest = rest.split('@', 1)[1]
        return scheme + '://' + rest
    except ValueError:
        return 'unparsed'


def _log_config():
    logging_setup.log_event(
        _log,
        'config',
        chat_model=_config.OLLAMA_CHAT_MODEL,
        embed_model=_config.OLLAMA_EMBED_MODEL,
        think_disabled=True,
        temperature=0,
        ollama_host=_config.OLLAMA_HOST,
        db=_db_summary(),
        top_k=TOP_K,
        log_level=os.environ.get('LOG_LEVEL', 'INFO').upper(),
        log_file=os.environ.get('LOG_FILE', 'backend/logs/regcopilot.log'),
    )


from contextlib import asynccontextmanager


@asynccontextmanager
async def _lifespan(app):
    _log_config()
    yield


app = FastAPI(title='RegCopilot', lifespan=_lifespan)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    asOfDate: str | None = None


def _default_asof():
    return date.today().isoformat()


def _to_date(value):
    return date.fromisoformat(value)


@app.post('/api/v1/ask')
def ask(req: AskRequest):
    request_id = logging_setup.new_request_id()
    total_start = time.perf_counter()

    as_of = req.asOfDate or _default_asof()
    try:
        as_of_date = _to_date(as_of)
    except ValueError:
        return JSONResponse(status_code=422, content={'error': 'invalid asOfDate'})

    logging_setup.log_event(
        _log,
        'ask',
        request_id=request_id,
        question=req.question[:200],
        as_of=str(as_of_date),
        chat_model=_config.OLLAMA_CHAT_MODEL,
        top_k=TOP_K,
        temperature=0,
        think_disabled=True,
    )

    with logging_setup.timed(_log, 'retrieve', request_id=request_id, top_k=TOP_K):
        results = retrieve(req.question, as_of_date)

    if not results:
        logging_setup.log_event(
            _log, 'ask_done', request_id=request_id, outcome='no_results',
            n_citations=0, total_ms=round((time.perf_counter() - total_start) * 1000, 1),
        )
        return _response(req.question, 'The relevant sources indicate that no active source answers this question.', [])

    logging_setup.log_event(_log, 'retrieve_done', level=logging.DEBUG,
                            request_id=request_id, n_results=len(results))

    with logging_setup.timed(_log, 'synthesize', request_id=request_id):
        answer_text = synthesize(req.question, results)

    if not answer_text.strip():
        logging_setup.log_event(_log, 'empty_answer', level=logging.WARNING,
                                request_id=request_id)

    verify_start = time.perf_counter()
    citations = []
    for r in results:
        citations.append({
            'source': {'id': r['location_id'], 'title': r['title'], 'type': r['doc_type'],
                       'publishedDate': r['status_date'], 'status': r['status'], 'statusDate': r['status_date']},
            'location': r['location_id'],
            'passage': sanitize_html(r['content']),
            'definitions': [],
        })
    verify_ms = round((time.perf_counter() - verify_start) * 1000, 1)
    logging_setup.log_event(_log, 'verify', level=logging.DEBUG,
                            request_id=request_id, duration_ms=verify_ms)

    logging_setup.log_event(
        _log,
        'ask_done',
        request_id=request_id,
        outcome='answer',
        n_citations=len(citations),
        total_ms=round((time.perf_counter() - total_start) * 1000, 1),
    )

    return _response(req.question, answer_text, citations)


def _response(question, answer_text, citations):
    return {
        'question': question,
        'answer': [{'text': answer_text}],
        'conflict': None,
        'citations': citations,
        'definitions': {},
    }


ROOT = Path(__file__).resolve().parent.parent.parent
PROTOTYPE = ROOT / 'artefacts' / 'regcopilot-prototype.html'


@app.get('/')
def index():
    return FileResponse(PROTOTYPE)
