# Proposal

## Why

The prototype backend runs with zero execution logging or timing: an analyst question (or an
ingest run) leaves no audit trail, and debugging this session surfaced real costs from that gap -
a pinned `.env` model override was invisible, thinking-mode models returned empty answers
silently, and slow LLM calls could not be localized. Adding structured, timing-bearing logs makes
the system auditable and debuggable without changing any user-facing behavior.

## What Changes

- Add a shared logging module (`backend/logging_setup.py`): JSON-structured stdlib logging to
  stdout and a rotating file, a `timed()` stage-timing helper, and short per-request correlation
  IDs.
- Emit a startup `config` audit record listing every variable in play (chat/embed models, think
  flag, host, DB host/db with credentials redacted, top_k, temperature, log level/file).
- Instrument the ask pipeline (`/api/v1/ask`) with correlation-ID-linked events and per-stage
  durations (retrieve, synthesize, verify), an `empty_answer` warning, and an INFO `ask_done`
  summary with outcome, citation count, and total time.
- Instrument the LLM adapter (`llm.py`) with per-call duration + sizes (DEBUG) and an empty-response
  warning.
- Instrument the ingest pipeline/CLI with run, extraction, embed-batch, store, and done events.
- Document the log level/file variables in the README; add `backend/logs/` to `.gitignore`; add
  logging tests.

No change to the `/api/v1/ask` response contract; timing is visible in logs only.

## Capabilities

### New Capabilities

- `execution-logging`: structured, correlation-ID-linked audit and timing records for the ask and
  ingest pipelines, covering startup configuration/variables audit, per-request stage timings, LLM
  call visibility, and ingest run audit.

### Modified Capabilities

(none - ask-answer and corpus-ingest behaviors are unchanged; this is additive observability.)

## Impact

- New module `backend/logging_setup.py`; edits to `api/main.py`, `llm.py`,
  `ingest/pipeline.py`, `ingest/cli.py`.
- Doc/config: `README.md` logging section; `backend/logs/` added to `.gitignore`; optional
  `LOG_LEVEL` / `LOG_FILE` env vars (defaults: INFO, `backend/logs/regcopilot.log`).
- New tests in `backend/tests/test_logging.py`.
- No new dependencies (Python stdlib `logging` only); no database or schema change.
