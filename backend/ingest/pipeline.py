from db.base import SessionLocal
from db.models import Chunk, Source, SourceVersion
from ingest.extract import assign_location_ids, chunk_pages, extract_text
from llm import llm


def ingest_pdf(pdf_path, source_key, title, doc_type, subject_area, published, effective_from, approve=False, max_chunks=None):
    pages = extract_text(pdf_path)
    chunks = assign_location_ids(chunk_pages(pages))
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
        vectors = llm.embed(texts)
        for chunk, vec in zip(chunks, vectors):
            session.add(Chunk(
                version_id=version.id, chunk_type=chunk['type'],
                location_id=chunk['location_id'], page_ref=chunk['page'],
                content=chunk['text'], embedding=vec,
            ))
        session.commit()
        return len(chunks)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
