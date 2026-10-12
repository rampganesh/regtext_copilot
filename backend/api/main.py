from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from retrieval.retrieve import retrieve
from synthesis.synthesize import synthesize
from verify.verify import sanitize_html

app = FastAPI(title='RegCopilot')


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    asOfDate: str | None = None


def _default_asof():
    return date.today().isoformat()


def _to_date(value):
    return date.fromisoformat(value)


@app.post('/api/v1/ask')
def ask(req: AskRequest):
    as_of = req.asOfDate or _default_asof()
    try:
        as_of_date = _to_date(as_of)
    except ValueError:
        return JSONResponse(status_code=422, content={'error': 'invalid asOfDate'})

    results = retrieve(req.question, as_of_date)
    if not results:
        return _response(req.question, 'The relevant sources indicate that no active source answers this question.', [])

    answer_text = synthesize(req.question, results)
    citations = []
    for r in results:
        citations.append({
            'source': {'id': r['location_id'], 'title': r['title'], 'type': r['doc_type'],
                       'publishedDate': r['status_date'], 'status': r['status'], 'statusDate': r['status_date']},
            'location': r['location_id'],
            'passage': sanitize_html(r['content']),
            'definitions': [],
        })
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
