# Spec Delta

## Purpose

Provide structured, correlation-id-linked audit and timing records for the ask and ingest pipelines, so a processed question (or ingest run) leaves an observable trail and debugging no longer requires guessing.

## ADDED Requirements

### Requirement: Startup configuration and variables audit

The system SHALL log the effective configuration and every variable in play at startup - the chat and embedding models, the thinking-disabled flag, the Ollama host, the database host and database name with credentials redacted, retrieval top_k, temperature, and the active log level/file - so drift between changes is visible.

#### Scenario: Startup emits a config record

- **WHEN** the API service or the ingest CLI starts
- **THEN** a `config` log record exists containing the effective variables (chat/embed models, think flag, host, redacted database host/db, top_k, temperature, log level, log file)

#### Scenario: Credentials are not leaked

- **WHEN** the startup config record is written
- **THEN** the database value contains no username or password

### Requirement: Per-request audit with timing

The system SHALL log a correlation-id-linked trail for each question with per-stage timings (retrieve, synthesize, verify) and a summary containing outcome, citation count, and total time, and SHALL log the variables in play (model, top_k, temperature, think flag). Timing SHALL NOT change the API response body.

#### Scenario: Question produces a correlated timed trail

- **WHEN** an analyst submits a question to the ask endpoint
- **THEN** the logs contain `ask` and `ask_done` records sharing one request id, with per-stage durations and an `ask_done` total that includes outcome and citation count

#### Scenario: Empty synthesized answer is a warning

- **WHEN** the synthesised answer is empty
- **THEN** a WARNING log record identifies the request

### Requirement: LLM call visibility

The system SHALL log the model, endpoint, payload and response sizes, and duration for each chat or embed call, and SHALL warn whenever a chat response is empty regardless of log level.

#### Scenario: Chat call is logged with duration

- **WHEN** a chat call completes
- **THEN** a log record exists with the model, endpoint, prompt and response sizes, and a non-negative duration

#### Scenario: Empty chat response warns

- **WHEN** a chat call returns empty text
- **THEN** a WARNING log record names the model and endpoint

### Requirement: Ingest run audit

The system SHALL log the source key, page and chunk counts, embed batch timings, and total time for an ingest run.

#### Scenario: Ingest run is auditable

- **WHEN** an ingest run completes
- **THEN** the logs contain ingest, extraction, per-batch embed timing, store, and done records with counts and total time
