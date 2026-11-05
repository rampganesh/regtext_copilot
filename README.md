# RegCopilot V1 - initial functional prototype

A minimal evidence-led research assistant for UK Basel 3.1 questions: ingest a PDF,
embed its paragraphs with a local model, store them in PostgreSQL with pgvector, and
answer questions with verified citations.

## Prerequisites

- Python 3.12 (use the project virtualenv .venv)
- PostgreSQL 16+ with the pgvector extension
- Ollama running on http://localhost:11434 with these models pulled:
  - hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest (embeddings)
  - gemma4:12b (chat, optional baseline)
  - nemotron-3-nano:4b (chat, synthesis default; invoked with thinking disabled)

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

## Logging and timing

The backend emits structured (JSON) execution logs for audit and debugging with timing.

- Level: `LOG_LEVEL` env (default `INFO`). Set `LOG_LEVEL=DEBUG` to see per-stage timings and
  per-LLM-call detail.
- File: rotating file `backend/logs/regcopilot.log` (override with `LOG_FILE`), plus stdout.
- Startup emits a `config` record with the effective variables (models, think flag, host, db
  host/db with credentials redacted, top_k, temperature, log level/file).
- Each `POST /api/v1/ask` emits a `request_id`-correlated trail: `ask` (incl. variables in play),
  `retrieve`/`retrieve_done`/`synthesize`/`verify` (timings), `empty_answer` (warning),
  `ask_done` (outcome, citation count, total_ms). LLM calls emit `llm_chat`/`llm_embed` with
  duration and sizes; ingest emits `ingest`/`extract_done`/`embed_batch`/`stored`/`ingest_done`.

## Test

 cd backend && python -m pytest
