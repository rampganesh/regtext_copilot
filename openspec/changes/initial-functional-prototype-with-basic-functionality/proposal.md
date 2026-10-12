# Proposal

## Why

RegCopilot V1 is an evidence-led Retrieval-Augmented Generation research assistant for UK Basel 3.1 regulatory reporting analysts, but only planning artefacts exist today - there is no running software. The earliest valuable slice is the walking skeleton (one question in, one verified, evidence-led answer out), built on a minimal corpus. This change delivers that minimum so the workflow can be exercised end to end before further vertical features are added.

## What Changes

- Add a minimal, runnable backend that ingests a regulatory PDF, chunks it, embeds the chunks with a local model, and stores them for retrieval in PostgreSQL with pgvector.
- Add a single ask endpoint that accepts a natural-language question plus an as-of date and returns an evidence-led answer with verifiable, non-fabricated citations.
- Serve the frozen prototype UI and wire its ask action to the real endpoint behind a demo flag.
- Use local model serving (Ollama) for embeddings and synthesis, behind a swappable provider adapter.

## Capabilities

### New Capabilities

- ask-answer: the core search-and-answer capability - given a question and an as-of date, return a relevant, evidence-led answer with citations whose quoted text is verified against the stored corpus.
- corpus-ingest: load, chunk, embed and store approved regulatory documents so they are addressable and retrievable by the ask-answer capability.

### Modified Capabilities

(none - greenfield)

## Impact

- New backend project structure, FastAPI app, database schema and migrations, ingest pipeline, retrieval, synthesis, and verify modules.
- PostgreSQL plus pgvector database (native service; no Docker available on this machine).
- Local Ollama models (bge-base-en-v1.5 for embeddings, gemma4:12b for synthesis) behind a provider adapter.
- The frozen prototype HTML is served by the backend; only the ask function is edited.

