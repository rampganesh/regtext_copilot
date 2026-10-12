import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date
from ingest.pipeline import ingest_pdf

def main():
    pdf = sys.argv[1]
    source_key = sys.argv[2] if len(sys.argv) > 2 else 'ps126'
    title = sys.argv[3] if len(sys.argv) > 3 else 'PS1/26'
    doc_type = sys.argv[4] if len(sys.argv) > 4 else 'policy-statement'
    subject = sys.argv[5] if len(sys.argv) > 5 else 'Basel 3.1'
    n = ingest_pdf(pdf, source_key, title, doc_type, subject, date(2026, 1, 1), date(2027, 1, 1), approve=True)
    print('ingested %d chunks' % n)

if __name__ == '__main__':
    main()
