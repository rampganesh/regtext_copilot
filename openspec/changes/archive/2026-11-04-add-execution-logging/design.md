# Design

## Context

The backend is a small FastAPI + Ollama + PostgreSQL prototype with no logging at all. The
session that produced this change repeatedly hit config and timing blind spots (an invisible
`.env` model override, empty thinking-mode responses, unlocalizable LLM slowness). See
proposal.md - Why. The approach must stay within the library's-only, no-new-dependency rule and
must not change the frozen `/api/v1/ask` response shape.

## Goals / Non-Goals

**Goals:**
- One place controlling log format, level, and handlers (`logging_setup.py`).
- A startup `config` record listing every variable in play, enabling diff-across-changes audit.
- Correlation-id-linked, per-stage timed trail per question (retrieve, synthesize, verify) and
  per LLM call (chat/embed), plus ingest-run events.
- Quiet by default at INFO: audit/startup/outcome lines only; stage timing and per-LLM-call detail
  at DEBUG. Warnings (empty/slow) always visible.

**Non-Goals:**
- DB-backed audit table (deferred; file + stdout enough for the local prototype).
- Timing data in the API response body or a metrics endpoint (response contract stays frozen).
- Reworking the eval harness logging (it times itself).

## Decisions

- **Stdlib `logging`, JSON records.** Zero new dependencies, matching the project's libraries-only
  constraint. Alternatives considered: structlog/loguru (rejected - new dependency; the project
  explicitly rejects framework churn), the stdlib text format (rejected - not machine-parseable for
  audit diffing).
- **stdout + rotating file.** `StreamHandler` for development visibility plus
  `RotatingFileHandler` (5 MB x 3) under `backend/logs/` for a durable local trail. Alternative:
  DB-backed audit (deferred) and stdout-only (loses history).
- **JSON single event per record** via a small `log_event`/`timed` helper, so format, field names,
  and handlers have one source of truth. A 4-line change per call site, instead of free-form
  `logger.info(f"...")` strings.
- **Per-request correlation id** (8-hex uuid) echoed on every record for a question, so the whole
  pipeline of one ask is reconstructable after the fact.
- **Logging can never break the request path**: `setup_logging()` is idempotent and falls back to
  `NullHandler` on any handler-config error; the logs directory is created with
  `mkdir(parents=True, exist_ok=True)`.

## Risks / Trade-offs

- Log noise from big prompts → never log embeddings or full chunk bodies; question text truncated to
  200 chars.
- INFO-level verbosity → default level is a curated quiet set (config/ask_done/ingest_done/warnings);
  detail is opt-in via `LOG_LEVEL=DEBUG`.
- A config write failure must not take the service down → handled by the NullHandler fallback above.
