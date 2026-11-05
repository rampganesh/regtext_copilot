# Tasks

## 1. Logging module

- [x] 1.1 Create `backend/logging_setup.py`: JSON formatter (ts/level/logger/event/fields), stdout + rotating-file handlers, env `LOG_LEVEL`/`LOG_FILE`, idempotent `setup_logging()` with `NullHandler` fallback for any handler-config error (verify: a unit test parses a logged line's JSON payload)
- [x] 1.2 Add `new_request_id()` and the `timed()` / `log_event()` helpers so stage durations and correlation IDs are produced from one place (verify: unit test asserts `duration_ms` and `request_id` are present on the emitted record)

## 2. Ask pipeline instrumentation

- [x] 2.1 In `api/main.py`, call `setup_logging()` and emit a startup `config` record with the effective variables (chat/embed models, think flag, ollama host, redacted db host/db, top_k, temperature, log level/file) via a lifespan handler (verify: startup log shows the record; no `on_event` deprecation warning)
- [x] 2.2 Emit `ask` (with the variables in play), per-stage `timed()` events for retrieve/synthesize/verify, a WARNING `empty_answer` event, and an INFO `ask_done` summary with outcome, citation count, and total_ms (verify: one request id links the trail; pytest `test_ask_logs_correlation_id` passes)
- [x] 2.3 Never alter the `/api/v1/ask` response body because of logging (verify: response JSON shape unchanged)

## 3. LLM adapter instrumentation

- [x] 3.1 In `llm.py`, log `llm_chat` (model, endpoint, prompt/response sizes, duration_ms) and `llm_embed` (model, n_texts, duration_ms) at DEBUG, and embed batches as `embed_batch` (verify: a chat call appears in the log with non-negative duration)
- [x] 3.2 Emit a WARNING when a chat response is empty (verify: warning fires when response is empty, regardless of log level)

## 4. Ingest instrumentation

- [x] 4.1 In `ingest/pipeline.py`, log `ingest` (source key, embed model), `extract_done` (pages, chunks), `embed_all`/`embed_batch` timings, `store`, and `ingest_done` (total_ms) (verify: an ingest run produces this event sequence)
- [x] 4.2 In `ingest/cli.py`, call `setup_logging()` before ingesting (verify: CLI run prints the audit trail)

## 5. Docs, hygiene, tests

- [x] 5.1 README: document `LOG_LEVEL`/`LOG_FILE` and that startup emits the effective-variables `config` record (verify: the section reads with examples)
- [x] 5.2 `.gitignore`: add `backend/logs/` (verify: the file lists it)
- [x] 5.3 Add `backend/tests/test_logging.py` with duration/correlation/JSON-format tests and get the full pytest suite green (verify: `python -m pytest backend/tests -q` passes)

## Workflow follow-up

- Archive the change after review requirements are satisfied.
