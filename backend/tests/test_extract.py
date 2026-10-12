from ingest.extract import assign_location_ids, chunk_pages, split_paragraphs


def test_split_paragraphs():
    text = 'first paragraph\n\nsecond paragraph\n\nthird'
    parts = split_paragraphs(text)
    assert parts == ['first paragraph', 'second paragraph', 'third']


def test_chunk_pages_non_empty():
    pages = ['alpha para\n\nbeta para']
    chunks = chunk_pages(pages)
    assert len(chunks) == 2
    assert all(c['text'] for c in chunks)


def test_location_ids_unique():
    pages = ['a', 'b']
    chunks = assign_location_ids(chunk_pages(pages))
    ids = [c['location_id'] for c in chunks]
    assert len(set(ids)) == len(ids)
