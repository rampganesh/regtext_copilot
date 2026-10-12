from sqlalchemy import select

from db.base import SessionLocal
from db.models import Chunk, Source, SourceVersion
from llm import llm


def _resolve_status(version, as_of_date):
    if version.effective_from is not None and as_of_date < version.effective_from:
        return 'future-effective'
    return 'final/operative'


def retrieve(question, as_of_date, top_k=5):
    qvec = llm.embed([question])[0]
    session = SessionLocal()
    try:
        rows = session.execute(
            select(Chunk, Source, SourceVersion)
            .join(SourceVersion, Chunk.version_id == SourceVersion.id)
            .join(Source, SourceVersion.source_id == Source.id)
            .where(Source.approval_state == 'active')
            .where(SourceVersion.published_date <= as_of_date)
            .order_by(Chunk.embedding.cosine_distance(qvec))
            .limit(top_k)
        ).all()
        return [
            {
                'location_id': chunk.location_id,
                'content': chunk.content,
                'title': source.title,
                'doc_type': source.doc_type,
                'status': _resolve_status(version, as_of_date),
                'status_date': str(version.effective_from),
            }
            for chunk, source, version in rows
        ]
    finally:
        session.close()
