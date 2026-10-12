import re

import pymupdf as fitz

MAX_WORDS = 300


def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        pages.append(page.get_text('text'))
    doc.close()
    return pages


def split_paragraphs(text):
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text)]
    return [b for b in blocks if b]


def _hard_split_words(text, max_words):
    words = text.split()
    out = []
    for i in range(0, len(words), max_words):
        out.append(' '.join(words[i:i + max_words]))
    return out


def _split_long(text, max_words):
    words = text.split()
    if len(words) <= max_words:
        return [text]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    parts = []
    current = []
    count = 0
    for s in sentences:
        add = len(s.split())
        if add > max_words:
            if current:
                parts.append(' '.join(current))
                current = []
                count = 0
            parts.extend(_hard_split_words(s, max_words))
        elif current and count + add > max_words:
            parts.append(' '.join(current))
            current = [s]
            count = add
        else:
            current.append(s)
            count += add
    if current:
        parts.append(' '.join(current))
    return parts


def chunk_pages(pages):
    chunks = []
    for page_index, page_text in enumerate(pages):
        for para in split_paragraphs(page_text):
            for sub in _split_long(para, MAX_WORDS):
                chunks.append({'page': page_index + 1, 'text': sub, 'type': 'paragraph'})
    return chunks


def assign_location_ids(chunks):
    for i, chunk in enumerate(chunks):
        chunk['location_id'] = 'p%s-%s' % (chunk['page'], i)
    return chunks
