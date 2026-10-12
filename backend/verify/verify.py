import re


def normalize(text):
    return re.sub(r'\s+', ' ', text or '').strip()


def verify_verbatim(citation_text, chunk_content):
    cleaned = _strip_tags(citation_text)
    if not cleaned:
        return False
    return normalize(cleaned) in normalize(chunk_content)


def _strip_tags(text):
    return re.sub(r'<[^>]+>', '', text or '')


def sanitize_html(text):
    if text is None:
        return ''
    # Drop script blocks and their contents entirely.
    text = re.sub(r'(?is)<script.*?</script>', '', text)
    # Only keep span tags whose class is hl or qual; strip all other tags
    # (including their attributes) and all other inline markup.
    out = []
    i = 0
    for m in re.finditer(r'<[^>]+>', text):
        out.append(text[i:m.start()])
        tag = m.group(0)
        if _keep(tag):
            out.append(tag)
        i = m.end()
    out.append(text[i:])
    return ''.join(out)


def _keep(tag):
    body = tag.lower()
    if body.startswith('</span>'):
        return True
    if body.startswith('<span'):
        return (('class=hl' in body and 'hl' in body) or ('class=qual' in body))
    return False
