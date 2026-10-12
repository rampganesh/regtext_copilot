# RegCopilot V1 - initial functional prototype

A minimal evidence-led research assistant for UK Basel 3.1 questions: ingest a PDF,
embed its paragraphs with a local model, store them in PostgreSQL with pgvector, and
answer questions with verified citations.

## Prerequisites

- Python 3.12 (use the project virtualenv .venv)
- PostgreSQL 16+ with the pgvector extension
- Ollama running on http://localhost:11434 with these models pulled:
  - hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest (embeddings)
  - gemma4:12b (chat)

## Setup

1. Copy .env.example to .env and fill in DATABASE_URL and model names.
2. Install dependencies:
   pip install -r backend/requirements.txt
3. Create the schema (requires an active DATABASE_URL):
   cd backend && alembic upgrade head

## Ingest a document

    cd backend
    python ingest/cli.py ../docs/ps126app1.pdf ps126 PS1/26 policy-statement Basel\ 3.1

## Run the API

    cd backend
    uvicorn api.main:app --reload

Then open http://localhost:8000/ for the prototype UI, or POST a question:

    curl -X POST http://localhost:8000/api/v1/ask -H Content-Type: application/json \
      -d '{" question\:\What is the output floor?\,\asOfDate\:\2027-01-01\}'

## Test

 cd backend && python -m pytest
