import logging
import time

from db.base import SessionLocal
from db.models import Chunk, Source, SourceVersion
from ingest.extract import assign_location_ids, chunk_pages, extract_text
from llm import llm
from logging_setup import get_logger, log_event, timed

_log = get_logger('ingest')


def ingest_pdf(pdf_path, source_key, title, doc_type, subject_area, published, effective_from, approve=False, max_chunks=None):
    total_start = time.perf_counter()
    from config import OLLAMA_EMBED_MODEL
    log_event(_log, 'ingest', pdf=str(pdf_path), source_key=source_key, embed_model=OLLAMA_EMBED_MODEL)

    with timed(_log, 'extract', level=logging.DEBUG):
        pages = extract_text(pdf_path)
    chunks = assign_location_ids(chunk_pages(pages))
    log_event(_log, 'extract_done', level=logging.DEBUG, pages=len(pages), chunks=len(chunks))
    if max_chunks is not None:
        chunks = chunks[:max_chunks]

    session = SessionLocal()
    try:
        source = session.query(Source).filter_by(source_key=source_key).first()
        if source is None:
            source = Source(
                source_key=source_key, title=title, doc_type=doc_type,
                subject_area=subject_area, approval_state='active' if approve else 'pending',
                content_owner='Regulatory Content Owner',
            )
            session.add(source)
            session.flush()

        version = SourceVersion(
            source_id=source.id, version_label='v1', published_date=published,
            effective_from=effective_from, pdf_path=pdf_path,
        )
        session.add(version)
        session.flush()

        texts = [c['text'] for c in chunks]
        with timed(_log, 'embed_all', level=logging.DEBUG, n_texts=len(texts)):
            vectors = llm.embed(texts)
        with timed(_log, 'store', level=logging.DEBUG):
            for chunk, vec in zip(chunks, vectors):
                session.add(Chunk(
                    version_id=version.id, chunk_type=chunk['type'],
                    location_id=chunk['location_id'], page_ref=chunk['page'],
                    content=chunk['text'], embedding=vec,
                ))
            session.commit()
        log_event(_log, 'stored', level=logging.DEBUG, chunks=len(chunks))
        total_ms = round((time.perf_counter() - total_start) * 1000, 1)
        log_event(_log, 'ingest_done', chunks=len(chunks), total_ms=total_ms, source_key=source_key)
        return len(chunks)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
