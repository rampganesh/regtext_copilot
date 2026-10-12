from verify.verify import sanitize_html, verify_verbatim


def test_verify_verbatim_passes_exact():
    assert verify_verbatim('output floor', 'The output floor is 72.5%.') is True


def test_verify_verbatim_normalizes_whitespace():
    assert verify_verbatim('output   floor', 'The output floor is X.') is True


def test_verify_verbatim_rejects_fabrication():
    assert verify_verbatim('this text does not exist', 'The output floor is X.') is False


def test_verify_verbatim_strips_tags():
    assert verify_verbatim('<span class=hl>output floor</span>', 'The output floor is X.') is True


def test_sanitizer_keeps_hl_and_qual():
    out = sanitize_html('<span class=hl>x</span> and <span class=qual>y</span>')
    assert '<span class=hl>' in out
    assert '<span class=qual>' in out


def test_sanitizer_strips_script():
    out = sanitize_html('<script>alert(1)</script>hello')
    assert 'alert' not in out
    assert 'hello' in out


def test_sanitizer_strips_other_tags():
    out = sanitize_html('<b>bold</b><span class=hl>keep</span>')
    assert '<b>' not in out
    assert '<span class=hl>' in out


def test_sanitizer_empty():
    assert sanitize_html(None) == ''
